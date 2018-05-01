import sys
import os
import logging

import trade_rule

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

import core.nodes.kdj_node
import core.nodes.macd_node
import core.nodes.k_line_node
import core.nodes.osc_node
import core.nodes.basic_node

ndays = 5
forecast_days = 0
capacity = ndays + forecast_days

rsi_days_1 = 12
rsi_days_2 = 72

def create_nodes_rsi_1(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.basic_node.create_rsi_node(nm, from_name, rsi_days_1, capacity).name)

    return node_names

def create_nodes_rsi_2(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.basic_node.create_rsi_node(nm, from_name, rsi_days_2, capacity).name)

    return node_names

specs = [
    create_nodes_rsi_1,
    create_nodes_rsi_2,
]

rsi_col_1 = "Close_RSI_{}".format(rsi_days_1)
rsi_col_2 = "Close_RSI_{}".format(rsi_days_2)

def cross(v1, v2, days):
    for i in range(1, days - 1):
        if (all([v1[j] <= v2[j] for j in range(i)])
            and all([v1[j] > v2[j] for j in range(i, days)])):
            return True

    return False

def in_range(v, begin, end):
    return all([x >=begin and x <=end for x in v])

def build_nodes():
    nm = core.nodes_manager.NodesManager()

    #"PriceNode"
    core.nodes.price_node.create_price_node(nm, capacity)

    nodes_names = []

    for nodes_creator in specs:
        nodes_names.extend(nodes_creator(nm, "Close", capacity))

    nodes_names = list(set(nodes_names))

    return (nm, nodes_names)

class TradeRule(trade_rule.TradeRule):
    def __init__(self):
        super(TradeRule, self).__init__()

        self._last_days = []
        self._max_price = 0
        self._nm, self._node_names = build_nodes()

        self._nodes = self._nm.output_wires[""]

    def on_data(self, data):
        self._last_days.append(data)
        tmp_max = max([x.close_price for x in self._last_days])
        self._max_price = max(tmp_max, self._max_price)

        while len(self._last_days) > ndays:
            del self._last_days[0]

        for node in self._nodes:
            node.data_income("", data)

        super(TradeRule, self).on_data(data)

    def _should_buy(self, data):
        rsi_1 = self._nm.nodes[rsi_col_1].snapshot()
        rsi_2 = self._nm.nodes[rsi_col_2].snapshot()

        if len(rsi_1) < ndays or len(rsi_2) < ndays:
            return False

        if (in_range(rsi_1, 40, 100)
            and in_range(rsi_2, 40, 100)
            and cross(rsi_1, rsi_2, ndays)
        ):
            return True

        return False

    def _should_sell(self, data):
        rsi_1 = self._nm.nodes[rsi_col_1].snapshot()
        rsi_2 = self._nm.nodes[rsi_col_2].snapshot()

        if len(rsi_1) < ndays or len(rsi_2) < ndays:
            return False

        if (in_range(rsi_1, 0, 60)
            and in_range(rsi_2, 0, 60)
            and cross(rsi_2, rsi_1, ndays)
        ):
            return True

        return False

    def _do_sell(self, data):
        super(TradeRule, self)._do_sell(data)
        self._max_price = 0

    def _do_buy(self, data):
        super(TradeRule, self)._do_buy(data)
        self._max_price = 0
