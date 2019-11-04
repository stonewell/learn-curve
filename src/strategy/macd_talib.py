import logging

from zipline.api import order, order_target_percent
from zipline.api import set_benchmark, get_datetime
from zipline.finance import commission, slippage

from talib import MACD, MA

from .strategy_base import StrategyBase


def create_strategy(args):
    return MacdTaLib()


class MacdTaLib(StrategyBase):
    def __init__(self):
        super().__init__('MacdTaLib')

        self.short_ema_min_ = 2
        self.long_ema_min_ = 6
        self.short_ema_step_ = 1
        self.long_ema_step_ = 1
        self.ema_max_ = 40

        self.buy_price_confirm_days_ = 2
        self.buy_price_confirm_ma_days_ = 2

        self.sell_price_confirm_days_ = 2
        self.sell_price_confirm_ma_days_ = 40

    def initialize(self, context, stock_ids):
        super().initialize(context, stock_ids)

        context.portfolio_origin = {}
        context.portfolio_highest = {}
        context.stock_shares = {}

        context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(slippage.VolumeShareSlippage())
        set_benchmark(context.assets[0])

        for asset in context.assets:
            context.portfolio_highest[asset] = 0.0
            context.portfolio_origin[asset] = 0.0
            context.stock_shares[asset] = 0

    def handle_single_asset_data(self, context, asset, data):
        short_ema_value, \
            long_ema_value, \
            signal_value, \
            self.buy_price_confirm_ma_days_, \
            self.buf_price_confirm_days_, \
            self.sell_price_confirm_ma_days_, \
            self.sell_price_confirm_days_ = self.current_parameter_

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

        ma10 = MA(trailing_window.values, 10)
        ma5 = MA(trailing_window.values, 5)
        ma2 = MA(trailing_window.values, self.buy_price_confirm_ma_days_)
        ma40 = MA(trailing_window.values, self.sell_price_confirm_ma_days_)

        v_ma10 = MA(volume_trailing_window.values, 10)
        v_ma5 = MA(volume_trailing_window.values, 5)

        k, d, j = self.kdj(data, asset, 9)

        _long = (
            True
            and self.lh_cross_n_days(macd[-5:], macd_signal[-5:], 5)
            and macd[-1] > macd_signal[-1] * 1.01
            and all(trailing_window[-1 * (i + 1)] > ma2[-1 * (i + 1)] for i in range(self.buy_price_confirm_days_))
            and self.lh_cross_n_days(ma5[-5:], ma10[-5:], 5)
            and self.lh_cross_n_days(v_ma5[-5:], v_ma10[-5:], 5)
            and not self.hl_cross_n_days(k[-5:], d[-5:], 5)
            and not all(jj > 100 for jj in j[-3:])
            and all(x > 0 for x in macd_signal[-3:])
            and (macd_signal[-3] < macd_signal[-2] and macd_signal[-2] < macd_signal[-1])
        )
        _short = (
            True
            and self.hl_cross_n_days(macd[-5:], macd_signal[-5:], 5)
            and macd[-1] < macd_signal[-1] * .99
            and self.hl_cross_n_days(ma5[-5:], ma10[-5:], 5)
        )

        pv = data.current(asset, "price")

        if context.stock_shares[asset] > 0:
            _short_high = context.stock_shares[asset] * pv >= context.portfolio_origin[asset] * 1.15

            _short_low = (
                not _long
                and (
                    False
                    # or context.stock_shares[asset] * pv * 1.1 < context.portfolio_highest[asset]
                    or all(trailing_window[-1 * (i + 1)] < ma40[-1 * (i + 1)]
                           for i in range(self.sell_price_confirm_days_))
                )
            )

            _long = False

            if context.portfolio_highest[asset] < context.stock_shares[asset] * pv:
                context.portfolio_highest[asset] = context.stock_shares[asset] * pv

            if _short_high:
                logging.debug('%s short because protfolio is high', asset)
            if _short_low:
                logging.debug('%s short because protfolio is low', asset)

            _short = _short or _short_high or _short_low

        pct_per_stock = 1.0 / len(context.assets)
        cash = context.portfolio.cash * pct_per_stock

        if _long and cash > pv and context.stock_shares[asset] == 0:
            number_of_shares = int(cash / pv / 100) * 100

            if number_of_shares > 0:
                order(asset, number_of_shares)
                context.stock_shares[asset] = number_of_shares
                context.portfolio_origin[asset] = number_of_shares * pv
                context.portfolio_highest[asset] = context.stock_shares[asset] * pv
                logging.debug('%s buy %s shares at %s on:%s, j:%s',
                              asset, number_of_shares, pv, get_datetime(),
                              j.values[-3:])
                self.update_learn_context(context, asset, data, True)
        elif _short and context.stock_shares[asset] > 0:
            order_target_percent(asset, 0)
            number_of_shares = context.stock_shares[asset]
            context.portfolio_origin[asset] = 0.0
            context.portfolio_highest[asset] = 0.0
            context.stock_shares[asset] = 0
            logging.debug('%s sell %s shares at %s on:%s',
                          asset, number_of_shares, pv, get_datetime())
            self.update_learn_context(context, asset, data, False)

    def parameter_set(self):
        #parameter_set = list((x, y, int((x+y)/4)) \
        #                     for x in range(self.short_ema_min_, self.ema_max_, self.short_ema_step_) \
        #                     for y in range(self.long_ema_min_, self.ema_max_, self.long_ema_step_) \
        #                     if x < y)

        #for value in parameter_set:
        #    yield value

        # x:buy ma, y: buf, z: sell ma, u: sell
        parameter_set = list((x, y, z, u) \
                             for x in range(2, 5 + 1) \
                             for y in range(2, 5 + 1) \
                             for z in range(10, 60 + 1, 5) \
                             for u in range(2, 5 + 1)
                             )

        for x, y, z, u in parameter_set:
            yield (12, 26, 9, x, y, z, u)
        #yield (13, 26, 9, 3, 2, 40, 2)

    def get_default_parameter(self):
        return (13, 26, 9, 3, 2, 40, 2)

    def __repr__(self):
        short_ema_value, long_ema_value, signal_value, x, y, z, u = \
            self.current_parameter_ if self.current_parameter_ is not None else (None, None, None, None, None, None, None)
        return 'MacdTaLib with short ema:{}, long ema:{}, signal:{}, buy confirm_ma:{}, buf confirm:{}, sell confirm ma:{}, sell confirm:{}'.format(short_ema_value,
                                                                                                                                                    long_ema_value, signal_value, x, y, z, u)
