# app.py
import os
from flask import Flask, request, jsonify # type: ignore
import joblib # type: ignore
from flask_cors import CORS # type: ignore
from dotenv import load_dotenv # type: ignore
from supabase import create_client, Client # type: ignore


# Load environment variables from a .env file
load_dotenv()

# Fetch the Supabase URL, API key, and DATABASE_URL from environment variables
url = os.getenv("REACT_APP_SUPABASE_URL")
key = os.getenv("REACT_APP_SUPABASE_ANON_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
    
# Ensure the variables are set
if not url or not key:
    raise ValueError("Supabase URL or key is not set in environment variables.")
if not DATABASE_URL:
    raise ValueError("Database URL is not set in environment variables.")

# Create Supabase client (you can still use Supabase for other features)
supabase: Client = create_client(url, key)

# Export the Supabase client for use in other parts of your application
def get_supabase_client():
    return supabase


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

supabase = get_supabase_client()

# Load the model
model = joblib.load('crop_recommendation_model.pkl')

@app.route('/')
def index():
    return "Crop Recommendation API is running."

@app.route('/sensordata', methods=['GET'])
def get_sensor_data():
    # Fetch the sensor data from PostgreSQL
    response = supabase.table('sensor_data') \
        .select('id, nitrogen, phosphorus, potassium, soilMoisture, created_at') \
        .order('created_at', desc=True) \
        .limit(1) \
        .execute()
    return jsonify(response.data)

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

@app.route('/sensordata', methods=['POST'])
def send_to_supabase():
    try:
        data = request.get_json()

        # Check if all required fields are present in the request
        required_fields = ['nitrogen', 'phosphorus', 'potassium', 'conductivity', 'soilMoisture']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required data'}), 400

        # Prepare the data to send to Supabase
        payload = {
            'nitrogen': data['nitrogen'],
            'phosphorus': data['phosphorus'],
            'potassium': data['potassium'],
            'conductivity': data['conductivity'],
            'soilMoisture': data['soilMoisture']
        }

        # Send the data to Supabase
        response = supabase.table('sensor_data').insert([payload]).execute()

        # ✅ Use attributes, not .get()
        if response.data:
            return jsonify({'message': 'Data sent successfully!', 'data': response.data}), 201
        elif response.error:
            return jsonify({'error': 'Failed to send data', 'details': str(response.error)}), 500
        else:
            return jsonify({'error': 'Unknown error occurred'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)