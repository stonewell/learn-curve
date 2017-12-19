import trade_rule

ndays = 5

class TradeRule(trade_rule.TradeRule):
    def __init__(self):
        super(TradeRule, self).__init__()

        self._last_days = []
        self._max_price = 0

    def on_data(self, data):
        self._last_days.append(data)
        tmp_max = max([x.close_price for x in self._last_days])
        self._max_price = max(tmp_max, self._max_price)

        while len(self._last_days) > ndays:
            del self._last_days[0]

        super(TradeRule, self).on_data(data)

    def _should_buy(self, data):
        if len(self._last_days) < ndays:
            return False
        prices = [v.close_price for v in self._last_days]

        if prices[-1] < prices[0] and prices[-1] - min(prices) > min(prices) * .02:
            return True
        return False

    def _should_sell(self, data):
        if len(self._last_days) < ndays:
            return False
        prices = [v.close_price for v in self._last_days]

        if max(prices) - prices[-1] > self._max_price * .02:
            return True

        return False

    def _do_sell(self, data):
        super(TradeRule, self)._do_sell(data)
        self._max_price = 0

    def _do_buy(self, data):
        super(TradeRule, self)._do_buy(data)
        self._max_price = 0
