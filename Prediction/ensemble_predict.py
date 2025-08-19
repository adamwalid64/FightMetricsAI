# =========================
# OOF Stacking Ensemble for UFC Prediction Models
# =========================
import os
import json
import numpy as np
import pandas as pd
import joblib
import random
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, classification_report, confusion_matrix

# Import your existing models
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

# Torch MLP wrapper (sklearn-style)
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)
torch.manual_seed(RANDOM_STATE)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_STATE)

class TorchMLPClassifier:
    """Minimal sklearn-like wrapper for a PyTorch MLP with scaling inside."""
    def __init__(self, hidden=(96, 48, 24), dropout=0.1, lr=1e-3, weight_decay=1e-4,
                 batch_size=256, max_epochs=100, patience=12, verbose=False):
        self.hidden = hidden
        self.dropout = dropout
        self.lr = lr
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.patience = patience
        self.verbose = verbose
        self.scaler = StandardScaler()
        self.model_ = None
        self.pos_weight_ = None

    def _build(self, in_dim):
        layers, prev = [], in_dim
        for h in self.hidden:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(self.dropout)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        net = nn.Sequential(*layers)
        return net.to(DEVICE)

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        Xs = self.scaler.fit_transform(X)
        Xtr = torch.tensor(Xs, dtype=torch.float32, device=DEVICE)
        ytr = torch.tensor(y, dtype=torch.float32, device=DEVICE)

        pos = (y == 1).sum()
        neg = (y == 0).sum()
        self.pos_weight_ = None
        if pos > 0 and neg > 0:
            self.pos_weight_ = torch.tensor([neg / max(pos, 1)], dtype=torch.float32, device=DEVICE)

        self.model_ = self._build(Xtr.shape[1])
        opt = torch.optim.Adam(self.model_.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        crit = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight_) if self.pos_weight_ is not None else nn.BCEWithLogitsLoss()

        ds = TensorDataset(Xtr, ytr)
        dl = DataLoader(ds, batch_size=self.batch_size, shuffle=True)

        best_state, best_loss = None, float("inf")
        wait = self.patience
        for epoch in range(1, self.max_epochs+1):
            self.model_.train()
            epoch_loss = 0.0
            for xb, yb in dl:
                opt.zero_grad()
                logits = self.model_(xb).squeeze(1)
                loss = crit(logits, yb)
                loss.backward()
                opt.step()
                epoch_loss += loss.item()
            if self.verbose:
                print(f"[TorchMLP] epoch {epoch} loss={epoch_loss/len(dl):.4f}")
            # early stopping on train loss (simple + fast)
            if epoch_loss < best_loss - 1e-5:
                best_loss = epoch_loss
                best_state = {k: v.detach().cpu().clone() for k, v in self.model_.state_dict().items()}
                wait = self.patience
            else:
                wait -= 1
                if wait <= 0:
                    break
        if best_state is not None:
            self.model_.load_state_dict(best_state)

        return self

    def predict_proba(self, X):
        assert self.model_ is not None, "Call fit first"
        X = np.asarray(X, dtype=float)
        Xs = self.scaler.transform(X)
        xb = torch.tensor(Xs, dtype=torch.float32, device=DEVICE)
        self.model_.eval()
        with torch.no_grad():
            logits = self.model_(xb).squeeze(1)
            probs = torch.sigmoid(logits).detach().cpu().numpy()
        # return as (n,2) like sklearn
        probs = np.clip(probs, 1e-7, 1-1e-7)
        return np.column_stack([1-probs, probs])

    # convenience for saving
    def save(self, path_prefix):
        os.makedirs(os.path.dirname(path_prefix), exist_ok=True)
        torch.save(self.model_.state_dict(), path_prefix + "_model.pt")
        joblib.dump(self.scaler, path_prefix + "_scaler.pkl")
        # Save input_dim along with other metadata
        meta = dict(
            hidden=list(self.hidden), 
            dropout=float(self.dropout),
            input_dim=self.model_[0].in_features if self.model_ is not None else None
        )
        with open(path_prefix + "_meta.json", "w") as f:
            json.dump(meta, f, indent=2)

