import logging


class StrategyBase(object):
    def __init__(self, name):
        super().__init__()
        self.name_ = name
        self.stock_ids_ = []

    def initialize(self, context, stock_ids):
        self.stock_ids_ = stock_ids
