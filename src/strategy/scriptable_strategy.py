import logging
from functools import lru_cache, cache

import talib

from cachetools import Cache, keys, cached

from .strategy_base import StrategyBase, SelectWithBuySellData

import pandas as pd
import pytz
import bt
import numpy as np

local_cache = Cache(maxsize=42)

def hash_key_for_2(data1, *args):
    return keys.hashkey(id(data1), *args)

def MACDHist(*args):
    _, _, macd_hist = talib.MACD(*args)

    return macd_hist

class ScriptableStrategy(StrategyBase):
    def __init__(self, name, buy_script, sell_script, buy_name='close', sell_name='close'):
        super().__init__(name)
        self.buy_script_ = buy_script
        self.sell_script_ = sell_script
        self.buy_name_ = buy_name
        self.sell_name_ = sell_name

        logging.debug('script for strategy %s: buy:%s, sell:%s, buy on:%s, sell on:%s',
                      self.name_,
                      self.buy_script_,
                      self.sell_script_,
                      self.buy_name_,
                      self.sell_name_)

    def _get_buildin_values(self):
        return {}

    @staticmethod
    @cached(cache=local_cache, key=hash_key_for_2)
    def __ref(data, ref_days):
        return data.shift(-ref_days)

    @staticmethod
    def __make_func(func):
        @cached(cache=local_cache, key=hash_key_for_2)
        def wrapper(data, *args):
            return data.apply(lambda v: func(v, *args))

        return wrapper

    def get_buy_name(self):
        return self.buy_name_

    def get_sell_name(self):
        return self.sell_name_

    @staticmethod
    @cached(cache=local_cache, key=hash_key_for_2)
    def __create_dataframe(all_data, name='close'):
        trading_data = {}
        for data in all_data:
            trading_data[data.stock_id] = data.data_frame[name]

        panel = pd.DataFrame(data=trading_data)

        return panel.fillna(method='pad')

    def get_sell_data(self, data):
        return self.__create_dataframe(data, self.get_sell_name())

    def get_buy_data(self, data):
        return __create_dataframe(data, self.get_buy_name())

    def get_strategy(self, data):
        data_globals = {
            'C' : self.__create_dataframe(data, 'close'),
            'O' : self.__create_dataframe(data, 'open'),
            'H' : self.__create_dataframe(data, 'high'),
            'L' : self.__create_dataframe(data, 'low'),
            'V' : self.__create_dataframe(data, 'volume'),
        }

        data_globals['MA'] = self.__make_func(talib.MA)
        data_globals['MACDHist'] = self.__make_func(MACDHist)
        data_globals['RSI'] = self.__make_func(talib.RSI)
        data_globals['REF'] = self.__ref

        data_globals.update(self._get_buildin_values())

        buy_data = eval(self.buy_script_, data_globals)
        sell_data = eval(self.sell_script_, data_globals)

        strategy = bt.Strategy(self.name_,
                               [bt.algos.RunDaily(),
                                SelectWithBuySellData(buy_data, sell_data),
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()])

        return strategy

