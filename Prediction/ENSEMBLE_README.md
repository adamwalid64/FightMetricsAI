# UFC Ensemble Prediction System

This directory contains an Out-of-Fold (OOF) Stacking Ensemble system that combines your existing UFC prediction models for improved accuracy.

## Overview

The ensemble system uses a stacking approach where:
1. **Base Models**: Your existing XGBoost, CatBoost, Logistic Regression, and MLP models
2. **OOF Predictions**: Cross-validation predictions to prevent data leakage
3. **Meta-Learner**: A Logistic Regression model that learns to combine base model predictions

## Files

- `ensemble_predict.py` - Main ensemble training script
- `ensemble_integration.py` - Integration script for using the ensemble
- `custom_inputs.py` - Enhanced prediction script (shows individual + ensemble)
- `test_enhanced_predictions.py` - Test script for the enhanced system
- `check_ensemble_status.py` - Diagnostic script to check ensemble setup
- `ENSEMBLE_README.md` - This documentation file

## Quick Start

### 1. Train the Ensemble

```bash
cd Prediction
python ensemble_predict.py
```

This will:
- Load your UFC dataset from `../Data/large_dataset.csv`
- Train all base models using 5-fold cross-validation
- Generate OOF predictions for each model
- Train a meta-learner on the OOF predictions
- Save all artifacts to `ensemble_artifacts/` directory

### 2. Use the Enhanced Prediction System

The enhanced `custom_inputs.py` now shows both individual model predictions AND ensemble predictions:

```python
# Run the enhanced prediction function
from custom_inputs import getCustomPredict

# This will show:
# 1. Individual model predictions (XGBoost, CatBoost, Logistic Regression, MLP)
# 2. Voting system results
# 3. Ensemble prediction (if available)
# 4. Comprehensive comparison
result = getCustomPredict(fighter1_id, fighter2_id)
```

### 3. Use the Ensemble Directly

```python
from ensemble_integration import get_ensemble_prediction

# Get prediction for two fighters
result = get_ensemble_prediction(fighter1_id, fighter2_id)

if result:
    print(f"Winner: {result['winner_name']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Base model predictions: {result['base_predictions']}")
```

## How It Works

### Data Flow
1. **Data Loading**: Uses the same dataset and features as your existing models
2. **Feature Engineering**: Calculates fighter differences (same as `custom_inputs.py`)
3. **Cross-Validation**: 5-fold stratified split to generate OOF predictions
4. **Model Training**: Each base model is trained on 4 folds, predicts on 1 fold
5. **Meta-Learning**: Logistic Regression learns optimal weights for combining predictions

### Base Models
- **XGBoost**: Gradient boosting with your existing hyperparameters
- **CatBoost**: Categorical boosting with your existing hyperparameters  
- **Logistic Regression**: Linear model with StandardScaler preprocessing
- **MLP**: PyTorch neural network with your existing architecture (96→48→24)

### Meta-Learner
- **Algorithm**: Logistic Regression
- **Input**: OOF predictions from all base models
- **Output**: Final ensemble probability

## Integration with Existing Code

### Replace Individual Model Calls

**Before (individual models):**
```python
# Individual predictions
p1_xgb = xgb_model.predict_proba(X1)[0][1]
p1_cat = catboost_model.predict_proba(X1)[0][1]
p1_lgreg = lgreg_model.predict_proba(X1_scaled)[0][1]
p1_mlp = mlp_model(X1_tensor).sigmoid().cpu().numpy()[0]

# Simple voting
votes = [p1_xgb > 0.5, p1_cat > 0.5, p1_lgreg > 0.5, p1_mlp > 0.5]
winner = "fighter1" if sum(votes) > 2 else "fighter2"
```

**After (ensemble):**
```python
from ensemble_integration import get_ensemble_prediction

# Single ensemble prediction
result = get_ensemble_prediction(fighter1_id, fighter2_id)
winner = result['winner_name']
confidence = result['confidence']
```

### Update main.py

