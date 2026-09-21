import yfinance as yf

 

class YFinanceClient:

    def __init__(self, api_key=None):

        # api_key not needed for yfinance

        self.api_key = api_key

    @staticmethod
    def normalize_symbol(symbol):
        return (symbol or "").strip().upper()

    def validate_symbol(self, symbol):
        """Validate a ticker symbol against Yahoo Finance metadata and history."""
        normalized_symbol = self.normalize_symbol(symbol)
        if not normalized_symbol:
            return {
                "is_valid": False,
                "normalized_symbol": normalized_symbol,
                "message": "Ticker symbol is empty."
            }

        try:
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info or {}
            history = ticker.history(period="1d")

            has_info = bool(info.get("symbol") or info.get("shortName") or info.get("longName"))
            has_history = history is not None and not history.empty
            is_valid = has_info or has_history

            return {
                "is_valid": is_valid,
                "normalized_symbol": normalized_symbol,
                "message": "Symbol validated by Yahoo Finance." if is_valid else "Symbol not found in Yahoo Finance.",
                "info": info
            }
        except Exception as e:
            return {
                "is_valid": False,
                "normalized_symbol": normalized_symbol,
                "message": f"Yahoo validation failed: {e}",
                "info": {}
            }

 

    def get_income_statement(self, symbol, limit=1):

        """Get income statement data from Yahoo Finance"""

        try:

            ticker = yf.Ticker(symbol)

            income_stmt = ticker.income_stmt

            if income_stmt is not None:

                return income_stmt.iloc[:limit].to_dict()

            return {}

        except Exception as e:

            print(f"Error fetching income statement: {e}")

            return {}

 

    def get_balance_sheet(self, symbol, limit=1):

        """Get balance sheet data from Yahoo Finance"""

        try:

            ticker = yf.Ticker(symbol)

            balance_sheet = ticker.balance_sheet

            if balance_sheet is not None:

                return balance_sheet.iloc[:limit].to_dict()

            return {}

        except Exception as e:

            print(f"Error fetching balance sheet: {e}")

            return {}

 

    def get_cash_flow(self, symbol, limit=5):

        """Get cash flow statement data from Yahoo Finance"""

        try:

            ticker = yf.Ticker(symbol)

            cash_flow = ticker.cash_flow

            if cash_flow is not None:

                return cash_flow.iloc[:limit].to_dict()

            return {}

        except Exception as e:

            print(f"Error fetching cash flow: {e}")

            return {}

 

    def get_dividends(self, symbol):

        """Get dividend data from Yahoo Finance"""

        try:

            ticker = yf.Ticker(symbol)

            dividends = ticker.dividends

            if dividends is not None and len(dividends) > 0:

                return {"historical": [{"date": str(date), "dividend": value} for date, value in dividends.items()]}

            return {"historical": []}

        except Exception as e:

            print(f"Error fetching dividends: {e}")

            return {"historical": []}

 

    def get_info(self, symbol):

        """Get general stock info from Yahoo Finance"""

        try:

            ticker = yf.Ticker(symbol)

            info = ticker.info

            return info

        except Exception as e:

            print(f"Error fetching info: {e}")

            return {}

 

    def get_book_value_per_share(self, symbol):

        """Extract book value per share from balance sheet"""

        try:

            ticker = yf.Ticker(symbol)

            balance_sheet = ticker.balance_sheet

           

            if balance_sheet is not None and not balance_sheet.empty:

                # Use the correct field names from Yahoo Finance

                total_equity = balance_sheet.loc['Stockholders Equity'].iloc[0]

                shares_outstanding = balance_sheet.loc['Ordinary Shares Number'].iloc[0]

               

                if total_equity and shares_outstanding and shares_outstanding != 0:

                    return total_equity / shares_outstanding

           

            return 0

        except Exception as e:

            print(f"Error fetching book value per share: {e}")

            return 0

 

    def get_earnings_per_share(self, symbol):

        """Extract earnings per share from info"""

        try:

            ticker = yf.Ticker(symbol)

            info = ticker.info

            return info.get('trailingEps', 0)

        except Exception as e:

            print(f"Error fetching EPS: {e}")

            return 0

 

    def get_latest_dividend(self, symbol):

        """Extract latest dividend from dividends data"""

        try:

            ticker = yf.Ticker(symbol)

            dividends = ticker.dividends

            if dividends is not None and len(dividends) > 0:

                return dividends.iloc[0]

            return 0

        except Exception as e:

            print(f"Error fetching latest dividend: {e}")

            return 0

 

    def get_cash_flows_list(self, symbol, limit=5):

        """Extract operating cash flows from cash flow statement"""

        try:

            ticker = yf.Ticker(symbol)

            cash_flow = ticker.cash_flow

            if cash_flow is not None and not cash_flow.empty:

                if 'Operating Cash Flow' in cash_flow.index:

                    flows = cash_flow.loc['Operating Cash Flow'].dropna().head(limit).tolist()

                    return flows

            return []

        except Exception as e:

            print(f"Error fetching cash flows: {e}")

            return []

 

    def get_symbol_search(self, query):

        """Search for symbol (basic implementation)"""

        try:

            ticker = yf.Ticker(query)

            info = ticker.info

            return [{"symbol": query, "name": info.get("longName", "")}]

        except Exception as e:

            print(f"Error searching symbol: {e}")

            return []

    def get_fundamentals_snapshot(self, symbol, cash_flow_limit=5):
        """Return a consolidated fundamentals payload for valuation workflows."""
        normalized_symbol = self.normalize_symbol(symbol)
        info = self.get_info(normalized_symbol)
        return {
            "symbol": normalized_symbol,
            "info": info,
            "earnings_per_share": self.get_earnings_per_share(normalized_symbol),
            "book_value_per_share": self.get_book_value_per_share(normalized_symbol),
            "dividend": self.get_latest_dividend(normalized_symbol),
            "cash_flows": self.get_cash_flows_list(normalized_symbol, limit=cash_flow_limit)
        }