from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import logging

import dataset

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


def next_batch(results, iterator_count=1, batch_count=None):
    features = []
    labels = []

    loop = batch_count if batch_count else len(results)

    index = 0
    for it in range(iterator_count):
        if index + loop >= len(results):
            index = 0

        for i in range(loop):
            values = []
            for n in range(ndays):
                values.append(results[index + i]['macd_{}'.format(n)])

            features.append(values)
            labels.append([1, 0, 0] if results[index + i]['label'] == 1 else [0, 1, 0] if results[index + i]['label'] == 2 else [0, 0, 1])

        index += loop
        if index >= len(results):
            index = 0

        yield (features, labels)


def to_tensors(results):
    features = []
    labels = []

    loop = len(results)

    for i in range(loop):
        values = []
        for n in range(ndays):
            values.append(results[i]['macd_{}'.format(n)])

        features.append(values)
        labels.append([1, 0, 0] if results[i]['label'] == 1 else [0, 1, 0] if results[i]['label'] == 2 else [0, 0, 1])

    return (features, labels)


def train_model():
    feature_db_name = "macd_features_{}_{}_{}.db".format(ndays, forecast_days, change_delta)

    if not os.path.isdir(feature_path):
        os.makedirs(feature_path)

    db = dataset.connect(''.join(["sqlite:///", os.path.join(feature_path, feature_db_name)]))
    result = [row for row in db['features'].all()]
    test_results = [row for row in db['tests'].all()]

    # Create the model
    x = tf.placeholder(tf.float32, [None, ndays])
    W = tf.Variable(tf.zeros([ndays, labels_count]))
    b = tf.Variable(tf.zeros([labels_count]))
    y = tf.matmul(x, W) + b

    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, labels_count])

    # The raw formulation of cross-entropy,
    #
    #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
    #                                 reduction_indices=[1]))
    #
    # can be numerically unstable.
    #
    # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
    # outputs of 'y', and then average across the batch.
    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits_v2(labels=y_, logits=y))
    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

    sess = tf.InteractiveSession()
    tf.global_variables_initializer().run()

    # Train
    for batch_xs, batch_ys in next_batch(result, 1000, 100):
        sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

    # Test trained model
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    test_x, test_y = to_tensors(test_results)
    print(sess.run(accuracy, feed_dict={x: test_x,
                                        y_: test_y}))


if __name__ == '__main__':
    try:
        train_model()
    except:
        logging.exception('unknown error')
