#!/usr/bin/env python3
"""Scrape UFC fighter stats and compute an MMA math rating.

This module mirrors the letter/pagination flow of :mod:`ufc_scrape.py`
but instead of pushing the data to MySQL it stores a subset of the
information in ``CSV`` format.  In addition to the basic bio stats we
calculate a custom "fighter rating" based on the rules provided in the
prompt.  The scraper examines each fighter's last five bouts and awards
or deducts points according to the model description.

Internet access to ``ufcstats.com`` and an installed Playwright runtime
(``playwright install``) are required for the script to run.
"""

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from datetime import datetime
from dateutil.parser import parse as parse_date
import csv
import re
import traceback

# --- Model scoring helpers --------------------------------------------------
# Base values taken from the user's MMA math model description.

# Ranking points for beating opponents based on their UFC ranking
RANK_POINTS = {i: 16 - i for i in range(16)}
RANK_POINTS[0] = 16


def sanitize(value, convert_func=None):
    """Convert placeholders and safely apply ``convert_func``.

    ``ufcstats`` occasionally embeds odd whitespace or multiple values in the
    table cells (for example ``'0\n\n1'`` for the round).  This helper makes a
    best effort to clean such artefacts before conversion so that callers do not
    have to wrap every numeric field in ``try/except`` blocks.
    """

    if value in {"--", "", None}:
        return None

    if convert_func is int:
        # Remove everything except the first integer that appears in the string.
        m = re.search(r"-?\d+", value.replace("\n", " "))
        if not m:
            return None
        value = m.group()

    try:
        return convert_func(value) if convert_func else value
    except (ValueError, TypeError):
        return None


def is_finish(method: str) -> bool:
    """Return True if ``method`` represents a stoppage (non decision)."""
    if not method:
        return False
    m = method.lower()
    return not ("decision" in m)


def compute_mma_score(fights, age, total_losses, country=None):
    """Compute a fighter rating following the MMA math rules."""

    score = 0
    finish_streak = 0
    all_wins = True

    # fights are expected oldest -> newest
    for fight in fights:
        result = fight.get("result")
        method = fight.get("method", "") or ""
        rank = fight.get("opponent_rank")
        champ = fight.get("opponent_is_champ", False)

        if result == "Win":
            if champ:
                score += RANK_POINTS[0]
            elif isinstance(rank, int) and 0 <= rank <= 15:
                score += RANK_POINTS.get(rank, 0)

            if is_finish(method):
                finish_streak += 1
                score += 5 + max(finish_streak - 1, 0)
            else:
                finish_streak = 0
                if fight.get("all_rounds_judges", False):
                    score += 5
        elif result == "Loss":
            all_wins = False
            finish_streak = 0
            if is_finish(method):
                score -= 3
            else:
                score -= 2
        else:
            all_wins = False
            finish_streak = 0

    if age is not None and age > 35:
        score -= 5 + (age - 35)

    if total_losses == 0:
        score += 5
    elif all_wins and len(fights) >= 5:
        score += 3

    if country:
        for fight in fights:
            fight_country = fight.get("fight_country") or fight.get("location_country")
            if (
                fight_country
                and fight_country == country
                and country not in {"USA", "United States"}
            ):
                score += 5
                break

    return score


