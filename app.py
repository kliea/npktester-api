import os
import requests
from flask import Flask, request, jsonify # type: ignore
import joblib # type: ignore
from flask_cors import CORS # type: ignore
from dotenv import load_dotenv # type: ignore
from time import time

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
FIREBASE_SECRET = os.getenv("FIREBASE_SECRET")
USER_ID = "e6piaHKYkFhkTMsXmVbgc30wQEv1"

if not DATABASE_URL or not FIREBASE_SECRET:
    raise ValueError("DATABASE_URL or FIREBASE_SECRET not set in .env")

app = Flask(__name__)
CORS(app)

# Load the model
model = joblib.load('crop_recommendation_model.pkl')

@app.route('/')
def index():
    return "Crop Recommendation API is running."

@app.route('/sensordata', methods=['GET'])
def get_all_sensor_data():
    try:
        url = f"{DATABASE_URL}/UsersData/{USER_ID}/readings.json"
        params = {
            "auth": FIREBASE_SECRET,
            "orderBy": '"$key"',
            "limitToLast": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            return jsonify({"error": "No sensor data found."}), 404
        
        # Extract the latest entry
        latest_timestamp = list(data.keys())[0]
        latest_data = data[latest_timestamp]
        
        return jsonify(latest_data)

    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = data.get('features')

    if not features or not isinstance(features, list) or len(features) != 3:
        return jsonify({'error': 'Invalid input. Must be a list of 3 NPK values.'}), 400

    prediction = model.predict([features])[0]
    response = {'prediction': prediction}

    def calculate_fertilizer(deficit, fertilizer_type):
        if deficit <= 10:
            return 0
        if fertilizer_type == 'Urea':
            return round(min(deficit / 2.5, 78), 1)
        elif fertilizer_type == 'TSP':
            return min((deficit // 10 + 1) * 18, 180)
        elif fertilizer_type == 'MOP':
            return min((deficit // 10 + 1) * 6, 60)
        return 0

    def get_recommended_levels(crop):
        recommendations = {
            'maize': {'N': 197, 'P': 70, 'K': 180},
            'rice': {'N': 175, 'P': 87, 'K': 178},
            'kidneybeans': {'N': 138, 'P': 222, 'K': 166},
            'mungbean': {'N': 66, 'P': 83, 'K': 100},
            'banana': {'N': 660, 'P': 303, 'K': 1513},
            'mango': {'N': 51, 'P': 25, 'K': 76},
            'orange': {'N': 244, 'P': 73, 'K': 220},
            'papaya': {'N': 27, 'P': 97, 'K': 27},
            'coconut': {'N': 188, 'P': 125, 'K': 250},
            'coffee': {'N': 27, 'P': 97, 'K': 27}
        }
        return recommendations.get(crop)

    recommended = get_recommended_levels(prediction)

    if recommended:
        current = {'N': int(features[0]), 'P': int(features[1]), 'K': int(features[2])}
        deficit = {k: max(recommended[k] - current[k], 0) for k in recommended}

        fertilizers = {
            'Urea': calculate_fertilizer(deficit['N'], 'Urea'),
            'TSP': calculate_fertilizer(deficit['P'], 'TSP'),
            'MOP': calculate_fertilizer(deficit['K'], 'MOP')
        }
        response['needed_nutrients'] = fertilizers

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
