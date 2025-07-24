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

    f1 = df.loc[df['id'] == fighter1, columns].iloc[0]
    f2 = df.loc[df['id'] == fighter2, columns].iloc[0]

    # Get fighter names for display
    fighter1_name = df.loc[df['id'] == fighter1, 'name'].iloc[0]
    fighter2_name = df.loc[df['id'] == fighter2, 'name'].iloc[0]

    f1_height = height_str_to_cm(f1['height'])
    f2_height = height_str_to_cm(f2['height'])

    # # Debug: Print fighter stats
    # print(f"\n=== Fighter Comparison ===")
    # print(f"Fighter {fighter1} ({fighter1_name}) vs Fighter {fighter2} ({fighter2_name})")
    # print(f"{fighter1_name} Stats: SLpM={f1['SLpM']:.2f}, SApM={f1['SApM']:.2f}, Str_Acc={f1['Str_Acc']:.1f}%, Str_Def={f1['Str_Def']:.1f}%")
    # print(f"{fighter2_name} Stats: SLpM={f2['SLpM']:.2f}, SApM={f2['SApM']:.2f}, Str_Acc={f2['Str_Acc']:.1f}%, Str_Def={f2['Str_Def']:.1f}%")
    # print(f"{fighter1_name}: Age={f1['age']}, Height={f1['height']}, Reach={f1['reach']}, Wins={f1['wins']}, Losses={f1['losses']}")
    # print(f"{fighter2_name}: Age={f2['age']}, Height={f2['height']}, Reach={f2['reach']}, Wins={f2['wins']}, Losses={f2['losses']}")

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
    return winner_info




# Testing the model on live data

# REAL TIME TEST 1: SUCCESS --- Kamaru Usman vs Joaquin Buckley
# Usman id: 402
# Buckley id: 3043
# getCustomPredict(3043, 402)

# REAL TIME TEST 2: SUCCESS --- Belal Muhammad vs JDM
# JDM id: 698
# Belal Muhammad id: 1997
# getCustomPredict(698, 1997)

# REAL TIME TEST 3: SUCCESS --- Pimblett vs Chandler
# Pimblett id: 2306
# Chandler id: 504
# getCustomPredict(504, 2306)

# REAL TIME TEST 4: SUCCESS --- Sandhagen vs. Figueiredo
# Sandhagen id: 2599
# Figueiredo id: 894
# getCustomPredict(894, 2599)

# REAL TIME TEST 5: SUCCESS --- Moreno vs. Erceg
# Moreno id: 1978
# Erceg id: 847
# getCustomPredict(1978, 847)

# REAL TIME TEST 6: SUCCESS --- Holland vs. Luque
# Holland id: 1251
# Luque id: 1698
# getCustomPredict(1251, 1698)

# REAL TIME TEST 7: SUCCESS --- Edwards vs. Brady
# Brady id: 351
# Edwards id: 810
# getCustomPredict(810, 351)

# REAL TIME TEST 8: SUCCESS --- Adesanya vs. Imavov
# Adesanya id: 18
# Imavov id: 1313
# getCustomPredict(18, 1313)

# # REAL TIME TEST 9: Hit --- Moicano vs. Dariush
# # Moicano id: 1943
# # Dariush id: 658
# getCustomPredict(1943, 658)
# # Prediction: Dariush
# # Win: 10/10 profit

# REAL TIME TEST 10: Hit --- Topuria vs. Oliveira
# Oliveira id: 2141
# Topuria id: 2989
# getCustomPredict(2141, 2989)
# Predicted Winner: Fighter 2141 (ID 2141) — Confidence: 0.76
# Win: 10/34.5 profit

# REAL TIME TEST 11: Miss --- Talbott vs. Lima
# Talbott id: 2921
# Lima id: 1649
# getCustomPredict(2921, 1649)
# Prediction: Lima
# Win: 10/5.10 profit

# REAL TIME TEST 12: HIT --- Hermansson vs. Rodrigues
# Hermansson id: 1212
# Rodrigues id: 2483
# getCustomPredict(2483, 1212)
# Prediction: Hermansson
# Win: 10/16.5

# REAL TIME TEST 13: SUCCESS --- Strickland vs. DDP 2
# Strickland id: 2891
# DDP id: 772
# getCustomPredict(772, 2891)


# REAL TIME TEST 14: Miss --- Cejudo vs. Song 2
# Cejudo id: 494
# Song id: 2811
# getCustomPredict(494, 2811)
# Prediction: DDP

# REAL TIME TEST 15: SUCCESS --- Pantoja vs Kai kara-France
# Pantoja id: 2685
# Kai kara-France id: 1737
# getCustomPredict(1737, 2685)



## UFC Fight Night: Lewis vs. Teixeira

# REAL TIME TEST 16: LIVE --- # Lewis vs Teixeira
# Lewis id: 1992
# Teixeira id: 3589
# getCustomPredict(3589, 1992)

# REAL TIME TEST 17: LIVE --- # Thompson vs Bonfim
# Thompson id: 3615
# Bonfim id: 387
# getCustomPredict(3615, 387)

# REAL TIME TEST 18: LIVE --- # Kattar vs Garcia
# Kattar id: 1749
# Garcia id: 1197
# getCustomPredict(1197, 1749)

# REAL TIME TEST 19: LIVE --- # Landwehr vs Charriere
# Landwehr id: 1903
# Charriere id: 617
# getCustomPredict(617, 1903)

# REAL TIME TEST 20: LIVE --- # Petrino vs Lane
# Petrino id: 2785
# Lane id: 1904
# getCustomPredict(2785, 1904)

# REAL TIME TEST 21: LIVE --- # Matthews vs Njokuani
# Matthews id: 2218
# Njokuani id: 2566
# getCustomPredict(725, 1844)

# REAL TIME TEST 22: LIVE --- # Matthews vs Njokuani
# Matthews id: 228
# Njokuani id: 2566
# getCustomPredict(1196, 1748)

# getCustomPredict(3962, 1679)