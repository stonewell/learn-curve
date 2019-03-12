import logging

import pandas as pd

from zipline.data.bundles import register
from cn_a.tushare_bundle import ingest as tushare_ingest
from zipline.utils.calendars import register_calendar

from cn_a.tushare_calendar import CNAExchangeCalendar


start_session = pd.Timestamp('2016-1-4', tz='utc')
end_session = pd.Timestamp('2018-12-28', tz='utc')

tmp_no_trading_date = [pd.Timestamp('2016-06-27 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-06-28 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-06-29 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-06-30 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-01 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-04 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-05 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-06 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-07 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-08 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-11 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-12 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-13 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-14 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-15 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-18 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-19 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-20 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-21 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-22 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-25 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-26 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-27 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-28 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-07-29 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-01 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-02 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-03 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-04 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-05 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-08 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-09 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-10 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-11 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-12 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-15 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-16 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-17 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-18 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-19 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-22 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-23 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-24 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-25 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-26 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-29 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-30 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-08-31 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-01 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-02 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-05 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-06 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-07 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-08 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-09 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-12 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-13 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-14 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-19 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-20 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-21 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-22 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-23 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-26 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-27 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-28 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-29 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-09-30 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-12-01 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-12-02 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-12-05 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-12-06 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2016-12-07 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-01-24 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-01-25 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-01-26 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-03 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-06 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-07 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-08 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-09 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-10 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-13 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-14 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-15 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-16 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-17 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-20 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-21 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-22 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-23 00:00:00+0000', tz='UTC'),
                       pd.Timestamp('2017-02-24 00:00:00+0000', tz='UTC')]

try:
    register_calendar('CN_A',
                  CNAExchangeCalendar(tmp_no_trading_date),
                  True)
except:
    logging.exception('failed register calendar')
    raise

register(
    'cn_a_tushare_bundle',
    tushare_ingest,
    calendar_name='CN_A', # CN Shanghai
    start_session=start_session,
    end_session=end_session
)
