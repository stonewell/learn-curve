import os
import sys
import argparse
import datetime
import logging
import json

import pandas as pd

from learn.peak_analyze import PeakAnalyze

sys.dont_write_bytecode = True


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
                        action="append", required=True, dest="stock_ids")
    parser.add_argument("-e", "--expression", help="expression to evaluate on stock price",
                        action="append", required=True, dest="expressions")
    parser.add_argument("--data_range", help="stock data range", nargs=2, required=True,
                        type=valid_date,
                        metavar=('<begin date>', '<end date>'))
    parser.add_argument("--stock_data_provider", help="data provider for stock data",
                        type=str, metavar='<name>', default='stock_data_provider.cn_a.vip_dataset')
    parser.add_argument('-o', "--output", help="save generated data to the file", required=True,
                        type=argparse.FileType('w', encoding='utf-8'), metavar='<output file>')
    parser.add_argument('-p', "--parameters", help="parameters for peak analysis",
                        type=argparse.FileType('r', encoding='utf-8'), metavar='<parameter file>')
    parser.add_argument('--norm_data', help="nromalize stock data", action="store_true")

    return parser.parse_args()

def validate_args(args):
    if args.data_range[0] >= args.data_range[1]:
        raise argparse.ArgumentTypeError('invalid data range:{}'.format(args.data_range))

def main():
    args = parse_arguments()

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))
    logging.debug('stock_ids:{}'.format(args.stock_ids))
    logging.debug('expressions:{}'.format(args.expressions))
    logging.debug('data_range:{}'.format(args.data_range))
    logging.debug('data_provider:{}'.format(args.stock_data_provider))

    validate_args(args)

    provided_params = {}

    if args.parameters is not None:
        provided_params.update(json.load(args.parameters))

    for stock_id in args.stock_ids:
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

if __name__ == '__main__':
    main()