def load_ufc_data():
    """Load and prepare UFC data for ensemble training"""
    print("Loading UFC dataset...")
    
    # Load the dataset (same as in your notebooks)
    df = pd.read_csv("../Data/large_dataset.csv")
    
    # Create binary winner label
    df['winner_binary'] = df['winner'].map({'Red': 1, 'Blue': 0})
    
    # Define features (same as in your notebooks)
    diff_features = [
        'SLpM_total_diff', 'SApM_total_diff', 'sig_str_acc_total_diff',
        'td_acc_total_diff', 'str_def_total_diff', 'td_def_total_diff',
        'sub_avg_diff', 'td_avg_diff', 'age_diff', 'height_diff', 
        'reach_diff', 'wins_total_diff', 'losses_total_diff'
    ]
    
    # Drop rows with missing values in key columns
    df = df.dropna(subset=diff_features + ['winner_binary'])
    
    # Reverse for chronological ordering (same as your notebooks)
    df = df.iloc[::-1].reset_index(drop=True)
    
    # Split dataset (same split as your notebooks)
    split_idx = int(len(df) * (2 / 3))
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    # Define features and targets
    X_train = train_df[diff_features]
    y_train = train_df['winner_binary']
    X_test = test_df[diff_features]
    y_test = test_df['winner_binary']
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Features: {len(diff_features)}")
    
    return X_train, y_train, X_test, y_test, diff_features

# -----------------------
# Define base models (matching your existing models)
# -----------------------
def get_base_models():
    """Get base models with parameters matching your existing trained models"""
    BASE_MODELS = {
        "xgb": XGBClassifier(
            n_estimators=500, max_depth=4, learning_rate=0.06, subsample=0.9, 
            colsample_bytree=0.8, reg_lambda=1.0, random_state=RANDOM_STATE, 
            n_jobs=-1, tree_method="hist"
        ),
        "cat": CatBoostClassifier(
            iterations=700, depth=5, learning_rate=0.07, l2_leaf_reg=3.0,
            loss_function="Logloss", verbose=False, random_seed=RANDOM_STATE
        ),
        "lgr": LogisticRegression(max_iter=2000, C=2.0, class_weight=None, 
                                 n_jobs=-1, solver="lbfgs", random_state=RANDOM_STATE),
        "mlp": TorchMLPClassifier(
            hidden=(96, 48, 24), dropout=0.1, lr=1e-3, weight_decay=1e-4,
            batch_size=256, max_epochs=120, patience=15, verbose=False
        )
    }
    return BASE_MODELS

