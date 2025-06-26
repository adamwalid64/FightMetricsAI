import matplotlib.pyplot as plt
from xgboost import plot_importance
import pandas as pd
import joblib
import plotly.graph_objects as go

# import model
model = joblib.load("xgb_ufc_model.pkl")

# import data
df = pd.read_csv("../Data/scraped-ufc-data.csv", sep=';')

# Get feature importance
importance = model.get_booster().get_score(importance_type='gain')
sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
features, scores = zip(*sorted_items)


fig = go.Figure(
    go.Bar(
        x=scores,
        y=features,
        orientation='h',
        marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=1))
    )
)

fig.update_layout(
    title='XGBoost Feature Importance (by Gain)',
    xaxis_title='Importance Score',
    yaxis_title='Feature',
    template='plotly_dark',
    height=600
)

fig.show()