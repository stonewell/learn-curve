import logging

from .scriptable_strategy import ScriptableStrategy


def create_strategy(args = None):
    return __R3()

class __RSIStrategyBase(ScriptableStrategy):
    def __init__(self, rsi_days, sell_value, buy_value, ma_value, drop_days, rsi_drop_first_value):
        super().__init__('RSI_%d_%d_%d_ma_%d_drop_%d_%d'
                         % (rsi_days, sell_value, buy_value, ma_value, drop_days, rsi_drop_first_value),
                         self.__get_buy_script(rsi_days, drop_days, rsi_drop_first_value, buy_value, ma_value),
                         'RSI(C, %d) > %d' % (rsi_days, sell_value),
                         'close',
                         'close')
        self.rsi_days_ = rsi_days
        self.sell_value_ = sell_value
        self.buy_value_ = buy_value
        self.ma_value_ = ma_value
        self.drop_days_ = drop_days
        self.rsi_drop_first_value_ = rsi_drop_first_value

    def __get_buy_script(self, rsi_days, drop_days, rsi_drop_first_value, buy_value, ma_value):
        rsi = 'RSI(C, %d)' % rsi_days

        parts = []
        parts.append('(%s<%d)' % (rsi, buy_value))

        last_rsi = rsi
        for i in range(drop_days):
            tmp_rsi = 'REF(%s, -%d)' % (rsi, (i + 1))
            parts.append('(%s<%s)' % (last_rsi, tmp_rsi))

            last_rsi = tmp_rsi

        parts.append('(%s>%d)' % (last_rsi, rsi_drop_first_value))
        parts.append('(C>MA(C, %d))' % (ma_value))

        s = ' & '.join(parts)

        return s

class __R3(__RSIStrategyBase):
    def __init__(self):
        super().__init__(2, 70, 10, 200, 3, 60)

