
import yliveticker
import threading
import time

#Ticker Class to store ticker Data
class TickerData:
    def __init__(self):
        self.latest = None

    def update(self, ticker_object):
        self.latest = ticker_object
    
    def get(self):
        return self.latest

#Create instance to hold ticker Data
ticker_data = TickerData()

# Callback function to handle incoming messages
def on_new_msg(ws, msg):
    ticker_data.update(msg)  # stores full ticker object
    print(msg)


# Callback for errors
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Callback for close events
def on_close(ws):
    print("WebSocket connection closed.")


def run_ticker(symbol):
    print(f"starting ticker stream in background for {symbol}")
    yliveticker.YLiveTicker(
        on_ticker=on_new_msg,
        ticker_names=[symbol],
        on_error=on_error,
        on_close=on_close
    )

def start_ticker_stream(symbol):
    ticker_thread = threading.Thread(target=run_ticker, args=(symbol,), daemon=True)
    ticker_thread.start()
    return ticker_thread

if __name__ == "__main__":
    selected_symbol = input("Enter ticker symbol: ").strip().upper()
    if not selected_symbol:
        raise ValueError("A ticker symbol is required.")

    start_ticker_stream(selected_symbol)
    print("main thread is free to do other things")

    try:
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nStopping...")

