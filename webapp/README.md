# Web Application

This directory contains a minimal setup for a React + Vite frontend and a Flask backend.

## Backend

The backend exposes a `/predict` endpoint that loads the trained model from `../Prediction/xgb_ufc_model.pkl` and returns predictions.

To run the backend:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Frontend

The frontend is a simple React application created with Vite. Install dependencies and start the development server:

```bash
cd frontend
npm install
npm run dev
```

The app expects the Flask backend to run on `http://localhost:5000`.
