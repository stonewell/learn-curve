import logging

from zipline.api import symbol

import numpy as np

import pyfolio as pf
from pyfolio import timeseries


class StrategyBase(object):
    def __init__(self):
        super().__init__()
        self.current_parameter_ = None

    def initialize(self, context, stock_ids):
        context.assets = [symbol(id) for id in stock_ids]

    def handle_data(self, context, data):
        for asset in context.assets:
            self.handle_single_asset_data(context, asset, data)

    def handle_single_asset_data(self, context, asset, data):
        raise NotImplementedError

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
