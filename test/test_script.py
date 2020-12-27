import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, medfilt, wiener, hilbert

import talib

try:
    from . import module_loader
except:
    import module_loader

sys.dont_write_bytecode = True

stock_data_provider = module_loader.load_module_from_file('stock_data_provider.cn_a.vip_dataset')
load_data = module_loader.load_module_func(stock_data_provider,
                                                 'load_stock_data')
data = load_data('600369')
data2 = load_data('600732')

print(data.data_frame.head())

def __create_pd_panel(all_data, name='close'):
    trading_data = {}
    for data in all_data:
        trading_data[data.stock_id] = data.data_frame[name]

    panel = pd.DataFrame(data=trading_data)

    return panel

p = __create_pd_panel([data])

print(p.head())

def __generate_data_globals(all_data):
    data_globals = {
        'C' : __create_pd_panel(all_data, 'close').fillna(method='pad'),
        'O' : __create_pd_panel(all_data, 'open').fillna(method='pad'),
        'H' : __create_pd_panel(all_data, 'high').fillna(method='pad'),
        'L' : __create_pd_panel(all_data, 'low').fillna(method='pad'),
        'V' : __create_pd_panel(all_data, 'volume').fillna(method='pad'),
    }

    return data_globals

data_globals = __generate_data_globals([data, data2])
print(data_globals)

def make_func(func):
    def wrapper(data, days):
        return data.apply(lambda v: func(v, days))

    return wrapper

def ref(data, ref_days):
    return data.shift(-ref_days)

data_globals['MA'] = make_func(talib.MA)
data_globals['RSI'] = make_func(talib.RSI)
data_globals['Ref'] = ref

#script = '(C>MA(C,200)) & (C<MA(C,5)) & (H<Ref(H,-1)) & (L<Ref(L,-1)) & (Ref(H,-1)<Ref(H,-2)) & (Ref(L,-1)<Ref(L,-2)) & (Ref(H,-2)<Ref(H,-3)) & (Ref(L,-2)<Ref(L,-3))'
script = '(C>MA(C, 200)) & (RSI(C, 4) < 25)'

v = eval(script, data_globals)
print(v.head())
print(v[(v['600369'] == True) | (v['600732'] == True)].dropna())
