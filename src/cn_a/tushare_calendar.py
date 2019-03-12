import os
import sys

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

import tushare as ts
from cn_a import tushare_token


def init_trade_calendar():
    pro_api = ts.pro_api(tushare_token)

    trade_cal = pro_api.trade_cal(exchange='', start_date='19990101', end_date='20191231')

    not_open = trade_cal['is_open'] == 0
    trade_date = trade_cal[not_open]['cal_date']

    file_path = os.path.join(os.path.split(__file__)[0], 'tushare_not_trading_date.py')
    with open(file_path, 'w') as of:
        of.write('import pandas as pd\n\n\n')

        of.write('not_trading_date=pd.to_datetime([')
        for cal_date in trade_date:
            of.write('"')
            of.write(cal_date)
            of.write('",\n')

        of.write('])\n')


class CNAExchangeCalendar(TradingCalendar):
    """
    An exchange calendar for trading assets in CN A

    Open Time: 9:30AM, UTC
    Close Time: 15:00PM, UTC
    """

    def __init__(self, tmp_no_trading_date):
        from .tushare_not_trading_date import not_trading_date

        self.tmp_no_trading_date = tmp_no_trading_date
        self.holidays = []
        self.holidays.extend(self.tmp_no_trading_date)
        self.holidays.extend(not_trading_date)

        super().__init__()

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
          weekmask=weekmask,
          holidays=self.holidays
      )

if __name__ == '__main__':
    init_trade_calendar()
