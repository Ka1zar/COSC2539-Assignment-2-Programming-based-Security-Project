from flask import Flask, request, render_template_string
import sqlite3
from time import time
import logging
import html

app = Flask(__name__)

# Setting up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Home Route
@app.route('/')
def home():
    return "Welcome to the Security Demo!"

# Links
@app.route('/links')
def display_links():
    return '''
        <h1>Test Links for Security Attacks</h1>
        <ul>
            <li><a href="/login">Test SQL Injection (Login)</a></li>
            <li><a href="/comments">Test XSS (Comments)</a></li>
            <li><a href="/secure-login">Test Brute Force (Login)</a></li>
            <li><a href="/api/data">Test API Exploitation</a></li>
        </ul>
    '''

# SQL Injection Vulnerability
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        result = c.execute(query).fetchone()
        conn.close()
        if result:
            logging.info(f"Login successful for username: {username}")
            return "Login successful!"
        else:
            logging.warning(f"Invalid login attempt for username: {username}")
            return "Invalid credentials!"
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# XSS Vulnerability

comments_db = []


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        comment = request.form['comment']

        # Append the comment to the database
        comments_db.append(comment)

        # Log the sanitized comment to app.log
        logging.info(f"New comment submitted: {comment}")

    # Render the page with the comments
    return render_template_string('''
        <h2>Submit a comment:</h2>
        <form method="post">
            Comment: <input type="text" name="comment"><br>
            <input type="submit" value="Submit">
        </form>

        <h3>Comments:</h3>
        <ul>
            {% for comment in comments %}
                <li>{{ comment | safe }}</li>  <!-- Use the 'safe' filter here -->
            {% endfor %}
        </ul>
    ''', comments=comments_db)

# Brute Force Simulation

users_db = {
    'admin': 'password123',  # Example valid credentials
}

# Dictionary to track login attempts for each username (with timestamps)
login_attempts = {}

@app.route('/secure-login', methods=['GET', 'POST'])
def secure_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        now = time()

        # Check if the user has attempted too many times in the last 5 seconds
        if username in login_attempts:
            last_attempt_time = login_attempts[username]['last_attempt_time']
            attempt_count = login_attempts[username]['attempt_count']

            # Block login if there are too many attempts in a short time
            if attempt_count >= 5 and now - last_attempt_time < 5:
                return "Too many attempts. Please try again later."

        # Update login attempts for this username
        login_attempts[username] = {
            'last_attempt_time': now,  # Timestamp of this attempt
            'attempt_count': login_attempts.get(username, {}).get('attempt_count', 0) + 1
        }

        # Check credentials against the mock database
        if username in users_db and users_db[username] == password:
            logging.info(f"Login attempt for username: {username}.")
            return "Login successful!"  # Successful login
        else:
            return "Invalid credentials!"  # Invalid login

    # If GET request, return login form
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# API Exploitation Simulation
@app.route('/api/data', methods=['GET'])
def api_data():
    token = request.headers.get('Authorization')
    if token != "Bearer securetoken":
        return {"error": "Unauthorized"}, 401
    return {"data": "Sensitive data exposed!"}

# Log Requests
@app.after_request
def log_request(response):
    logging.info(f"{request.method} {request.path} - {response.status_code}")
    return response

# Run the app
if __name__ == '__main__':
    print("Flask app running on http://127.0.0.1:5000/links")
    app.run(debug=True)
