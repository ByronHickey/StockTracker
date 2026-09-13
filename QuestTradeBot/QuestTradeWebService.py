
from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

# Replace these with your Questrade API Centre details
CLIENT_ID = 'm8cKlDia1uNhm8tVzO0tqPhRgA_1321F0'
# Questrade expects exact match. E.g., 'http://localhost:5000/callback' 
REDIRECT_URI = 'http://localhost:5000/callback'  

AUTH_URL = 'https://login.questrade.com/oauth2/authorize'
TOKEN_URL = 'https://login.questrade.com/oauth2/token'

@app.route('/login')
def login():
    """Step 1: Redirect the user to Questrade's login page."""
    authorization_uri = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(authorization_uri)

@app.route('/callback')
def callback():
    """Step 2: Catch the code query parameter sent by Questrade."""
    auth_code = request.args.get('code')
    
    if not auth_code:
        return "Authorization failed or access was denied.", 400

    # Step 3: Exchange the authorization code for Questrade tokens
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID
    }
    
    # Questrade returns access_token, refresh_token, and api_server URL
    response = requests.post(TOKEN_URL, data=token_data)
    
    if response.status_code != 200:
        return f"Error exchanging token: {response.text}", response.status_code
        
    token_payload = response.json()
    return jsonify({
        "message": "Authentication successful!",
        "api_server": token_payload.get("api_server"),
        "access_token": token_payload.get("access_token"),
        "refresh_token": token_payload.get("refresh_token")
    })

if __name__ == '__main__':
    # Run locally on port 5000
    app.run(port=5000, debug=True)
