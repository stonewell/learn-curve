import tushare as ts
from cn_a import tushare_token
from numpy import empty
from pandas import DataFrame, Index, Timedelta, NaT
import pandas as pd

from zipline.utils.cli import maybe_show_progress


def ingest(environ,
           asset_db_writer,
           minute_bar_writer,
           daily_bar_writer,
           adjustment_writer,
           calendar,
           start_session,
           end_session,
           cache,
           show_progress,
           output_dir):
    symbols = ['600019.SH']

    pro_api = ts.pro_api(tushare_token)

    dtype = [('start_date', 'datetime64[ns]'),
                 ('end_date', 'datetime64[ns]'),
                 ('auto_close_date', 'datetime64[ns]'),
                 ('symbol', 'object')]
    metadata = DataFrame(empty(len(symbols), dtype=dtype))

    with maybe_show_progress(symbols, show_progress,
                             label='Loading CN A %s pricing data: ' % (symbols)) as it:
        for sid, symbol in enumerate(it):
            tushare_daily = ts.pro_bar(pro_api=pro_api,
                               ts_code=symbol,
                               asset='E',
                               start_date=start_session.strftime('%Y%m%d'),
                               end_date=end_session.strftime('%Y%m%d'),
                               adj='qfq')

            tushare_daily['day'] = pd.to_datetime(tushare_daily['trade_date'])
            tushare_daily['volume'] = tushare_daily['vol']
            tushare_daily['id'] = tushare_daily['ts_code']

            tushare_daily = tushare_daily.filter(items=['day', 'open', 'high', 'low', 'close', 'volume'])
            tushare_daily = tushare_daily.set_index('day').sort_index()

            start_date = tushare_daily.index[0]
            end_date = tushare_daily.index[-1]

            end_date = start_date if start_date > end_date else end_date

            # The auto_close date is the day after the last trade.
            ac_date = end_date + Timedelta(days=1)
            metadata.iloc[sid] = start_date, end_date, ac_date, symbol

            daily_bar_writer.write([(sid, tushare_daily)], show_progress=show_progress)

    metadata['exchange'] = 'SSE'
    asset_db_writer.write(equities=metadata)
    adjustment_writer.write(None)
