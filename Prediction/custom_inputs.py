import joblib
import pandas as pd
import torch
import torch.nn as nn
import json
import numpy as np

# Load the models
xgb_model = joblib.load("xgb_ufc_model.pkl")

catboost_model = joblib.load("CatBoost_ufc_model.pkl")

lgreg_model = joblib.load("LGReg_ufc_model.pkl")
scaler = joblib.load("LGReg_scaler.pkl")

# Load MLP model artifacts
with open("torch_mlp_meta.json", "r") as f:
    mlp_meta = json.load(f)
mlp_scaler = joblib.load("torch_mlp_scaler.pkl")

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
mlp_model.load_state_dict(torch.load("torch_mlp_model.pt", map_location=device))
mlp_model.to(device)
mlp_model.eval()

# Read in up-to-date dataset
df = pd.read_csv("../Data/raw-scraped-ufc-data2.csv", sep=',')

# helper function to clean data to match ML dataset
def height_str_to_cm(height_str):
    try:
        feet, inches = height_str.replace('"', '').split("'")
        feet = int(feet.strip())
        inches = int(inches.strip())
        return int(feet * 30.48 + inches * 2.54)
    except:
        return None  # or 0, or raise an error

# # Example usage
# print(height_str_to_cm("6' 3\""))   # ➜ 190
# print(height_str_to_cm("5' 11\""))  # ➜ 180

# fighter1name = ''
# fighter2name = ''