def parse_recent_fights(profile_page):
    """Return dictionaries describing the fighter's last five bouts.

    The logic mirrors the win-streak scraping in ``ufc_scrape.py`` but also
    extracts additional details used by :func:`compute_mma_score`.
    """

    fights = []
    try:
        profile_page.wait_for_selector(
            "tbody.b-fight-details__table-body", timeout=5000
        )
        rows = profile_page.query_selector_all(
            "tbody.b-fight-details__table-body tr"
        )
        for row in rows:
            cells = row.query_selector_all("td")
            if not cells or len(cells) < 2:
                continue

            result_text = cells[0].inner_text().strip().capitalize()
            if result_text in {"", "--", "Scheduled"}:
                continue

            opponent_name = cells[1].inner_text().strip() if len(cells) > 1 else ""
            event_text = cells[3].inner_text().strip() if len(cells) > 3 else ""
            fight_date = None
            if event_text:
                try:
                    fight_date = parse_date(event_text, fuzzy=True).date()
                except Exception:
                    fight_date = None

            method = sanitize(cells[4].inner_text().strip()) if len(cells) > 4 else ""
            round_val = sanitize(cells[5].inner_text().strip(), int) if len(cells) > 5 else None
            time_val = sanitize(cells[6].inner_text().strip()) if len(cells) > 6 else ""

            all_rounds = (
                bool(method and "decision" in method.lower())
                and time_val == "5:00"
                and round_val in {3, 5}
            )

            location_country = None
            try:
                event_link_el = cells[2].query_selector("a") if len(cells) > 2 else None
                event_link = event_link_el.get_attribute("href") if event_link_el else None
                if event_link:
                    event_page = profile_page.context.new_page()
                    event_page.goto(event_link, timeout=10000)
                    event_page.wait_for_selector("li.b-list__box-list-item", timeout=5000)
                    for item in event_page.query_selector_all("li.b-list__box-list-item"):
                        label = (item.query_selector("strong") or item.query_selector("i"))
                        if label and "location" in label.inner_text().lower():
                            loc = item.inner_text().split(":")[-1].strip()
                            location_country = loc.split(",")[-1].strip()
                            break
                    event_page.close()
            except Exception:
                traceback.print_exc()

            # --- scrape fight details for ranking and title info ---
            opponent_rank = None
            opponent_is_champ = False
            try:
                fight_link_el = cells[1].query_selector("a")
                fight_link = fight_link_el.get_attribute("href") if fight_link_el else None
                if fight_link:
                    fight_page = profile_page.context.new_page()
                    fight_page.goto(fight_link, timeout=10000)
                    fight_page.wait_for_selector("body", timeout=5000)
                    body_text = fight_page.inner_text("body").lower()

                    champ_keywords = [
                        "title fight",
                        "title bout",
                        "championship bout",
                        "championship",
                        "world championship",
                        "ufc title",
                    ]
                    if any(k in body_text for k in champ_keywords):
                        opponent_is_champ = True

                    rank_match = re.search(r"(?:rank|ranked)\s*#?\s*(\d+)", body_text)
                    if not rank_match:
                        rank_match = re.search(r"#(\d+)", body_text)
                    if rank_match:
                        opponent_rank = int(rank_match.group(1))
                    fight_page.close()
            except Exception:
                traceback.print_exc()

            fights.append(
                {
                    "result": result_text,
                    "method": method,
                    "opponent": opponent_name,
                    "opponent_rank": opponent_rank,
                    "opponent_is_champ": opponent_is_champ,
                    "all_rounds_judges": all_rounds,
                    "location_country": location_country,
                    "date": fight_date,
                }
            )

            if len(fights) == 5:
                break
    except Exception:
        traceback.print_exc()

    return fights


def scrape_ufc_events(output_csv="fighter_mma_scores.csv"):
    """Main entry: scrape stats and MMA math score for every fighter."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://www.ufcstats.com/statistics/fighters")

        base_url = "http://www.ufcstats.com"
        letter_links = page.query_selector_all("ul.b-statistics__nav-items li a")
        letter_urls = []

        for link in letter_links:
            href = link.get_attribute("href")
            if href and "char=" in href:
                letter_urls.append(urljoin(base_url, href))

        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "name",
                "nickname",
                "age",
                "wins",
                "losses",
                "draws",
                "mma_score",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for letter_url in letter_urls:
                current_page = 1
                page.goto(letter_url)
                print(f"\nScraping letter tab: {letter_url}")
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
                            name = f"{fname} {lname}"
                            profile_url = fname_el.get_attribute("href")

                            nickname = sanitize(cols[2].inner_text().strip())
                            wins = int(cols[7].inner_text().strip())
                            losses = int(cols[8].inner_text().strip())
                            draws = int(cols[9].inner_text().strip())

                            # --- scrape profile for age and recent fights ---
                            age = None
                            country = None
                            fights = []
                            try:
                                prof = context.new_page()
                                prof.goto(profile_url)
                                prof.wait_for_selector("div.b-list__info-box")
                                bio_items = prof.query_selector_all("div.b-list__info-box")[0].query_selector_all("li")
                                for item in bio_items:
                                    label_el = item.query_selector("i")
                                    if not label_el:
                                        continue
                                    label = label_el.inner_text().strip().lower()
                                    value = item.inner_text().replace(label_el.inner_text(), "").strip()
                                    if "date of birth" in label or "dob" in label:
                                        dob_clean = re.sub(r"\(.*?\)", "", value).strip()
                                        dob_date = parse_date(dob_clean, fuzzy=True).date()
                                        today = datetime.today().date()
                                        age = today.year - dob_date.year - (
                                            (today.month, today.day) < (dob_date.month, dob_date.day)
                                        )
                                    elif "fighting out of" in label or "country" in label or "birth place" in label:
                                        country = value.split(",")[-1].strip()
                                fights = parse_recent_fights(prof)
                            except Exception:
                                traceback.print_exc()
                            finally:
                                try:
                                    prof.close()
                                    page.wait_for_timeout(300)
                                except Exception:
                                    pass

                            if page.is_closed():
                                page = context.new_page()
                                page.goto(letter_url)

                            mma_score = compute_mma_score(fights, age, losses, country)
                            writer.writerow({
                                "name": name,
                                "nickname": nickname,
                                "age": age,
                                "wins": wins,
                                "losses": losses,
                                "draws": draws,
                                "mma_score": mma_score,
                            })
                            print(f"{name} | Age: {age} | Record: {wins}-{losses}-{draws} | Rating: {mma_score}")
                        except Exception:
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
                        except Exception:
                            continue

                    if next_link:
                        current_page += 1
                        next_link.click()
                        page.wait_for_timeout(1500)
                    else:
                        print(f"ALL PAGES SCRAPED FOR LETTER: {letter_url.split('=')[-1].upper()}")
                        break

        browser.close()


if __name__ == "__main__":
    scrape_ufc_events()
