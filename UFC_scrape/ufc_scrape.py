from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import re
import traceback
from datetime import datetime
from dateutil.parser import parse as parse_date
import mysql.connector

def sanitize(value, convert_func=None):
    """Converts '--' to None. If convert_func is provided, applies it to the sanitized value."""
    if value == "--":
        return None
    return convert_func(value) if convert_func else value

def scrape_ufc_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://www.ufcstats.com/statistics/fighters")

        base_url = "http://www.ufcstats.com"
        letter_links = page.query_selector_all("ul.b-statistics__nav-items li a")
        letter_urls = []

        # MYSQL Connection
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='7b8f9m2e',
            database='ufc_data'
        )
        cursor = conn.cursor()

        for link in letter_links:
            href = link.get_attribute("href")
            if href and "char=" in href:
                full_url = urljoin(base_url, href)
                letter_urls.append(full_url)

        for letter_url in letter_urls:
            current_page = 1
            page.goto(letter_url)
            print(f"\n Scraping letter tab: {letter_url}")

            while True:
                print(f"Scraping page: {page.url}")
                rows = page.query_selector_all("tr.b-statistics__table-row")

                for row in rows:
                    try:
                        cols = row.query_selector_all("td")
                        if len(cols) < 11:
                            continue

                        fname_el = cols[0].query_selector("a")
                        lname_el = cols[1].query_selector("a")
                        fname = fname_el.inner_text().strip()
                        lname = lname_el.inner_text().strip()
                        name = fname + " " + lname
                        profile_url = fname_el.get_attribute("href")

                        nickname = cols[2].query_selector("a").inner_text().strip()
                        height = sanitize(cols[3].inner_text().strip())
                        weight = sanitize(cols[4].inner_text().strip(), lambda x: int(x[:3]))
                        reach = sanitize(cols[5].inner_text().strip(), lambda x: float(x[:4]))
                        stance = sanitize(cols[6].inner_text().strip())
                        wins = int(cols[7].inner_text().strip())
                        losses = int(cols[8].inner_text().strip())
                        draws = int(cols[9].inner_text().strip())
                        belt = bool(cols[10].query_selector("img") is not None)

                        SLpM = Str_Acc = SApM = Str_Def = TD_Avg = TD_Acc = TD_Def = Sub_Avg = "N/A"
                        DOB = Age = "N/A"

                        try:
                            profile_page = context.new_page()
                            profile_page.goto(profile_url, timeout=10000)

                            try:
                                profile_page.wait_for_selector("div.b-list__info-box", timeout=15000)
                                info_blocks = profile_page.query_selector_all("div.b-list__info-box")

                                if len(info_blocks) >= 1:
                                    bio_items = info_blocks[0].query_selector_all("li")
                                    for item in bio_items:
                                        label_el = item.query_selector("i")
                                        if not label_el:
                                            continue
                                        label = label_el.inner_text().strip().lower()
                                        if "date of birth" in label or "dob" in label:
                                            dob_str = item.inner_text().replace(label_el.inner_text(), "").strip()
                                            DOB = sanitize(dob_str)
                                            if DOB:
                                                # remove any parentheses like "(Age 31)" and parse the remaining text
                                                DOB_clean = re.sub(r"\(.*?\)", "", DOB).strip()
                                                try:
                                                    dob_date = parse_date(DOB_clean, fuzzy=True).date()
                                                    today = datetime.today().date()
                                                    Age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                                                except Exception:
                                                    pass

                                if len(info_blocks) >= 2:
                                    stat_items = info_blocks[1].query_selector_all("li")
                                    for item in stat_items:
                                        label_el = item.query_selector("i")
                                        if not label_el:
                                            continue
                                        label = label_el.inner_text().strip().lower()
                                        value = item.inner_text().replace(label_el.inner_text(), "").strip()

                                        if "slpm" in label:
                                            SLpM = sanitize(value, float)
                                        elif "str. acc." in label:
                                            Str_Acc = sanitize(value.replace('%', '').strip(), int)
                                        elif "sapm" in label:
                                            SApM = sanitize(value, float)
                                        elif "str. def" in label:
                                            Str_Def = sanitize(value.replace('%', '').strip(), int)
                                        elif "td avg" in label:
                                            TD_Avg = sanitize(value, float)
                                        elif "td acc" in label:
                                            TD_Acc = sanitize(value.replace('%', '').strip(), int)
                                        elif "td def" in label:
                                            TD_Def = sanitize(value.replace('%', '').strip(), int)
                                        elif "sub. avg" in label:
                                            Sub_Avg = sanitize(value, float)
                                else:
                                    print("⚠️ Career stats block not found or malformed.")
                            except Exception as e:
                                print("⚠️ Career stats block not loaded in time.")
                                traceback.print_exc()
                        except Exception as e:
                            print(f"⚠️ Failed to open or scrape fighter profile: {e}")
                            traceback.print_exc()

                        win_streak = 0
                        try:
                            profile_page.wait_for_selector("tbody.b-fight-details__table-body", timeout=5000)
                            fight_rows = profile_page.query_selector_all("tbody.b-fight-details__table-body tr")

                            if not fight_rows:
                                print("⚠️ No fight rows found.")

                            for row in fight_rows:
                                cells = row.query_selector_all("td")
                                if not cells or len(cells) < 2:
                                    continue

                                result_text = cells[0].inner_text().strip().capitalize()

                                if result_text in {"", "--", "Scheduled"}:
                                    continue
                                if result_text == "Win":
                                    win_streak += 1
                                elif result_text in {"Loss", "Draw", "Nc"}:
                                    break
                        except Exception as e:
                            print("⚠️ Could not load or parse fight history for win streak:", e)

                        finally:
                            try:
                                profile_page.close()
                                page.wait_for_timeout(300)
                            except:
                                pass

                        if page.is_closed():
                            page = context.new_page()
                            page.goto(letter_url)


                        # MYSQL Server Pipelining
                        insert_query = """
                        INSERT INTO ufc_fighters (
                            name, nickname, dob, age, height, weight, reach, stance,
                            winstreak, wins, losses, draws, belt,
                            SLpM, Str_Acc, SApM, Str_Def, TD_Avg, TD_Acc, TD_Def, Sub_Avg
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            name,
                            nickname,
                            DOB if DOB != "N/A" else None,
                            Age if isinstance(Age, int) and Age >= 0 else None,
                            height,
                            weight,
                            reach,
                            stance,
                            win_streak,
                            wins,
                            losses,
                            draws,
                            belt,
                            SLpM if SLpM != "N/A" else 0.0,
                            Str_Acc if Str_Acc != "N/A" else 0,
                            SApM if SApM != "N/A" else 0.0,
                            Str_Def if Str_Def != "N/A" else 0,
                            TD_Avg if TD_Avg != "N/A" else 0.0,
                            TD_Acc if TD_Acc != "N/A" else 0,
                            TD_Def if TD_Def != "N/A" else 0,
                            Sub_Avg if Sub_Avg != "N/A" else 0.0
                        ))
                        conn.commit()

                        print(f"Full Name: {name} | DOB: {DOB} | Age: {Age} | Nickname: {nickname} | Height: {height} | Weight: {weight} | Reach: {reach} | Stance: {stance} | Winstreak: {win_streak} | Wins: {wins} | Losses: {losses} | Draws: {draws} | Belt: {belt} | SLpM: {SLpM} | Str. Acc: {Str_Acc} | SApM: {SApM} | Str. Def: {Str_Def} | TD Avg: {TD_Avg} | TD Acc: {TD_Acc} | TD Def: {TD_Def} | Sub. Avg: {Sub_Avg}")

                    except Exception as e:
                        print("❌ Unexpected error on fighter row:")
                        traceback.print_exc()
                        continue

                page_links = page.query_selector_all("li.b-statistics__paginate-item")
                next_link = None

                for link in page_links:
                    try:
                        text = link.inner_text().strip()
                        if text.isdigit() and int(text) == current_page + 1:
                            next_link = link
                            break
                    except:
                        continue

                if next_link:
                    current_page += 1
                    next_link.click()
                    page.wait_for_timeout(1500)
                else:
                    print(F"ALL PAGES SCRAPED FOR LETTER: {letter_url.split('=')[-1].upper()}")
                    break

        browser.close()

scrape_ufc_events()
