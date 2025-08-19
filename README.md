## UFC Prediction Suite — Scraping, Machine Learning, RAG, and Web App

An end-to-end MMA analytics platform that scrapes real fighter data, trains multiple models, ensembles predictions, and augments them with a Retrieval-Augmented Generation (RAG) expert analysis pipeline — all shipped in a full-stack web app (Flask + React).

### What you can do
- Predict winners using an ensemble of XGBoost, CatBoost, Logistic Regression, and a Torch MLP
- See model votes and contribution per base learner, plus aggregate feature importance
- Run a news/sentiment-driven RAG analysis that writes an expert-style fight breakdown with confidence
- Scrape UFC fighter stats and live news sentiment for upcoming matchups
- Use a modern web UI for predictions, RAG workflows, and fighter browsing

---

## Web Scraping — Production-Ready Data Feeds

- Fighter stats scraper (`UFC_scrape/ufc_scrape.py`):
  - Headless Chromium via Playwright navigates `ufcstats` tabs and fighter profiles
  - Extracts biometrics and career stats: SLpM, SApM, Str_Acc, Str_Def, TD_Avg, TD_Acc, TD_Def, Sub_Avg, wins/losses/draws, belt, age, reach, height, stance, more
  - Traverses fight history to derive recent win streak and context
  - Outputs a consolidated lookup used by the ML stack (`Data/raw-scraped-ufc-data2.csv`)
  - Optional: pipelined inserts to MySQL (see `SQL/database-init.sql` for schema)

- Sentiment/news scraper (`UFC_scrape/ufc_sentiment_scrape.py`):
  - Pulls recent articles for a given fight, with a progress callback designed for server-sent events (SSE)
  - Feeds the RAG pipeline by creating datasets under `Data/sentiment_datasets/`

Result: a continuously refreshable data fabric — structured stats for modeling and fresh media signals for RAG.

---

## Machine Learning — Stacked Ensemble, Calibrated and Explainable

- Base learners: XGBoost, CatBoost, Logistic Regression (with scaler), Torch MLP (with scaler and metadata)
- Stacking ensemble with out-of-fold (OOF) meta-features and a Logistic Regression meta-learner
- Global feature scaling at inference for robust, reproducible results
- Rich introspection:
  - Per-model feature importance endpoints (XGB/Cat/LR/MLP weight attribution)
  - Aggregate importance across all models
  - Model votes and per-fighter probabilities exposed to the UI

Artifacts live in `Prediction/` and `Prediction/ensemble_artifacts/` (`xgb.joblib`, `cat.joblib`, `lgr.joblib`, `mlp_model.pt`, `global_scaler.pkl`, `meta_learner.joblib`, `ensemble_meta.json`, etc.).

Programmatic entrypoint: `Prediction/ensemble_integration.py` exposes `get_ensemble_prediction(fighter1_id, fighter2_id)` returning predicted winner, ensemble probability, base predictions, and confidence.

Bonus: an MMA Math heuristic (`Prediction/ufc_predict_math.py`) demonstrates a transparent ruleset using last-five fights as a baseline comparator.

---

## RAG — Media Intelligence Meets Fight Analytics

- Pipeline (`RAG/SentimentRAG/`):
  1) Scrape fight-specific articles (sentiment datasets under `Data/sentiment_datasets/`)
  2) Convert to LangChain `Document`s and chunk; persist to `Data/langchain_documents/*.pkl`
  3) Build FAISS vector store and retrieve top-K articles per query
  4) LLM analysis with `ChatOpenAI` (default `gpt-4o`) to produce an expert breakdown and decisive pick
  5) Token and cost estimation reported back with results

- Frontend integration: `/rag-query-progress` streams real-time progress (SSE) from scrape → load → chunk → embed → analyze, powering a granular progress UI and a polished final write-up.

Key files: `RAG/SentimentRAG/load_sentiment_data.py`, `RAG/SentimentRAG/ufcRAG.py`.

Requires a project root `.env` with `OPENAI_API_KEY`.

---

## Web App — Flask API + React UI

