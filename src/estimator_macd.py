from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import logging

import dataset

import numpy as np
import tensorflow as tf

# add modules to sys path
module_path = os.path.join(os.path.dirname(__file__), "..", "modules")
data_path = os.path.join(os.path.dirname(__file__), "..", "data")
vipdoc_path = os.path.join(os.path.dirname(__file__), "..", "vip", "vipdoc")
feature_path = os.path.join(os.path.dirname(__file__), "..", "feature")

sys.path.append(module_path)
sys.dont_write_bytecode = True

ndays = 5
forecast_days = 5
capacity = ndays + forecast_days
change_delta = 5
changes = 1 + float(change_delta) / 100
labels_count = 3


def to_tensors(results, skip_label_3=True):
    features = []
    labels = []

    loop = len(results)

    for i in range(loop):
        if skip_label_3 and results[i]['label'] == 3:
            continue

        values = []
        for n in range(ndays):
            values.append(results[i]['macd_{}'.format(n)])

        features.append(values)
        labels.append(results[i]['label'] - 1)

    return (features, labels)


def estimate_macd():
    feature_db_name = "macd_features_{}_{}_{}.db".format(ndays, forecast_days, change_delta)

    db = dataset.connect(''.join(["sqlite:///", os.path.join(feature_path, feature_db_name)]))
    result = [row for row in db['features'].all()]
    test_results = [row for row in db['tests'].all()]

    # Specify that all features have real-value data
    feature_columns = [tf.feature_column.numeric_column("x", shape=[ndays])]

    # Build 3 layer DNN with 10, 20, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[10, 20, 10],
                                            n_classes=3,
                                            model_dir="/tmp/iris_model")

    train_data, train_labels = to_tensors(result, False)

    # Define the training inputs
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(train_data)},
        y=np.array(train_labels),
        num_epochs=None,
        shuffle=True)

    # Train model.
    classifier.train(input_fn=train_input_fn, steps=2000000)

    test_data, test_labels = to_tensors(test_results, True)

    # Define the test inputs
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": np.array(test_data)},
      y=np.array(test_labels),
      num_epochs=1,
      shuffle=False)

    # Evaluate accuracy.
    accuracy_score = classifier.evaluate(input_fn=test_input_fn)["accuracy"]

    print("\nTest Accuracy: {0:f}\n".format(accuracy_score))


if __name__ == '__main__':
    estimate_macd()
