# =========================
# Check Ensemble Status
# =========================
# This script checks if the ensemble is properly set up and working

import os
import sys

def check_ensemble_status():
    """Check the current status of the ensemble system"""
    print("UFC Ensemble Status Check")
    print("=" * 40)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    # Check if ensemble artifacts exist
    ensemble_dir = os.path.join(current_dir, "ensemble_artifacts")
    print(f"\nEnsemble artifacts directory: {ensemble_dir}")
    
    if os.path.exists(ensemble_dir):
        print("✓ Ensemble artifacts directory exists")
        
        # List contents
        try:
            files = os.listdir(ensemble_dir)
            print(f"  Contents ({len(files)} files):")
            for file in files:
                print(f"    - {file}")
        except Exception as e:
            print(f"  Error listing contents: {e}")
    else:
        print("⚠ Ensemble artifacts directory NOT found")
        print("  The ensemble needs to be trained")
    
    # Check if ensemble_integration.py exists
    integration_file = os.path.join(current_dir, "ensemble_integration.py")
    print(f"\nEnsemble integration file: {integration_file}")
    
    if os.path.exists(integration_file):
        print("✓ Ensemble integration file exists")
    else:
        print("⚠ Ensemble integration file NOT found")
    
    # Check if ensemble_predict.py exists
    predict_file = os.path.join(current_dir, "ensemble_predict.py")
    print(f"\nEnsemble training file: {predict_file}")
    
    if os.path.exists(predict_file):
        print("✓ Ensemble training file exists")
    else:
        print("⚠ Ensemble training file NOT found")
    
    # Try to import ensemble modules
    print(f"\nTesting imports...")
    
    try:
        import ensemble_integration
        print("✓ Successfully imported ensemble_integration")
    except ImportError as e:
        print(f"✗ Failed to import ensemble_integration: {e}")
    
    try:
        import ensemble_predict
        print("✓ Successfully imported ensemble_predict")
    except ImportError as e:
        print(f"✗ Failed to import ensemble_predict: {e}")
    
    # Summary and recommendations
    print(f"\n{'='*40}")
    print("SUMMARY & RECOMMENDATIONS")
    print(f"{'='*40}")
    
    if os.path.exists(ensemble_dir) and os.path.exists(integration_file):
        print("✓ Ensemble system is ready to use!")
        print("  You can now run custom_inputs.py to see ensemble predictions")
    elif os.path.exists(integration_file) and os.path.exists(predict_file):
        print("⚠ Ensemble system is set up but not trained")
        print("  To train the ensemble:")
        print("  1. Make sure you're in the Prediction directory")
        print("  2. Run: python ensemble_predict.py")
        print("  3. Wait for training to complete")
        print("  4. Test with: python custom_inputs.py")
    else:
        print("✗ Ensemble system is not properly set up")
        print("  Missing required files")
        print("  Check that all ensemble files are in the Prediction directory")

if __name__ == "__main__":
    check_ensemble_status()
