import pandas as pd
from talib import RSI
from .feature_base import LearnFeature


class RsiFeature(LearnFeature):
    def __init__(self):
        super().__init__('RsiFeature')
        self.rsi_period_ = 12
        self.rsi_look_back_ = 3
        self.rsi_ = []
        self.buy_rsi_ = None
        self.buy_price_ = 0.0
        self.data_columns_ = ['Rsi_{}'.format(x + 1) for x in range(self.rsi_look_back_)]
        self.data_columns_.insert(0, 'Op')

    def handle_asset_data(self, context, asset, data, is_buy):
        if is_buy:
            trailing_window = data.history(asset, 'price', self.rsi_period_ * 2, '1d')

            self.buy_rsi_ = RSI(trailing_window.values, timeperiod=self.rsi_period_)[-1 * self.rsi_look_back_:]
            self.buy_price_ = data.current(asset, "price")
        elif self.buy_rsi_ is not None:
            row = [data.current(asset, "price") >= self.buy_price_]
            row.extend(self.buy_rsi_)
            self.rsi_.append(row)
            self.buy_rsi_ = None

    def finalize_learning_data(self):
        if len(self.rsi_) == 0:
            return

    def get_learning_data(self):
        return pd.DataFrame(self.rsi_, columns=self.data_columns_)
