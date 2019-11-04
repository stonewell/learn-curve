import logging

from zipline.api import symbol

import numpy as np

import pyfolio as pf
from pyfolio import timeseries


class StrategyBase(object):
    def __init__(self, name):
        super().__init__()
        self.current_parameter_ = None
        self.name_ = name
        self.learn_context_ = None

    def initialize(self, context, stock_ids):
        context.assets = [symbol(id) for id in stock_ids]

    def handle_data(self, context, data):
        for asset in context.assets:
            self.handle_single_asset_data(context, asset, data)

    def handle_single_asset_data(self, context, asset, data):
        raise NotImplementedError

    def update_learn_context(self, context, asset, data, is_buy):
        if self.learn_context_:
            self.learn_context_.handle_asset_data(context, asset, data, is_buy)

    def analyze(self, context, results):
        returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results)

        perf_stats = timeseries.perf_stats(returns,
                                           positions=positions,
                                           transactions=transactions)

        logging.info(perf_stats)
        logging.info("Sharpe Ratio:{}%".format(np.round(perf_stats.loc['Sharpe ratio'] * 100)))

    def before_trading_start(self, context, data):
        pass

    def parameter_set(self):
        return list()

    def __get_current_parameter(self):
        return self.current_parameter_

    def __set_current_parameter(self, parameter):
        self.current_parameter_ = parameter

    current_parameter = property(__get_current_parameter, __set_current_parameter)

    def __get_name(self):
        return self.name_

    def __set_name(self, name):
        self.name_ = name

    name = property(__get_name, __set_name)

    def lh_cross_n_days(self, v1, v2, n):
        for i in range(n - 1):
            v = (
                all(v1[x] >= v1[i] for x in range(i + 1, n))
                and all(v1[x] >= v2[x] for x in range(i, n))
                and max(v1[i:]) == v1[-1]
                )

            if v:
                return True

        return False

    def hl_cross_n_days(self, v1, v2, n):
        for i in range(n - 1):
            v = (
                True
                and all(v1[x] <= v1[i] for x in range(i + 1, n))
                and all(v1[x] <= v2[x] for x in range(i, n))
                )

            if v:
                return True

        return False

    def kdj(self, data, asset, n):
        trailing_window = data.history(asset, 'price', n * 3, '1d')
        high_trailing_window = data.history(asset, 'high', n * 3, '1d')
        low_trailing_window = data.history(asset, 'low', n * 3, '1d')

        low_list = low_trailing_window.rolling(window=n).min()
        high_list = high_trailing_window.rolling(window=n).max()

        rsv = (trailing_window - low_list) / (high_list - low_list) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()

        j = 3 * k - 2 * d

        return (k, d, j)

    def get_default_parameter(self):
        return None

    def __get_learn_context(self):
        return self.learn_context_

    def __set_learn_context(self, learn_context):
        self.learn_context_ = learn_context

    learn_context = property(__get_learn_context, __set_learn_context)