def train_ensemble():
    """Train the OOF stacking ensemble"""
    # Load data
    X_train, y_train, X_test, y_test, diff_features = load_ufc_data()
    
    # Get base models
    BASE_MODELS = get_base_models()
    
    # Convert to numpy arrays
    Xtr = X_train.values
    ytr = y_train.values.astype(int)
    Xte = X_test.values
    yte = y_test.values.astype(int)
    
    # Create and fit global scaler on training data
    print("\n--- Creating Global Feature Scaler ---")
    global_scaler = StandardScaler()
    Xtr_scaled = global_scaler.fit_transform(Xtr)
    Xte_scaled = global_scaler.transform(Xte)
    print(f"Global scaler fitted on {Xtr_scaled.shape[0]} training samples")
    
    # Setup cross-validation
    K = 5
    skf = StratifiedKFold(n_splits=K, shuffle=True, random_state=RANDOM_STATE)
    
    # Initialize OOF predictions matrix
    oof = np.zeros((len(Xtr), len(BASE_MODELS)))
    model_keys = list(BASE_MODELS.keys())
    
    print(f"\nBuilding OOF predictions with {K} folds...")
    print(f"Base models: {model_keys}")
    
    # Build OOF predictions for each model
    for m_idx, m_name in enumerate(model_keys):
        print(f"\n--- Training {m_name.upper()} ---")
        oof_col = np.zeros(len(Xtr))
        
        for fold, (tr_idx, va_idx) in enumerate(skf.split(Xtr, ytr), 1):
            X_tr, y_tr = Xtr_scaled[tr_idx], ytr[tr_idx]
            X_va, y_va = Xtr_scaled[va_idx], ytr[va_idx]
            
            # Create fresh instance per fold (NO scaler needed since features are pre-scaled)
            if m_name == "xgb":
                m = XGBClassifier(**BASE_MODELS[m_name].get_params())
            elif m_name == "cat":
                m = CatBoostClassifier(**BASE_MODELS[m_name].get_params())
            elif m_name == "lgr":
                m = LogisticRegression(max_iter=2000, C=2.0, n_jobs=-1, 
                                     solver="lbfgs", random_state=RANDOM_STATE)
            elif m_name == "mlp":
                m = TorchMLPClassifier(
                    hidden=(96, 48, 24), dropout=0.1, lr=1e-3, weight_decay=1e-4,
                    batch_size=256, max_epochs=120, patience=15, verbose=False
                )
            
            # Fit on K-1 folds (using pre-scaled features)
            m.fit(X_tr, y_tr)
            
            # Predict on held-out fold
            p = m.predict_proba(X_va)[:, 1]
            oof_col[va_idx] = p
            
            print(f"  Fold {fold}: OOF filled for {len(va_idx)} rows")
        
        oof[:, m_idx] = oof_col
    
    print(f"\nOOF matrix shape: {oof.shape}")
    print(f"OOF columns: {model_keys}")
    
    # Fit meta-learner on OOF predictions
    print("\n--- Training Meta-Learner ---")
    meta = LogisticRegression(max_iter=5000, C=1.0, solver="lbfgs", random_state=RANDOM_STATE)
    meta.fit(oof, ytr)
    
    # Refit base models on ALL training data for test-time (using pre-scaled features)
    print("\n--- Refitting Base Models on Full Training Data ---")
    fit_models = {}
    for m_name in model_keys:
        print(f"Refitting {m_name}...")
        base = BASE_MODELS[m_name]
        
        if m_name == "xgb":
            model = XGBClassifier(**base.get_params())
        elif m_name == "cat":
            model = CatBoostClassifier(**base.get_params())
        elif m_name == "lgr":
            model = LogisticRegression(max_iter=2000, C=2.0, n_jobs=-1, 
                                     solver="lbfgs", random_state=RANDOM_STATE)
        elif m_name == "mlp":
            model = TorchMLPClassifier(
                hidden=(96, 48, 24), dropout=0.1, lr=1e-3, weight_decay=1e-4,
                batch_size=256, max_epochs=120, patience=15, verbose=False
            )
        
        model.fit(Xtr_scaled, ytr)
        fit_models[m_name] = model
    
    # Test-time predictions (using pre-scaled features)
    print("\n--- Making Test Predictions ---")
    P_test = []
    for m_name in model_keys:
        P_test.append(fit_models[m_name].predict_proba(Xte_scaled)[:, 1])
    P_test = np.column_stack(P_test)
    
    # Meta-learner prediction
    y_pred = (meta.predict_proba(P_test)[:, 1] >= 0.5).astype(int)
    
    # Print metrics
    print("\n=== STACKED ENSEMBLE TEST METRICS ===")
    print(f"Accuracy:        {accuracy_score(yte, y_pred):.4f}")
    print(f"Balanced Acc:    {balanced_accuracy_score(yte, y_pred):.4f}")
    print(f"F1-macro:        {f1_score(yte, y_pred, average='macro'):.4f}")
    print(f"\nClassification Report:")
    print(classification_report(yte, y_pred, digits=3))
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(yte, y_pred))
    
    # Save ensemble artifacts
    save_ensemble_artifacts(fit_models, meta, diff_features, model_keys, global_scaler)
    
    return fit_models, meta, oof, P_test

