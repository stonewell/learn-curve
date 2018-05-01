import sys
import os
import logging

import tushare as ts
import requests_cache

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")
feature_path = os.path.join(os.path.dirname(__file__), "..", "feature")

sys.path.append(module_path)
sys.dont_write_bytecode = True

from data.day_data import DayData

requests_cache.install_cache("cache")


def call_stock_trade_test(user_info, stock_symbol):
    logging.info('Processing:{}'.format(stock_symbol))

    trade_rule, day_begin, day_end = user_info

    try:
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

def get_rule():
    from trade_rules.rule_5_days_2_percent_last_day_only import TradeRule as tr1
    from trade_rules.rule_macd_cross import TradeRule as tr2
    from trade_rules.rule_kdj_cross import TradeRule as tr3
    from trade_rules.rule_rsi_cross import TradeRule as tr4
    from trade_rules.rule_kama_ma_cross import TradeRule as tr5
    from trade_rules.rule_ma_cross import TradeRule as tr6

    rules = {
        '2%':tr1,
        'macd':tr2,
        'kama_ma':tr5,
        'ma':tr6
        }

    for n in rules:
        yield (n, rules[n]())

def trade_test():

    for n, rule in get_rule():
        print '-------- Evaluate', n
        call_stock_trade_test((rule, '2017-11-01', '2018-04-30'),
                          '600019')
        print '----------------------'

if __name__ == '__main__':
    try:
        trade_test()
    except:
        logging.exception('unknown error')
