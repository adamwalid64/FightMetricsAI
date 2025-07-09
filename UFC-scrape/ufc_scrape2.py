#!/usr/bin/env python3
"""Scrape UFC fighter stats and compute a basic MMA math score.

This script replicates ``ufc_scrape.py`` but tailors the data for a
prototype MMA math model. It pulls fighter information from
``http://www.ufcstats.com/statistics/fighters`` and examines the last
five bouts for each fighter. Basic scoring rules derived from the MMA
model description are applied and saved along with the fighter stats.

Note: Running this script requires internet access to ``ufcstats.com``
and Playwright installed with ``playwright install``.
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
WIN_MAP = {
    "finish": 5,
    "finishStreak1x": 1,
    "2judgesWin": 5,
}


def sanitize(value, convert_func=None):
    """Convert '--' placeholders and optionally apply ``convert_func``."""
    if value == "--" or value == "" or value is None:
        return None
    return convert_func(value) if convert_func else value


def is_finish(method: str) -> bool:
    """Return True if ``method`` represents a stoppage (non decision)."""
    if not method:
        return False
    m = method.lower()
    return not ("decision" in m)


def compute_mma_score(fights, age, total_losses):
    """Compute a very simplified MMA math score.

    Parameters
    ----------
    fights : list of dict
        Output from ``parse_recent_fights`` containing result and method.
    age : int or None
        Fighter age.
    total_losses : int
        Number of official UFC losses.
    """
    points = 0
    finish_streak = 0
    all_wins = True

    for f in fights:
        res = f.get("result")
        meth = f.get("method", "")
        if res == "Win":
            if is_finish(meth):
                points += WIN_MAP["finish"]
                finish_streak += 1
                points += WIN_MAP["finishStreak1x"] * finish_streak
            else:
                finish_streak = 0
        elif res == "Loss":
            all_wins = False
            finish_streak = 0
            if "decision" in meth.lower():
                points -= 2
            else:
                points -= 3
        else:
            all_wins = False
            finish_streak = 0

    if age and age > 35:
        points -= 5 + (age - 35)

    if total_losses == 0:
        points += 5

    if all_wins and len(fights) == 5:
        points += 3

    return points


def parse_recent_fights(profile_page):
    """Parse the last five fights from the fighter profile page."""
    fights = []
    try:
        profile_page.wait_for_selector("tbody.b-fight-details__table-body", timeout=5000)
        rows = profile_page.query_selector_all("tbody.b-fight-details__table-body tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) < 2:
                continue
            result_text = cells[0].inner_text().strip().capitalize()
            if result_text in {"", "--", "Scheduled"}:
                continue
            method = sanitize(cells[6].inner_text().strip()) if len(cells) > 6 else ""
            fights.append({"result": result_text, "method": method})
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
                while True:
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
                                    if "date of birth" in label or "dob" in label:
                                        dob_str = item.inner_text().replace(label_el.inner_text(), "").strip()
                                        dob_clean = re.sub(r"\(.*?\)", "", dob_str).strip()
                                        dob_date = parse_date(dob_clean, fuzzy=True).date()
                                        today = datetime.today().date()
                                        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                                        break
                                fights = parse_recent_fights(prof)
                            except Exception:
                                traceback.print_exc()
                            finally:
                                try:
                                    prof.close()
                                except Exception:
                                    pass

                            mma_score = compute_mma_score(fights, age, losses)
                            writer.writerow({
                                "name": name,
                                "nickname": nickname,
                                "age": age,
                                "wins": wins,
                                "losses": losses,
                                "draws": draws,
                                "mma_score": mma_score,
                            })
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
                        break

        browser.close()


if __name__ == "__main__":
    scrape_ufc_events()
