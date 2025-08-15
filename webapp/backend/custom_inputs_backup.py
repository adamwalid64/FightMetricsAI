import joblib
import os
import pandas as pd

# Load the models
MODEL_PATH = os.path.join(os.path.dirname(__file__), "xgb_ufc_model.pkl")
xgb_model = joblib.load(MODEL_PATH)

# Load additional models if they exist
try:
    catboost_model = joblib.load(os.path.join(os.path.dirname(__file__), "CatBoost_ufc_model.pkl"))
    lgreg_model = joblib.load(os.path.join(os.path.dirname(__file__), "LGReg_ufc_model.pkl"))
    scaler = joblib.load(os.path.join(os.path.dirname(__file__), "LGReg_scaler.pkl"))
    has_additional_models = True
except FileNotFoundError:
    has_additional_models = False

# Read in up-to-date dataset that ships with the backend
DATA_PATH = os.path.join(os.path.dirname(__file__), "scraped-ufc-data.csv")
df = pd.read_csv(DATA_PATH, sep=',')

# helper function to clean data to match ML dataset
def height_str_to_cm(height_str):
    try:
        feet, inches = height_str.replace('"', '').split("'")
        feet = int(feet.strip())
        inches = int(inches.strip())
        return int(feet * 30.48 + inches * 2.54)
    except:
        return None  # or 0, or raise an error

# enter fighter ids ex: calcdiff(64, 22)
def getCustomPredict(fighter1, fighter2):
    columns = ['SLpM', 'SApM', 'Str_Acc', 'TD_Acc', 'Str_Def', 'TD_Def', 'Sub_Avg',
               'TD_Avg', 'age', 'height', 'reach', 'wins', 'losses']

    f1 = df.loc[df['id'] == fighter1, columns].iloc[0]
    f2 = df.loc[df['id'] == fighter2, columns].iloc[0]

    # Get fighter names for display
    fighter1_name = df.loc[df['id'] == fighter1, 'name'].iloc[0]
    fighter2_name = df.loc[df['id'] == fighter2, 'name'].iloc[0]

    f1_height = height_str_to_cm(f1['height']) or 0
    f2_height = height_str_to_cm(f2['height']) or 0

    def make_input(winner, loser, winner_height, loser_height):
        return pd.DataFrame([{
            'SLpM_total_diff': winner['SLpM'] - loser['SLpM'],
            'SApM_total_diff': winner['SApM'] - loser['SApM'],
            'sig_str_acc_total_diff': winner['Str_Acc'] - loser['Str_Acc'],
            'td_acc_total_diff': winner['TD_Acc'] - loser['TD_Acc'],
            'str_def_total_diff': winner['Str_Def'] - loser['Str_Def'],
            'td_def_total_diff': winner['TD_Def'] - loser['TD_Def'],
            'sub_avg_diff': winner['Sub_Avg'] - loser['Sub_Avg'],
            'td_avg_diff': winner['TD_Avg'] - loser['TD_Avg'],
            'age_diff': winner['age'] - loser['age'],
            'height_diff': winner_height - loser_height,
            # 'weight_diff': winner['weight'] - loser['weight'],
            'reach_diff': winner['reach'] - loser['reach'],
            'wins_total_diff': winner['wins'] - loser['wins'],
            'losses_total_diff': winner['losses'] - loser['losses']
        }])

    # Try both orders
    X1 = make_input(f1, f2, f1_height, f2_height)  # Fighter1 vs Fighter2
    X2 = make_input(f2, f1, f2_height, f1_height)  # Fighter2 vs Fighter1

    # Predict both directions with XGBoost
    p1_xgb = xgb_model.predict_proba(X1)[0][1]  # prob f1 wins
    p2_xgb = xgb_model.predict_proba(X2)[0][1]  # prob f2 wins

    # Initialize variables for additional models
    p1_cat = p2_cat = p1_lgreg = p2_lgreg = 0.5

    # Predict both directions with CatBoost and Logistic Regression if available
    if has_additional_models:
        p1_cat = catboost_model.predict_proba(X1)[0][1]  # prob f1 wins
        p2_cat = catboost_model.predict_proba(X2)[0][1]  # prob f2 wins

        X1_scaled = scaler.transform(X1)
        X2_scaled = scaler.transform(X2)
        p1_lgreg = lgreg_model.predict_proba(X1_scaled)[0][1] # prob f1 wins
        p2_lgreg = lgreg_model.predict_proba(X2_scaled)[0][1] # prob f2 wins

    # Voting system: Each model gets one vote
    # Determine each model's vote
    xgb_vote = "fighter1" if p1_xgb > p2_xgb else "fighter2"
    cat_vote = "fighter1" if p1_cat > p2_cat else "fighter2"
    lgreg_vote = "fighter1" if p1_lgreg > p2_lgreg else "fighter2"
    
    # Count votes
    votes = [xgb_vote, cat_vote, lgreg_vote]
    fighter1_votes = votes.count("fighter1")
    fighter2_votes = votes.count("fighter2")
    
    # Determine winner by majority vote
    if fighter1_votes > fighter2_votes:
        winner = "fighter1"
        winner_name = fighter1_name
        winner_id = fighter1
        confidence = fighter1_votes / 3.0  # Confidence based on vote majority
    elif fighter2_votes > fighter1_votes:
        winner = "fighter2"
        winner_name = fighter2_name
        winner_id = fighter2
        confidence = fighter2_votes / 3.0  # Confidence based on vote majority
    else:
        # Tie - use average probabilities as tiebreaker
        avg_p1 = (p1_xgb + p1_cat + p1_lgreg) / 3
        avg_p2 = (p2_xgb + p2_cat + p2_lgreg) / 3
        
        if avg_p1 > avg_p2:
            winner = "fighter1"
            winner_name = fighter1_name
            winner_id = fighter1
            confidence = 0.5  # Lower confidence for tiebreaker
        else:
            winner = "fighter2"
            winner_name = fighter2_name
            winner_id = fighter2
            confidence = 0.5  # Lower confidence for tiebreaker

    return winner_id, confidence 