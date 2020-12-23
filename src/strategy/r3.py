import logging

from talib import RSI, MA

from .strategy_base import StrategyBase,SelectWithBuySellData

import pandas as pd
import pytz
import bt
import numpy as np


def create_strategy(args = None):
    return __R3()

class __RSIStrategyBase(StrategyBase):
    def __init__(self, rsi_days, sell_value, buy_value, ma_value, drop_days, rsi_drop_first_value):
        super().__init__('RSI_%d_%d_%d_ma_%d_drop_%d_%d'
                         % (rsi_days, sell_value, buy_value, ma_value, drop_days, rsi_drop_first_value))
        self.rsi_days_ = rsi_days
        self.sell_value_ = sell_value
        self.buy_value_ = buy_value
        self.ma_value_ = ma_value
        self.drop_days_ = drop_days
        self.rsi_drop_first_value_ = rsi_drop_first_value

    def get_strategy(self, data):
        rsi_data = data.apply(lambda v: RSI(v, self.rsi_days_))

        rsi_drop_data = self.__generate_drop_data(rsi_data)
        rsi_buy_data = (
            (rsi_data < self.buy_value_)
            & (data > data.apply(lambda v: MA(v, self.ma_value_)))
            & rsi_drop_data
        )

        rsi_sell_data = rsi_data > self.sell_value_

        strategy = bt.Strategy(self.name_,
                               [bt.algos.RunDaily(),
                                SelectWithBuySellData(rsi_buy_data, rsi_sell_data),
                                bt.algos.WeighMeanVar(),
                                bt.algos.Rebalance()])

        return strategy

    def __generate_drop_data(self, rsi_data):
        drop_data = None

        last_data = rsi_data
        for i in range(self.drop_days_):
            data = last_data.shift(1)

            if drop_data is None:
                drop_data = last_data < data
            else:
                drop_data = drop_data & (last_data < data)

            last_data = data

        drop_data = drop_data & (last_data > self.rsi_drop_first_value_)

        return drop_data


class __R3(__RSIStrategyBase):
    def __init__(self):
        super().__init__(2, 70, 10, 200, 3, 60)