def save_ensemble_artifacts(fit_models, meta, diff_features, model_keys, global_scaler):
    """Save ensemble artifacts for later use"""
    STACK_DIR = "ensemble_artifacts"
    os.makedirs(STACK_DIR, exist_ok=True)
    
    print(f"\n--- Saving Ensemble Artifacts to {STACK_DIR} ---")
    
    # Save global scaler
    joblib.dump(global_scaler, os.path.join(STACK_DIR, "global_scaler.pkl"))
    print("Saved global scaler")
    
    # Save base models
    for name, model in fit_models.items():
        if name == "mlp":
            # Custom save for torch wrapper
            model.save(os.path.join(STACK_DIR, f"{name}"))
        else:
            joblib.dump(model, os.path.join(STACK_DIR, f"{name}.joblib"))
        print(f"Saved {name} model")
    
    # Save meta-learner
    joblib.dump(meta, os.path.join(STACK_DIR, "meta_learner.joblib"))
    print("Saved meta-learner")
    
    # Save metadata
    metadata = {
        "features": diff_features,
        "base_models": model_keys,
        "threshold": 0.5,
        "ensemble_type": "OOF_Stacking",
        "meta_learner": "LogisticRegression"
    }
    
    with open(os.path.join(STACK_DIR, "ensemble_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("Saved ensemble metadata")
    
    print(f"\nAll ensemble artifacts saved in ./{STACK_DIR}")

def load_ensemble_for_prediction():
    """Load trained ensemble for making predictions"""
    # Use absolute path to ensemble artifacts directory
    STACK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ensemble_artifacts")
    
    if not os.path.exists(STACK_DIR):
        raise FileNotFoundError(f"Ensemble artifacts not found in {STACK_DIR}. Please run train_ensemble() first.")
    
    print(f"Loading ensemble from {STACK_DIR}...")
    
    # Load metadata
    with open(os.path.join(STACK_DIR, "ensemble_meta.json"), "r") as f:
        metadata = json.load(f)
    
    print(f"Loaded metadata: {len(metadata['features'])} features, {len(metadata['base_models'])} base models")
    
    # Load global scaler
    global_scaler = joblib.load(os.path.join(STACK_DIR, "global_scaler.pkl"))
    print("Loaded global scaler")

    # Load base models
    fit_models = {}
    for model_name in metadata["base_models"]:
        print(f"Loading {model_name} model...")
        try:
            if model_name == "mlp":
                # Load MLP components
                with open(os.path.join(STACK_DIR, f"{model_name}_meta.json"), "r") as f:
                    mlp_meta = json.load(f)
                mlp_scaler = joblib.load(os.path.join(STACK_DIR, f"{model_name}_scaler.pkl"))
                
                print(f"  MLP metadata: {mlp_meta}")
                print(f"  MLP scaler shape: {mlp_scaler.n_features_in_ if hasattr(mlp_scaler, 'n_features_in_') else 'Unknown'}")
                
                # Recreate MLP model
                model = TorchMLPClassifier(
                    hidden=tuple(mlp_meta["hidden"]), 
                    dropout=mlp_meta["dropout"]
                )
                model.scaler = mlp_scaler
                
                # Get input_dim from metadata or infer from scaler
                input_dim = mlp_meta.get("input_dim")
                if input_dim is None:
                    # Fallback: infer from scaler or use default
                    input_dim = len(metadata["features"])
                    print(f"  Warning: input_dim not found in MLP metadata, using {input_dim}")
                
                print(f"  Building MLP with input_dim={input_dim}")
                model.model_ = model._build(input_dim)
                model.model_.load_state_dict(torch.load(os.path.join(STACK_DIR, f"{model_name}_model.pt"), map_location=DEVICE))
                model.model_.to(DEVICE)
                print(f"  ✓ MLP loaded successfully")
            else:
                model = joblib.load(os.path.join(STACK_DIR, f"{model_name}.joblib"))
                print(f"  ✓ {model_name} loaded successfully")
            
            fit_models[model_name] = model
        except Exception as e:
            print(f"  ✗ Error loading {model_name}: {e}")
            raise e
    
    # Load meta-learner
    print("Loading meta-learner...")
    meta = joblib.load(os.path.join(STACK_DIR, "meta_learner.joblib"))
    print("✓ Meta-learner loaded successfully")
    
    return fit_models, meta, metadata, global_scaler

def predict_with_ensemble(fighter1_data, fighter2_data, fit_models, meta, metadata, global_scaler):
    """Make prediction using the trained ensemble"""
    print(f"Making ensemble prediction...")
    print(f"Fighter1 data keys: {list(fighter1_data.keys())}")
    print(f"Fighter2 data keys: {list(fighter2_data.keys())}")
    print(f"Expected features: {metadata['features']}")
    
    # Calculate differences (same logic as in custom_inputs.py)
    def safe_diff(val1, val2):
        if pd.isna(val1) or pd.isna(val2):
            return 0.0
        return val1 - val2
    
    # Create feature differences
    features = metadata["features"]
    
    # Helper function to convert height string to cm (same as in custom_inputs.py)
    def height_str_to_cm(height_str):
        try:
            if pd.isna(height_str):
                return 0
            feet, inches = height_str.replace('"', '').split("'")
            feet = int(feet.strip())
            inches = int(inches.strip())
            return int(feet * 30.48 + inches * 2.54)
        except:
            return 0
    
    # Convert heights to cm for proper difference calculation
    f1_height = height_str_to_cm(fighter1_data['height'])
    f2_height = height_str_to_cm(fighter2_data['height'])
    
    X = pd.DataFrame([{
        'SLpM_total_diff': safe_diff(fighter1_data['SLpM'], fighter2_data['SLpM']),
        'SApM_total_diff': safe_diff(fighter1_data['SApM'], fighter2_data['SApM']),
        'sig_str_acc_total_diff': safe_diff(fighter1_data['Str_Acc'], fighter2_data['Str_Acc']),
        'td_acc_total_diff': safe_diff(fighter1_data['TD_Acc'], fighter2_data['TD_Acc']),
        'str_def_total_diff': safe_diff(fighter1_data['Str_Def'], fighter2_data['Str_Def']),
        'td_def_total_diff': safe_diff(fighter1_data['TD_Def'], fighter2_data['TD_Def']),
        'sub_avg_diff': safe_diff(fighter1_data['Sub_Avg'], fighter2_data['Sub_Avg']),
        'td_avg_diff': safe_diff(fighter1_data['TD_Avg'], fighter2_data['TD_Avg']),
        'age_diff': safe_diff(fighter1_data['age'], fighter2_data['age']),
        'height_diff': safe_diff(f1_height, f2_height),  # Use converted heights
        'reach_diff': safe_diff(fighter1_data['reach'], fighter2_data['reach']),
        'wins_total_diff': safe_diff(fighter1_data['wins'], fighter2_data['losses']),
        'losses_total_diff': safe_diff(fighter1_data['losses'], fighter2_data['losses'])
    }])
    
    print(f"Created feature differences DataFrame:")
    print(f"  Shape: {X.shape}")
    print(f"  Columns: {list(X.columns)}")
    print(f"  Sample values: {X.iloc[0].to_dict()}")
    
    # Apply global scaling to features (same as during training)
    X_scaled = global_scaler.transform(X[features].astype(float).values)
    print(f"Applied global scaling to features")
    
    # Get base model predictions (using scaled features)
    base_predictions = []
    for model_name in metadata["base_models"]:
        try:
            model = fit_models[model_name]
            print(f"  Getting prediction from {model_name}...")
            
            if model_name == "mlp":
                # MLP already has its own scaler, but we'll use the global scaled features
                print(f"    MLP input shape: {X_scaled.shape}")
                X_tensor = torch.tensor(X_scaled, dtype=torch.float32, device=DEVICE)
                print(f"    MLP tensor shape: {X_tensor.shape}")
                
                # Check if model is properly loaded
                if model.model_ is None:
                    print(f"    Error: MLP model is None!")
                    prob = 0.5
                else:
                    model.model_.eval()
                    with torch.no_grad():
                        logits = model.model_(X_tensor)
                        print(f"    MLP logits shape: {logits.shape}")
                        prob = float(torch.sigmoid(logits).cpu().numpy()[0])
                        print(f"    MLP raw prob: {prob}")
            else:
                # All other models get the globally scaled features
                prob_array = model.predict_proba(X_scaled)[:, 1]
                prob = float(prob_array[0])
                print(f"    {model_name} raw prob: {prob}")
            
            # Ensure prob is a scalar float
            if not isinstance(prob, (int, float)) or np.isnan(prob):
                print(f"    Warning: {model_name} returned invalid prob: {prob}, using 0.5")
                prob = 0.5
            
            base_predictions.append(prob)
            print(f"    Final {model_name} prob: {prob}")
            
        except Exception as e:
            print(f"    Error with {model_name} model: {e}")
            print(f"    Model type: {type(model)}")
            if model_name == "mlp":
                print(f"    MLP model state: model_={model.model_ is not None}, scaler={model.scaler is not None}")
            # Use fallback probability instead of crashing
            print(f"    Using fallback probability 0.5 for {model_name}")
            base_predictions.append(0.5)
    
    print(f"  All base predictions: {base_predictions}")
    
    # Meta-learner prediction
    try:
        base_predictions_array = np.array(base_predictions, dtype=float).reshape(1, -1)
        print(f"  Reshaped base predictions: {base_predictions_array.shape}, values: {base_predictions_array}")
        
        # Ensure the array is valid for the meta-learner
        if np.any(np.isnan(base_predictions_array)) or np.any(np.isinf(base_predictions_array)):
            print(f"  Warning: Invalid values in base predictions, clipping to [0,1]")
            base_predictions_array = np.clip(base_predictions_array, 0.0, 1.0)
        
        ensemble_prob = float(meta.predict_proba(base_predictions_array)[:, 1][0])
        print(f"  Final ensemble probability: {ensemble_prob}")
        
        # Ensure ensemble probability is valid
        if np.isnan(ensemble_prob) or np.isinf(ensemble_prob):
            print(f"  Warning: Invalid ensemble probability, using 0.5")
            ensemble_prob = 0.5
        
        return ensemble_prob, base_predictions
        
    except Exception as e:
        print(f"  Error in meta-learner prediction: {e}")
        print(f"  Using fallback ensemble probability 0.5")
        return 0.5, base_predictions

if __name__ == "__main__":
    print("UFC Ensemble Prediction Training")
    print("=" * 40)
    
    # Train the ensemble
    fit_models, meta, oof, P_test = train_ensemble()
    
    print("\n" + "=" * 40)
    print("Ensemble training completed successfully!")
    print("You can now use load_ensemble_for_prediction() to load the trained ensemble")
    print("and predict_with_ensemble() to make predictions on new fighter data.")
