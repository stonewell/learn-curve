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
import core.nodes.kama_node

kama_days = 2
ma_days = 5

def create_nodes_ma(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.basic_node.create_ma_node(nm, from_name, ma_days, capacity).name)

    return node_names

def create_nodes_kama(nm, from_name, capacity):
    node_names = []
    node_names.append(core.nodes.kama_node.create_kama_node(nm, from_name, kama_days, capacity).name)

    return node_names

specs = [
    create_nodes_kama,
    create_nodes_ma,
]

kama_col = "Close_KAMA_{}".format(kama_days)
ma_col = "Close_MA_{}".format(ma_days)

ndays = 5
forecast_days = 0
capacity = ndays + forecast_days


def cross(v1, v2, days):
    for i in range(1, days - 1):
        if (all([v1[j] <= v2[j] for j in range(i)])
            and all([v1[j] > v2[j] for j in range(i, days)])):
            return True

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
        kamas = self._nm.nodes[kama_col].snapshot()
        mas = self._nm.nodes[ma_col].snapshot()

        if len(kamas) < ndays or len(mas) < ndays:
            return False

        if cross(kamas, mas, ndays):
            return True

        return False

    def _should_sell(self, data):
        kamas = self._nm.nodes[kama_col].snapshot()
        mas = self._nm.nodes[ma_col].snapshot()

        if len(kamas) < ndays or len(mas) < ndays:
            return False

        if cross(mas, kamas, ndays):
            return True

        return False

    def _do_sell(self, data):
        super(TradeRule, self)._do_sell(data)
        self._max_price = 0

    def _do_buy(self, data):
        super(TradeRule, self)._do_buy(data)
        self._max_price = 0
