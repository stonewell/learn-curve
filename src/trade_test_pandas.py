import sys
import os
import logging

import pandas_datareader.data as web
import pandas as pd
import datetime
import requests_cache

from trade_rules.rule_utils import get_rule, call_stock_trade_test

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")
feature_path = os.path.join(os.path.dirname(__file__), "..", "feature")

sys.path.append(module_path)
sys.dont_write_bytecode = True

from data.day_data import DayData

requests_cache.install_cache("cache")

def get_day_data(stock_symbol, day_begin, day_end):
    f = web.DataReader(stock_symbol, 'morningstar', day_begin, day_end)

    for symbol,date in f.index:
        v = DayData()
        v.stock_id = stock_symbol
        v.amount = f.loc[(symbol, date)].Volume
        v.close_price = f.loc[(symbol, date)].Close
        v.open_price = f.loc[(symbol, date)].Open
        v.highest_price = f.loc[(symbol, date)].High
        v.lowest_price = f.loc[(symbol, date)].Low
        v.date = date

        yield v

def trade_test():
    for n, rule in get_rule():
        print '-------- Evaluate', n
        call_stock_trade_test((rule, '20170101', '20180430'),
                              'SYMC',
                              get_day_data)
        print '----------------------'

if __name__ == '__main__':
    try:
        trade_test()
    except:
        logging.exception('unknown error')
