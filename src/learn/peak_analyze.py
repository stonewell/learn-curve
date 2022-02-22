import logging

from scipy.signal import find_peaks, medfilt, wiener, hilbert

from stock_data_provider import create_dataframe, filter_dataframe
from .indicator_collect import IndicatorCollect


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

        data = filter_dataframe(create_dataframe(self.all_loaded_data_, column),
                                      self.start_date_,
                                      self.end_date_)

        if len(data.columns) > 1:
            raise ValueError('must be single stock, but get:%s' % stock_id)

        values = data[data.columns[0]].values
        self.peak_index_, _ = find_peaks(values, **kwargs)
        self.trough_index_, _ = find_peaks(-values, **kwargs)


    def analyze(self, indicator_script, back_days, forward_days):
        c = IndicatorCollect(indicator_script)

        return (c.collect(self.all_loaded_data_, back_days, forward_days, self.peak_index_),
                c.collect(self.all_loaded_data_, back_days, forward_days, self.trough_index_))
