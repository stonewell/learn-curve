import os
import sys
import logging
from functools import lru_cache

import numpy as np

import pandas as pd
import pytz

import pyfolio as pf
from pyfolio import timeseries

from zipline import run_algorithm

from cn_a.vip_dataset import load_stock_data

sys.dont_write_bytecode = True

@lru_cache(maxsize=42)
def _load_data(symbol):
    return load_stock_data(symbol)

@lru_cache(maxsize=42)
def _load_algo_func(algo_module, name):
    try:
        return getattr(algo_module, name)
    except AttributeError:
        return None

def _create_pd_panel(data):
    trading_data = {}
    trading_data[data.stock_id] = data.data_frame

    panel = pd.Panel(trading_data)
    panel.minor_axis = ["open","high","low","close","volume"]
    panel.major_axis = panel.major_axis.tz_localize(pytz.utc)

    return panel

def _general_analyze(perf_data):
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(perf_data)

    perf_stats = timeseries.perf_stats(returns,
                                       positions=positions,
                                       transactions=transactions)

    logging.info(perf_stats)
    logging.info("Sharpe Ratio:{}%".format(np.round(perf_stats.loc['Sharpe ratio'] * 100)))

class AlgoRunner(object):
    def __init__(self, algo, capital_base):
        self.initialize_ = _load_algo_func(algo, "initialize")
        self.handle_data_ = _load_algo_func(algo, "handle_data")
        self.before_trading_start_ = _load_algo_func(algo, "before_trading_start")
        self.analyze_ = _load_algo_func(algo, "analyze")
        self.algo_ = algo
        self.capital_base_ = capital_base


    def run(self, symbol, start_date = None, end_date = None, analyze_func = None):
        data = _load_data(symbol)
        start_date = pd.to_datetime(start_date or data.trading_date[0], utc=True)
        end_date = pd.to_datetime(end_date or data.trading_date[-1], utc=True)
        setattr(self.algo_, 'symbol_id', str(data.stock_id))

        panel = _create_pd_panel(data)

        def tmp_analyze_func(context=None, results=None):
            if analyze_func is not None:
                analyze_func(results)
            elif self.analyze_ is not None:
                self.analyze_(context, results)
            else:
                _general_analyze(results)

        perf_data = run_algorithm(start=start_date,
                                  end=end_date,
                                  trading_calendar=data.trading_cal,
                                  data=panel,
                                  capital_base=self.capital_base_,
                                  initialize=self.initialize_,
                                  handle_data=self.handle_data_,
                                  before_trading_start=self.before_trading_start_,
                                  analyze=tmp_analyze_func,
                                  default_extension=False)

        return perf_data


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.INFO)
    data = _load_data(600019)

    logging.debug('vip data:\n{}'.format(data.data_frame.tail()))
    logging.debug('vip data holidays:\n{}'.format(data.holidays[:10]))

    from cn_a.algos import dual_ema_talib as algo

    runner = AlgoRunner(algo, 100000.0)
    runner.run(600019, start_date=pd.to_datetime('2015-01-01', utc=True),
               end_date=pd.to_datetime('2017-01-01', utc=True))
    #runner.run(600019, start_date=pd.to_datetime('2015-01-01', utc=True), analyze_func=lambda x:algo.__analyze(None, x))
