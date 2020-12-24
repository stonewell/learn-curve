import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, medfilt, wiener, hilbert

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

start_date = '20200101'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)

all_data = panel = __create_pd_panel([data]).fillna(method='pad')
bench_data = __create_pd_panel([bench_data]).fillna(method='pad')

panel = panel[(panel.index >= start_date) & (panel.index <= end_date)]
bench_data = bench_data[(bench_data.index >= start_date) & (bench_data.index <= end_date)]

panel.plot()

for col in panel.columns:
    c1=panel[col]
    peaks, _ = find_peaks(c1.values, height = -3, threshold = None, distance=5)
    c1.iloc[peaks].plot(style='ro', label='peaks')

    peaks, _ = find_peaks(-c1.values, threshold = None, distance=5)
    c1.iloc[peaks].plot(style='go', label='troughs')

plt.show()
