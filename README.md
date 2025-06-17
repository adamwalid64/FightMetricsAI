# ⚠️ Work in Progress

This project is still under development and subject to change.

## UFC Stats Scraper

This Python script uses Playwright to scrape detailed UFC fighter statistics from [ufcstats.com](http://www.ufcstats.com/statistics/fighters). It collects general and career-specific stats for each fighter by navigating through the website's alphabetized pages.

### 📦 Features

- Iterates through all alphabet tabs on the UFC stats page
- Collects fighter summary data: name, nickname, height, weight, stance, reach, win/loss/draw record, and belt status
- Visits each fighter's profile to extract career statistics like:
  - Strikes Landed per Minute (SLpM)
  - Striking Accuracy
  - Strikes Absorbed per Minute (SApM)
  - Striking Defense
  - Takedown Average
  - Takedown Accuracy
  - Takedown Defense
  - Submission Average

### 🛠 Installation

1. Install Python 3.8 or higher.
2. Install Playwright and required dependencies:

```bash
pip install playwright
playwright install
