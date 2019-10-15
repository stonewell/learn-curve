import logging

from zipline.api import order, order_target_percent
from zipline.api import set_benchmark
from zipline.finance import commission, slippage

from .strategy_base import StrategyBase


def create_strategy(args):
    return Turtle()


class Turtle(StrategyBase):
    def __init__(self):
        super().__init__()

    def initialize(self, context, stock_ids):
        super().initialize(context, stock_ids)

        context.portfolio_highest = {}
        context.price_highest = {}
        context.stock_shares = {}
        context.stock_n = {}

        context.set_commission(commission.PerShare(cost=.0075, min_trade_cost=1.0))
        context.set_slippage(slippage.VolumeShareSlippage())
        set_benchmark(context.assets[0])

        for asset in context.assets:
            context.price_highest[asset] = 0.0
            context.portfolio_highest[asset] = 0.0
            context.stock_shares[asset] = 0
            context.stock_n[asset] = []

    def handle_single_asset_data(self, context, asset, data):
        donchian_days = self.current_parameter_

        trailing_window = data.history(asset, 'price', donchian_days + 1, '1d')
        high_trailing_window = data.history(asset, 'high', donchian_days + 1, '1d')
        low_trailing_window = data.history(asset, 'low', donchian_days + 1, '1d')

        if trailing_window.isnull().values.any():
            return

        donchian_up = high_trailing_window.max()
        donchian_down = low_trailing_window.min()
        donchian_mid = (donchian_up + donchian_down) / 2

        # calculate N
        n = 0.0

        for i in range(donchian_days):
            true_range = max(high_trailing_window[-1 - i] - low_trailing_window[-1 - i],
                             abs(high_trailing_window[-1 - i] - trailing_window[-2 - i]),
                             abs(trailing_window[-2 - i] - low_trailing_window[-1 - i]))

            n += true_range

        n = n / donchian_days

        pct_per_stock = 1.0 / len(context.assets)
        cash = context.portfolio.cash * pct_per_stock
        price = data.current(asset, 'price')

        unit = cash * .01 / n

        logging.debug('stock:{}, n:{}, unit:{}, amount:{}'.format(asset, n, unit, unit / price))

    def parameter_set(self):
        yield (20)

    def __repr__(self):
        donchian_days = self.current_parameter_
        return 'Turtle with donachian days:{}'.format(donchian_days)
