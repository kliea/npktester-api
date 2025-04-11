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
        .select('id, nitrogen, phosphorus, potassium, created_at') \
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
        response['needed_nutrients'] = {
            'N': 197 - int(features[0]),
            'P': 70 - int(features[1]),
            'K': 180 - int(features[2])
        }
    elif prediction == 'rice':
        response['needed_nutrients'] = {
            'N': 175 - int(features[0]),
            'P': 87 - int(features[1]),
            'K': 178 - int(features[2])
        }

    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
