import logging

from .scriptable_strategy import ScriptableStrategy


def create_strategy(args = None):
    return __RSI_4_25_75_MA_200()

class __RSIStrategyBase(ScriptableStrategy):
    def __init__(self, rsi_days, sell_value, buy_value, ma_value):
        super().__init__('RSI_%d_%d_%d_ma_%d' % (rsi_days, sell_value, buy_value, ma_value),
                         '(RSI(C, %d) < %d) & (C > MA(C, %d))' % (rsi_days, buy_value, ma_value),
                         'RSI(C, %d) > %d' % (rsi_days, sell_value),
                         'close',
                         'close')
        self.rsi_days_ = rsi_days
        self.sell_value_ = sell_value
        self.buy_value_ = buy_value
        self.ma_value_ = ma_value

    def get_strategy(self, data):
        s = super().get_strategy(data)

        print(self.buy_data_.tail(1))
        print(self.sell_data_.tail(1))

        return s

class __RSI_4_25_75_MA_200(__RSIStrategyBase):
    def __init__(self):
        super().__init__(4, 80, 25, 200)
