from dataclasses import dataclass
import time

from YahooStockService.YFinanceClient import YFinanceClient
from YahooStockService.StockValuation import StockValuation
from YahooStockService.yahoostockservice import start_ticker_stream, ticker_data
from QuestTradeBot.OrderAndDataFunctions import (
    get_market_quote,
    place_order,
    validate_symbol as validate_questrade_symbol,
)
from QuestTradeBot.QuestTradeTokenRefresh import get_valid_access_token


@dataclass
class SymbolContext:
    raw_symbol: str
    normalized_symbol: str
    yfinance_valid: bool
    questrade_valid: bool
    questrade_symbol_id: int | None
    errors: list[str]


class TradingController:
    def __init__(self, growth_rate=0.05, discount_rate=0.10, cash_flow_limit=5):
        self.finance_client = YFinanceClient()
        self.growth_rate = growth_rate
        self.discount_rate = discount_rate
        self.cash_flow_limit = cash_flow_limit

    @staticmethod
    def normalize_symbol(raw_symbol):
        return (raw_symbol or "").strip().upper()

    def get_user_symbol(self):
        symbol = input("Enter ticker symbol: ")
        normalized_symbol = self.normalize_symbol(symbol)
        if not normalized_symbol:
            raise ValueError("Ticker symbol is required.")
        return symbol, normalized_symbol

    def build_symbol_context(self, raw_symbol):
        normalized_symbol = self.normalize_symbol(raw_symbol)
        errors = []

        yfinance_result = self.finance_client.validate_symbol(normalized_symbol)
        yfinance_valid = yfinance_result.get("is_valid", False)
        if not yfinance_valid:
            errors.append(yfinance_result.get("message", "Yahoo Finance validation failed."))

        questrade_valid = False
        questrade_symbol_id = None

        token_info = get_valid_access_token()
        if token_info:
            questrade_result = validate_questrade_symbol(normalized_symbol, token_info=token_info)
            questrade_valid = questrade_result.get("is_valid", False)
            questrade_symbol_id = questrade_result.get("symbolId")
            if not questrade_valid:
                errors.append(questrade_result.get("message", "Questrade validation failed."))
        else:
            errors.append("Questrade token not available; trading validation skipped.")

        return SymbolContext(
            raw_symbol=raw_symbol,
            normalized_symbol=normalized_symbol,
            yfinance_valid=yfinance_valid,
            questrade_valid=questrade_valid,
            questrade_symbol_id=questrade_symbol_id,
            errors=errors,
        )

    def run_analysis_pipeline(self, symbol_context):
        if not symbol_context.yfinance_valid:
            raise ValueError("Analysis requires a symbol that validates in Yahoo Finance.")

        start_ticker_stream(symbol_context.normalized_symbol)
        time.sleep(3)

        current_ticker = ticker_data.get()
        share_price = 0
        if isinstance(current_ticker, dict):
            share_price = current_ticker.get("price", 0)

        fundamentals = self.finance_client.get_fundamentals_snapshot(
            symbol_context.normalized_symbol,
            cash_flow_limit=self.cash_flow_limit,
        )

        if not share_price:
            share_price = fundamentals.get("info", {}).get("currentPrice", 0)

        stock = StockValuation(
            share_price=share_price,
            earnings_per_share=fundamentals["earnings_per_share"],
            book_value_per_share=fundamentals["book_value_per_share"],
            dividend=fundamentals["dividend"],
            growth_rate=self.growth_rate,
            discount_rate=self.discount_rate,
            cash_flows=fundamentals["cash_flows"],
        )

        return {
            "symbol": symbol_context.normalized_symbol,
            "share_price": share_price,
            "pe_ratio": stock.pe_ratio(),
            "pb_ratio": stock.pb_ratio(),
            "ddm_value": stock.dividend_discount_model(),
            "dcf_value": stock.discounted_cash_flow(),
        }

    def run_trade_pipeline(self, symbol_context, account_id, quantity, order_type="Market", price=None, action="Buy", dry_run=True):
        if not symbol_context.questrade_valid:
            raise ValueError("Trading requires a symbol that validates in Questrade.")

        token_info = get_valid_access_token()
        if not token_info:
            raise ValueError("Unable to obtain a valid Questrade access token.")

        quote = get_market_quote(
            ticker=symbol_context.normalized_symbol,
            symbol_id=symbol_context.questrade_symbol_id,
            token_info=token_info,
        )

        if dry_run:
            return {
                "symbol": symbol_context.normalized_symbol,
                "mode": "dry_run",
                "quote": quote,
            }

        order_response = place_order(
            account_id=account_id,
            ticker=symbol_context.normalized_symbol,
            quantity=quantity,
            order_type=order_type,
            price=price,
            action=action,
            symbol_id=symbol_context.questrade_symbol_id,
            token_info=token_info,
        )

        return {
            "symbol": symbol_context.normalized_symbol,
            "mode": "live",
            "quote": quote,
            "order_response": order_response,
        }


if __name__ == "__main__":
    controller = TradingController()
    raw_symbol, _ = controller.get_user_symbol()
    context = controller.build_symbol_context(raw_symbol)

    print(f"Selected symbol: {context.normalized_symbol}")
    print(f"Yahoo Finance valid: {context.yfinance_valid}")
    print(f"Questrade valid: {context.questrade_valid}")

    if context.errors:
        print("Validation notes:")
        for item in context.errors:
            print(f"- {item}")

    if context.yfinance_valid:
        analysis = controller.run_analysis_pipeline(context)
        print("Analysis results:")
        for key, value in analysis.items():
            print(f"{key}: {value}")
