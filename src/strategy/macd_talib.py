import logging

from .scriptable_strategy import ScriptableStrategy


def create_strategy(args = None):
    return __MACD4()

class __MACDStrategyBase(ScriptableStrategy):
    def __init__(self, macd_days, fastperiod=12, slowperiod=26, signalperiod=9):
        super().__init__('MACD_%d_%d_%d_%d'
                         % (fastperiod, slowperiod, signalperiod, macd_days),
                         self.__get_buy_script(fastperiod, slowperiod, signalperiod, macd_days),
                         'C > REF(C, -1)',
                         'close',
                         'close')
        self.macd_days_ = macd_days
        self.fastperiod_ = fastperiod
        self.slowperiod_ = slowperiod
        self.signalperiod_ = signalperiod

    def __get_buy_script(self, fastperiod, slowperiod, signalperiod, macd_days):
        macd = 'MACDHist(C, %d, %d, %d)' % (fastperiod, slowperiod, signalperiod)

        parts = []

        last_macd = macd
        for i in range(macd_days):
            tmp_macd = 'REF(%s, -%d)' % (macd, (i + 1))
            parts.append('(%s<%s)' % (last_macd, tmp_macd))

            last_macd = tmp_macd

        parts.append('(%s<0)' % (macd))

        s = ' & '.join(parts)

        return s

class __MACD4(__MACDStrategyBase):
    def __init__(self):
        super().__init__(4)
