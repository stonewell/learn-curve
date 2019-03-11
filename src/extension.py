import pandas as pd

from zipline.data.bundles import register
from cn_a.tushare_bundle import ingest as tushare_ingest
from zipline.utils.calendars import register_calendar

from cn_a.tushare_calendar import CNAExchangeCalendar


start_session = pd.Timestamp('2016-1-4', tz='utc')
end_session = pd.Timestamp('2018-1-2', tz='utc')

register_calendar('CN_A',
                  CNAExchangeCalendar(),
                  True)

register(
    'cn_a_tushare_bundle',
    tushare_ingest,
    calendar_name='CN_A', # CN Shanghai
    start_session=start_session,
    end_session=end_session
)
