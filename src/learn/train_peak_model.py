import os
import sys
import argparse
import datetime
import logging
import json
import pathlib

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
    parser.add_argument("-n", "--interval", type=int, help='days interval for training', default=5)
    parser.add_argument('-o', "--output", help="save generated model to the file", required=True,
                        type=argparse.FileType('w', encoding='utf-8'), metavar='<output file>')
    parser.add_argument('-i', "--input", help="training data directory for peak analysis", required=True,
                        type=pathlib.Path, metavar='<training data directory>')

    return parser.parse_args()

def validate_args(args):
    if args.interval <= 0:
        raise argparse.ArgumentTypeError('invalid training interval:{}'.format(args.interval))

def main():
    args = parse_arguments()

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))

    validate_args(args)

    features = []
    label = []

    for training_file in args.input.iterdir():
        training_data = load_data(training_file, args)

        print(training_data)

        if len(training_data) < args.interval:
            raise argparse.ArgumentTypeError('too few training data, need at least {}.'.format(args.interval))

        features_, label_ = build_features_and_label(training_data, args)

        features.extend(features_)
        label.extend(label_)

    train_model(features, label, args)

def load_data(training_file, args):
    return pd.read_csv(training_file)

def build_features_and_label(training_data, args):
    return [], []

def train_model(features, label, args):
    pass

if __name__ == '__main__':
    main()
