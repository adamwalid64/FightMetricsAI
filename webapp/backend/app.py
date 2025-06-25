from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'xgb_ufc_model.pkl')
model = joblib.load(MODEL_PATH)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)

    fighter_one = data.get('fighterOne')
    fighter_two = data.get('fighterTwo')
    features = data.get('features')

    print('Fighter One:', fighter_one)
    print('Fighter Two:', fighter_two)
    print('Features:', features)

    if features:
        features = np.array(features).reshape(1, -1)
        pred = model.predict(features)[0]
        return jsonify({'prediction': pred})

    return jsonify({'message': 'Names received'})

if __name__ == '__main__':
    app.run(debug=True)
