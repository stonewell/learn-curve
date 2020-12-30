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

data = load_data('600369')
data1 = load_data('600999')
data2 = load_data('600732')
bench_data = load_data('000001')

def __create_pd_panel(all_data):
    trading_data = {}
    for data in all_data:
        trading_data[data.stock_id] = data.data_frame['close']

    panel = pd.DataFrame(data=trading_data)

    return panel

start_date = '20201001'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)

all_loaded_data = [data, data1, data2]

all_data = panel = __create_pd_panel(all_loaded_data).fillna(method='pad')
bench_data = __create_pd_panel([bench_data]).fillna(method='pad')

panel = panel[(panel.index >= start_date) & (panel.index <= end_date)]
bench_data = bench_data[(bench_data.index >= start_date) & (bench_data.index <= end_date)]

bt.merge(panel, bench_data).plot()
plt.show()

# create the strategy
from strategy.rsi_25_75_talib import create_strategy
from strategy.r3 import create_strategy as r3_create_strategy
from strategy.sma import above_sma, long_only_ew

ss = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

s = create_strategy().get_strategy(all_loaded_data)

r3_s = r3_create_strategy().get_strategy(all_loaded_data)

# create a backtest and run it
test = bt.Backtest(s, panel)
test_s = bt.Backtest(ss, panel)
test_r3_s = bt.Backtest(r3_s, panel)

sma10 = above_sma(data=panel, sma_per=10, name='sma10', start=start_date)
sma20 = above_sma(data=panel, sma_per=20, name='sma20', start=start_date)
sma40 = above_sma(data=panel, sma_per=40, name='sma40', start=start_date)
benchmark = long_only_ew(data=bench_data, name='spy', start=start_date)

res = bt.run(test, test_s, sma10, sma20, sma40, benchmark, test_r3_s)
#res = bt.run(sma10)

trans = res.get_transactions()

if len(trans) > 0:
    res.plot()
    plt.show()

    res.plot_histogram()
    plt.show()

    print(trans.to_string())

# ok and what about some stats?
res.display()
