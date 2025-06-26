from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import pandas as pd

# Import custom prediction function
import custom_inputs
from custom_inputs import getCustomPredict

# Read in csv file
DATA_PATH = os.path.join(os.path.dirname(__file__), 'scraped-ufc-data.csv')
df = pd.read_csv(DATA_PATH, sep=';')

def get_fighter_id(name, df):
    # Return fighter ID from dataframe using case-insensitive match
    match = df[df['name'].str.lower() == name.lower()]
    if not match.empty:
        return int(match.iloc[0]['id'])
    return None

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'xgb_ufc_model.pkl')
model = joblib.load(MODEL_PATH)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)

    fighter_one = data.get('fighterOne')
    fighter_two = data.get('fighterTwo')

    print('Fighter One:', fighter_one)
    print('Fighter Two:', fighter_two)


    fighter_one_id = get_fighter_id(fighter_one, df)
    fighter_two_id = get_fighter_id(fighter_two, df)

    print('Fighter One ID:', fighter_one_id)
    print('Fighter Two ID:', fighter_two_id)

    winner_id, confidence = getCustomPredict(fighter_one_id, fighter_two_id)

    if winner_id is None:
        return jsonify({'error': 'Unable to determine winner'}), 400

    winner_row = df[df['id'] == winner_id]
    winner_name = winner_row['name'].iloc[0] if not winner_row.empty else str(winner_id)

    return jsonify({'prediction': winner_name, 'confidence': confidence})

if __name__ == '__main__':
    app.run(debug=True)
