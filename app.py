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

    prediction = model.predict([features])[0]  # prediction[0] directly
    response = {'prediction': prediction}

    if prediction == 'maize':
        nit = 197 - int(features[0])
        phos= 70 - int(features[1])
        pot = 180 - int(features[2])
        
        if nit > 10:
            nit = 7.8
        elif nit > 20:
            nit = 15.6
        elif nit > 30:
            nit = 23.4
        elif nit > 40:
            nit = 31.2
        elif nit > 50:
            nit = 39
        elif nit > 60:
            nit = 46.8
        elif nit > 70:
            nit = 54.6
        elif nit > 80:
            nit = 62.4
        elif nit > 90:
            nit = 70.2
        elif nit > 100:
            nit = 78
            
        if phos > 10:
            phos = 18
        elif phos > 20:
            phos = 36
        elif phos > 30:
            phos = 54
        elif phos > 40:
            phos = 72
        elif phos > 50: 
            phos = 90
        elif phos > 60:
            phos = 108
        elif phos > 70:
            phos = 126
        elif phos > 80:
            phos = 144
        elif phos > 90:
            phos = 162
        elif phos > 100:
            phos = 180
            
        if pot > 10:
            pot = 6
        elif pot > 20:
            pot = 12
        elif pot > 30:
            pot = 18
        elif pot > 40:
            pot = 24
        elif phos > 50: 
            phos = 30
        elif phos > 60:
            phos = 36
        elif phos > 70:
            phos = 42
        elif phos > 80:
            phos = 48
        elif phos > 90:
            phos = 54
        elif phos > 100:
            phos = 60
        
        
        response['needed_nutrients'] = {
            'Urea': nit,
            'TSP': phos,
            'MOP': pot
        }
    elif prediction == 'rice':
        nit = 175 - int(features[0])
        phos = 87 - int(features[1])
        pot =  178 - int(features[2])
        
        if nit > 10:
            nit = 7.8
        elif nit > 20:
            nit = 15.6
        elif nit > 30:
            nit = 23.4
        elif nit > 40:
            nit = 31.2
        elif nit > 50:
            nit = 39
        elif nit > 60:
            nit = 46.8
        elif nit > 70:
            nit = 54.6
        elif nit > 80:
            nit = 62.4
        elif nit > 90:
            nit = 70.2
        elif nit > 100:
            nit = 78
            
        if phos > 10:
            phos = 18
        elif phos > 20:
            phos = 36
        elif phos > 30:
            phos = 54
        elif phos > 40:
            phos = 72
        elif phos > 50: 
            phos = 90
        elif phos > 60:
            phos = 108
        elif phos > 70:
            phos = 126
        elif phos > 80:
            phos = 144
        elif phos > 90:
            phos = 162
        elif phos > 100:
            phos = 180
            
        if pot > 10:
            pot = 6
        elif pot > 20:
            pot = 12
        elif pot > 30:
            pot = 18
        elif pot > 40:
            pot = 24
        elif phos > 50: 
            phos = 30
        elif phos > 60:
            phos = 36
        elif phos > 70:
            phos = 42
        elif phos > 80:
            phos = 48
        elif phos > 90:
            phos = 54
        elif phos > 100:
            phos = 60
        response['needed_nutrients'] = {
            'Urea': nit,
            'TSP': phos,
            'MOP': pot
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
