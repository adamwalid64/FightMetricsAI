import joblib
import pandas as pd

# Load the models
xgb_model = joblib.load("xgb_ufc_model.pkl")

catboost_model = joblib.load("CatBoost_ufc_model.pkl")

lgreg_model = joblib.load("LGReg_ufc_model.pkl")
scaler = joblib.load("LGReg_scaler.pkl")

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

    # # Debug: Print fighter stats
    # print(f"\n=== Fighter Comparison ===")
    # print(f"Fighter {fighter1} ({fighter1_name}) vs Fighter {fighter2} ({fighter2_name})")
    # print(f"{fighter1_name} Stats: SLpM={f1['SLpM']:.2f}, SApM={f1['SApM']:.2f}, Str_Acc={f1['Str_Acc']:.1f}%, Str_Def={f1['Str_Def']:.1f}%")
    # print(f"{fighter2_name} Stats: SLpM={f2['SLpM']:.2f}, SApM={f2['SApM']:.2f}, Str_Acc={f2['Str_Acc']:.1f}%, Str_Def={f2['Str_Def']:.1f}%")
    # print(f"{fighter1_name}: Age={f1['age']}, Height={f1['height']}, Reach={f1['reach']}, Wins={f1['wins']}, Losses={f1['losses']}")
    # print(f"{fighter2_name}: Age={f2['age']}, Height={f2['height']}, Reach={f2['reach']}, Wins={f2['wins']}, Losses={f2['losses']}")

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

    # # Debug: Print the differences
    # print(f"\n=== Model Input Differences ===")
    # print(f"{fighter1_name} vs {fighter2_name} differences:")
    # for col in X1.columns:
    #     print(f"  {col}: {X1[col].iloc[0]:.2f}")
    
    # print(f"\n{fighter2_name} vs {fighter1_name} differences:")
    # for col in X2.columns:
    #     print(f"  {col}: {X2[col].iloc[0]:.2f}")

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

    print(f"\n=== XGBoost Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_xgb:.3f}")
    print(f"{fighter2_name} wins probability: {p2_xgb:.3f}")

    print(f"\n=== CatBoost Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_cat:.3f}")
    print(f"{fighter2_name} wins probability: {p2_cat:.3f}")

    print(f"\n=== Logistic Regression Model Predictions ===")
    print(f"{fighter1_name} wins probability: {p1_lgreg:.3f}")
    print(f"{fighter2_name} wins probability: {p2_lgreg:.3f}")

    # Voting system: Each model gets one vote
    print(f"\n=== Voting System (XGBoost + CatBoost + Logistic Regression) ===")
    
    # Determine each model's vote
    xgb_vote = "fighter1" if p1_xgb > p2_xgb else "fighter2"
    cat_vote = "fighter1" if p1_cat > p2_cat else "fighter2"
    lgreg_vote = "fighter1" if p1_lgreg > p2_lgreg else "fighter2"
    
    print(f"XGBoost vote: {xgb_vote}")
    print(f"CatBoost vote: {cat_vote}")
    print(f"Logistic Regression vote: {lgreg_vote}")
    
    # Count votes
    votes = [xgb_vote, cat_vote, lgreg_vote]
    fighter1_votes = votes.count("fighter1")
    fighter2_votes = votes.count("fighter2")
    
    print(f"Vote count - {fighter1_name}: {fighter1_votes}, {fighter2_name}: {fighter2_votes}")
    
    # Determine winner by majority vote
    if fighter1_votes > fighter2_votes:
        winner = "fighter1"
        winner_name = fighter1_name
        winner_id = fighter1
        confidence = fighter1_votes / 3.0  # Confidence based on vote majority
        print(f"✓ Majority vote winner: {fighter1_name} ({fighter1_votes}/3 votes)")
    elif fighter2_votes > fighter1_votes:
        winner = "fighter2"
        winner_name = fighter2_name
        winner_id = fighter2
        confidence = fighter2_votes / 3.0  # Confidence based on vote majority
        print(f"✓ Majority vote winner: {fighter2_name} ({fighter2_votes}/3 votes)")
    else:
        # Tie - use average probabilities as tiebreaker
        avg_p1 = (p1_xgb + p1_cat + p1_lgreg) / 3
        avg_p2 = (p2_xgb + p2_cat + p2_lgreg) / 3
        
        if avg_p1 > avg_p2:
            winner = "fighter1"
            winner_name = fighter1_name
            winner_id = fighter1
            confidence = 0.5  # Lower confidence for tiebreaker
            print(f"⚠ Tie detected - using average probabilities as tiebreaker")
            print(f"Winner: {fighter1_name} (avg prob: {avg_p1:.3f} vs {avg_p2:.3f})")
        else:
            winner = "fighter2"
            winner_name = fighter2_name
            winner_id = fighter2
            confidence = 0.5  # Lower confidence for tiebreaker
            print(f"⚠ Tie detected - using average probabilities as tiebreaker")
            print(f"Winner: {fighter2_name} (avg prob: {avg_p2:.3f} vs {avg_p1:.3f})")
    
    # Determine confidence level description
    if confidence == 1.0:
        confidence_desc = " (Unanimous vote)"
    elif confidence == 2/3:
        confidence_desc = " (Majority vote)"
    else:
        confidence_desc = " (Tiebreaker used)"
    
    winner_info = f"Predicted Winner: Fighter {winner_id} ({winner_name}) — Confidence: {confidence:.2f}{confidence_desc}"
    print(winner_info)
    return winner_id, confidence

# Add a test call to actually run the function when script is executed
if __name__ == "__main__":
    # Test with two fighter IDs - you can change these to any valid fighter IDs
    print("Running UFC prediction test...")
    result = getCustomPredict(1484, 907)  # Example fighter IDs
    print(f"Test completed. Result: {result}") 