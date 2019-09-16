import argparse
import datetime
import dateutil.relativedelta

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
        print('debug level:', args.debug)
        print('stock_ids:', args.stock_id)
        print('data_range:', args.data_range)
        print('optimize_range:', args.optimize_range)
        print('wfa_size:', args.wfa_size)
        print('wfa range:', [args.optimize_range[1], args.optimize_range[1] + args.wfa_size])
        print('strategy:', args.strategy)
        print('object_function:', args.object_function)
        print('data_provider:', args.stock_data_provider)
