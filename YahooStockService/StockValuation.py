
class StockValuation:
    def __init__(self, share_price, earnings_per_share, book_value_per_share, dividend, growth_rate, discount_rate, cash_flows):
        self.share_price = share_price
        self.eps = earnings_per_share
        self.bvps = book_value_per_share
        self.dividend = dividend
        self.growth_rate = growth_rate
        self.discount_rate = discount_rate
        self.cash_flows = cash_flows  # List of future cash flows

    def pe_ratio(self):
        return self.share_price / self.eps if self.eps else None

    def pb_ratio(self):
        return self.share_price / self.bvps if self.bvps else None
    def dividend_discount_model(self):
        if self.discount_rate > self.growth_rate:
            return self.dividend * (1 + self.growth_rate) / (self.discount_rate - self.growth_rate)
        return None
    def discounted_cash_flow(self):
        dcf_value = 0
        for t, cf in enumerate(self.cash_flows, start=1):
            dcf_value += cf / ((1 + self.discount_rate) ** t)
        return dcf_value

    def ev_to_ebitda(self, enterprise_value, ebitda):
        return enterprise_value / ebitda if ebitda else None
