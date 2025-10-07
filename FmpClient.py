import requests

class FMPClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def get_income_statement(self, symbol, limit=1):
        url = f"{self.base_url}/income-statement/{symbol}?limit={limit}&apikey={self.api_key}"
        return requests.get(url).json()

    def get_balance_sheet(self, symbol, limit=1):
        url = f"{self.base_url}/balance-sheet-statement/{symbol}?limit={limit}&apikey={self.api_key}"
        return requests.get(url).json()

    def get_cash_flow(self, symbol, limit=5):
        url = f"{self.base_url}/cash-flow-statement/{symbol}?limit={limit}&apikey={self.api_key}"
        return requests.get(url).json()

    def get_dividends(self, symbol):
        url = f"{self.base_url}/historical-price-full/stock_dividend/{symbol}?apikey={self.api_key}"
        return requests.get(url).json()

    def get_symbol_search(self, query):
        url = f"{self.base_url}/search?query={query}&limit=10&apikey={self.api_key}"
        return requests.get(url).json()
