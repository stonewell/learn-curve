import os
import sys
import logging
import math

import pandas as pd
import pytz

import bt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Tkagg')

from learn.peak_analyze import PeakAnalyze

sys.dont_write_bytecode = True

do_normalize_data = False


start_date = '20200101'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)

stock_ids = '600369'

p = PeakAnalyze(stock_ids, start_date, end_date, do_normalize_data, prominence=.2)

panel = p.analyze('RSI(C, 4)', 5, 5)

plt.plot(panel[0], 'r', label='peaks')
plt.plot(panel[1], 'g', label='troughs')

plt.show()
