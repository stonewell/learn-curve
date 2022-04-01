import os
import sys
import argparse
import datetime
import logging
import json
import pathlib

import pandas as pd
import numpy as np

from learn.peak_analyze import PeakAnalyze

sys.dont_write_bytecode = True


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", help="print debug information", action="count", default=0)
    parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0')
    parser.add_argument("-n", "--interval", type=int, help='days interval for training', default=5)
    parser.add_argument('-i', "--input", help="training data directory for peak analysis", required=True,
                        type=pathlib.Path, metavar='<training data directory>')
    parser.add_argument('-r', "--rule", help="rules for columns, <column index> <min> <max>, using given min max value to validate columns",
                        action='append',
                        nargs=3,
                        required=True,
                        dest='rules',
                        type=float,
                        metavar='value')

    return parser.parse_args()

def validate_args(args):
    if args.interval <= 0:
        raise argparse.ArgumentTypeError('invalid training interval:{}'.format(args.interval))

    if not args.input.is_dir():
        raise argparse.ArgumentTypeError('invalid training data directory:{}'.format(args.input))

    if len(args.rules) >= 0:
        for rule in args.rules:
            try:
                col = int(rule[0])

                if col < 1:
                    raise argparse.ArgumentTypeError('invalid rule, column index is not valid:{}'.format(rule))

                if rule[1] > rule[2]:
                    raise argparse.ArgumentTypeError('invalid rule, min should not great than max:{}'.format(rule))
            except argparse.ArgumentTypeError:
                raise
            except:
                logging.exception('fail')
                raise argparse.ArgumentTypeError('invalid rule:{}'.format(rule))


def main():
    args = parse_arguments()

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))

    validate_args(args)

    load_features_label(args.input, args)

def load_features_label(input_dir, args):
    invalid_files = []

    for training_file in input_dir.iterdir():
        training_data = load_data(training_file, args)

        if len(training_data) < args.interval:
            logging.error('{} too few training data, need at least {}.'.format(training_file, args.interval))
            invalid_files.append(training_file)
            continue

        for rule in args.rules:
            col = int(rule[0])
            min = rule[1]
            max = rule[2]

            logging.info('checking column:{}'.format(training_data.columns[col]))
            if any([x < min or x > max for x in training_data[training_data.columns[col]]]):
                logging.error('colume {} value not in range: {}, {} for file:{}'.format(col, min, max, training_file))
                invalid_files.append(training_file)
                break

    return invalid_files

def load_data(training_file, args):
    return pd.read_csv(training_file, index_col=0)


if __name__ == '__main__':
    main()
