# SC2CombatPredictor

SC2CombatPredictor is a toolchain that supports

* simulating army engagements in StarCraft II using a custom map, and
* predicting the outcome of army engagements using previous simulations as training data.

## Installation

### Dependencies

Officially, only the latest stable version official version of Python 3 is supported (lower ones may still work).
Installation of the following dependencies is required:

* [abseil](https://github.com/abseil/abseil-py)
* [Keras](https://keras.io/)
* [PySC2](https://github.com/deepmind/pysc2) (make sure to install via git, the pip package is outdated at the moment)
* [s2clientprotocol](https://pypi.python.org/pypi/s2clientprotocol/)

### Protobuf

* Install the latest version of [protoc](https://github.com/google/protobuf/releases) for your system.
* Download the [s2clientprotocol](https://github.com/Blizzard/s2client-proto/tree/master/s2clientprotocol) folder from the [s2client-proto](https://github.com/Blizzard/s2client-proto) repository, and save it in the `./data/` folder of this repository.
* `cd` into the `./data` folder and run: `protoc -I. --python_out=. *.proto`
* This ensure that the Python representation of the protobuf format is compiled. So you will have to rerun this  command whenever you update a `*.proto` file.

## Usage

SC2CombatPredictor currently consists of the StarCraft II custom map *CombatGenerator* and three python programms.

### Combat Generator

*CombatGenerator* is both the name of a StarCraft II custom map and a python program that automatically runs this maps and saves it's simulation as replays.

See the custom map in action:

[![CombatGenerator v1](https://i.imgur.com/n98l1oY.png)](https://youtu.be/bEdV4p0yA8A)

The map lets two random-sized armies (*Team Minerals* and *Team Vespene*) fight against each other repeatedly.
It features

* a chat-based interface for configuration
* multiple army compositions  (currently supports balls of marines, marauders, zealots, stalkers, zerglings, and roaches).
* shuffling of team army compositions and starting regions
* score tracking via the mineral/vespene resources display

For now, army size is chosen uniformly random between 1 and 40 supply, and armies are simply attack-moved into each other.
More complicated engagements including more diverse army compositions, formations, and micro controlling are planned to be implemented in the future.

The indented function of this map is to serve as a simulation ground for StarCraft 2 army engagements of all kinds in order to train machine learning models that can predict the winner based on army compositions, sizes, and formations.

The python program [`combat_generator.py`](https://github.com/lschmelzeisen/SC2CombatPredictor/blob/master/bin/combat_generator.py) can automatically set up a game on this map, step through it, and save it as a replay.
Because [chat interaction in the SC2 API is not implemented yet](https://github.com/Blizzard/s2client-proto/issues/29), as of now, **manual user configuration ingame through chat messages is required after the map is started**.

To run, clone this repository, cd into it, and execute:

```sh
$ python -m bin.combat_generator
```

Replays are currently saved as `./replays/SC2CombatPredictor.SC2Replay` but can be manually renamed.

Note: StarCraft II replays seem to be limited to about 6.5 hours (about 2000 rounds of engagements).
It is therefore probably no use to set the number of rounds per map higher than that.

### Combat Observer

The python program [`combat_observer.py`](https://github.com/lschmelzeisen/SC2CombatPredictor/blob/master/bin/combat_observer.py) analyzes all replays in `./replays/`, and stores initial army observations and engagement outcomes into a parsed replay file in `./replays_parsed/`.

To run, clone this repository, cd into it, make sure there is at least on replay in `./replays/`, and execute:

```sh
$ python -m bin.combat_observer
```

For testing, you may download a replay of [1000 marine vs marine engagements](https://drive.google.com/file/d/0B1wUqkcSl9XUd0ZlVnNFdE5VSkU/view?usp=sharing) (also includes the parsed result for directly learning a model)

### Combat Learner

The python program [`combat_learner.py`](https://github.com/lschmelzeisen/SC2CombatPredictor/blob/master/bin/combat_learner.py) iterates over all parsed replay in `./replays_parsed/` and tries to learn a model that can predict the outcome of army engagements using [Keras](https://keras.io/).

It currently achieves an accuracy of about 96% on simple marine vs marine engagements.

See [tf-keras-tutorial/MNIST CNN](https://github.com/knathanieltucker/tf-keras-tutorial/blob/master/MNISTCNN.ipynb) for the details on the currently used learning architecture (two convolutional layers and two dense layers with dropout).
Currently, the model only uses the screen feature layer `player_relative` as input (that is, unit type is not known to the model).
More complicated architectures are planned for the future.

To run, clone this repository, cd into it, make sure there is at least on parsed replay in `./replays_parsed/`, and execute:

```sh
$ python -m bin.combat_learner
```

You should see output similar to

```plain
Using TensorFlow backend.
Going to learn a model from parsed replay
"<path_to_repo>\replays_parsed\marine_vs_marine_1000.SC2Replay_parsed".
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
conv2d_1 (Conv2D)            (None, 81, 81, 32)        544
_________________________________________________________________
conv2d_2 (Conv2D)            (None, 78, 78, 64)        32832
_________________________________________________________________
max_pooling2d_1 (MaxPooling2 (None, 19, 19, 64)        0
_________________________________________________________________
dropout_1 (Dropout)          (None, 19, 19, 64)        0
_________________________________________________________________
flatten_1 (Flatten)          (None, 23104)             0
_________________________________________________________________
dense_1 (Dense)              (None, 128)               2957440
_________________________________________________________________
dropout_2 (Dropout)          (None, 128)               0
_________________________________________________________________
dense_2 (Dense)              (None, 2)                 258
=================================================================
Total params: 2,991,074
Trainable params: 2,991,074
Non-trainable params: 0
_________________________________________________________________
Train on 800 samples, validate on 100 samples
Epoch 1/10
33s - loss: 0.6200 - acc: 0.6800 - val_loss: 0.4745 - val_acc: 0.8500
Epoch 2/10
33s - loss: 0.4976 - acc: 0.7912 - val_loss: 0.3291 - val_acc: 0.9000
Epoch 3/10
33s - loss: 0.4789 - acc: 0.7762 - val_loss: 0.2670 - val_acc: 0.9100
Epoch 4/10
34s - loss: 0.4131 - acc: 0.8200 - val_loss: 0.2485 - val_acc: 0.9100
Epoch 5/10
31s - loss: 0.3287 - acc: 0.8787 - val_loss: 0.1815 - val_acc: 0.9400
Epoch 6/10
31s - loss: 0.3359 - acc: 0.8512 - val_loss: 0.1610 - val_acc: 0.9700
Epoch 7/10
32s - loss: 0.3009 - acc: 0.8812 - val_loss: 0.1170 - val_acc: 0.9700
Epoch 8/10
31s - loss: 0.2491 - acc: 0.9013 - val_loss: 0.1364 - val_acc: 0.9700
Epoch 9/10
34s - loss: 0.2389 - acc: 0.9012 - val_loss: 0.1140 - val_acc: 0.9700
Epoch 10/10
36s - loss: 0.2073 - acc: 0.9200 - val_loss: 0.1023 - val_acc: 0.9800
 50/100 [==============>...............] - ETA: 0s
100/100 [==============================] - 1s
Loss = 0.12825651839375496
Acc = 0.9599999785423279
Done.
```
