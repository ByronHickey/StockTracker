import requests

try:
    from .QuestTradeTokenRefresh import get_valid_access_token
except ImportError:
    from QuestTradeTokenRefresh import get_valid_access_token


def normalize_symbol(ticker):
    return (ticker or "").strip().upper()


def _resolve_token_info(token_info=None):
    return token_info if token_info else get_valid_access_token()


def resolve_symbol_id(ticker, token_info=None):
    """Resolve a text ticker into a Questrade symbolId."""
    normalized_ticker = normalize_symbol(ticker)
    token_payload = _resolve_token_info(token_info)
    if not token_payload:
        return {
            "is_valid": False,
            "ticker": normalized_ticker,
            "symbolId": None,
            "message": "Missing or expired Questrade token."
        }

    headers = {"Authorization": f"Bearer {token_payload['access_token']}"}
    api_server = token_payload['api_server']
    search_url = f"{api_server}v1/symbols?names={normalized_ticker}"
    search_res = requests.get(search_url, headers=headers)

    if search_res.status_code != 200:
        return {
            "is_valid": False,
            "ticker": normalized_ticker,
            "symbolId": None,
            "message": f"Symbol lookup failed: {search_res.text}"
        }

    symbols = search_res.json().get("symbols", [])
    if not symbols:
        return {
            "is_valid": False,
            "ticker": normalized_ticker,
            "symbolId": None,
            "message": "Ticker not found in Questrade."
        }

    return {
        "is_valid": True,
        "ticker": normalized_ticker,
        "symbolId": symbols[0]["symbolId"],
        "message": "Ticker validated in Questrade.",
        "token_info": token_payload
    }


def validate_symbol(ticker, token_info=None):
    """Validate a symbol and return a compact controller-friendly payload."""
    result = resolve_symbol_id(ticker, token_info=token_info)
    return {
        "is_valid": result["is_valid"],
        "ticker": result["ticker"],
        "symbolId": result["symbolId"],
        "message": result["message"]
    }


def get_market_quote(ticker=None, symbol_id=None, token_info=None):
    """Retrieves real-time market data (Bid, Ask, Last Price) for a given symbol."""
    token_payload = _resolve_token_info(token_info)
    if not token_payload:
        return None

    normalized_ticker = normalize_symbol(ticker) if ticker else None
    headers = {"Authorization": f"Bearer {token_payload['access_token']}"}
    api_server = token_payload['api_server']

    if symbol_id is None:
        if not normalized_ticker:
            raise ValueError("ticker or symbol_id is required to fetch a market quote.")
        symbol_result = resolve_symbol_id(normalized_ticker, token_info=token_payload)
        if not symbol_result["is_valid"]:
            print(f"❌ {symbol_result['message']}")
            return None
        symbol_id = symbol_result["symbolId"]

    # Step 2: Fetch the actual market quote using that ID
    quote_url = f"{api_server}v1/markets/quotes/{symbol_id}"
    quote_res = requests.get(quote_url, headers=headers)

    if quote_res.status_code == 200:
        data = quote_res.json()['quotes'][0]
        return {
            "ticker": normalized_ticker,
            "symbolId": symbol_id,
            "bid": data.get("bidPrice"),
            "bid_size": data.get("bidSize"),
            "ask": data.get("askPrice"),
            "ask_size": data.get("askSize"),
            "last_trade": data.get("lastTradePrice")
        }
    return None


def place_order(account_id, ticker, quantity, order_type="Market", price=None, action="Buy", symbol_id=None, token_info=None):
    """
    Executes a purchase or sale order.
    Supported order_types: 'Market', 'Limit'
    Supported actions: 'Buy', 'Sell'
    """
    token_payload = _resolve_token_info(token_info)
    if not token_payload:
        return None

    normalized_ticker = normalize_symbol(ticker)
    resolved_symbol_id = symbol_id
    if resolved_symbol_id is None:
        symbol_result = resolve_symbol_id(normalized_ticker, token_info=token_payload)
        if not symbol_result["is_valid"]:
            print(f"❌ {symbol_result['message']}")
            return None
        resolved_symbol_id = symbol_result["symbolId"]

    headers = {
        "Authorization": f"Bearer {token_payload['access_token']}",
        "Content-Type": "application/json"
    }
    api_server = token_payload['api_server']
    
    # Base structure required by Questrade API
    order_payload = {
        "symbolId": resolved_symbol_id,
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
        print(f"✅ Order submitted successfully for {normalized_ticker}!")
        return response.json()
    else:
        print(f"❌ Order failed: {response.text}")
        return None
