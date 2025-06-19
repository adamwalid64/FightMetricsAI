# ⚠️ Work in Progress

This project is still under development and subject to change.

## UFC Stats Scraper & ML Predictor

This project scrapes detailed UFC fighter statistics from [ufcstats.com](http://www.ufcstats.com/statistics/fighters) and applies machine learning to predict fighter performance using XGBoost.

---

### 🕸 Web Scraping (Playwright)

The script collects general and career-specific stats for each fighter by navigating through the website's alphabetized tabs.

#### Scraped Stats Include:

- Name, Nickname, Height, Weight, Reach
- Stance, Win/Loss/Draw Record, Belt Status
- Career Stats:
  - Strikes Landed per Minute (SLpM)
  - Striking Accuracy
  - Strikes Absorbed per Minute (SApM)
  - Striking Defense
  - Takedown Average, Accuracy, Defense
  - Submission Average

### Additional Data-sets

https://www.kaggle.com/datasets/mdabbert/ultimate-ufc-dataset?resource=download
https://www.key2stats.com/data-set/view/1551

---

### 🤖 Machine Learning (XGBoost)

A simple XGBoost classifier is used to predict a fighter's performance category (e.g., high vs. low) based on numerical statistics.

#### ML Pipeline:

- Loads real or placeholder fighter data
- Preprocesses and splits data into train/test sets
- Trains an `XGBClassifier`
- Evaluates model using accuracy, classification report, and confusion matrix

#### Sample Features Used:

- Height, Weight, Reach
- SLpM, Striking Accuracy, SApM, Striking Defense
- TD Avg, TD Accuracy, TD Defense
- Submission Avg

---

### 🛠 Installation

```bash
pip install playwright xgboost scikit-learn pandas numpy
playwright install
