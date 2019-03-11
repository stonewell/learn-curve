# for setting our open and close times
from datetime import time
# for setting our start and end sessions
import pandas as pd
# for setting which days of the week we trade on
from pandas.tseries.offsets import CustomBusinessDay
# for setting our timezone
from pytz import timezone

# for creating and registering our calendar
from trading_calendars import register_calendar, TradingCalendar
from zipline.utils.memoize import lazyval


def init_trade_calendar(output_dir):
    pass


class CNAExchangeCalendar(TradingCalendar):
    """
    An exchange calendar for trading assets in CN A

    Open Time: 9:30AM, UTC
    Close Time: 15:00PM, UTC
    """

    @property
    def name(self):
      """
      The name of the exchange, which Zipline will look for
      when we run our algorithm and pass TFS to
      the --trading-calendar CLI flag.
      """
      return "CN_A"

    @property
    def tz(self):
      """
      The timezone in which we'll be running our algorithm.
      """
      return timezone("Asia/Shanghai")

    open_times = (
        (None, time(9, 31)),
    )
    close_times = (
        (None, time(15, 0)),
    )


    @lazyval
    def day(self):
      """
      The days on which our exchange will be open.
      """
      weekmask = "Mon Tue Wed Thu Fri Sat Sun"
      return CustomBusinessDay(
          weekmask=weekmask
      )
