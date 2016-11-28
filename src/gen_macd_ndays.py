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

from rl.rl import ReinforceLearn
from values import Values
from action import DefaultAction
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

    func_update_rl = user_info

    _last_values = None

    def __output_line():
        values = []

        #close price
        values.extend([v.close_price for v in nm.nodes['Price'].snapshot()[:1]])

        #close price change in forecast days
        close_changes = [float(v.close_price) for v in nm.nodes['Price'].snapshot()[1: 1 + forecast_days]]

        high_idx = -1
        high = -1
        low_idx = -1
        low = -1

        for c_index in range(len(close_changes)):
            if high == -1:
                high_idx = c_index
                high = close_changes[c_index]
            elif close_changes[c_index] > high:
                high_idx = c_index
                high = close_changes[c_index]

            if low_idx == -1:
                low_idx = c_index
                low = close_changes[c_index]
            elif close_changes[c_index] < low:
                low_idx = c_index
                low = close_changes[c_index]

        #determin forecast changes
        forecast_changes = 0

        if high_idx == 0 and low_idx > 0:
            forecast_changes = (low - close_changes[0]) / close_changes[0] * 100
        elif high_idx > 0 and low_idx == 0:
            forecast_changes = (high - close_changes[0]) / close_changes[0] * 100
        elif high_idx > 0 and low_idx > 0:
            if high_idx < low_idx:
                forecast_changes = (high - close_changes[0]) / close_changes[0] * 100
            else:
                forecast_changes = (low - close_changes[0]) / close_changes[0] * 100
            
        for name in node_names:
            values.extend(nm.nodes[name].snapshot()[:1])

        rl_values = [float(v) for v in values]

        if _last_values is not None:
            rl_values.extend([
                forecast_changes,
                values[1] - _last_values[1],
                values[2] - _last_values[2]
                ])
        else:
            rl_values.extend([0.0] * len(values))

        logging.error('{}, {}, {}, {}'.format(rl_values, close_changes, (high_idx, high), (low_idx, low)))
        func_update_rl(Values(*rl_values))

        return values

    try:
        with open(stock_data_file,'rb') as f:
            done = read_data(f, nodes, capacity)
            _last_values = __output_line()
            
            while not done:
                done = read_data(f, nodes, 1)
                _last_values = __output_line()
            #end while
        #end with
    except:
        logging.exception('Error process:{}'.format(stock_data_file))

def gen_model():
    stock_data_looper = StockDataLooper(vipdoc_path)

    act = DefaultAction()

    rl_model = ReinforceLearn(MacdNDays(5), act)

    def __update_rl(values):
        state = rl_model.get_state(values)

        if state is None:
            return
        
        #action = rl_model.select_action(state)
        for action in range(act.get_action_count()):
            rl_model.learn(values, state, action)

    if True:
        stock_data_looper.loop_stocks_with_code(call_stock_gen_model,
                                                    __update_rl,
                                                    [600019, 600050])
    else:
        stock_data_looper.loop_hu_shen_300_stocks(call_stock_gen_model,
                                                    __update_rl)

    print rl_model.table

if __name__ == '__main__':
    try:
        gen_model()
    except:
        logging.exception('unknown error')
