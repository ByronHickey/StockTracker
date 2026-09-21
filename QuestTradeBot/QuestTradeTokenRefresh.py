import os
import json
import time
import requests

TOKEN_FILE = "questrade_tokens.json"
TOKEN_URL = "https://login.questrade.com/oauth2/token"

def load_tokens():
    """Load stored credentials from the local JSON file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def save_tokens(token_payload):
    """Save the updated token payload and calculate its exact expiry timestamp."""
    # access_token is valid for 1800 seconds (30 minutes)
    token_payload['expires_at'] = time.time() + token_payload.get('expires_in', 1800)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_payload, f, indent=4)
    print("🔄 Tokens successfully updated and saved locally.")

def refresh_questrade_token():
    """Exchanges the current refresh token for a fresh token pair."""
    tokens = load_tokens()
    if not tokens or 'refresh_token' not in tokens:
        raise ValueError(f"No refresh token found. Please run your Flask app first to populate {TOKEN_FILE}.")

    print("Attempting to refresh access token...")
    
    # Payload format required by Questrade OAuth2
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token']
    }
    
    response = requests.post(TOKEN_URL, data=refresh_data)
    
    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        return new_tokens
    else:
        print(f"❌ Failed to refresh token: {response.text}")
        # Common issue: If the refresh token was already used or expired (3 days max lifetime),
        # you must go back to the app/Questrade UI to get a fresh one.
        return None

def get_valid_access_token():
    """Returns a valid access token, automatically refreshing it if it has expired."""
    tokens = load_tokens()
    if not tokens:
        return None
        
    # Check if the access token has expired (or expires in the next 10 seconds)
    if time.time() >= (tokens.get('expires_at', 0) - 10):
        print("⏰ Access token expired or expiring soon.")
        tokens = refresh_questrade_token()
        
    return tokens

# --- Example API Usage ---
if __name__ == "__main__":
    # Ensure your initial tokens from the Flask callback are saved into 'questrade_tokens.json'
    # in this format: {"access_token": "...", "refresh_token": "...", "api_server": "...", "expires_in": 1800}
    
    token_info = get_valid_access_token()
    
    if token_info:
        access_token = token_info['access_token']
        api_server = token_info['api_server']
        
        # Pull account details using the fresh token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Example API call to see active trading accounts
        accounts_url = f"{api_server}v1/accounts"
        account_response = requests.get(accounts_url, headers=headers)
        
        if account_response.status_code == 200:
            print("\nSuccessfully connected to Questrade API!")
            print(json.dumps(account_response.json(), indent=2))
        else:
            print(f"API Call Failed: {account_response.text}")
