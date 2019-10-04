#!/usr/bin/env python
#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Dual Moving Average Crossover algorithm.
This algorithm buys apple once its short moving average crosses
its long moving average (indicating upwards momentum) and sells
its shares once the averages cross again (indicating downwards
momentum).
"""
import logging

from zipline.api import order, order_target_percent
from zipline.api import set_benchmark
from zipline.finance import commission, slippage

from talib import EMA

from .strategy_base import StrategyBase


def create_strategy():
    return DualEmaTaLib()


class DualEmaTaLib(StrategyBase):
    def __init__(self):
        super().__init__()

    def initialize(self, context, stock_ids):
        super().initialize(context, stock_ids)

        context.portfolio_highest = {}
        context.price_highest = {}
        context.stock_shares = {}

        context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(slippage.VolumeShareSlippage())
        set_benchmark(context.assets[0])

        for asset in context.assets:
            context.price_highest[asset] = 0.0
            context.portfolio_highest[asset] = 0.0
            context.stock_shares[asset] = 0

    def handle_single_asset_data(self, context, asset, data):
        trailing_window = data.history(asset, 'price', 80, '1d')

        if trailing_window.isnull().values.any():
            return

        short_ema = EMA(trailing_window.values, timeperiod=13)
        long_ema = EMA(trailing_window.values, timeperiod=26)

        vv = data.history(asset, ['high', 'low'], 5, '1d')

        vv = (vv['high'] - vv['low']).mean()

        vvv = data.history(asset, ['high', 'low'], 3, '1d')

        vvv = (vvv['high'] - vvv['low']).mean() * .5

        _long = (short_ema[-1] > long_ema[-1]) and (short_ema[-2] >= long_ema[-2])
        _short = (short_ema[-1] < long_ema[-1]) and (short_ema[-2] <= long_ema[-2])

        pv = data.current(asset, "price")

        if context.price_highest[asset] < pv:
            context.price_highest[asset] = pv - vvv

        #trailing_stop = MA(trailing_window.values, timeperiod=3)[-1] < context.price_highest[asset]
        #_short = _short or (context.portfolio_highest[asset] > pv) or trailing_stop

        pct_per_stock = 1.0 / len(context.assets)
        cash = context.portfolio.cash * pct_per_stock

        if _long and cash > pv and context.stock_shares[asset] == 0:
            number_of_shares = int(cash / pv)
            order(asset, number_of_shares)
            context.portfolio_highest[asset] = pv - vv
            context.stock_shares[asset] = number_of_shares
            logging.debug('{} buy {} shares at {}'.format(asset, number_of_shares, pv))
        elif _short and context.stock_shares[asset] > 0:
            order_target_percent(asset, 0)
            number_of_shares = context.stock_shares[asset]
            context.portfolio_highest[asset] = 0.0
            context.price_highest[asset] = 0.0
            context.stock_shares[asset] = 0
            logging.debug('{} sell {} shares at {}'.format(asset, number_of_shares, pv))

    # elif context.portfolio_highest > 0 and (context.portfolio_highest * 1.1 <= pv) and context.invested:
    #     if context.portfolio.positions[context.asset].amount < 10:
    #         order(context.asset, context.portfolio.positions[context.asset].amount * -1)
    #         context.invested = False
    #     else:
    #         order(context.asset, context.portfolio.positions[context.asset].amount * -0.1)
    #     sell = True
    #     context.portfolio_highest = 0.0

    #record(SH600019=data.current(asset, "price"),
    #       short_ema=short_ema[-1],
    #       long_ema=long_ema[-1],
    #       buy=buy,
    #       sell=sell)
