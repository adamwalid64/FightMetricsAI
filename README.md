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
- For each fighter's **last five UFC bouts**:
  - Opponent name and ranking (or champion status)
  - Fight result and method of victory
  - Event date, location and whether judges gave all rounds

### Additional Data

https://www.kaggle.com/datasets/mdabbert/ultimate-ufc-dataset?resource=download |
https://www.key2stats.com/data-set/view/1551 |
https://www.kaggle.com/datasets/maksbasher/ufc-complete-dataset-all-events-1996-2024/data

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
```


### MMA Math Model

The project includes a Python implementation of the "MMA Math" algorithm.
Call `prediction.ufc_predict_math.mathmodel(df, fighter_id, opponent_id=None)`
to score a fighter using only their last five fights. Passing an `opponent_id`
adds relative-victory bonuses that compare both fighters' recent opponents.

🧠 MMA Fight Prediction Model — Scoring Formula and Rules
🎯 Goal:
Predict the winner of an upcoming MMA fight by calculating the total points accumulated by each fighter based on their last five UFC fights. The fighter with the higher score is predicted to win.

📊 Point Allocation Rules
Victory Based on Opponent's Ranking:

Defeated UFC Champion → +16 points

Defeated Rank #1 → +15 points

Defeated Rank #2 → +14 points

...

Defeated Rank #15 → +1 point

Loss Penalties:

Loss → −2 points

Loss via KO/TKO/Submission ("getting finished") → −3 points

MMA Math Bonus:

If Fighter A beats an opponent that Fighter B has lost to (within both fighters' last 5 fights) → +5 points

If Fighter B has avenged that loss → award only +1 point instead

Finish Bonus:

KO/TKO/Submission → +5 points

Finish Streak Bonus: +1 point for each consecutive finish (cumulative with base bonus)

E.g. 3 consecutive finishes = 3×5 = 15 base + 3 streak bonus = 18 total

Decision Shutout Bonus:

If fighter wins by decision and 2 or more judges give them all rounds → +5 points

Age Penalty:

If fighter is over 35 years old → −5 points

Additional −1 point for each year over 35

E.g. Fighter is 38 → −5 −1 −1 −1 = −8 points

Undefeated Bonuses:

Undefeated in UFC overall → +5 points

Undefeated in last 5 UFC fights → +3 points (if not already awarded 5 for being UFC-undefeated)

Dodgy Judge Bonus (Home-Country Bonus):

If fighter is fighting in their home country and opponent is not, and the fight is not in the United States → +5 points

🧾 Required Data Per Fighter (last 5 UFC fights):
You need to gather the following fields per fight per fighter:

Opponent name

Opponent UFC rank at time of fight (0 = Champion, 1 = #1, etc.)

Whether the bout was a title fight (opponent entering as champion)

Win or loss?

Method of win/loss (Decision, KO, TKO, Sub, Doctor stoppage)

Was the fighter finished?

Round-by-round judge scorecards (to check for 30–27 or equivalent from 2+ judges)

Event date (to track fight streaks)

Location of fight (for dodgy judge bonus)

Fighter's current age

Fighter's country of origin

UFC record (to determine undefeated status)

✅ Prediction Output:
For a given matchup between Fighter A and Fighter B, the program should:

Gather all relevant data for their last 5 UFC fights

Apply the above scoring logic to each fighter

Output both total scores and declare the predicted winner (fighter with higher score)

## Web Application Setup

See [webapp/README.md](webapp/README.md) for instructions on running the React frontend and Flask backend that serve predictions from the trained model.

