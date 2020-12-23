import sys
import logging

import pandas as pd
import pytz

import bt

try:
    from . import module_loader
except:
    import module_loader

sys.dont_write_bytecode = True

class AlgoRunner(object):
    def __init__(self, stock_data_provider, capital_base, parameters):
        self.stock_data_provider_ = stock_data_provider
        self.load_data_ = module_loader.load_module_func(stock_data_provider,
                                                        'load_stock_data')

        self.capital_base_ = capital_base
        self.parameters_ = parameters

    def __create_pd_panel(self, all_data):
        trading_data = {}

        for data in all_data:
            trading_data[data.stock_id] = data.data_frame['close']

        panel = pd.DataFrame(data=trading_data)

        return panel

    def ensure_stock_data(self, symbols):
        for symbol in symbols:
            self.load_data_(symbol)

    def run(self, algo, symbols, start_date=None, end_date=None, analyze_func=None):
        data = []
        for symbol in symbols:
            data.append(self.load_data_(symbol))

        if start_date:
            start_date = pd.to_datetime(start_date)

        if end_date:
            end_date = pd.to_datetime(end_date)

        panel = self.__create_pd_panel(data)

        filtered_panel = panel
        if start_date and end_date:
            filtered_panel = panel[(panel.index >= start_date) & (panel.index <= end_date)]

        test = bt.Backtest(algo.get_strategy(panel), filtered_panel)

        return bt.run(test)
