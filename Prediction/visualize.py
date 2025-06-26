import pandas as pd
import joblib
import plotly.graph_objects as go

# Load model and data
model = joblib.load("xgb_ufc_model.pkl")
df = pd.read_csv("../Data/scraped-ufc-data.csv", sep=';')

# Compute feature importance
importance = model.get_booster().get_score(importance_type='gain')
sorted_items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
features, scores = zip(*sorted_items)

# Create animation frames that reveal bars one by one
frames = [
    go.Frame(
        data=[go.Bar(
            x=scores[:i + 1],
            y=features[:i + 1],
            orientation='h',
            marker=dict(color='rgba(58,71,80,0.6)', line=dict(color='rgba(58,71,80,1.0)', width=1))
        )]
    )
    for i in range(len(features))
]

fig = go.Figure(data=[go.Bar(orientation='h')], frames=frames)

fig.update_layout(
    title='XGBoost Feature Importance (by Gain)',
    xaxis_title='Importance Score',
    yaxis_title='Feature',
    template='plotly_dark',
    height=600,
    updatemenus=[
        {
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 500, 'redraw': True},
                        'fromcurrent': True
                    }]
                }
            ]
        }
    ]
)

fig.write_html('feature_importance.html', auto_open=False)
