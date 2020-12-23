import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib.pyplot as plt

from talib import RSI, MA

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

start_date = '20150101'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)
all_data = panel = __create_pd_panel([data, data1, data2]).fillna(method='pad')

panel = panel[(panel.index >= start_date) & (panel.index <= end_date)]
panel.plot()
plt.show()

# create the strategy
from strategy.rsi_25_75_talib import create_strategy

ss = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

s = create_strategy().get_strategy(all_data)

# create a backtest and run it
test = bt.Backtest(s, panel)
test_s = bt.Backtest(ss, panel)
res = bt.run(test, test_s)

trans = res.get_transactions()

if len(trans) > 0:
    res.plot()
    plt.show()

    res.plot_histogram()
    plt.show()

    print(trans.head(100))

# ok and what about some stats?
res.display()
