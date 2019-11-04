import pandas as pd
from talib import MACD
from .feature_base import LearnFeature


class MacdFeature(LearnFeature):
    def __init__(self):
        super().__init__('MacdFeature')
        self.macd_long_period_ = 26
        self.macd_short_period_ = 13
        self.macd_signal_period_ = 9

        self.macd_look_back_ = 3
        self.macd_ = []
        self.buy_macd_ = None
        self.buy_price_ = 0.0
        self.data_columns_ = ['Macd_{}'.format(x + 1) for x in range(self.macd_look_back_)]
        self.data_columns_.insert(0, 'Op')

    def handle_asset_data(self, context, asset, data, is_buy):
        if is_buy:
            trailing_window = data.history(asset, 'price', self.macd_long_period_ * 3, '1d')

            _, macd_signal, _ = MACD(trailing_window.values,
                                  fastperiod=self.macd_short_period_,
                                  slowperiod=self.macd_long_period_,
                                  signalperiod=self.macd_signal_period_)
            self.buy_macd_ = macd_signal[-1 * self.macd_look_back_:]

            self.buy_price_ = data.current(asset, "price")
        elif self.buy_macd_ is not None:
            row = [1 if data.current(asset, "price") >= self.buy_price_ else 0]
            row.extend(self.buy_macd_)
            self.macd_.append(row)
            self.buy_macd_ = None

    def finalize_learning_data(self):
        if len(self.macd_) == 0:
            return

    def get_learning_data(self):
        return pd.DataFrame(self.macd_, columns=self.data_columns_)
