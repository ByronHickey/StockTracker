import json
import time
from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

# Replace these with your Questrade API Centre details
CLIENT_ID = 'm8cKlDia1uNhm8tVzO0tqPhRgA_1321F0'
REDIRECT_URI = 'http://localhost:5000/callback'  

AUTH_URL = 'https://questrade.com'
TOKEN_URL = 'https://questrade.com'
TOKEN_FILE = 'questrade_tokens.json'

def save_tokens(token_payload):
    """Calculates the exact expiry time and saves tokens to the shared JSON file."""
    # access_token is valid for 1800 seconds (30 minutes)
    token_payload['expires_at'] = time.time() + token_payload.get('expires_in', 1800)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_payload, f, indent=4)
    print(f"💾 Initial credentials successfully saved to {TOKEN_FILE}")

@app.route('/login')
def login():
    """Step 1: Send user to Questrade authentication screen."""
    authorization_uri = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(authorization_uri)

@app.route('/callback')
def callback():
    """Step 2 & 3: Catch the callback code and boot up the token storage file."""
    auth_code = request.args.get('code')
    
    if not auth_code:
        return "Authorization failed or access was denied.", 400

    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID
    }
    
    response = requests.post(TOKEN_URL, data=token_data)
    
    if response.status_code != 200:
        return f"Error exchanging token: {response.text}", response.status_code
        
    token_payload = response.json()
    
    # HOOK: This binds the Flask app directly to your companion script!
    save_tokens(token_payload)
    
    return jsonify({
        "status": "Success! You can now run your companion script safely.",
        "api_server": token_payload.get("api_server")
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
