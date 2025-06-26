import joblib
import pandas as pd

# Load the model
model = joblib.load("xgb_ufc_model.pkl")

# Read in up-to-date dataset
df = pd.read_csv("../Data/scraped-ufc-data.csv", sep=';')
print(df.columns)

# helper function to clean data to match ML dataset
def height_str_to_cm(height_str):
    try:
        feet, inches = height_str.replace('"', '').split("'")
        feet = int(feet.strip())
        inches = int(inches.strip())
        return int(feet * 30.48 + inches * 2.54)
    except:
        return None  # or 0, or raise an error

# Example usage
print(height_str_to_cm("6' 3\""))   # ➜ 190
print(height_str_to_cm("5' 11\""))  # ➜ 180

# fighter1name = ''
# fighter2name = ''

# enter fighter ids ex: calcdiff(64, 22)
def getCustomPredict(fighter1, fighter2):
    columns = ['SLpM', 'SApM', 'Str_Acc', 'TD_Acc', 'Str_Def', 'TD_Def', 'Sub_Avg',
               'TD_Avg', 'age', 'height', 'weight', 'reach', 'wins', 'losses']

    f1 = df.loc[df['id'] == fighter1, columns].iloc[0]
    f2 = df.loc[df['id'] == fighter2, columns].iloc[0]

    f1_height = height_str_to_cm(f1['height'])
    f2_height = height_str_to_cm(f2['height'])


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
            'weight_diff': winner['weight'] - loser['weight'],
            'reach_diff': winner['reach'] - loser['reach'],
            'wins_total_diff': winner['wins'] - loser['wins'],
            'losses_total_diff': winner['losses'] - loser['losses']
        }])

    # Try both orders
    X1 = make_input(f1, f2, f1_height, f2_height)
    X2 = make_input(f2, f1, f2_height, f1_height)

    # Predict both directions
    p1 = model.predict_proba(X1)[0][1]  # prob f1 wins
    p2 = model.predict_proba(X2)[0][1]  # prob f2 wins (if f2 was first)

    # Choose the higher confidence direction
    if p1 >= p2:
        print(f"Predicted Winner: Fighter {fighter1} (ID {fighter1}) — Confidence: {p1:.2f}")
    else:
        print(f"Predicted Winner: Fighter {fighter2} (ID {fighter2}) — Confidence: {p2:.2f}")





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

# REAL TIME TEST 9: LIVE --- Moicano vs. Dariush
# Moicano id: 1943
# Dariush id: 658
# getCustomPredict(1943, 658)
# Prediction: Dariush
# Win: 10/10 profit

# REAL TIME TEST 10: LIVE --- Topuria vs. Oliveira
# Oliveira id: 2141
# Topuria id: 2989
# getCustomPredict(2141, 2989)
# Predicted Winner: Fighter 2141 (ID 2141) — Confidence: 0.76
# Win: 10/34.5 profit

# REAL TIME TEST 11: LIVE --- Talbott vs. Lima
# Talbott id: 2921
# Lima id: 1649
# getCustomPredict(2921, 1649)
# Prediction: Lima
# Win: 10/5.10 profit

# REAL TIME TEST 12: LIVE --- Hermansson vs. Rodrigues
# Hermansson id: 1212
# Rodrigues id: 2483
# getCustomPredict(2483, 1212)
# Prediction: Hermansson
# Win: 10/16.5

# REAL TIME TEST 12: SUCCESS --- Strickland vs. DDP 2
# Strickland id: 2891
# DDP id: 772
# getCustomPredict(772, 2891)


# REAL TIME TEST 12: Miss --- Cejudo vs. Song 2
# Cejudo id: 494
# Song id: 2811
# getCustomPredict(494, 2811)
# Prediction: DDP