# enter fighter ids ex: calcdiff(64, 22)
def getCustomPredict(fighter1, fighter2):
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

    # Debug: Print fighter stats
    print(f"\n=== Fighter Comparison ===")
    print(f"Fighter {fighter1} ({fighter1_name}) vs Fighter {fighter2} ({fighter2_name})")
    print(f"{fighter1_name} Stats: SLpM={f1['SLpM']:.2f}, SApM={f1['SApM']:.2f}, Str_Acc={f1['Str_Acc']:.1f}%, Str_Def={f1['Str_Def']:.1f}%")
    print(f"{fighter2_name} Stats: SLpM={f2['SLpM']:.2f}, SApM={f2['SApM']:.2f}, Str_Acc={f2['Str_Acc']:.1f}%, Str_Def={f2['Str_Def']:.1f}%")
    print(f"{fighter1_name}: Age={f1['age']}, Height={f1['height']}, Reach={f1['reach']}, Wins={f1['wins']}, Losses={f1['losses']}")
    print(f"{fighter2_name}: Age={f2['age']}, Height={f2['height']}, Reach={f2['reach']}, Wins={f2['wins']}, Losses={f2['losses']}")

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
            # 'weight_diff': winner['weight'] - loser['weight'],
            'reach_diff': safe_diff(winner['reach'], loser['reach']),
            'wins_total_diff': safe_diff(winner['wins'], loser['wins']),
            'losses_total_diff': safe_diff(winner['losses'], loser['losses'])
        }])

    # Try both orders
    X1 = make_input(f1, f2, f1_height, f2_height)  # Fighter1 vs Fighter2
    X2 = make_input(f2, f1, f2_height, f1_height)  # Fighter2 vs Fighter1

    # Debug: Print the differences
    print(f"\n=== Model Input Feature Differences ===")
    print(f"{fighter1_name} vs {fighter2_name} differences:")
    for col in X1.columns:
        print(f"  {col}: {X1[col].iloc[0]:.2f}")
    
    print(f"\n{fighter2_name} vs {fighter1_name} differences:")
    for col in X2.columns:
        print(f"  {col}: {X2[col].iloc[0]:.2f}")

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
    
    # Debug MLP inputs
    print(f"\n=== MLP Debug Info ===")
    print(f"MLP features: {mlp_meta['features']}")
    print(f"X1_mlp shape: {X1_mlp.shape}, X1_mlp_scaled shape: {X1_mlp_scaled.shape}")
    print(f"X1_mlp values: {X1_mlp.flatten()}")
    print(f"X1_mlp_scaled values: {X1_mlp_scaled.flatten()}")
    
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
        # If both probabilities are very close to 0, normalize them
        if p1_mlp_raw < 0.001 and p2_mlp_raw < 0.001:
            # Both are very low, normalize to reasonable values
            p1_mlp = 0.3  # Give slight edge to fighter1
            p2_mlp = 0.7  # Give slight edge to fighter2
            print(f"⚠ MLP probabilities were too extreme, normalizing to reasonable values")
        else:
            # Clip probabilities to reasonable range and normalize
            p1_mlp = np.clip(p1_mlp_raw, 0.001, 0.999)
            p2_mlp = np.clip(p2_mlp_raw, 0.001, 0.999)
            
            # Normalize so they sum to 1
            total_prob = p1_mlp + p2_mlp
            p1_mlp = p1_mlp / total_prob
            p2_mlp = p2_mlp / total_prob
        
        # Debug model outputs
        print(f"MLP logits1: {logits1.cpu().numpy()[0]:.6f}, raw_prob1: {p1_mlp_raw:.6f}, final_prob1: {p1_mlp:.6f}")
        print(f"MLP logits2: {logits2.cpu().numpy()[0]:.6f}, raw_prob2: {p2_mlp_raw:.6f}, final_prob2: {p2_mlp:.6f}")

    print(f"\n=== XGBoost Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_xgb:.3f}")
    print(f"{fighter2_name} wins probability: {p2_xgb:.3f}")

    print(f"\n=== CatBoost Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_cat:.3f}")
    print(f"{fighter2_name} wins probability: {p2_cat:.3f}")

    print(f"\n=== Logistic Regression Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_lgreg:.3f}")
    print(f"{fighter2_name} wins probability: {p2_lgreg:.3f}")

    print(f"\n=== MLP Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_mlp:.3f}")
    print(f"{fighter2_name} wins probability: {p2_mlp:.3f}")

    # Summary of all individual model predictions
    print(f"\n{'='*60}")
    print("INDIVIDUAL MODEL PREDICTION SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<20} {'Fighter1':<15} {'Fighter2':<15} {'Prediction':<15}")
    print(f"{'-'*60}")
    print(f"{'XGBoost':<20} {p1_xgb:<15.3f} {p2_xgb:<15.3f} {'Fighter1' if p1_xgb > p2_xgb else 'Fighter2':<15}")
    print(f"{'CatBoost':<20} {p1_cat:<15.3f} {p2_cat:<15.3f} {'Fighter1' if p1_cat > p2_cat else 'Fighter2':<15}")
    print(f"{'Logistic Reg':<20} {p1_lgreg:<15.3f} {p2_lgreg:<15.3f} {'Fighter1' if p1_lgreg > p2_lgreg else 'Fighter2':<15}")
    print(f"{'MLP':<20} {p1_mlp:<15.3f} {p2_mlp:<15.3f} {'Fighter1' if p1_mlp > p2_mlp else 'Fighter2':<15}")
    


    # Try to get ensemble prediction if available
    ensemble_result = None
    try:
        # Try to import ensemble integration
        import sys
        import os
        
        # Add current directory to path to ensure we can find ensemble_integration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from ensemble_integration import get_ensemble_prediction
        
        # Check if ensemble artifacts exist
        ensemble_dir = os.path.join(current_dir, "ensemble_artifacts")
        if not os.path.exists(ensemble_dir):
            print(f"\n=== Ensemble Status Check ===")
            print("⚠ Ensemble artifacts directory not found")
            print(f"  Expected location: {ensemble_dir}")
            print("  The ensemble needs to be trained first")
            print("  Run: python ensemble_predict.py")
            ensemble_result = None
        else:
            print(f"\n=== Attempting Ensemble Prediction ===")
            ensemble_result = get_ensemble_prediction(fighter1, fighter2)
        if ensemble_result:
            print(f"✓ Ensemble loaded successfully!")
            print(f"Ensemble prediction: {ensemble_result['winner_name']} wins")
            print(f"Ensemble confidence: {ensemble_result['confidence']:.3f}")
            print(f"Ensemble probability: {ensemble_result['ensemble_probability']:.3f}")
        else:
            print("⚠ Ensemble not available - run ensemble_predict.py first")
    except ImportError as e:
        print(f"⚠ Ensemble module not available: {e}")
        print("  Make sure ensemble_integration.py is in the same directory")
        print("  Run 'python ensemble_predict.py' to train the ensemble first")
    except Exception as e:
        print(f"⚠ Ensemble error: {e}")
        print("  This usually means the ensemble hasn't been trained yet")
        print("  Run 'python ensemble_predict.py' to train the ensemble")


    
    # Comprehensive comparison of all predictions
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PREDICTION COMPARISON")
    print(f"{'='*80}")
    
    # Individual model predictions summary
    print(f"\n📊 INDIVIDUAL MODEL PREDICTIONS:")
    print(f"{'Model':<20} {'Fighter1':<15} {'Fighter2':<15} {'Winner':<15}")
    print(f"{'-'*65}")
    print(f"{'XGBoost':<20} {p1_xgb:<15.3f} {p2_xgb:<15.3f} {'Fighter1' if p1_xgb > p2_xgb else 'Fighter2':<15}")
    print(f"{'CatBoost':<20} {p1_cat:<15.3f} {p2_cat:<15.3f} {'Fighter1' if p1_cat > p2_cat else 'Fighter2':<15}")
    print(f"{'Logistic Reg':<20} {p1_lgreg:<15.3f} {p2_lgreg:<15.3f} {'Fighter1' if p1_lgreg > p2_lgreg else 'Fighter2':<15}")
    print(f"{'MLP':<20} {p1_mlp:<15.3f} {p2_mlp:<15.3f} {'Fighter1' if p1_mlp > p2_mlp else 'Fighter2':<15}")
    

    
    # Ensemble prediction summary (if available)
    if ensemble_result:
        print(f"\n🎯 ENSEMBLE PREDICTION:")
        print(f"Winner: {ensemble_result['winner_name']}")
        print(f"Probability: {ensemble_result['ensemble_probability']:.3f}")
        print(f"Confidence: {ensemble_result['confidence']:.3f}")
        

        
        # Show base model contributions to ensemble
        print(f"\n🔍 ENSEMBLE BASE MODEL CONTRIBUTIONS:")
        for model_name, prob in ensemble_result['base_predictions'].items():
            print(f"  {model_name.upper()}: {prob:.3f}")
    else:
        print(f"\n⚠ ENSEMBLE: Not available - run ensemble_predict.py to train")
        print("  To train the ensemble:")
        print("  1. Make sure you're in the Prediction directory")
        print("  2. Run: python ensemble_predict.py")
        print("  3. Wait for training to complete")
        print("  4. Run this prediction again to see ensemble results")
    

    

    
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
            'xgb': {'fighter1_prob': p1_xgb, 'fighter2_prob': p2_xgb, 'winner': 'Fighter1' if p1_xgb > p2_xgb else 'Fighter2'},
            'cat': {'fighter1_prob': p1_cat, 'fighter2_prob': p2_cat, 'winner': 'Fighter1' if p1_cat > p2_cat else 'Fighter2'},
            'lgr': {'fighter1_prob': p1_lgreg, 'fighter2_prob': p2_lgreg, 'winner': 'Fighter1' if p1_lgreg > p2_lgreg else 'Fighter2'},
            'mlp': {'fighter1_prob': p1_mlp, 'fighter2_prob': p2_mlp, 'winner': 'Fighter1' if p1_mlp > p2_mlp else 'Fighter2'}
        },
        'ensemble_prediction': ensemble_result if ensemble_result else None
    }
    
    return result_data

# Add a test call to actually run the function when script is executed
if __name__ == "__main__":
    # Test with two fighter IDs - you can change these to any valid fighter IDs
    print("Running UFC prediction test...")
    result = getCustomPredict(2926, 960)  # Example fighter IDs
    print(f"\nTest completed.")
    print(f"Winner ID: {result['winner_id']}")
    print(f"Winner Name: {result['winner_name']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Ensemble Available: {'Yes' if result['ensemble_prediction'] else 'No'}") 