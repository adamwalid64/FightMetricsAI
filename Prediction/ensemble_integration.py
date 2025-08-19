# =========================
# Ensemble Integration with Existing UFC Prediction Code
# =========================
import pandas as pd
import numpy as np
from ensemble_predict import load_ensemble_for_prediction, predict_with_ensemble
import os

def get_ensemble_prediction(fighter1_id, fighter2_id):
    """
    Get ensemble prediction for two fighters using the trained stacking ensemble.
    This integrates with your existing fighter lookup system.
    """
    try:
        # Load the trained ensemble
        print("Loading trained ensemble...")
        fit_models, meta, metadata, global_scaler = load_ensemble_for_prediction()
        print(f"Loaded ensemble with {len(metadata['base_models'])} base models")
        
        # Load fighter data (same as in your existing code)
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "raw-scraped-ufc-data2.csv")
        fighter_lookup = pd.read_csv(data_path)
        
        # Get fighter data
        fighter1_data = fighter_lookup.loc[fighter_lookup['id'] == fighter1_id]
        fighter2_data = fighter_lookup.loc[fighter_lookup['id'] == fighter2_id]
        
        if fighter1_data.empty or fighter2_data.empty:
            print(f"Fighter not found: fighter1={fighter1_id}, fighter2={fighter2_id}")
            return None
        
        fighter1_name = fighter1_data['name'].iloc[0]
        fighter2_name = fighter2_data['name'].iloc[0]
        
        print(f"\n=== Ensemble Prediction: {fighter1_name} vs {fighter2_name} ===")
        
        # Get fighter stats for prediction
        columns = ['SLpM', 'SApM', 'Str_Acc', 'TD_Acc', 'Str_Def', 'TD_Def', 
                   'Sub_Avg', 'TD_Avg', 'age', 'height', 'reach', 'wins', 'losses']
        
        f1_stats = fighter1_data[columns].iloc[0]
        f2_stats = fighter2_data[columns].iloc[0]
        
        # Make ensemble prediction (pass global_scaler)
        ensemble_prob, base_predictions = predict_with_ensemble(f1_stats, f2_stats, fit_models, meta, metadata, global_scaler)
        
        # Display results
        print(f"\nBase Model Predictions:")
        for i, model_name in enumerate(metadata['base_models']):
            print(f"  {model_name.upper()}: {base_predictions[i]:.3f}")
        
        print(f"\nEnsemble Prediction: {ensemble_prob:.3f}")
        
        # Determine winner
        if ensemble_prob > 0.5:
            winner_name = fighter1_name
            winner_id = fighter1_id
            confidence = ensemble_prob
        else:
            winner_name = fighter2_name
            winner_id = fighter2_id
            confidence = 1 - ensemble_prob
        
        print(f"\nPredicted Winner: {winner_name} (ID: {winner_id})")
        print(f"Confidence: {confidence:.3f}")
        
        return {
            'winner_id': winner_id,
            'winner_name': winner_name,
            'ensemble_probability': ensemble_prob,
            'base_predictions': dict(zip(metadata['base_models'], base_predictions)),
            'confidence': confidence
        }
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run ensemble_predict.py first to train the ensemble.")
        return None
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

def compare_ensemble_with_individual_models(fighter1_id, fighter2_id):
    """
    Compare ensemble prediction with individual model predictions
    """
    print("=" * 60)
    print("COMPARING ENSEMBLE vs INDIVIDUAL MODELS")
    print("=" * 60)
    
    # Get ensemble prediction
    ensemble_result = get_ensemble_prediction(fighter1_id, fighter2_id)
    
    if ensemble_result is None:
        return
    
    print(f"\n{'='*60}")
    print("ENSEMBLE SUMMARY")
    print(f"{'='*60}")
    print(f"Winner: {ensemble_result['winner_name']}")
    print(f"Ensemble Probability: {ensemble_result['ensemble_probability']:.3f}")
    print(f"Confidence: {ensemble_result['confidence']:.3f}")
    
    print(f"\nBase Model Contributions:")
    for model_name, prob in ensemble_result['base_predictions'].items():
        print(f"  {model_name.upper()}: {prob:.3f}")
    
    # You can add comparison with your existing individual model predictions here
    # by calling your existing prediction functions

if __name__ == "__main__":
    # Example usage - replace with actual fighter IDs
    print("UFC Ensemble Integration Test")
    print("=" * 40)
    
    # Test with example fighter IDs (you can change these)
    fighter1_id = 1527  # Example fighter ID
    fighter2_id = 3035  # Example fighter ID
    
    print(f"Testing ensemble prediction for fighters {fighter1_id} vs {fighter2_id}")
    
    # Get ensemble prediction
    result = get_ensemble_prediction(fighter1_id, fighter2_id)
    
    if result:
        print(f"\nTest completed successfully!")
        print(f"Result: {result}")
    else:
        print("Test failed. Please ensure the ensemble is trained first.")
    
    print("\n" + "="*40)
    print("To train the ensemble, run: python ensemble_predict.py")
    print("To use in your main code, import and call get_ensemble_prediction()")

def test_ensemble_connection():
    """Test if ensemble can be loaded and basic functionality works"""
    try:
        print("Testing ensemble connection...")
        fit_models, meta, metadata = load_ensemble_for_prediction()
        print(f"✓ Ensemble loaded successfully!")
        print(f"  Base models: {metadata['base_models']}")
        print(f"  Features: {len(metadata['features'])}")
        return True
    except Exception as e:
        print(f"✗ Ensemble connection failed: {e}")
        return False
