from flask import Flask, request, jsonify, send_from_directory, Response
import os
import mysql.connector
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

# Connect to the JawsDB MySQL database
db_url = os.environ.get('JAWSDB_URL')
if db_url:
    # Parse the JAWSDB_URL
    db_url = db_url.replace("mysql://", "")  # Remove the "mysql://" prefix
    db_user, rest = db_url.split(":", 1)  # Split at the first ":"
    db_password, rest = rest.split("@", 1)  # Split at the "@"
    db_host_port, db_name = rest.split("/", 1)  # Split at the first "/"
    db_host = db_host_port.split(":")[0]  # Extract the host (ignore the port)

    # Establish the database connection
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
else:
    db_connection = None

# Authentication credentials
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')  # Default username: admin
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'password')  # Default password: password

def check_auth(username, password):
    """Check if the provided username and password are correct."""
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def authenticate():
    """Send a 401 response to request authentication."""
    return Response(
        'Unauthorized access. Please provide valid credentials.\n',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorator to enforce authentication on specific routes."""
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/location', methods=['POST'])
def location():
    try:
        # Parse the JSON data from the request
        location_data = request.get_json()
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO locations (latitude, longitude, user_agent, ip_address) VALUES (%s, %s, %s, %s)",
            (location_data['latitude'], location_data['longitude'], location_data['userAgent'], request.remote_addr)
        )
        db_connection.commit()
        return jsonify({"message": "Location saved successfully!"}), 200
    except Exception as e:
        print(f"Error handling location data: {e}")
        return jsonify({"error": "Failed to save location"}), 500

@app.route('/locations', methods=['GET'])
@requires_auth
def get_locations():
    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM locations")
        locations = cursor.fetchall()
        return jsonify(locations), 200
    except Exception as e:
        print(f"Error retrieving locations: {e}")
        return jsonify({"error": "Failed to retrieve locations"}), 500

if __name__ == '__main__':
    # Use the PORT environment variable provided by Heroku
    port = int(os.environ.get('PORT', 8000))  # Default to 8000 if PORT is not set
    app.run(host='0.0.0.0', port=port)