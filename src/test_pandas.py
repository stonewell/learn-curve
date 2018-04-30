import pandas_datareader.data as web
import pandas as pd
import datetime
import requests_cache

requests_cache.install_cache("cache")
start = datetime.datetime(2016, 1, 1)

end = datetime.datetime.now()

f = web.DataReader("SYMC", 'morningstar', start, end)

dates = pd.date_range('20160101', periods=100)
print f.shape
print f["Close"][-1], f.keys(), dir(f)
print f.Close['SYMC'].keys()
print f.tail()
print f.iloc[0]

symbol,date = f.index[100]
print date, f.loc[(symbol, date)].Close
