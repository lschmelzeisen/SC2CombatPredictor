#!/usr/bin/env python3

import os
import sys

import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.layers import Conv2D, Dropout, MaxPooling2D
from absl import app

from lib.config import REPLAYS_PARSED_DIR
from data import simulation_pb2


def main(unused_argv):
    # Set numpy print options so that numpy arrays containing feature layers
    # are printed completely. Useful for debugging.
    np.set_printoptions(threshold=(84 * 84), linewidth=(84 * 2 + 10))

    replay_parsed_files = []
    for root, dir, files in os.walk(REPLAYS_PARSED_DIR):
        for file in files:
            if file.endswith(".SC2Replay_parsed"):
                replay_parsed_files.append(os.path.join(root, file))

    for replay_parsed_file in replay_parsed_files:
        print('Going to learn a model from parsed replay "{}".'
              .format(replay_parsed_file), file=sys.stderr)

        simulation = simulation_pb2.Simulation()
        with open(replay_parsed_file, 'rb') as file:
            simulation.ParseFromString(file.read())

        # Collect input (only use screen_player_relative for now) and output
        # data.
        xs = []
        ys = []
        for battle in simulation.battle:
            obs = battle.initial_observation
            player_relative = obs.feature_layer_data.renders.player_relative

            data = np.frombuffer(player_relative.data, dtype=np.uint8) \
                .reshape((1, player_relative.size.x, player_relative.size.y))

            xs.append(data)
            ys.append(battle.outcome)

        # Convert temporary list to numpy arrays
        xs = np.concatenate(xs)
        ys = np.array(ys)

        # Make train / test split
        xs_train = xs[:-100]
        ys_train = ys[:-100]
        xs_test = xs[-100:]
        ys_test = ys[-100:]

        # Convert labels to one-hot.
        num_classes = 2
        ys_train = keras.utils.to_categorical(ys_train, num_classes=num_classes)
        ys_test = keras.utils.to_categorical(ys_test, num_classes=num_classes)

        # Shape inputs.
        img_rows, img_cols = 84, 84
        xs_train = xs_train.reshape(xs_train.shape[0], img_rows, img_cols, 1)
        xs_test = xs_test.reshape(xs_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

        # Normalize inputs.
        xs_train = xs_train.astype(np.float32) / 4
        xs_test = xs_test.astype(np.float32) / 4

        # Set up model architecture.
        model = Sequential()
        model.add(Conv2D(32, kernel_size=4, activation='relu',
                         input_shape=input_shape))
        model.add(Conv2D(64, kernel_size=4, activation='relu'))
        model.add(MaxPooling2D(pool_size=4))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation='softmax'))

        # Print summary of model architecture and parameters.
        model.summary()

        model.compile(
            loss='categorical_crossentropy',
            optimizer='adadelta',
            metrics=['accuracy'])

        # Fit model to training data.
        model.fit(
            xs_train,
            ys_train,
            epochs=10,
            batch_size=50,
            validation_split=1 / 9,
            verbose=2)

        # Evaluate model on testing data.
        score = model.evaluate(
            xs_test,
            ys_test,
            batch_size=50)
        for metric_name, metric_value in zip(model.metrics_names, score):
            print('{} = {}'.format(metric_name.capitalize(), metric_value))

    print('Done.', file=sys.stderr)


def entry_point():
    app.run(main)


if __name__ == '__main__':
    app.run(main)
