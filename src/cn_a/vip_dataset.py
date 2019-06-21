import sys
import os
import logging

#add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "..", "modules")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "..",  "..", "vip", "vipdoc")
data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")

sys.path.append(module_path)
sys.dont_write_bytecode = True

import data.data_loader
from tools.stock_data_looper import StockDataLooper

import pandas as pd
import datetime
import numpy


class VipDataSet(object):
    def __init__(self, stock_id):
        self.err = False
        self.stock_id = stock_id
        self.data_frame = pd.DataFrame(columns=['day', 'open', 'high', 'low', 'close', 'volume'])
        self.data_frame.set_index('day')
        self.holidays = None

def process_stock_file(userinfo, stock_data_file):
    data_frame = pd.DataFrame(columns=['day', 'open', 'high', 'low', 'close', 'volume'])
    stock_id = os.path.splitext(os.path.basename(stock_data_file))[0]

    logging.info('processing {}, id:{}'.format(stock_data_file, stock_id))

    try:
        with open(stock_data_file,'rb') as f:
            trading_date = []
            while True:
                d = data.data_loader.read_next_day_data(f)

                if d == None:
                    break
                day = pd.to_datetime(d.date, format='%Y%m%d')
                data_frame = data_frame.append({'day':day,
                                   'open':d.open_price,
                                   'high':d.highest_price,
                                   'low':d.lowest_price,
                                   'close':d.close_price,
                                   'volume':d.vol},
                                  True)
                trading_date.append(day)
            #end while
            data_frame = data_frame.set_index('day').sort_index()

            userinfo.data_frame = data_frame
            userinfo.err = False
            dr = pd.date_range(start=trading_date[0], end=trading_date[-1])
            userinfo.holidays = list(map(pd.to_datetime, numpy.setdiff1d(dr, pd.DatetimeIndex(trading_date))))
        #end with
    except:
        userinfo.err = True
        logging.exception('Error process:{}'.format(stock_data_file))


def normalize_data(data_frame):
    pass

def load_stock_data(symbol):
    stock_data_looper = StockDataLooper(vipdoc_path)

    data = VipDataSet(symbol)
    stock_data_looper.loop_stocks_with_code(process_stock_file,
                                            data,
                                            [symbol])

    if data.err:
        raise ValueError()
    normalize_data(data.data_frame)

    return data

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    data = load_stock_data(600019)

    logging.debug('vip data:\n{}'.format(data.data_frame.head()))
    logging.debug('vip data holidays:\n{}'.format(data.holidays[:10]))
