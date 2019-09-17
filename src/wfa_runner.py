import sys
import argparse
import datetime
import dateutil.relativedelta
import logging
import pandas as pd

sys.dont_write_bytecode = True

try:
    from . import module_loader
except:
    import module_loader

try:
    from . import algo_runner
except:
    import algo_runner


def valid_date(s):
   try:
       return datetime.datetime.strptime(s, "%Y%m%d").date()
   except:
       msg = "Not a valid date: '{0}'.".format(s)
       raise argparse.ArgumentTypeError(msg)

def valid_relative_date(s):
    if s.endswith('y'):
        return dateutil.relativedelta.relativedelta(years=+int(s[:-1]))
    elif s.endswith('m'):
        return dateutil.relativedelta.relativedelta(months=+int(s[:-1]))
    elif s.endswith('d'):
        return dateutil.relativedelta.relativedelta(days=+int(s[:-1]))
    else:
       raise argparse.ArgumentTypeError("Not a valid relative date: '{0}'.".format(s))

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="print debug information", action="count")
    parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0')
    parser.add_argument("-s", "--stock_id", help="stock ids to process", action="append", required=True)

    parser.add_argument("--data_range", help="stock data range", nargs=2, required=True,
                        type=valid_date,
                        metavar=('<begin date>', '<end date>'))
    parser.add_argument("--optimize_range", help="data range using to do optimize", nargs=2, required=True,
                        type=valid_date,
                        metavar=('<begin date>', '<end date>'))
    parser.add_argument("--wfa_size", help="walking forward analysis window size, such as 1y or 6m", required=True,
                        type=valid_relative_date, metavar='<size>')
    parser.add_argument("--strategy", help="trading strategy to evaluate", required=True,
                        type=str, metavar='<name>')
    parser.add_argument("--object_function", help="object function to evaluate trading strategy", required=True,
                        type=str, metavar='<name>')
    parser.add_argument("--stock_data_provider", help="data provider for stock data", required=True,
                        type=str, metavar='<name>')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    if args.debug is None:
        args.debug = 0

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))
    logging.debug('stock_ids:{}'.format(args.stock_id))
    logging.debug('data_range:{}'.format(args.data_range))
    logging.debug('optimize_range:{}'.format(args.optimize_range))
    logging.debug('wfa_size:{}'.format(args.wfa_size))
    logging.debug('wfa range:{}'.format([args.optimize_range[1], args.optimize_range[1] + args.wfa_size]))
    logging.debug('strategy:{}'.format(args.strategy))
    logging.debug('object_function:{}'.format(args.object_function))
    logging.debug('data_provider:{}'.format(args.stock_data_provider))

    strategy = module_loader.load_module_from_file(args.strategy)
    object_function = module_loader.load_module_from_file(args.object_function)
    stock_data_provider = module_loader.load_module_from_file(args.stock_data_provider)

    runner = algo_runner.AlgoRunner(strategy, object_function, stock_data_provider, 100000.0, args)
    runner.run(600019, start_date=pd.to_datetime('2015-01-01', utc=True)
               ,end_date=pd.to_datetime('2017-01-01', utc=True)
    )
