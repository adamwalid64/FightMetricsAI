# =========================
# Test Enhanced UFC Predictions
# =========================
# This script demonstrates the enhanced custom_inputs.py functionality
# that shows both individual model predictions and ensemble predictions

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_enhanced_predictions():
    """Test the enhanced prediction system"""
    print("Testing Enhanced UFC Prediction System")
    print("=" * 50)
    
    try:
        # Import the enhanced custom_inputs module
        import custom_inputs
        
        print("✓ Successfully imported enhanced custom_inputs module")
        
        # Test with example fighter IDs
        fighter1_id = 1527  # Example fighter ID
        fighter2_id = 3035  # Example fighter ID
        
        print(f"\nTesting predictions for fighters {fighter1_id} vs {fighter2_id}")
        print("This will show:")
        print("1. Individual model predictions (XGBoost, CatBoost, Logistic Regression, MLP)")
        print("2. Voting system results")
        print("3. Ensemble prediction (if available)")
        print("4. Comprehensive comparison")
        
        print(f"\n{'='*50}")
        print("RUNNING ENHANCED PREDICTIONS...")
        print(f"{'='*50}")
        
        # Run the enhanced prediction function
        result = custom_inputs.getCustomPredict(fighter1_id, fighter2_id)
        
        if result:
            winner_id, confidence = result
            print(f"\n✓ Test completed successfully!")
            print(f"Winner ID: {winner_id}")
            print(f"Confidence: {confidence:.3f}")
        else:
            print(f"\n⚠ Test failed - no result returned")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure custom_inputs.py is in the current directory")
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_ensemble_availability():
    """Test if ensemble is available"""
    print(f"\n{'='*50}")
    print("TESTING ENSEMBLE AVAILABILITY")
    print(f"{'='*50}")
    
    try:
        from ensemble_integration import get_ensemble_prediction
        print("✓ Ensemble integration module is available")
        
        # Try to load ensemble
        try:
            fit_models, meta, metadata = get_ensemble_prediction.__globals__['load_ensemble_for_prediction']()
            print("✓ Ensemble is trained and available")
            print(f"  Base models: {metadata['base_models']}")
            print(f"  Features: {len(metadata['features'])}")
        except Exception as e:
            print("⚠ Ensemble is not trained yet")
            print(f"  Error: {e}")
            print("  Run 'python ensemble_predict.py' to train the ensemble")
            
    except ImportError:
        print("✗ Ensemble integration module not available")
        print("  Make sure ensemble_integration.py exists")
    except Exception as e:
        print(f"✗ Error testing ensemble: {e}")

if __name__ == "__main__":
    print("Enhanced UFC Prediction System Test")
    print("=" * 50)
    
    # Test ensemble availability first
    test_ensemble_availability()
    
    # Test enhanced predictions
    test_enhanced_predictions()
    
    print(f"\n{'='*50}")
    print("TEST COMPLETED")
    print(f"{'='*50}")
    print("\nNext steps:")
    print("1. If ensemble is not available, run: python ensemble_predict.py")
    print("2. Test individual predictions: python custom_inputs.py")
    print("3. Test ensemble integration: python ensemble_integration.py")