```python
# Add ensemble import
from ensemble_integration import get_ensemble_prediction

def masterPrediction(fighter1id, fighter2id):
    # ... existing code ...
    
    # Replace individual model calls with ensemble
    ensemble_result = get_ensemble_prediction(fighter1id, fighter2id)
    
    if ensemble_result:
        print(f"Ensemble Prediction: {ensemble_result['winner_name']} wins")
        print(f"Confidence: {ensemble_result['confidence']:.3f}")
    
    # ... rest of existing code ...
```

## Performance Benefits

### Expected Improvements
- **Higher Accuracy**: Ensemble typically outperforms individual models
- **Better Calibration**: More reliable probability estimates
- **Reduced Variance**: Less sensitive to individual model failures
- **Robust Predictions**: Combines strengths of different algorithms

### Model Comparison
The ensemble learns which models are most reliable for different types of fights:
- **XGBoost**: Good for complex feature interactions
- **CatBoost**: Handles categorical features well
- **Logistic Regression**: Provides linear decision boundaries
- **MLP**: Captures non-linear patterns

## Advanced Usage

### Custom Ensemble Configuration

```python
from ensemble_predict import get_base_models, train_ensemble

# Customize base models
BASE_MODELS = get_base_models()
BASE_MODELS['custom_xgb'] = XGBClassifier(n_estimators=1000, max_depth=6)

# Train with custom configuration
fit_models, meta, oof, P_test = train_ensemble()
```

### Ensemble Analysis

```python
# Load trained ensemble
fit_models, meta, metadata = load_ensemble_for_prediction()

# Analyze base model contributions
base_predictions = []
for model_name in metadata['base_models']:
    model = fit_models[model_name]
    prob = model.predict_proba(X)[:, 1]
    base_predictions.append(prob)

# Meta-learner coefficients show model importance
print("Model Weights:", meta.coef_[0])
```

## Troubleshooting

### Common Issues

1. **"Ensemble artifacts not found"**
   - Solution: Run `python ensemble_predict.py` first

2. **Memory issues during training**
   - Solution: Reduce batch size in MLP or use fewer folds

3. **Slow training**
   - Solution: Reduce max_epochs for MLP or use fewer estimators for tree models

### Performance Tuning

- **Cross-validation folds**: Increase for better OOF estimates (slower training)
- **MLP architecture**: Adjust hidden layers and dropout
- **Meta-learner**: Try different algorithms (Ridge, SVM, etc.)

## File Structure After Training

```
Prediction/
├── ensemble_artifacts/
│   ├── xgb.joblib              # Trained XGBoost model
│   ├── cat.joblib              # Trained CatBoost model  
│   ├── lgr.joblib              # Trained Logistic Regression model
│   ├── mlp_model.pt            # Trained PyTorch MLP weights
│   ├── mlp_scaler.pkl          # MLP feature scaler
│   ├── mlp_meta.json           # MLP architecture metadata
│   ├── meta_learner.joblib     # Trained meta-learner
│   └── ensemble_meta.json      # Ensemble configuration
├── ensemble_predict.py          # Training script
├── ensemble_integration.py      # Integration script
└── ENSEMBLE_README.md           # This file
```

## Next Steps

1. **Check ensemble status**: `python check_ensemble_status.py`
2. **Train the ensemble**: `python ensemble_predict.py`
3. **Test enhanced predictions**: `python test_enhanced_predictions.py`
4. **Use enhanced predictions**: `python custom_inputs.py`
5. **Test ensemble integration**: `python ensemble_integration.py`
6. **Integrate with main.py**: Replace individual model calls
7. **Monitor performance**: Compare ensemble vs individual model accuracy
8. **Fine-tune**: Adjust hyperparameters based on results

## Support

For questions or issues:
1. Check the error messages in the console output
2. Verify all required packages are installed
3. Ensure the dataset path is correct
4. Check that individual models are working correctly

The ensemble system is designed to work seamlessly with your existing UFC prediction infrastructure while providing improved accuracy through model combination.
