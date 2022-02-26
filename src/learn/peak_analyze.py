import sys
import logging

from scipy.signal import find_peaks, medfilt, wiener, hilbert

from stock_data_provider import create_dataframe, filter_dataframe
from .indicator_collect import IndicatorCollect

import pandas as pd


try:
    from . import module_loader
except:
    import module_loader

sys.dont_write_bytecode = True

stock_data_provider = module_loader.load_module_from_file('stock_data_provider.cn_a.vip_dataset')
load_data = module_loader.load_module_func(stock_data_provider,
                                           'load_stock_data')

class PeakAnalyze(object):
    def __init__(self, stock_ids,
                 start_date=None, end_date=None,
                 do_normalize_data=False,
                 column='close',
                 **kwargs):
        self.all_loaded_data_ = load_data(stock_ids, do_normalize_data)
        self.stock_ids_ = stock_ids
        self.start_date_ = start_date
        self.end_date_ = end_date
        self.do_normalize_data_ = do_normalize_data

        self.data_ = data = filter_dataframe(create_dataframe(self.all_loaded_data_, column),
                                self.start_date_,
                                self.end_date_)

        if len(data.columns) > 1:
            raise ValueError('must be single stock, but get:%s' % stock_ids)

        values = data[data.columns[0]].values

        params = {
            "prominence":(.618, None),
            "threshold":None,
            "distance":5,
        }

        params.update(kwargs)

        self.peak_index_, _ = find_peaks(values, **params)
        self.trough_index_, _ = find_peaks(-values, **params)


    def analyze(self, indicator_script, back_days, forward_days):
        scripts = indicator_script

        if isinstance(indicator_script, str):
            scripts = [indicator_script]

        data = None

        for s in scripts:
            c = IndicatorCollect(s)

            tmp_data = c.collect(self.all_loaded_data_, self.start_date_, self.end_date_, back_days, forward_days)
            tmp_data = tmp_data.rename(lambda x:s, axis='columns')

            if data is not None:
                data = pd.concat([data, tmp_data], axis=1)
            else:
                data = tmp_data

        data.insert(len(data.columns), 'trade', [0] * len(data))

        data.iloc[self.peak_index_, data.columns.get_loc('trade')] = 100
        data.iloc[self.trough_index_, data.columns.get_loc('trade')] = 50

        return data
