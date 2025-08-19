## UFC Prediction Suite — Scraping, Machine Learning, RAG, and Web App

An end-to-end MMA analytics platform that scrapes data, trains multiple ML models, ensembles predictions, augments with a Retrieval-Augmented Generation (RAG) analysis pipeline, and serves everything through a full-stack web app (Flask + React).

### What you can do
- Predict winners of UFC fights using an ensemble of XGBoost, CatBoost, Logistic Regression, and a Torch MLP
- See how each model voted and contributed to the final prediction
- Explore feature importance across all models
- Run a news/sentiment-driven RAG analysis to generate an expert-style fight breakdown
- Scrape UFC fighter stats and news sentiment
- Use a modern web UI for predictions, RAG analysis, and fighter browsing

---

## Contents
- Features overview
- Project structure
- Setup and installation
- Back-end API (Flask)
- Front-end app (React + Vite)
- Data scraping
- Machine learning and ensemble
- RAG (news/sentiment) analysis
- Datasets
- Notebooks and CLI utilities
- Troubleshooting

---

## Features Overview

- Data scraping
  - UFC fighter statistics scraping and consolidation
  - News/sentiment scraping for upcoming fights with progress callbacks
- Machine learning
  - Individual models: XGBoost, CatBoost, Logistic Regression, Torch MLP
  - Stacking ensemble with out-of-fold (OOF) meta-learner (Logistic Regression)
  - Global feature scaling and robust inference utilities
- Feature importance
  - Endpoints for XGBoost, Logistic Regression, CatBoost, Torch MLP (weight attribution)
  - Aggregate endpoint to fetch all models’ importances at once
- RAG pipeline
  - Scrape articles, convert to LangChain documents, build FAISS vector store
  - Query LLM for expert breakdown, with token/cost estimation
  - Real-time progress via Server-Sent Events (SSE)
- Web app
  - Winner predictions with confidence and model votes
  - Feature importance charts (per model and combined)
  - RAG analysis card with live progress and final write-up
  - Fighter database browser

---

## Project Structure

```text
UFC-Prediction/
  Data/                      # CSVs and processed LangChain/RAG artifacts
  Prediction/                # ML training, ensemble artifacts, inference utilities
  RAG/                       # RAG pipelines (Sentiment and Math)
  SQL/                       # Optional database initialization script
  UFC_scrape/                # Fighter stats + sentiment/news scrapers
  webapp/                    # Full-stack app (Flask backend + React frontend)
  README.md                  # You are here
  requirements.txt           # Core Python dependencies
```

Key paths:
- `webapp/backend/app.py`: Flask API for predictions, feature importance, fighter data, and RAG endpoints
- `webapp/frontend/`: React app (Vite) with prediction UI, RAG pipeline, feature importance views
- `Prediction/ensemble_predict.py`: Train OOF-stacking ensemble and save artifacts
- `Prediction/ensemble_integration.py`: Load ensemble and make predictions; integrates with scraped fighter data
- `RAG/SentimentRAG/ufcRAG.py`: RAG prediction pipeline (LangChain + FAISS + OpenAI)
- `UFC_scrape/`: Scrapers for fighter stats and sentiment/news

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- For RAG: an OpenAI API key in a project-root `.env`

```
OPENAI_API_KEY=sk-...
```

### Python dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

If you plan to retrain the ensemble from scratch, also install: xgboost, catboost, scikit-learn, torch, joblib, pandas, numpy (already covered by `requirements.txt` in most cases).

### Frontend dependencies

```bash
cd webapp/frontend
npm install
```

### Backend (Flask) dependencies

```bash
cd webapp/backend
pip install -r requirements.txt
```

---

## Running the App

### Start the backend API (Flask)

```bash
cd webapp/backend
venv\Scripts\activate  # ensure the venv is active
python app.py
```

This exposes endpoints at `http://localhost:5000/`.

### Start the frontend (React + Vite)

```bash
cd webapp/frontend
npm run dev
```

Open the app at the printed local URL (typically `http://localhost:5173`).

---

## Backend API (Flask)

Base URL: `http://localhost:5000`

- `POST /predict`
  - Body: `{ "fighterOne": "Name", "fighterTwo": "Name" }`
  - Uses the ensemble and individual models to predict the winner, returning per-model probabilities, votes, and overall confidence

- `GET /feature-importance`
  - Alias for XGBoost importance; see below for model-specific endpoints

- `GET /feature-importance/xgboost`
- `GET /feature-importance/logistic-regression`
- `GET /feature-importance/catboost`
- `GET /feature-importance/mlp`
- `GET /feature-importance/all`
  - Returns feature names and scores per model (the MLP uses weight-based attribution)

- `GET /fighter-data`
  - Returns the fighter database (from `Data/raw-scraped-ufc-data2.csv`) as JSON

- `POST /rag-query`
  - One-shot RAG flow (scrape -> load -> chunk -> vectorize -> query LLM)

- `POST /rag-query-progress`
  - Same as above, but streams granular progress updates via SSE for the frontend progress bar

