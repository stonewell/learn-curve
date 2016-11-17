import sys
import os
import logging

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "Vipdoc")

sys.path.append(module_path)
sys.dont_write_bytecode = True

import tools.svm_nodes_creator
from tools.stock_data_looper import StockDataLooper

import data.data_loader
import core.nodes_manager

specs = [
    tools.svm_nodes_creator.create_nodes_dif_12_26,
    tools.svm_nodes_creator.create_nodes_dea_12_26_9,
]

capacity = 1

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

    def __output_line():
        values = []
        for name in sorted(nm.nodes.keys()):
            if name in node_names:
                values.extend(nm.nodes[name].snapshot()[:capacity])

        print ','.join([str(v) for v in values])

    try:
        with open(stock_data_file,'rb') as f:
            while True:
                done = read_data(f, nodes, capacity)
                __output_line()

                if done:
                    break
            #end while
        #end with
    except:
        logging.exception('Error process:{}'.format(stock_data_file))

def gen_model():
    stock_data_looper = StockDataLooper(vipdoc_path)

    stock_data_looper.loop_stocks_with_code(call_stock_gen_model,
                                                   None,
                                                   [600019])

if __name__ == '__main__':
    try:
        gen_model()
    except:
        logging.exception('unknown error')
