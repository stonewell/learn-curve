import sys
import os
import logging

import dataset

# add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")
feature_path = os.path.join(os.path.dirname(__file__), "..", "feature")

sys.path.append(module_path)
sys.dont_write_bytecode = True

from tools.stock_data_looper import StockDataLooper

dea_col = "Close_DEA_12_26_9"
dif_col = "Close_DIF_12_26"

ndays = 5
forecast_days = 5
capacity = ndays + forecast_days
change_delta = 5
changes = 1 + float(change_delta) / 100


def call_stock_gen_feature_set(user_info, stock_data_file):
    logging.info('Processing:{}'.format(stock_data_file))

    db_name, ext = os.path.splitext(os.path.basename(stock_data_file))

    db_file_name = os.path.join(data_path, ''.join([db_name, ".db"]))

    if not os.path.isfile(db_file_name):
        logging.error('{} not found.'.format(db_file_name))
        return

    db = dataset.connect(''.join(["sqlite:///", db_file_name]))

    day_begin, day_end, macd_db, gen_feature_set = user_info

    result = db.query('SELECT * FROM days_values WHERE date > {} and date < {}'.format(day_begin, day_end))

    macd = []
    prices = []

    macd_table = macd_db['features'] if gen_feature_set else macd_db['tests']

    features_rows = []
    for row in result:
        if len(macd) == ndays and len(prices) == forecast_days:
            if all([x>=prices[0] for x in prices]) and max(prices) >= prices[0] * changes and max(prices) == prices[-1]:
                features = {}
                features['date'] = macd[0][0]
                for i in range(len(macd)):
                    features['macd_{}'.format(i)] = macd[i][1]
                features['label'] = 1
                features_rows.append(features)
            elif all([x<=prices[0] for x in prices]) and min(prices) * changes <= prices[0] and min(prices) == prices[-1]:
                features = {}
                features['date'] = macd[0][0]
                for i in range(len(macd)):
                    features['macd_{}'.format(i)] = macd[i][1]
                features['label'] = 2
                features_rows.append(features)
            else:
                features = {}
                features['date'] = macd[0][0]
                for i in range(len(macd)):
                    features['macd_{}'.format(i)] = macd[i][1]
                features['label'] = 3
                features_rows.append(features)

        macd.append((row['date'], 2 * (row[dif_col] - row[dea_col])))
        prices.append(row['close'])

        while len(macd) > ndays:
            del macd[0]

        while len(prices) > forecast_days:
            del prices[0]

    macd_table.insert_many(features_rows)


def gen_feature_set():
    stock_data_looper = StockDataLooper(vipdoc_path)

    feature_db_name = "macd_features_{}_{}_{}.db".format(ndays, forecast_days, change_delta)

    if not os.path.isdir(feature_path):
        os.makedirs(feature_path)

    db = dataset.connect(''.join(["sqlite:///", os.path.join(feature_path, feature_db_name)]))
    db['features'].delete()
    db['tests'].delete()

    if False:
        stock_data_looper.loop_stocks_with_code(call_stock_gen_feature_set,
                                                (20160101, 20161231, db, True),
                                                [600019])
        stock_data_looper.loop_stocks_with_code(call_stock_gen_feature_set,
                                                (20170101, 20171231, db, False),
                                                [600019])
    else:
        stock_data_looper.loop_hu_shen_300_stocks(call_stock_gen_feature_set,
                                                  (20160101, 20161231, db, True))
        stock_data_looper.loop_hu_shen_300_stocks(call_stock_gen_feature_set,
                                                  (20167101, 20171231, db, False))


if __name__ == '__main__':
    try:
        gen_feature_set()
    except:
        logging.exception('unknown error')
