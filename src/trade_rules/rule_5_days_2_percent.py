import trade_rule

ndays = 5

class TradeRule(trade_rule.TradeRule):
    def __init__(self):
        super(TradeRule, self).__init__()

        self.last_days = []

    def on_data(self, data):
        self.last_days.append(data)

        while len(self.last_days) > ndays:
            del self.last_days[0]

        super(TradeRule, self).on_data(data)

    def _should_buy(self, data):
        if len(self.last_days) < ndays:
            return False
        prices = [v.close_price for v in self.last_days]

        if (all([x>=prices[0] for x in prices])):
            if prices[-1] >= max(prices):
                return False

            if max(prices) - prices[-1] < max(prices) * .02:
                return False
        if (all([x<=prices[0] for x in prices])):
            if (prices[-1] > min(prices)) and (prices[-1] - min(prices) > min(prices) * .02):
                return True
        return False

    def _should_sell(self, data):
        if len(self.last_days) < ndays:
            return False
        prices = [v.close_price for v in self.last_days]

        if prices[-1] < max(prices):
            if max(prices) - prices[-1] > max(prices) * .02:
                return True

        return False
