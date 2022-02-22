import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Tkagg')

from scipy.signal import find_peaks, medfilt, wiener, hilbert

from talib import RSI, MA

try:
    from . import module_loader
except:
    import module_loader

from stock_data_provider import create_dataframe, filter_dataframe

sys.dont_write_bytecode = True

stock_data_provider = module_loader.load_module_from_file('stock_data_provider.cn_a.vip_dataset')
load_data = module_loader.load_module_func(stock_data_provider,
                                                 'load_stock_data')

do_normalize_data = False

data = load_data('600369', do_normalize_data)
data1 = load_data('600999', do_normalize_data)
data2 = load_data('600732', do_normalize_data)
bench_data = load_data('000001', do_normalize_data)

start_date = '20200101'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)

all_data = panel = create_dataframe(data2, 'close')
bench_data = create_dataframe(bench_data, 'close')

panel = filter_dataframe(panel, start_date, end_date)
bench_data = filter_dataframe(bench_data, start_date, end_date)

panel.plot()

params = {
    "prominence":(.618, None),
    "threshold":None,
    "distance":5,
    }

for col in panel.columns:
    c1=panel[col]
    peaks, _ = find_peaks(c1.values, **params )
    c1.iloc[peaks].plot(style='ro', label='peaks')

    peaks, _ = find_peaks(-c1.values, **params)
    c1.iloc[peaks].plot(style='go', label='troughs')

plt.show()
