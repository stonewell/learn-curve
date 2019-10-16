import sys
import logging

import pandas as pd
import pytz

from zipline import run_algorithm

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
            trading_data[data.stock_id] = data.data_frame

        panel = pd.Panel(trading_data)
        panel.minor_axis = ["open","high","low","close","volume"]
        panel.major_axis = panel.major_axis.tz_localize(pytz.utc)

        return panel

    def ensure_stock_data(self, symbols):
        for symbol in symbols:
            self.load_data_(symbol)

    def run(self, algo, symbols, start_date=None, end_date=None, analyze_func=None):
        data = []
        for symbol in symbols:
            data.append(self.load_data_(symbol))

        start_date = pd.to_datetime(start_date, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)

        panel = self.__create_pd_panel(data)

        def tmp_analyze_func(context=None, results=None):
            if analyze_func is not None:
                analyze_func(context, results)
            else:
                algo.analyze(context, results)

        perf_data = run_algorithm(start=start_date,
                                  end=end_date,
                                  trading_calendar=data[0].trading_cal,
                                  data=panel,
                                  capital_base=self.capital_base_,
                                  initialize=lambda context: algo.initialize(context, symbols),
                                  handle_data=lambda context, data: algo.handle_data(context, data),
                                  before_trading_start=lambda context, data: algo.before_trading_start(context, data),
                                  analyze=tmp_analyze_func,
                                  default_extension=False)

        return perf_data
