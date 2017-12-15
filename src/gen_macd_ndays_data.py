import sys
import os
import logging

import dataset

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")

sys.path.append(module_path)
sys.dont_write_bytecode = True

import tools.svm_nodes_creator
from tools.stock_data_looper import StockDataLooper

import data.data_loader
import core.nodes_manager

from state.macd_ndays import MacdNDays

specs = [
    tools.svm_nodes_creator.create_nodes_dif_12_26,
    tools.svm_nodes_creator.create_nodes_dea_12_26_9,
]

ndays = 5
forecast_days = 5
capacity = ndays + forecast_days

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

def call_stock_gen_model(user_info, stock_data_file):
    logging.info('Processing:{}'.format(stock_data_file))

    nm, node_names = build_nodes()

    nodes = nm.output_wires[""]

    db_name, ext = os.path.splitext(os.path.basename(stock_data_file))

    db = dataset.connect(''.join(["sqlite:///", db_name, ".db"]))
    table = db['days_values']

    cells = []
    def __output_line():
        v = nm.nodes['Price'].snapshot()[-1]

        cell = dict(date=v.date,
                          open=v.open_price,
                          close=v.close_price,
                          high=v.highest_price,
                          low=v.lowest_price,
                          amount=v.amount,
                          vol=v.vol)
        for name in node_names:
            cell[name]= nm.nodes[name].snapshot()[-1]

        cells.append(cell)

    try:
        with open(stock_data_file,'rb') as f:
            done = read_data(f, nodes, capacity)
            __output_line()

            while not done:
                done = read_data(f, nodes, 1)
                __output_line()
            #end while
        #end with
        table.insert_many(cells)
    except:
        logging.exception('Error process:{}'.format(stock_data_file))

def gen_model():
    stock_data_looper = StockDataLooper(vipdoc_path)

    def __update_rl(values):
        pass

    if True:
        stock_data_looper.loop_stocks_with_code(call_stock_gen_model,
                                                    __update_rl,
                                                    [600050])
    else:
        stock_data_looper.loop_hu_shen_300_stocks(call_stock_gen_model,
                                                    __update_rl)


if __name__ == '__main__':
    try:
        gen_model()
    except:
        logging.exception('unknown error')
