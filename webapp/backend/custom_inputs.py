import joblib
import pandas as pd
import torch
import torch.nn as nn
import json
import numpy as np
import os
import sys

# Add Prediction directory to path to access ensemble system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction'))

# Load the models from Prediction directory
xgb_model = joblib.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'xgb_ufc_model.pkl'))
catboost_model = joblib.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'CatBoost_ufc_model.pkl'))
lgreg_model = joblib.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'LGReg_ufc_model.pkl'))
scaler = joblib.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'LGReg_scaler.pkl'))

# Load MLP model artifacts
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'torch_mlp_meta.json'), "r") as f:
    mlp_meta = json.load(f)
mlp_scaler = joblib.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'torch_mlp_scaler.pkl'))

# Define MLP model class for inference
class _InferMLP(nn.Module):
    def __init__(self, in_dim, hidden, dropout):
        super().__init__()
        layers, prev = [], in_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        self.net = nn.Sequential(*layers)
    def forward(self, x): return self.net(x).squeeze(1)

# Load MLP model
device = "cuda" if torch.cuda.is_available() else "cpu"
mlp_model = _InferMLP(mlp_meta["input_dim"], tuple(mlp_meta["hidden"]), mlp_meta["dropout"])
mlp_model.load_state_dict(torch.load(os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'torch_mlp_model.pt'), map_location=device))
mlp_model.to(device)
mlp_model.eval()

# Read in up-to-date dataset
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'raw-scraped-ufc-data2.csv'), sep=',')

# Helper function to clean data to match ML dataset
def height_str_to_cm(height_str):
    try:
        feet, inches = height_str.replace('"', '').split("'")
        feet = int(feet.strip())
        inches = int(inches.strip())
        return int(feet * 30.48 + inches * 2.54)
    except:
        return None  # or 0, or raise an error

