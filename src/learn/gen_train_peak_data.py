import os
import sys
import argparse
import datetime
import logging
import json
import pathlib
import multiprocessing as mp

import pandas as pd

from learn.peak_analyze import PeakAnalyze
module_path = os.path.join(os.path.dirname(__file__), "..", "..", "modules")

sys.path.append(module_path)

from stock_data_provider.cn_a.baostock_indexstock_query import load_all_indexes

sys.dont_write_bytecode = True

data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")

builtin_stock_id_groups = load_all_indexes(data_path)

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y%m%d").date()
    except:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="print debug information", action="count", default=0)
    parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0')
    parser.add_argument("-s", "--stock_id", help="stock ids to process",
                        action="append", required=False, dest="stock_ids")
    parser.add_argument("-sl", "--stock_id_list", help="file contains stock ids to process",
                        type=pathlib.Path, required=False, metavar='<stock id list>')
    parser.add_argument("-sg", "--stock_id_group", help="build in stock ids group to process",
                        type=str, required=False, metavar='<stock id group>',
                        choices=builtin_stock_id_groups.keys())
    parser.add_argument("-e", "--expression", help="expression to evaluate on stock price",
                        action="append", required=True, dest="expressions")
    parser.add_argument("--data_range", help="stock data range", nargs=2, required=True,
                        type=valid_date,
                        metavar=('<begin date>', '<end date>'))
    parser.add_argument("--stock_data_provider", help="data provider for stock data",
                        type=str, metavar='<name>', default='stock_data_provider.cn_a.vip_dataset')
    parser.add_argument('-o', "--output", help="save generated data to the directory using stock id as file name", required=True,
                        type=pathlib.Path, metavar='<output directory>')
    parser.add_argument('-p', "--parameters", help="parameters for peak analysis",
                        type=argparse.FileType('r', encoding='utf-8'), metavar='<parameter file>')
    parser.add_argument('--norm_data', help="nromalize stock data", action="store_true")
    parser.add_argument("--no_pool", help="do not run with pool",
                        action='store_true')

    return parser.parse_args()

def validate_args(args, stock_ids):
    if args.data_range[0] >= args.data_range[1]:
        raise argparse.ArgumentTypeError('invalid data range:{}'.format(args.data_range))

    if ((args.stock_ids is None or len(args.stock_ids) == 0)
        and args.stock_id_list is None
        and args.stock_id_group is None):
        raise argparse.ArgumentTypeError('missing stock ids')

    if stock_ids is None or (len(stock_ids) == 0):
        raise argparse.ArgumentTypeError('missing stock ids')

def main():
    args = parse_arguments()

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    stock_ids = load_stock_ids(args)

    logging.debug('debug level:{}'.format(args.debug))
    logging.debug('stock_ids:{}'.format(stock_ids))
    logging.debug('expressions:{}'.format(args.expressions))
    logging.debug('data_range:{}'.format(args.data_range))
    logging.debug('data_provider:{}'.format(args.stock_data_provider))

    validate_args(args, stock_ids)

    provided_params = {}

    if args.parameters is not None:
        provided_params.update(json.load(args.parameters))

    args.output.mkdir(parents=True, exist_ok=True)

    if args.no_pool:
      for stock_id in stock_ids:
        __run_single_stock(stock_id, provided_params, args)
    else:
      pool = mp.Pool(mp.cpu_count())

      pool.starmap_async(__run_single_stock,
                         list((stock_id, provided_params, args) for stock_id in stock_ids),
                         error_callback=lambda x:logging.error('starmap async failed:%s', x))

      pool.close()
      pool.join()

def __run_single_stock(stock_id, provided_params, args):
        params_ = {}

        #load default params
        try:
            params_.update(provided_params['default'])
        except:
            pass
        #load params for stock
        try:
            params_.update(provided_params[stock_id])
        except:
            pass

        p = PeakAnalyze(stock_id,
                        args.data_range[0],
                        args.data_range[1],
                        args.norm_data,
                        **params_)
        panel = p.analyze(args.expressions, 5, 5)

        print(panel)

        panel.to_csv(args.output / '{}.txt'.format(stock_id), index=True)

def load_stock_ids(args):
    stock_ids = []

    if args.stock_ids is not None:
        stock_ids.extend(args.stock_ids)

    if args.stock_id_list is not None:
        with args.stock_id_list.open as f:
            stock_ids.append(f.readline().replace('\r', '').replace('\n',''))

    if args.stock_id_group is not None:
        stock_ids.extend(builtin_stock_id_groups[args.stock_id_group].keys())

    return stock_ids

if __name__ == '__main__':
    mp.set_start_method('forkserver')

    main()
