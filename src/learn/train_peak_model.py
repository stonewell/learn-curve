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
                        type=pathlib.Path, metavar='<output file>')
    parser.add_argument('-i', "--input", help="training data directory for peak analysis", required=True,
                        type=pathlib.Path, metavar='<training data directory>')
    parser.add_argument('-t', "--validate_input", help="training validating data directory for peak analysis", required=True,
                        type=pathlib.Path, metavar='<training validating data directory>')

    return parser.parse_args()

def validate_args(args):
    if args.interval <= 0:
        raise argparse.ArgumentTypeError('invalid training interval:{}'.format(args.interval))

    if not args.input.is_dir():
        raise argparse.ArgumentTypeError('invalid training data directory:{}'.format(args.input))

    if not args.validate_input.is_dir():
        raise argparse.ArgumentTypeError('invalid training validation data directory:{}'.format(args.validate_input))

def main():
    args = parse_arguments()

    if args.debug > 0:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))

    validate_args(args)

    features, label = load_features_label(args.input, args)
    v_features, v_label = load_features_label(args.validate_input, args)

    train_model(features, label,
                v_features, v_label,
                args)

def load_features_label(input_dir, args):
    features = []
    label = []

    for training_file in input_dir.iterdir():
        training_data = load_data(training_file, args)

        if len(training_data) < args.interval:
            raise argparse.ArgumentTypeError('too few training data, need at least {}.'.format(args.interval))

        features_, label_ = build_features_and_label(training_data, args)

        features.extend(features_)
        label.extend(label_)

    return features, label

def load_data(training_file, args):
    return pd.read_csv(training_file, index_col=0)

def build_features_and_label(training_data, args):
    features_data = training_data[training_data.columns[:-1]].values.tolist()
    label_data = training_data['trade'].tolist()

    features = []
    label = []
    for index in range(0, len(features_data) - args.interval, 1):
        entries = features_data[index : index + args.interval]

        features.append(entries)

        l = label_data[index + args.interval]

        #if before or after change range label is not 0
        #and current label is 0, use before/after label
        check_range = 1
        if l == 0:
            for t in range(check_range):
                try:
                    l1 = label_data[index + args.interval - t - 1]
                except:
                    l1 = 0

                try:
                    l2 = label_data[index + args.interval + t + 1]
                except:
                    l2 = 0

                l = l1 if l1 != 0 else l2 if l2 != 0 else 0

                if l != 0:
                    break

        label.append(l)

    #one hot encode label
    label_array = np.zeros((len(label), 3), dtype = np.int8)

    for label_index, l in enumerate(label):
        l_index = l if l == 0 else 1 if l == 50 else 2
        label_array[label_index, l_index] = 1

    return features, label_array.tolist()

def train_model(features, label,
                v_features, v_label,
                args):
    train_model_keras_rnn(features, label,
                          v_features, v_label,
                          args)

def train_model_keras_rnn(features, label,
                          v_features, v_label,
                          args):
    from keras.models import Sequential
    from keras.layers import LSTM, Dense, Dropout
    from keras import Input

    model = Sequential()

    model.add(Input(shape=(args.interval, 3)))

    model.add(LSTM(64,
                   return_sequences=False,
                   dropout=0.1,
                   recurrent_dropout=0.1))

    model.add(Dense(64,
                    activation='relu'))

    model.add(Dropout(0.5))

    model.add(Dense(3,
                    activation='softmax'))

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    model.summary()

    from keras.callbacks import EarlyStopping, ModelCheckpoint

    # Create callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5),
        ModelCheckpoint(args.output,
                        save_best_only=True,
                        save_weights_only=False)
    ]

    history = model.fit(features,
                        label,
                        epochs=150,
                        callbacks=callbacks,
                        validation_data=(v_features, v_label))


if __name__ == '__main__':
    main()
