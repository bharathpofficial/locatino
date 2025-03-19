from flask import Flask, request, jsonify, send_from_directory
import json
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

# Define the base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/location', methods=['POST'])
def location():
    try:
        # Parse the JSON data from the request
        location_data = request.get_json()
        location_data['ip_address'] = request.remote_addr  # Add the client's IP address
        logging.debug(f"Request data: {location_data}")
        print(f"Received location: {location_data}")

        # Save the location data to a file
        received_location_path = os.path.join(DATA_DIR, 'received_location.json')
        with open(received_location_path, 'a') as f:  # Append to the file for permanent storage
            f.write(json.dumps(location_data) + '\n')

        # Respond to the client
        return jsonify({"message": "Location, device, and IP details received successfully!"}), 200
    except Exception as e:
        print(f"Error handling location data: {e}")
        return jsonify({"error": "Failed to process location data"}), 500

@app.route('/config.json')
def config():
    return send_from_directory(DATA_DIR, 'config.json')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # Use the PORT environment variable provided by Heroku
    app.run(host='0.0.0.0', port=port)