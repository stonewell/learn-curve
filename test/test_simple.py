import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib.pyplot as plt

from strategy.rsi_25_75_talib import create_strategy
from strategy.sma import above_sma, long_only_ew

#tickers = 'aapl,msft,c,gs,ge,tsla,fb'
tickers = 'nus'
start_date = '2020-01-01'

sma10 = above_sma(tickers, sma_per=10, name='sma10', start=start_date)
sma20 = above_sma(tickers, sma_per=20, name='sma20', start=start_date)
sma40 = above_sma(tickers, sma_per=40, name='sma40', start=start_date)
benchmark = long_only_ew('spy', name='spy', start=start_date)

data = bt.get(tickers, start=start_date)

# create the strategy
s = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

ss = create_strategy().get_strategy(data)

# create a backtest and run it
test = bt.Backtest(s, data)
test_s = bt.Backtest(ss, data)

res = bt.run(test, test_s, sma10, sma20, sma40, benchmark)

res.plot()
plt.show()

# ok and what about some stats?
res.display()
