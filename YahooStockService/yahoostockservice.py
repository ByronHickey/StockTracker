
import yliveticker
#from FmpClient import FMPClient
from YFinanceClient import YFinanceClient
from StockValuation import StockValuation
import threading
import time

#Ticker Class to store ticker Data
class TickerData:
    def __init__(self):
        self.latest=None

    def update(self,ticker_object):
        self.latest=self = ticker_object
    
    def get(self):
        return self.latest

#Create instance to hold ticker Data
ticker_data= TickerData()

# Callback function to handle incoming messages
def on_new_msg(ws, msg):
    ticker_data.update(msg) #stores full ticker object
    print(msg)


# Callback for errors
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Callback for close events
def on_close(ws):
    print("WebSocket connection closed.")



def run_ticker():
    print("starting ticker stream in background")  # Start the WebSocket stream with error handling
    yliveticker.YLiveTicker(
        on_ticker=on_new_msg,
        ticker_names=["AAPL"],
        on_error=on_error,
        on_close=on_close
    )

if __name__ == "__main__":
    #start ticker in background thread
    ticker_thread = threading.Thread(target=run_ticker, daemon=True)
    ticker_thread.start()

    #Main thread continues here
    print("main thread is free to do other things")

    try:
        #give ticker time to start
        time.sleep(3)

        finance_analyss = YFinanceClient()

        #get ticker object
        current_ticker = ticker_data.get()
        if current_ticker and 'price' in current_ticker:
            share_price = current_ticker['price']
        else:
            #fallback use yfinance price
            info = finance_analyss.get_info("AAPL")
            share_price = info.get("currentPrice", 0)
        
        print(f"Using share price: {share_price}")

        #Get analysis data from /yfinance


        stock = StockValuation(
            share_price=share_price,
            earnings_per_share=finance_analyss.get_earnings_per_share("AAPL"),
            book_value_per_share=finance_analyss.get_book_value_per_share("AAPL"),
            dividend=finance_analyss.get_latest_dividend("AAPL"),
            growth_rate=0.05,
            discount_rate=0.10,
            cash_flows=finance_analyss.get_cash_flows_list("AAPL", limit=5)
        )

        print("P/E Ratio:", stock.pe_ratio())
        print("P/B Ratio:", stock.pb_ratio())
        print("DDM Value:", stock.dividend_discount_model())
        print("DCF Value:", stock.discounted_cash_flow())
        

        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nStopping...")