Example curl:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"fighterOne": "Max Holloway", "fighterTwo": "Dustin Poirier"}'
```

---

## Web Frontend (React)

Primary views/components under `webapp/frontend/src/`:
- `App.jsx`: Home and prediction UX, ensemble contributions/votes, and feature importance sections
- `RAGPipeline.jsx`: RAG workflow UI with live progress and final expert write-up
- `FighterDatabase.jsx`: Fighter list/table backed by `/fighter-data`
- `AllModelsFeatureImportance.jsx` and `FeatureImportanceChart.jsx`: Model-specific and aggregate feature importance visualizations

Assets live under `webapp/frontend/img/`.

---

## Data Scraping

Scrapers live in `UFC_scrape/`:
- `ufc_scrape.py` / `ufc_scrape2.py`: Fighter stats scraping from public sources (e.g., ufcstats)
- `ufc_sentiment_scrape.py`: News/sentiment scraping for an upcoming fight; supports a progress callback used by the SSE endpoint

Outputs populate `Data/` (e.g., `raw-scraped-ufc-data2.csv`) and `Data/sentiment_datasets/`.

Optional SQL schema: `SQL/database-init.sql` to initialize a relational store if you want to persist scraped data in a DB.

---

## Machine Learning and Ensemble

Models supported:
- XGBoost (`Prediction/xgb_ufc_model.pkl`)
- CatBoost (`Prediction/CatBoost_ufc_model.pkl`)
- Logistic Regression (`Prediction/LGReg_ufc_model.pkl` + scaler)
- Torch MLP (`Prediction/torch_mlp_model.pt` + scaler + metadata)

Stacking Ensemble (OOF):
- Code: `Prediction/ensemble_predict.py`
- Base models are trained via Stratified K-Fold; out-of-fold predictions form meta-features
- Meta-learner: Logistic Regression over base model probabilities
- Artifacts saved to `Prediction/ensemble_artifacts/`:
  - `xgb.joblib`, `cat.joblib`, `lgr.joblib`, `mlp_model.pt` (+ `mlp_scaler.pkl`, `mlp_meta.json`)
  - `global_scaler.pkl`, `meta_learner.joblib`, `ensemble_meta.json`

Training from scratch:
```bash
cd Prediction
python ensemble_predict.py
```

Loading and inference:
- `Prediction/ensemble_integration.py` provides `get_ensemble_prediction(fighter1_id, fighter2_id)` and utilities to compare/inspect base predictions and the final ensemble probability.
- The web backend integrates these calls behind `/predict`.

Feature importance
- Provided per-model through Flask endpoints
- The frontend renders charts for XGBoost, Logistic Regression, CatBoost, and MLP

---

## RAG: News/Sentiment Analysis

Path: `RAG/SentimentRAG/`

Pipeline summary:
1) Scrape articles and sentiment for a specific fight (via `UFC_scrape/ufc_sentiment_scrape.py`)
2) Load and convert articles to LangChain `Document`s
3) Chunk and persist to `Data/langchain_documents/*.pkl`
4) Build a FAISS vector store and query with `ChatOpenAI`
5) Token and cost estimation is logged and returned

Key files:
- `load_sentiment_data.py`: Load/save chunked/processed documents
- `ufcRAG.py`: Orchestrates FAISS + ChatOpenAI (`gpt-4o` by default), performs the expert analysis, and returns the write-up, costs, and doc counts

Runtime requirements:
- `.env` at project root with `OPENAI_API_KEY`

Frontend UX:
- `RAGPipeline.jsx` calls `/rag-query-progress` to show a live, granular progress bar from scrape through LLM analysis, and renders the final prediction write-up.

Optional: `RAG/MathRAG/mathRAG.py` for math/logic-based RAG experiments.

---

## Datasets

Local CSVs under `Data/` (examples):
- `raw-scraped-ufc-data2.csv`: Consolidated fighter stats lookup used by the API
- `large_dataset.csv`, `ufc-master.csv`, and historical datasets
- `sentiment_datasets/*`: Fight-specific news datasets used for RAG
- `langchain_documents/*`: Chunked LangChain documents

External references (for research/augmentation):
- Kaggle and other sources listed in the historical README; this project focuses on ensembled ML + RAG on top of consolidated fighter stats

---

## Notebooks and CLI Utilities

Notebooks in `Prediction/` show training/usage examples for individual models:
- `ufc_predict_XGB.ipynb`
- `ufc_predict_CatBoost.ipynb`
- `ufc_predict_LGReg.ipynb`

Utilities:
- `Prediction/custom_inputs.py`: Integrates feature engineering with models/ensemble for prediction by fighter IDs
- `Prediction/test_enhanced_predictions.py`: Basic tests/examples for prediction flows

---

## Troubleshooting

- RAG returns an auth or model error
  - Ensure `.env` exists at project root with a valid `OPENAI_API_KEY`
  - Confirm network access and model name (`gpt-4o` by default) are available to your account

- `/predict` says a fighter isn’t found
  - The lookup is driven by `Data/raw-scraped-ufc-data2.csv` — verify names match exactly or update the dataset

- Feature importance endpoint fails for a model
  - The backend contains multiple fallbacks; ensure the corresponding model artifact exists under `Prediction/`

- Frontend cannot reach backend
  - Start Flask on port 5000 and Vite on 5173; CORS is configured for localhost
  - Check console logs for blocked requests

---

## License

For personal/educational use. Verify third-party dataset and model license terms before distribution.

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

