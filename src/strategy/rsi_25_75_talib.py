import logging

from talib import RSI, MA

from .strategy_base import StrategyBase

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
        rsi_buy_data = data.apply(lambda v: RSI(v, self.rsi_days_)) <= self.buy_value_
        rsi_sell_data = data.apply(lambda v: RSI(v, self.rsi_days_)) >= self.sell_value_
        ma_data = data > data.apply(lambda v: MA(v, self.ma_value_))

        strategy = bt.Strategy(self.name_,
                               [bt.algos.RunDaily(),
                                RSISelect(rsi_buy_data, rsi_sell_data, ma_data),
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()])

        return strategy

class RSI_4_25_75_MA_200(RSIStrategyBase):
    def __init__(self):
        super().__init__(4, 55, 25, 200)

class RSISelect(bt.Algo):
    def __init__(self, rsi_buy_data, rsi_sell_data, ma_data):
        self.rsi_buy_data_ = rsi_buy_data
        self.rsi_sell_data_ = rsi_sell_data
        self.ma_data_ = ma_data

    def __call__(self, target):
        d = pd.to_datetime(target.now)

        sell_list = set()
        if d in self.rsi_sell_data_.index:
            sig = self.rsi_sell_data_.loc[d]

            sig = sig[sig == True]

            sell_list = set(sig.index)

        buy_list = set()

        if d in self.rsi_buy_data_.index and d in self.ma_data_.index:
            sig = self.rsi_buy_data_.loc[d]
            sig = sig[sig == True]

            sig_ma = self.ma_data_.loc[d]
            sig_ma = sig_ma[sig_ma == True]

            buy_list = set(sig.index) & set(sig_ma.index)

        selected = buy_list - sell_list

        for cname in target.children:
            if cname in sell_list:
                continue

            c = target.children[cname]

            if target.fixed_income:
                v = c.notional_value
            else:
                v = c.value

            # if non-zero and non-null, we need to keep
            if v != 0. and not np.isnan(v):
                selected.add(cname)

        target.temp['selected'] = list(selected)

        # return True because we want to keep on moving down the stack
        return True
