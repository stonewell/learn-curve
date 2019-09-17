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

from zipline.api import order, record, symbol, order_target_percent
from zipline.finance import commission, slippage
# Import exponential moving average from talib wrapper
from talib import EMA, MA
import pandas as pd
import numpy as np

symbol_id = None

def initialize(context):
    context.asset = symbol(symbol_id)

    # To keep track of whether we invested in the stock or not
    context.invested = False
    context.portfolio_highest = 0.0
    context.price_highest = 0.0

    # Explicitly set the commission/slippage to the "old" value until we can
    # rebuild example data.
    # github.com/quantopian/zipline/blob/master/tests/resources/
    # rebuild_example_data#L105
    context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
    context.set_slippage(slippage.VolumeShareSlippage())


def handle_data(context, data):
    trailing_window = data.history(context.asset, 'price', 80, '1d')
    if trailing_window.isnull().values.any():
        return
    short_ema = EMA(trailing_window.values, timeperiod=13)
    long_ema = EMA(trailing_window.values, timeperiod=26)

    vv = data.history(context.asset, ['high', 'low'], 5, '1d')

    vv = (vv['high'] - vv['low']).mean()

    vvv = data.history(context.asset, ['high', 'low'], 3, '1d')

    vvv = (vvv['high'] - vvv['low']).mean() * .5

    buy = False
    sell = False

    _long = (short_ema[-1] > long_ema[-1]) and (short_ema[-2] >= long_ema[-2])
    _short = (short_ema[-1] < long_ema[-1]) and (short_ema[-2] <= long_ema[-2])

    pv = data.current(context.asset, "price")

    if context.price_highest < pv:
        context.price_highest = pv - vvv

    trailing_stop = MA(trailing_window.values, timeperiod=3)[-1] < context.price_highest
    _short = _short or (context.portfolio_highest > pv) or trailing_stop

    if _short and context.invested:
        print(context.portfolio_highest, pv, context.price_highest, (context.portfolio_highest > pv), trailing_stop)

    if _long and not context.invested:
        order_target_percent(context.asset, 1)
        context.invested = True
        buy = True
        context.portfolio_highest = data.current(context.asset, "price") - vv
    elif _short and context.invested:
        order_target_percent(context.asset, 0)
        context.invested = False
        sell = True
        context.portfolio_highest = 0.0
        context.price_highest = 0.0
    # elif context.portfolio_highest > 0 and (context.portfolio_highest * 1.1 <= pv) and context.invested:
    #     if context.portfolio.positions[context.asset].amount < 10:
    #         order(context.asset, context.portfolio.positions[context.asset].amount * -1)
    #         context.invested = False
    #     else:
    #         order(context.asset, context.portfolio.positions[context.asset].amount * -0.1)
    #     sell = True
    #     context.portfolio_highest = 0.0

    record(SH600019=data.current(context.asset, "price"),
           short_ema=short_ema[-1],
           long_ema=long_ema[-1],
           buy=buy,
           sell=sell)

# Note: this function can be removed if running
# this algorithm on quantopian.com
def __analyze(context=None, results=None):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    import logbook
    logbook.StderrHandler().push_application()
    log = logbook.Logger('Algorithm')

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('Portfolio value (USD)')

    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('Price (USD)')

    # If data has been record()ed, then plot it.
    # Otherwise, log the fact that no data has been recorded.
    if 'SH600019' in results and 'short_ema' in results and 'long_ema' in results:
        results[['SH600019', 'short_ema', 'long_ema']].plot(ax=ax2)

        ax2.plot(
            results.index[results.buy],
            results.loc[results.buy, 'long_ema'],
            '^',
            markersize=10,
            color='m',
        )
        ax2.plot(
            results.index[results.sell],
            results.loc[results.sell, 'short_ema'],
            'v',
            markersize=10,
            color='k',
        )
        plt.legend(loc=0)
        plt.gcf().set_size_inches(18, 8)
    else:
        msg = '600019.SH, short_ema and long_ema data not captured using record().'
        ax2.annotate(msg, xy=(0.1, 0.5))
        log.info(msg)

    plt.show()


def _test_args():
    """Extra arguments to use when zipline's automated tests run this example.
    """
    import pandas as pd

    return {
        'start': pd.Timestamp('2016-01-04', tz='utc'),
        'end': pd.Timestamp('2018-12-28', tz='utc'),
    }
