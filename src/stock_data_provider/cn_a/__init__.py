#load stock data from vip data for cn_a
from functools import lru_cache

from . import vip_dataset

@lru_cache(maxsize=42)
def load_stock_data(symbol):
    return vip_dataset.load_stock_data(symbol)
