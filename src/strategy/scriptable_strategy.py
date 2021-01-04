import logging

from .strategy_base import StrategyBase, SelectWithBuySellData
from stock_data_provider import create_dataframe
from stock_data_provider.utils import get_data_globals

import bt


class ScriptableStrategy(StrategyBase):
    def __init__(self, name, buy_script, sell_script, buy_name='close', sell_name='close'):
        super().__init__(name)
        self.buy_script_ = buy_script
        self.sell_script_ = sell_script
        self.buy_name_ = buy_name
        self.sell_name_ = sell_name
        self.buy_data_ = None
        self.sell_data_ = None

        logging.debug('script for strategy %s: buy:%s, sell:%s, buy on:%s, sell on:%s',
                      self.name_,
                      self.buy_script_,
                      self.sell_script_,
                      self.buy_name_,
                      self.sell_name_)

    def _get_buildin_values(self):
        return {}

    def get_buy_name(self):
        return self.buy_name_

    def get_sell_name(self):
        return self.sell_name_

    def get_sell_data(self, data):
        return create_dataframe(data, self.get_sell_name())

    def get_buy_data(self, data):
        return create_dataframe(data, self.get_buy_name())

    def get_strategy(self, data):
        data_globals = get_data_globals(data)
        data_globals.update(self._get_buildin_values())

        self.buy_data_ = buy_data = eval(self.buy_script_, data_globals)
        self.sell_data_ = sell_data = eval(self.sell_script_, data_globals)

        strategy = bt.Strategy(self.name_,
                               [bt.algos.RunDaily(),
                                SelectWithBuySellData(buy_data, sell_data),
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()])

        return strategy

