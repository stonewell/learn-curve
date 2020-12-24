import logging

from talib import RSI, MA

from .strategy_base import StrategyBase, SelectWithBuySellData

import pandas as pd
import pytz
import bt
import numpy as np


def create_strategy(args = None):
    return RSI_4_25_75_MA_200()

class RSIStrategyBase(StrategyBase):
    def __init__(self, rsi_days, sell_value, buy_value, ma_value):
        super().__init__('RSI_%d_%d_%d_ma_%d' % (rsi_days, sell_value, buy_value, ma_value))
        self.rsi_days_ = rsi_days
        self.sell_value_ = sell_value
        self.buy_value_ = buy_value
        self.ma_value_ = ma_value

    def get_strategy(self, data):
        rsi_data = data.apply(lambda v: RSI(v, self.rsi_days_))
        rsi_buy_data = (rsi_data < self.buy_value_) & (data > data.apply(lambda v: MA(v, self.ma_value_)))
        rsi_sell_data = rsi_data > self.sell_value_

        strategy = bt.Strategy(self.name_,
                               [bt.algos.RunDaily(),
                                SelectWithBuySellData(rsi_buy_data, rsi_sell_data),
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()])

        return strategy

class RSI_4_25_75_MA_200(RSIStrategyBase):
    def __init__(self):
        super().__init__(4, 55, 25, 30)
