
import yliveticker
from FmpClient import FMPClient
from StockValuation import StockValuation

# Callback function to handle incoming messages
def on_new_msg(ws, msg):
    print(msg)

# Start the WebSocket stream
"""
yliveticker.YLiveTicker(
    on_ticker=on_new_msg,
    ticker_names=["HD"]
)
"""

# Callback for errors
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Callback for close events
def on_close(ws):
    print("WebSocket connection closed.")

if __name__ == "__main__":
    # Start the WebSocket stream with error handling
    yliveticker.YLiveTicker(
        on_ticker=on_new_msg,
        ticker_names=["HD"],
        on_error=on_error,
        on_close=on_close
    )




fmp = FMPClient(api_key="d26fb39r01qvraiq386gd26fb39r01qvraiq3870")

def safe_api_call(callable_fn, *args, **kwargs):
    try:
        result = callable_fn(*args, **kwargs)
        if not result:
            print(f"Warning: No data returned for {callable_fn.__name__} with args {args}")
        return result
    except Exception as e:
        print(f"Error during {callable_fn.__name__}({args}): {e}")
        return None

# Example calls
income = safe_api_call(fmp.get_income_statement, "AAPL")
balance = safe_api_call(fmp.get_balance_sheet, "AAPL")
cash_flow = safe_api_call(fmp.get_cash_flow, "AAPL")
dividends = safe_api_call(fmp.get_dividends, "AAPL")



stock = StockValuation(
    share_price=150,
    earnings_per_share=5,
    book_value_per_share=50,
    dividend=2,
    growth_rate=0.05,
    discount_rate=0.10,
    cash_flows=[10, 12, 14, 16, 18]
)

print("P/E Ratio:", stock.pe_ratio())
print("P/B Ratio:", stock.pb_ratio())
print("DDM Value:", stock.dividend_discount_model())
print("DCF Value:", stock.discounted_cash_flow())