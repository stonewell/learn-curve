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

from state.macd_ndays import MacdNDays

specs = [
    tools.svm_nodes_creator.create_nodes_dif_12_26,
    tools.svm_nodes_creator.create_nodes_dea_12_26_9,
]

dea_col = "Close_DEA_12_26_9"
dif_col = "Close_DIF_12_26"

ndays = 5
forecast_days = 0
capacity = ndays + forecast_days


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
        difs = self._nm.nodes[dif_col].snapshot()
        deas = self._nm.nodes[dea_col].snapshot()

        if len(difs) < ndays or len(deas) < ndays:
            return False

        for i in range(1, ndays - 1):
            if (all([difs[j] <= deas[j] for j in range(i)])
                and all([difs[j] > deas[j] for j in range(i, ndays)])):
                return True

        return False

    def _should_sell(self, data):
        difs = self._nm.nodes[dif_col].snapshot()
        deas = self._nm.nodes[dea_col].snapshot()

        if len(difs) < ndays or len(deas) < ndays:
            return False

        for i in range(1, ndays - 1):
            if (all([difs[j] >= deas[j] for j in range(i)])
                and all([difs[j] < deas[j] for j in range(i, ndays)])):
                return True

        return False

    def _do_sell(self, data):
        super(TradeRule, self)._do_sell(data)
        self._max_price = 0

    def _do_buy(self, data):
        super(TradeRule, self)._do_buy(data)
        self._max_price = 0
