class TradeRule(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._stock_on_hand = False
        self._sell_stock = False
        self._buy_stock = False
        self._buy_data = None
        self._trade_records = []

    def on_data(self, data):
        if self._stock_on_hand and self._sell_stock:
            self._do_sell(data)
        elif not self._stock_on_hand and self._buy_stock:
            self._do_buy(data)
        elif self._stock_on_hand and self._should_sell(data):
            self._sell_stock = True
        elif not self._stock_on_hand and self._should_buy(data):
            self._buy_stock = True

    def _should_buy(self, data):
        return False

    def _should_sell(self, data):
        return False

    def _do_sell(self, data):
        if not self._buy_data:
            raise ValueError("buy data empty")
        self._trade_records.append((self._buy_data, data))
        self._stock_on_hand = False
        self._sell_stock = False
        self._buy_data = None

    def _do_buy(self, data):
        if self._buy_data:
            raise ValueError('buy again')

        self._buy_data = data
        self._stock_on_hand = True
        self._buy_stock = False

    def final_results(self):
        trade_results = []
        total_gain = 0.0

        for buy_data, sell_data in self._trade_records:
            buy_price = (buy_data.close_price + buy_data.open_price) / 2
            sell_price = (sell_data.close_price + sell_data.open_price) / 2
            gain = (sell_price - buy_price) / buy_price

            trade_results.append((buy_data.date, sell_data.date, gain))
            total_gain += gain

        return trade_results, total_gain
