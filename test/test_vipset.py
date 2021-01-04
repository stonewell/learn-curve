import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib.pyplot as plt

from talib import RSI, MA
from stock_data_provider import create_dataframe, filter_dataframe

try:
    from . import module_loader
except:
    import module_loader

sys.dont_write_bytecode = True

stock_data_provider = module_loader.load_module_from_file('stock_data_provider.cn_a.vip_dataset')
load_data = module_loader.load_module_func(stock_data_provider,
                                                 'load_stock_data')

do_normalize_data = False

all_loaded_data = load_data('600369,600999,600732,601066', do_normalize_data)
#all_loaded_data = load_data('600019,600050,600030,600584,600036,600406', do_normalize_data)
#all_loaded_data = load_data('600019,600050,600584', do_normalize_data)
#all_loaded_data = load_data('600519,000858,601318,600036,603288,600276,600900,600887', do_normalize_data)

bench_data = load_data('sh000001', do_normalize_data)

start_date = '20200701'
end_date = '20201231'

print(start_date, end_date)

all_data = panel = create_dataframe(all_loaded_data, 'close')
bench_data = create_dataframe(bench_data, 'close')

panel = filter_dataframe(panel, start_date, end_date)
bench_data = filter_dataframe(bench_data, start_date, end_date)

bt.merge(panel).plot()
plt.show()

# create the strategy
from strategy.rsi_25_75_talib import create_strategy
from strategy.r3 import create_strategy as r3_create_strategy
from strategy.sma import above_sma, long_only_ew
from strategy.macd_talib import create_strategy as macd_create_strategy
from strategy.ibs import create_strategy as ibs_create_strategy
from strategy.ibs_rsi import create_strategy as ibs_rsi_create_strategy

ss = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

s = create_strategy().get_strategy(all_loaded_data)

r3_s = r3_create_strategy().get_strategy(all_loaded_data)
macd_s = macd_create_strategy().get_strategy(all_loaded_data)
ibs_s = ibs_create_strategy().get_strategy(all_loaded_data)
ibs_rsi_s = ibs_rsi_create_strategy().get_strategy(all_loaded_data)

# create a backtest and run it
test = bt.Backtest(s, panel)
test_s = bt.Backtest(ss, panel)
test_r3_s = bt.Backtest(r3_s, panel)
test_macd_s = bt.Backtest(macd_s, panel)
test_ibs_s = bt.Backtest(ibs_s, panel)
test_ibs_rsi_s = bt.Backtest(ibs_rsi_s, panel)

sma10 = above_sma(data=panel, sma_per=10, name='sma10', start=start_date)
sma20 = above_sma(data=panel, sma_per=20, name='sma20', start=start_date)
sma40 = above_sma(data=panel, sma_per=40, name='sma40', start=start_date)
benchmark = long_only_ew(data=bench_data, name='sh000001', start=start_date)
long_only = long_only_ew(data=panel, name='bench', start=start_date)

res = bt.run(test, test_s, sma10, sma20, sma40, benchmark, test_r3_s, test_macd_s, test_ibs_s, test_ibs_rsi_s)
#res = bt.run(test_ibs_s, test, test_r3_s, test_macd_s, test_ibs_rsi_s, long_only)

trans = res.get_transactions()

if len(trans) > 0:
    res.plot()
    plt.show()

    res.plot_histogram()
    plt.show()

    print(trans.to_string())

# ok and what about some stats?
res.display()
