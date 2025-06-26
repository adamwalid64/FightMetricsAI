"""Visualize XGBoost feature importance in an animated bar chart."""

import pandas as pd
import joblib
import plotly.graph_objects as go

# Load model and data
model = joblib.load("xgb_ufc_model.pkl")
df = pd.read_csv("../Data/scraped-ufc-data.csv", sep=";")

# Compute feature importance
importance = model.get_booster().get_score(importance_type="gain")
sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
features, scores = zip(*sorted_items)

# Map generic feature names like "f0" to the column names used when the
# model was trained. This helps ensure the displayed labels are
# human readable and that the importance values correspond to the correct
# columns.
try:
    booster = model.get_booster()
    feature_names = booster.feature_names
    if feature_names and feature_names[0].startswith("f") and feature_names[0][1:].isdigit():
        features = [df.columns[int(name[1:])] for name in features]
except Exception:
    pass

# Create animation frames that reveal bars one by one
frames = [
    go.Frame(
        data=[go.Bar(
            x=scores[: i + 1],
            y=features[: i + 1],
            orientation="h",
            marker=dict(
                color="rgba(255,0,0,0.6)",
                line=dict(color="rgba(255,0,0,1.0)", width=1),
            ),
        )]
    )
    for i in range(len(features))
]

fig = go.Figure(data=[go.Bar(orientation="h")], frames=frames)

fig.update_layout(
    title="XGBoost Feature Importance (by Gain)",
    xaxis_title="Importance Score",
    yaxis_title="Feature",
    template="plotly_dark",
    font=dict(family="Arial", size=18),
    height=600,
    updatemenus=[
        {
            "type": "buttons",
            "showactive": False,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 500, "redraw": True},
                            "fromcurrent": True,
                        },
                    ],
                }
            ],
        }
    ],
)

fig.write_html('feature_importance.html', auto_open=False)
