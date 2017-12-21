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

from state.macd_ndays import MacdNDays

capacity = 1

specs = [
]

def read_data(f, nodes, count):
    for i in range(count):
        d = data.data_loader.read_next_day_data(f)

        if (d == None):
            return True

        for node in nodes:
            node.data_income("", d)
        #for i in range(1, count)

    return False

def build_nodes():
    nm = core.nodes_manager.NodesManager()

    #"PriceNode"
    core.nodes.price_node.create_price_node(nm, capacity)

    nodes_names = []

    for nodes_creator in specs:
        nodes_names.extend(nodes_creator(nm, "Close", capacity))

    nodes_names = list(set(nodes_names))

    return (nm, nodes_names)

def call_stock_trade_test(user_info, stock_data_file):
    logging.info('Processing:{}'.format(stock_data_file))

    nm, node_names = build_nodes()

    nodes = nm.output_wires[""]

    trade_rule, day_begin, day_end = user_info

    def __output_line():
        v = nm.nodes['Price'].snapshot()[-1]

        if v.date >= day_begin and v.date <= day_end:
            trade_rule.on_data(v)

    try:
        with open(stock_data_file,'rb') as f:
            done = read_data(f, nodes, capacity)
            __output_line()

            while not done:
                done = read_data(f, nodes, 1)
                __output_line()
            #end while
        #end with

        records, total = trade_rule.final_results()

        if total < 0.20:
            trade_rule.reset()
            return
        print stock_data_file
        for r in records:
            print r
        print total, [x[2] > 0 for x in records].count(True), [x[2] < 0 for x in records].count(True)
        print sum([x[2] if x[2] > 0 else 0 for x in records]), sum([x[2] if x[2] < 0 else 0 for x in records])
        print ""
        print ""
        trade_rule.reset()
    except:
        logging.exception('Error process:{}'.format(stock_data_file))

def trade_test():
    stock_data_looper = StockDataLooper(vipdoc_path)

    if not os.path.isdir(data_path):
        os.makedirs(data_path)

    #from trade_rules.rule_5_days_2_percent_last_day_only import TradeRule
    #from trade_rules.rule_macd_cross import TradeRule
    # from trade_rules.rule_kdj_cross import TradeRule
    # from trade_rules.rule_rsi_cross import TradeRule
    from trade_rules.rule_kama_ma_cross import TradeRule

    if True:
        stock_data_looper.loop_stocks_with_code(call_stock_trade_test,
                                                (TradeRule(), 20170101, 20171231),
                                                [600782])
    else:
        stock_data_looper.loop_hu_shen_300_stocks(call_stock_trade_test,
                                                  (TradeRule(), 20160101, 20161231)
                                                  )


if __name__ == '__main__':
    try:
        trade_test()
    except:
        logging.exception('unknown error')
