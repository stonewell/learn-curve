import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt

try:
    from . import module_loader
except:
    import module_loader

sys.dont_write_bytecode = True

stock_data_provider = module_loader.load_module_from_file('stock_data_provider.cn_a.vip_dataset')
load_data = module_loader.load_module_func(stock_data_provider,
                                                 'load_stock_data')

data = load_data('600019')
data1 = load_data('600050')
data2 = load_data('600732')

def __create_pd_panel(all_data):
    trading_data = {}
    for data in all_data:
        trading_data[data.stock_id] = data.data_frame['close']

    panel = pd.DataFrame(data=trading_data)

    return panel

panel = __create_pd_panel([data2]).fillna(method='pad')

# create the strategy
s = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

# create a backtest and run it
test = bt.Backtest(s, panel)
res = bt.run(test)

res.plot()

# ok and what about some stats?
res.display()
