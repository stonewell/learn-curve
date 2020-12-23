import logging
import bt
import pandas as pd
import numpy as np


class StrategyBase(object):
    def __init__(self, name):
        super().__init__()
        self.name_ = name
        self.stock_ids_ = []

    def initialize(self, context, stock_ids):
        self.stock_ids_ = stock_ids

class SelectWithBuySellData(bt.Algo):
    def __init__(self, buy_data, sell_data):
        self.buy_data_ = buy_data
        self.sell_data_ = sell_data

    def __call__(self, target):
        d = pd.to_datetime(target.now)

        sell_list = set()
        if d in self.sell_data_.index:
            sig = self.sell_data_.loc[d]

            sig = sig[sig == True]

            sell_list = set(sig.index)

        buy_list = set()

        if d in self.buy_data_.index:
            sig = self.buy_data_.loc[d]
            sig = sig[sig == True]

            buy_list = set(sig.index)

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
