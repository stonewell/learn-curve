import logging

from .scriptable_strategy import ScriptableStrategy


def create_strategy(args = None):
    return __Strategy()

class __StrategyBase(ScriptableStrategy):
    def __init__(self, buy_value, sell_value, rsi_days, rsi_value):
        super().__init__('IBS_%f_%f_RSI_%d_%d'
                         % (buy_value, sell_value, rsi_days, rsi_value),
                         '(((C-L)/(H-L)) < %f) & (RSI(C, %d) < %d)' % (buy_value, rsi_days, rsi_value),
                         '((C-L)/(H-L)) > %f' % sell_value,
                         'close',
                         'close')

        self.buy_value_ = buy_value
        self.sell_value_ = sell_value
        self.rsi_days_ = rsi_days
        self.rsi_value_ = rsi_value

class __Strategy(__StrategyBase):
    def __init__(self):
        super().__init__(0.2, 0.8, 2, 10)