Backend (`webapp/backend/app.py`):
- `POST /predict` — Ensemble prediction with per-model probabilities, votes, and confidence
- `GET /feature-importance/(xgboost|logistic-regression|catboost|mlp|all)` — Explainability endpoints
- `GET /fighter-data` — Full fighter table from `Data/raw-scraped-ufc-data2.csv`
- `POST /rag-query` and `POST /rag-query-progress` — One-shot vs. streaming RAG flows with SSE

Frontend (`webapp/frontend/`):
- `App.jsx` — Core prediction UI with ensemble votes and confidence
- `AllModelsFeatureImportance.jsx` + `FeatureImportanceChart.jsx` — Rich model explainability
- `RAGPipeline.jsx` — Live RAG workflow with progress and final expert write-up
- `FighterDatabase.jsx` — Browse fighters backed by `/fighter-data`

Result: an interactive analyst console — run predictions, inspect why, and read an expert narrative, all in one place.

---

## Run It Locally

### 1) Prerequisites
- Python 3.10+
- Node.js 18+
- For RAG: `.env` at project root with your OpenAI key

```
OPENAI_API_KEY=sk-...
```

### 2) Install Python deps

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

If retraining, ensure `xgboost`, `catboost`, `scikit-learn`, `torch`, `joblib`, `pandas`, `numpy` are installed (the root `requirements.txt` covers most).

### 3) Backend deps

```bash
cd webapp/backend
pip install -r requirements.txt
```

### 4) Frontend deps

```bash
cd webapp/frontend
npm install
```

### 5) Start services

Backend (Flask):
```bash
cd webapp/backend
python app.py
```
Serves at `http://localhost:5000/`.

Frontend (Vite + React):
```bash
cd webapp/frontend
npm run dev
```
Open the printed URL (typically `http://localhost:5173`).

### 6) Data notes
- The app reads fighters from `Data/raw-scraped-ufc-data2.csv` (included). To rebuild, use `UFC_scrape/ufc_scrape.py` (MySQL optional) or ship your own CSV in the same schema.
- RAG needs `.env` and will generate `Data/sentiment_datasets/` and `Data/langchain_documents/` automatically during runs.

### (Optional) Retrain the ensemble
```bash
cd Prediction
python ensemble_predict.py
```

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
- `webapp/backend/app.py` — Flask API for predictions, feature importance, fighter data, and RAG
- `webapp/frontend/` — React app (Vite) for prediction UI, RAG pipeline, and explainability
- `Prediction/ensemble_predict.py` — Train OOF-stacking ensemble and save artifacts
- `Prediction/ensemble_integration.py` — Inference entrypoint for the ensemble
- `RAG/SentimentRAG/ufcRAG.py` — FAISS + OpenAI expert analysis pipeline

---

## Datasets & Notebooks

Datasets under `Data/`:
- `raw-scraped-ufc-data2.csv` — primary fighter lookup used by the API
- `sentiment_datasets/*` — fight-specific news datasets (RAG)
- `langchain_documents/*` — persisted, chunked LangChain docs

Notebooks in `Prediction/`:
- `ufc_predict_XGB.ipynb`, `ufc_predict_CatBoost.ipynb`, `ufc_predict_LGReg.ipynb`

Utilities:
- `Prediction/custom_inputs.py` — feature engineering + model integration for ID-based predictions
- `Prediction/test_enhanced_predictions.py` — basic tests/examples for prediction flows

---

## Troubleshooting

- RAG auth/model error: ensure `.env` contains a valid `OPENAI_API_KEY` and your account has access to the configured model (`gpt-4o` by default)
- Fighter not found: names must match `Data/raw-scraped-ufc-data2.csv`
- Feature-importance errors: verify the corresponding model artifact exists under `Prediction/`
- Frontend cannot reach backend: run Flask on 5000 and Vite on 5173 (CORS enabled for localhost)

---

## License

For personal/educational use. Verify third-party dataset and model license terms before distribution.

---

## ⚠️ Work in Progress

This project is under active development and subject to change.

