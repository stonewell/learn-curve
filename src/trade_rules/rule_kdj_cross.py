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

ndays = 5
forecast_days = 0
capacity = ndays + forecast_days

kdj_days = 9

def create_nodes_k(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.kdj_node.create_k_node(nm, from_name, kdj_days, capacity).name)

    return node_names

def create_nodes_d(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.kdj_node.create_d_node(nm, from_name, kdj_days, capacity).name)

    return node_names

def create_nodes_j(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.kdj_node.create_j_node(nm, from_name, kdj_days, capacity).name)

    return node_names

specs = [
    create_nodes_k,
    create_nodes_d,
    create_nodes_j
]

k_col = "Close_K_{}".format(kdj_days)
d_col = "Close_D_{}".format(kdj_days)
j_col = "Close_J_{}".format(kdj_days)

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
        k = self._nm.nodes[k_col].snapshot()
        d = self._nm.nodes[d_col].snapshot()
        j = self._nm.nodes[j_col].snapshot()

        if len(k) < ndays or len(d) < ndays or len(j) < ndays:
            return False

        if (in_range(k, 0, 40)
            and in_range(d, 0, 40)
            #and in_range(j, 40, 60)
            and cross(k, d, ndays)
            #and cross(j, d, ndays)
        ):
            return True

        return False

    def _should_sell(self, data):
        k = self._nm.nodes[k_col].snapshot()
        d = self._nm.nodes[d_col].snapshot()
        j = self._nm.nodes[j_col].snapshot()

        if len(k) < ndays or len(d) < ndays or len(j) < ndays:
            return False

        if (in_range(k, 80, 100)
            and in_range(d, 80, 100)
            #and in_range(j, 70, 90)
            and cross(d, k, ndays)
            #and cross(d, j, ndays)
        ):
            return True

        return False

    def _do_sell(self, data):
        super(TradeRule, self)._do_sell(data)
        self._max_price = 0

    def _do_buy(self, data):
        super(TradeRule, self)._do_buy(data)
        self._max_price = 0
