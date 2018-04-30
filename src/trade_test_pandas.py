import sys
import os
import logging

import dataset

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")
feature_path = os.path.join(os.path.dirname(__file__), "..", "feature")

sys.path.append(module_path)
sys.dont_write_bytecode = True

import tools.svm_nodes_creator
from tools.stock_data_looper import StockDataLooper

import data.data_loader
import core.nodes_manager
from data.day_data import DayData

from state.macd_ndays import MacdNDays

import pandas_datareader.data as web
import pandas as pd
import datetime
import requests_cache

requests_cache.install_cache("cache")

capacity = 1

specs = [
]

def call_stock_trade_test(user_info, stock_symbol):
    logging.info('Processing:{}'.format(stock_symbol))

    trade_rule, day_begin, day_end = user_info

    try:
        f = web.DataReader(stock_symbol, 'morningstar', day_begin, day_end)

        for symbol,date in f.index:
            v = DayData()
            v.stock_id = stock_symbol
            v.amount = f.loc[(symbol, date)].Volume
            v.close_price = f.loc[(symbol, date)].Close
            v.open_price = f.loc[(symbol, date)].Open
            v.high_price = f.loc[(symbol, date)].High
            v.low_price = f.loc[(symbol, date)].Low
            v.date = date

            trade_rule.on_data(v)

        records, total = trade_rule.final_results()

        if total < 0.20 and False:
            trade_rule.reset()
            return
        print stock_symbol
        for r in records:
            print r
        print total, [x[2] > 0 for x in records].count(True), [x[2] < 0 for x in records].count(True)
        print sum([x[2] if x[2] > 0 else 0 for x in records]), sum([x[2] if x[2] < 0 else 0 for x in records])
        print ""
        print ""
        trade_rule.reset()
    except:
        logging.exception('Error process:{}'.format(stock_symbol))

def trade_test():
    #from trade_rules.rule_5_days_2_percent_last_day_only import TradeRule
    #from trade_rules.rule_macd_cross import TradeRule
    #from trade_rules.rule_kdj_cross import TradeRule
    #from trade_rules.rule_rsi_cross import TradeRule
    from trade_rules.rule_kama_ma_cross import TradeRule
    #from trade_rules.rule_ma_cross import TradeRule

    call_stock_trade_test((TradeRule(), '20160101', '20180430'),
                          'NFLX')

if __name__ == '__main__':
    try:
        trade_test()
    except:
        logging.exception('unknown error')
