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
from strategy.r3 import create_strategy as r3_create_strategy

#tickers = 'aapl,msft,c,gs,ge,tsla,fb'
tickers = 'AVGO'
start_date = '2017-01-01'

data = bt.get(tickers, start=start_date)
sma = data.rolling(720).mean()

print(sma.tail(5))
