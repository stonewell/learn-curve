import sys
import os
import logging


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
        'kdj':tr3,
        'rsi':tr4,
        'kama_ma':tr5,
        'ma':tr6
        }

    for n in rules:
        yield (n, rules[n]())

def call_stock_trade_test(user_info, stock_symbol, get_day_data):
    logging.info('Processing:{}'.format(stock_symbol))

    trade_rule, day_begin, day_end = user_info

    try:
        for v in get_day_data(stock_symbol, day_begin, day_end):
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
