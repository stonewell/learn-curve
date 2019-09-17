import os

import tushare as ts
import pandas as pd
from . import tushare_token


def load_adjfactor(symbol, data_path):
    adj_file = os.path.join(data_path, symbol, 'adj.txt')

    if os.path.exists(adj_file):
        return load_adjfactor_from_file(adj_file)

    pro_api = ts.pro_api(tushare_token)

    data_set = pro_api.adj_factor(ts_code=symbol,
                                  trade_date='')

    if not os.path.exists(os.path.dirname(adj_file)):
        os.makedirs(os.path.normpath(os.path.dirname(adj_file)), exist_ok=True)

    with open(adj_file, 'w') as f:
        for index, v in data_set.iterrows():
            f.write('{},{}\n'.format(v['trade_date'], v['adj_factor']))
        # end for
    # end with

    return load_adjfactor_from_file(adj_file)


def load_adjfactor_from_file(adj_file):
    values = {}

    with open(adj_file, 'r') as f:
        for line in f:
            parts = line.strip('\n').split(',')
            values[pd.to_datetime(parts[0])] = float(parts[1])
        # end for
    # end with

    return values
