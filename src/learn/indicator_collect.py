import logging

from stock_data_provider import create_dataframe
from stock_data_provider.utils import get_data_globals


class IndicatorCollect(object):
    def __init__(self, indicator_script):
        self.indicator_script_ = indicator_script

    def _get_buildin_values(self):
        return {}

    def collect(self, all_loaded_data, back_days, forward_days, selected_index = None):
        data_globals = get_data_globals(all_loaded_data)
        data_globals.update(self._get_buildin_values())

        data = eval(self.indicator_script_, data_globals)

        if selected_index:
            data = data.iloc[selected_index]

        return data
