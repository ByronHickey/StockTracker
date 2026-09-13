import requests
import json
# Assuming get_valid_access_token() is imported or present in your script

def get_market_quote(ticker):
    """Retrieves real-time market data (Bid, Ask, Last Price) for a given symbol."""
    token_info = get_valid_access_token()
    if not token_info:
        return None
        
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    api_server = token_info['api_server']
    
    # Step 1: Questrade requires matching the text ticker to a unique internal symbolId
    search_url = f"{api_server}v1/symbols?names={ticker}"
    search_res = requests.get(search_url, headers=headers)
    
    if search_res.status_code != 200 or not search_res.json().get('symbols'):
        print(f"❌ Could not find symbol ID for ticker: {ticker}")
        return None
        
    symbol_id = search_res.json()['symbols'][0]['symbolId']
    
    # Step 2: Fetch the actual market quote using that ID
    quote_url = f"{api_server}v1/markets/quotes/{symbol_id}"
    quote_res = requests.get(quote_url, headers=headers)
    
    if quote_res.status_code == 200:
        data = quote_res.json()['quotes'][0]
        return {
            "ticker": ticker,
            "symbolId": symbol_id,
            "bid": data.get("bidPrice"),
            "bid_size": data.get("bidSize"),
            "ask": data.get("askPrice"),
            "ask_size": data.get("askSize"),
            "last_trade": data.get("lastTradePrice")
        }
    return None

def place_order(account_id, ticker, quantity, order_type="Market", price=None, action="Buy"):
    """
    Executes a purchase or sale order.
    Supported order_types: 'Market', 'Limit'
    Supported actions: 'Buy', 'Sell'
    """
    token_info = get_valid_access_token()
    if not token_info:
        return None
        
    # Standard security measure: Always fetch current market data to extract the correct symbolId
    quote = get_market_quote(ticker)
    if not quote:
        return None

    headers = {
        "Authorization": f"Bearer {token_info['access_token']}",
        "Content-Type": "application/json"
    }
    api_server = token_info['api_server']
    
    # Base structure required by Questrade API
    order_payload = {
        "symbolId": quote["symbolId"],
        "quantity": quantity,
        "action": action,         # "Buy" or "Sell"
        "orderType": order_type,   # "Market" or "Limit"
        "timeInForce": "Day",     # Good for the day
        "primaryRoute": "AUTO"
    }
    
    # Conditional logic based on execution choices
    if order_type.lower() == "limit":
        if not price:
            raise ValueError("⚠️ A specific limit price is strictly required for Limit orders.")
        order_payload["limitPrice"] = price

    order_url = f"{api_server}v1/accounts/{account_id}/orders"
    
    # Note: Use POST to execute. For a safe test, you can swap the endpoint to '/orders/impact' 
    # to calculate the financial impact without sending a live trade to the exchange.
    response = requests.post(order_url, json=order_payload, headers=headers)
    
    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ Order submitted successfully for {ticker}!")
        return response.json()
    else:
        print(f"❌ Order failed: {response.text}")
        return None
