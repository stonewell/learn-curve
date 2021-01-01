import logging

from .scriptable_strategy import ScriptableStrategy


def create_strategy(args = None):
    return __IBS()

class __IBSStrategyBase(ScriptableStrategy):
    def __init__(self, buy_value, sell_value):
        super().__init__('IBS_%f_%f'
                         % (buy_value, sell_value),
                         '((C-L)/(H-L)) < %f' % buy_value,
                         '((C-L)/(H-L)) > %f' % sell_value,
                         'close',
                         'close')

        self.buy_value_ = buy_value
        self.sell_value_ = sell_value

class __IBS(__IBSStrategyBase):
    def __init__(self):
        super().__init__(0.2, 0.8)
