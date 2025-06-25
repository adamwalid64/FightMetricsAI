from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import pandas as pd

# Read in csv file
df = pd.read_csv('scraped-ufc-data.csv')

def get_fighter_id(name, df):
    match = df[df['name'].str.lower() == name.lower()]
    if not match.empty:
        return match.iloc[0]['fighter_id']
    else:
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

    return jsonify({'message': 'Names received'})

if __name__ == '__main__':
    app.run(debug=True)
