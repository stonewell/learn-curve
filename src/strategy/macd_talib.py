import logging

from zipline.api import order, order_target_percent
from zipline.api import set_benchmark, get_datetime
from zipline.finance import commission, slippage

from talib import MACD, MA, MFI, TRIX

from .strategy_base import StrategyBase


def create_strategy():
    return MacdTaLib()


class MacdTaLib(StrategyBase):
    def __init__(self):
        super().__init__()

        self.short_ema_min_ = 2
        self.long_ema_min_ = 6
        self.short_ema_step_ = 1
        self.long_ema_step_ = 1
        self.ema_max_ = 40

    def initialize(self, context, stock_ids):
        super().initialize(context, stock_ids)

        context.portfolio_highest = {}
        context.price_highest = {}
        context.stock_shares = {}

        context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(slippage.VolumeShareSlippage())
        set_benchmark(context.assets[0])

        for asset in context.assets:
            context.price_highest[asset] = 0.0
            context.portfolio_highest[asset] = 0.0
            context.stock_shares[asset] = 0

    def handle_single_asset_data(self, context, asset, data):
        short_ema_value, long_ema_value, signal_value = self.current_parameter_

        trailing_window = data.history(asset, 'price', long_ema_value * 3, '1d')
        high_trailing_window = data.history(asset, 'high', long_ema_value * 3, '1d')
        low_trailing_window = data.history(asset, 'low', long_ema_value * 3, '1d')
        volume_trailing_window = data.history(asset, 'volume', long_ema_value * 3, '1d')

        if trailing_window.isnull().values.any():
            return

        macd, macd_signal, macd_history = MACD(trailing_window.values,
                                               fastperiod=short_ema_value,
                                               slowperiod=long_ema_value,
                                               signalperiod=signal_value)

        mfi = MFI(high_trailing_window.values,
                  low_trailing_window.values,
                  trailing_window.values,
                  volume_trailing_window.values,
                  timeperiod=14)

        mfi_ma6 = MA(mfi, 6)

        trix = TRIX(trailing_window.values,
                    timeperiod=12)

        trix_ma20 = MA(trix, 20)

        ma10 = MA(trailing_window.values, 10)
        ma5 = MA(trailing_window.values, 5)
        ma2 = MA(trailing_window.values, 2)
        ma40 = MA(trailing_window.values, 40)

        v_ma10 = MA(volume_trailing_window.values, 10)
        v_ma5 = MA(volume_trailing_window.values, 5)

        k, d, j = self.kdj(data, asset, 9)

        _long = (
            True
            #and macd[-1] > 0 and macd_signal[-1] > 0
            #and macd[-2] > 0 and macd_signal[-2] > 0
            and self.lh_cross_n_days(macd[-5:], macd_signal[-5:], 5)
            and macd[-1] > macd_signal[-1] * 1.01
            and trailing_window[-1] > ma2[-1]
            #and macd[-1] > macd_signal[-1] and macd[-2] > macd_signal[-2]
            #and macd[-1] > macd[-2]
            #and macd[-3] < macd_signal[-1] and macd[-4] < macd_signal[-4]
            #and ma5[-1] > ma10[-1] and ma5[-2] > ma10[-2]
            #and mfi[-1] > mfi_ma6[-1] and mfi[-2] > mfi_ma6[-2]
            #and trix[-1] > trix_ma20[-1]
            #and trailing_window.values[-1] > ma10[-1] and trailing_window.values[-2] > ma10[-2]
            and self.lh_cross_n_days(ma5[-5:], ma10[-5:], 5)
            and self.lh_cross_n_days(v_ma5[-5:], v_ma10[-5:], 5)
            and not self.hl_cross_n_days(k[-5:], d[-5:], 5)
            and not all([jj > 100 for jj in j[-3:]])
                 )
        _short = (
            True
            #and macd[-1] < 0 and macd_signal[-1] < 0
            #and macd[-2] < 0 and macd_signal[-2] < 0
            #and ma5[-1] < ma10[-1] and ma5[-2] < ma10[-2]
            #and macd[-1] < macd_signal[-1] and macd[-2] < macd_signal[-2]
            #and macd[-1] < macd[-2]
            and self.hl_cross_n_days(macd[-5:], macd_signal[-5:], 5)
            and macd[-1] < macd_signal[-1] * .99
            #and macd[-3] > macd_signal[-3] and macd[-4] > macd_signal[-4]
            #and mfi[-1] < mfi_ma6[-1] and mfi[-2] < mfi_ma6[-2]
            #and trix[-1] < trix_ma20[-1]
            #and trailing_window.values[-1] < ma10[-1] and trailing_window.values[-2] < ma10[-2]
            and self.hl_cross_n_days(ma5[-5:], ma10[-5:], 5)
        )

        pv = data.current(asset, "price")

        if context.stock_shares[asset] > 0:
            _short_high = context.stock_shares[asset] * pv >= context.portfolio_highest[asset] * 1.2

            _short_low = not _long and (
                False
                # or context.stock_shares[asset] * pv * 1.1 < context.price_highest[asset]
                or trailing_window[-1] < ma40[-1]
            ) \
            and not (context.stock_shares[asset] * pv > context.portfolio_highest[asset])

            if pv > ma5[-1] and ma5[-1] > ma10[-1]:
                #_short_high = False
                #_short_low = False
                pass

            _long = False

            if context.price_highest[asset] < context.stock_shares[asset] * pv:
                context.price_highest[asset] = context.stock_shares[asset] * pv

            if _short_high:
                logging.debug('{} short because protfolio is high'.format(asset))
            if _short_low:
                logging.debug('{} short because protfolio is low'.format(asset))

            _short = _short or _short_high or _short_low

        pct_per_stock = 1.0 / len(context.assets)
        cash = context.portfolio.cash * pct_per_stock

        if _long and cash > pv and context.stock_shares[asset] == 0:
            number_of_shares = int(cash / pv)
            order(asset, number_of_shares)
            context.stock_shares[asset] = number_of_shares
            context.portfolio_highest[asset] = number_of_shares * pv
            context.price_highest[asset] = context.stock_shares[asset] * pv
            logging.debug('{} buy {} shares at {} on:{}, j:{}'.format(asset, number_of_shares, pv, get_datetime(),
                                                                              j.values[-3:]))
        elif _short and context.stock_shares[asset] > 0:
            order_target_percent(asset, 0)
            number_of_shares = context.stock_shares[asset]
            context.portfolio_highest[asset] = 0.0
            context.price_highest[asset] = 0.0
            context.stock_shares[asset] = 0
            logging.debug('{} sell {} shares at {} on:{}'.format(asset, number_of_shares, pv, get_datetime()))

    def parameter_set(self):
        #parameter_set = list((x, y, int((x+y)/4)) \
        #                     for x in range(self.short_ema_min_, self.ema_max_, self.short_ema_step_) \
        #                     for y in range(self.long_ema_min_, self.ema_max_, self.long_ema_step_) \
        #                     if x < y)

        #for value in parameter_set:
        #    yield value
        yield (12, 26, 9)


    def __repr__(self):
        short_ema_value, long_ema_value, signal_value = \
            self.current_parameter_ if self.current_parameter_ is not None else (None, None, None)
        return 'MacdTaLib with short ema:{}, long ema:{}, signal:{}'.format(short_ema_value,
                                                                            long_ema_value, signal_value)
