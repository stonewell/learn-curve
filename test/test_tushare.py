import tushare as ts

fs = ts.get_k_data('600019', start='2018-01-01', end='2018-04-30')

print fs.tail()

print fs.T[10].date, len(fs.index), fs.keys()

for x in fs.T:
    print x, fs.T[x]
    break
