import sys
import argparse
import datetime
import logging
import dateutil.relativedelta
import multiprocessing as mp

import numpy as np

import pyfolio as pf
from pyfolio import timeseries

try:
    from . import module_loader
except:
    import module_loader

try:
    from . import algo_runner
except:
    import algo_runner

sys.dont_write_bytecode = True


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
    parser.add_argument("-s", "--stock_id", help="stock ids to process", action="append", required=True, dest="stock_ids")

    parser.add_argument("--capital_base", help="initial capital base value, default 100000.0",
                        type=float, default=100000.0)
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

def validate_args(args):
    if args.data_range[0] >= args.data_range[1]:
        raise argparse.ArgumentTypeError('invalid data range:{}'.format(args.data_range))

    if args.optimize_range[0] >= args.optimize_range[1]:
        raise argparse.ArgumentTypeError('invalid optimize range:{}'.format(args.optimize_range))

    if (args.optimize_range[0] < args.data_range[0] or
        args.optimize_range[0] >= args.data_range[1] or
        args.optimize_range[1] <= args.data_range[0] or
        args.optimize_range[0] > args.data_range[1]):
        raise argparse.ArgumentTypeError('invalid optimize range:{}, data range:{}'.format(args.optimize_range, args.data_range))

    if (args.optimize_range[1] + args.wfa_size <= args.optimize_range[1]):
        raise argparse.ArgumentTypeError('invalid wfa size:{}'.format(args.wfa_size))

    if (args.optimize_range[1] + args.wfa_size > args.data_range[1]):
        raise argparse.ArgumentTypeError('invalid wfa size:{}'.format(args.wfa_size))


class Analyzer(object):
    def __init__(self, obj_func_module):
        super().__init__()

        self.parameter_ = None
        self.obj_func_module_ = obj_func_module
        self.object_function_accept_ = module_loader.load_module_func(obj_func_module, 'accept')
        self.object_function_better_ = module_loader.load_module_func(obj_func_module, 'better_results')
        self.best_results_ = None

    def analyze(self, result):
        for parameter, results in result:
            if results is None:
                continue
            returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results)

            perf_stats = timeseries.perf_stats(returns,
                                               positions=positions,
                                               transactions=transactions)

            logging.info(perf_stats)
            logging.info("Sharpe Ratio:{}%".format(np.round(perf_stats.loc['Sharpe ratio'] * 100)))

            cur_results = (results, perf_stats)
            if self.object_function_accept_(cur_results) and self.object_function_better_(cur_results, self.best_results_):
                self.best_results_ = cur_results
                self.parameter_ = parameter

def algo_running_worker(args, parameter):
    strategy_module = module_loader.load_module_from_file(args.strategy)
    stock_data_provider = module_loader.load_module_from_file(args.stock_data_provider)

    create_strategy = module_loader.load_module_func(strategy_module, 'create_strategy')
    strategy = create_strategy()

    runner = algo_runner.AlgoRunner(stock_data_provider, args.capital_base, args)
    symbols = args.stock_ids
    start_date = args.optimize_range[0]
    end_date = args.optimize_range[1]

    def tmp_analyze_func(context=None, results=None):
        pass

    strategy.current_parameter = parameter

    logging.info('running strategy:%s', strategy)

    try:
        perf_data = runner.run(strategy,
                               symbols,
                               start_date=start_date,
                               end_date=end_date,
                               analyze_func=tmp_analyze_func)

        return (parameter, perf_data)
    except:
        logging.exception('running strategy:%s failed', strategy)
        return (parameter, None)

def wfa_runner_main():
    args = parse_arguments()

    if args.debug is None:
        args.debug = 0

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))
    logging.debug('stock_ids:{}'.format(args.stock_ids))
    logging.debug('data_range:{}'.format(args.data_range))
    logging.debug('optimize_range:{}'.format(args.optimize_range))
    logging.debug('wfa_size:{}'.format(args.wfa_size))
    logging.debug('wfa range:{}'.format([args.optimize_range[1], args.optimize_range[1] + args.wfa_size]))
    logging.debug('strategy:{}'.format(args.strategy))
    logging.debug('object_function:{}'.format(args.object_function))
    logging.debug('data_provider:{}'.format(args.stock_data_provider))

    validate_args(args)

    strategy_module = module_loader.load_module_from_file(args.strategy)
    object_function_module = module_loader.load_module_from_file(args.object_function)
    stock_data_provider = module_loader.load_module_from_file(args.stock_data_provider)

    create_strategy = module_loader.load_module_func(strategy_module, 'create_strategy')
    strategy = create_strategy()

    analyzer = Analyzer(object_function_module)

    runner = algo_runner.AlgoRunner(stock_data_provider, args.capital_base, args)

    pool = mp.Pool(mp.cpu_count())

    parameter_set = strategy.parameter_set()

    pool.starmap_async(algo_running_worker,
                       list((args, parameter) for parameter in parameter_set),
                       callback=analyzer.analyze,
                       error_callback=lambda x:logging.error('startmap async failed:%s', x))

    pool.close()
    pool.join()

    if analyzer.best_results_ is None:
        logging.error('non parameter of strategy:[%s] is suitable for the stock:%s', strategy, args.stock_ids)
        return

    perf_stats = analyzer.best_results_[1]

    logging.info('Best results:%s', perf_stats)

    strategy.current_parameter = analyzer.parameter_
    logging.info('optimized strategy:%s', strategy)

    # do wfa analyze
    wfa_begin = args.optimize_range[1]
    wfa_end = wfa_begin + args.wfa_size

    while True:
        logging.info('running wfa on out of sample data:%s=>%s', wfa_begin, wfa_end)

        runner.run(strategy,
                   args.stock_ids,
                   start_date=wfa_begin,
                   end_date=wfa_end,
                   analyze_func=None)

        wfa_begin = wfa_end
        wfa_end = wfa_begin + args.wfa_size

        if wfa_begin >= args.data_range[1]:
            break

        if wfa_end > args.data_range[1]:
            wfa_end = args.data_range[1]
        logging.info('next wfa:%s=>%s', wfa_begin, wfa_end)

if __name__ == '__main__':
    wfa_runner_main()