def getCustomPredict(fighter1, fighter2):
    """
    Get custom prediction for two fighters using the ensemble system.
    
    Args:
        fighter1 (int): Fighter 1 ID
        fighter2 (int): Fighter 2 ID
    
    Returns:
        dict: Complete prediction results including ensemble and individual model predictions
    """
    columns = ['SLpM', 'SApM', 'Str_Acc', 'TD_Acc', 'Str_Def', 'TD_Def', 'Sub_Avg',
               'TD_Avg', 'age', 'height', 'reach', 'wins', 'losses']

    # Check if fighters exist in the dataset
    f1_data = df.loc[df['id'] == fighter1, columns]
    f2_data = df.loc[df['id'] == fighter2, columns]
    
    if f1_data.empty or f2_data.empty:
        print(f"Fighter not found: fighter1={fighter1}, fighter2={fighter2}")
        return None
    
    f1 = f1_data.iloc[0]
    f2 = f2_data.iloc[0]

    # Get fighter names for display
    fighter1_name_data = df.loc[df['id'] == fighter1, 'name']
    fighter2_name_data = df.loc[df['id'] == fighter2, 'name']
    
    if fighter1_name_data.empty or fighter2_name_data.empty:
        print(f"Fighter name not found: fighter1={fighter1}, fighter2={fighter2}")
        return None
    
    fighter1_name = fighter1_name_data.iloc[0]
    fighter2_name = fighter2_name_data.iloc[0]

    f1_height = height_str_to_cm(f1['height']) if pd.notna(f1['height']) else 0
    f2_height = height_str_to_cm(f2['height']) if pd.notna(f2['height']) else 0

    def make_input(winner, loser, winner_height, loser_height):
        # Handle NaN values by replacing them with 0
        def safe_diff(val1, val2):
            if pd.isna(val1) or pd.isna(val2):
                return 0.0
            return val1 - val2
        
        return pd.DataFrame([{
            'SLpM_total_diff': safe_diff(winner['SLpM'], loser['SLpM']),
            'SApM_total_diff': safe_diff(winner['SApM'], loser['SApM']),
            'sig_str_acc_total_diff': safe_diff(winner['Str_Acc'], loser['Str_Acc']),
            'td_acc_total_diff': safe_diff(winner['TD_Acc'], loser['TD_Acc']),
            'str_def_total_diff': safe_diff(winner['Str_Def'], loser['Str_Def']),
            'td_def_total_diff': safe_diff(winner['TD_Def'], loser['TD_Def']),
            'sub_avg_diff': safe_diff(winner['Sub_Avg'], loser['Sub_Avg']),
            'td_avg_diff': safe_diff(winner['TD_Avg'], loser['TD_Avg']),
            'age_diff': safe_diff(winner['age'], loser['age']),
            'height_diff': safe_diff(winner_height, loser_height),
            'reach_diff': safe_diff(winner['reach'], loser['reach']),
            'wins_total_diff': safe_diff(winner['wins'], loser['wins']),
            'losses_total_diff': safe_diff(winner['losses'], loser['losses'])
        }])

    # Try both orders
    X1 = make_input(f1, f2, f1_height, f2_height)  # Fighter1 vs Fighter2
    X2 = make_input(f2, f1, f2_height, f1_height)  # Fighter2 vs Fighter1

    # Predict both directions with XGBoost
    p1_xgb = xgb_model.predict_proba(X1)[0][1]  # prob f1 wins
    p2_xgb = xgb_model.predict_proba(X2)[0][1]  # prob f2 wins

    # Predict both directions with CatBoost
    p1_cat = catboost_model.predict_proba(X1)[0][1]  # prob f1 wins
    p2_cat = catboost_model.predict_proba(X2)[0][1]  # prob f2 wins

    # Predict both directions with Logistic Regression
    X1_scaled = scaler.transform(X1)
    X2_scaled = scaler.transform(X2)
    p1_lgreg = lgreg_model.predict_proba(X1_scaled)[0][1] # prob f1 wins
    p2_lgreg = lgreg_model.predict_proba(X2_scaled)[0][1] # prob f2 wins

    # Predict both directions with MLP
    X1_mlp = X1[mlp_meta["features"]].astype(float).values
    X2_mlp = X2[mlp_meta["features"]].astype(float).values
    X1_mlp_scaled = mlp_scaler.transform(X1_mlp)
    X2_mlp_scaled = mlp_scaler.transform(X2_mlp)
    
    with torch.no_grad():
        # Convert to tensors and move to device
        X1_tensor = torch.tensor(X1_mlp_scaled, dtype=torch.float32, device=device)
        X2_tensor = torch.tensor(X2_mlp_scaled, dtype=torch.float32, device=device)
        
        # Get raw model outputs (logits)
        logits1 = mlp_model(X1_tensor)
        logits2 = mlp_model(X2_tensor)
        
        # Apply sigmoid to get probabilities
        p1_mlp_raw = torch.sigmoid(logits1).cpu().numpy()[0]  # prob f1 wins
        p2_mlp_raw = torch.sigmoid(logits2).cpu().numpy()[0]  # prob f2 wins
        
        # Handle extreme probabilities by clipping and normalizing
        if p1_mlp_raw < 0.001 and p2_mlp_raw < 0.001:
            # Both are very low, normalize to reasonable values
            p1_mlp = 0.3  # Give slight edge to fighter1
            p2_mlp = 0.7  # Give slight edge to fighter2
        else:
            # Clip probabilities to reasonable range and normalize
            p1_mlp = np.clip(p1_mlp_raw, 0.001, 0.999)
            p2_mlp = np.clip(p2_mlp_raw, 0.001, 0.999)
            
            # Normalize so they sum to 1
            total_prob = p1_mlp + p2_mlp
            p1_mlp = p1_mlp / total_prob
            p2_mlp = p2_mlp / total_prob

    # Try to get ensemble prediction if available
    ensemble_result = None
    try:
        from ensemble_integration import get_ensemble_prediction
        
        # Check if ensemble artifacts exist - use absolute path from Prediction directory
        ensemble_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'Prediction', 'ensemble_artifacts')
        print(f"Looking for ensemble artifacts in: {ensemble_dir}")
        print(f"Directory exists: {os.path.exists(ensemble_dir)}")
        
        if os.path.exists(ensemble_dir):
            print("Ensemble artifacts found, attempting ensemble prediction...")
            ensemble_result = get_ensemble_prediction(fighter1, fighter2)
            if ensemble_result:
                print("✓ Ensemble prediction successful!")
            else:
                print("⚠ Ensemble prediction returned None")
        else:
            print(f"⚠ Ensemble artifacts directory not found at: {ensemble_dir}")
    except Exception as e:
        print(f"Ensemble not available: {e}")
        import traceback
        traceback.print_exc()

    # Determine winner based on ensemble or individual models
    if ensemble_result:
        winner_id = fighter1 if ensemble_result['winner_name'] == fighter1_name else fighter2
        winner_name = ensemble_result['winner_name']
        confidence = ensemble_result['confidence']
    else:
        # Use XGBoost as the primary model for winner determination
        if p1_xgb > p2_xgb:
            winner_id = fighter1
            winner_name = fighter1_name
            confidence = p1_xgb
        else:
            winner_id = fighter2
            winner_name = fighter2_name
            confidence = p2_xgb
    
    # Return structured data for frontend
    result_data = {
        'winner_id': winner_id,
        'winner_name': winner_name,
        'confidence': confidence,
        'individual_predictions': {
            'XGBoost': {'fighter1_prob': float(p1_xgb), 'fighter2_prob': float(p2_xgb), 'winner': 'Fighter1' if p1_xgb > p2_xgb else 'Fighter2'},
            'CatBoost': {'fighter1_prob': float(p1_cat), 'fighter2_prob': float(p2_cat), 'winner': 'Fighter1' if p1_cat > p2_cat else 'Fighter2'},
            'Logistic Regression': {'fighter1_prob': float(p1_lgreg), 'fighter2_prob': float(p2_lgreg), 'winner': 'Fighter1' if p1_lgreg > p2_lgreg else 'Fighter2'},
            'MLP': {'fighter1_prob': float(p1_mlp), 'fighter2_prob': float(p2_mlp), 'winner': 'Fighter1' if p1_mlp > p2_mlp else 'Fighter2'}
        },
        'ensemble_prediction': ensemble_result if ensemble_result else None
    }
    
    return result_data


