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

do_normalize_data = True


start_date = '20200101'
end_date = '20201231'

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

print(start_date, end_date)

stock_ids = '600369'

p = PeakAnalyze(stock_ids, start_date, end_date, do_normalize_data, prominence=.1)

panel = p.analyze(['RSI(C, 4)', 'RSI(V, 9)', 'MACDHist(C, 12, 26, 9)'], 5, 5)

print(p.peak_index_)

#d = panel[[panel.columns[0], panel.columns[1]]]
d = panel[panel.columns[:-1]]
print(panel)

plt.plot(d[panel['trade']==100], 'ro', label='peaks')
plt.plot(d[panel['trade']==50], 'go', label='troughs')
plt.plot(d)

plt.show()
