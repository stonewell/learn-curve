import sys
import os
import logging

import tushare as ts
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
    f = ts.get_k_data(stock_symbol, start=day_begin, end=day_end)

    for i in f.T:
        d = f.T[i]
        v = DayData()
        v.stock_id = stock_symbol
        v.amount = d.volume
        v.close_price = d.close
        v.open_price = d.open
        v.highest_price = d.high
        v.lowest_price = d.low
        v.date = d.date

        yield v

def trade_test():

    for n, rule in get_rule():
        print '-------- Evaluate', n
        call_stock_trade_test((rule, '2017-11-01', '2018-04-30'),
                              '600019',
                              get_day_data)
        print '----------------------'

if __name__ == '__main__':
    try:
        trade_test()
    except:
        logging.exception('unknown error')
