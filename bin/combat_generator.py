#!/usr/bin/env python3
# Copyright 2017 Lukas Schmelzeisen. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

from absl import app
from pysc2 import run_configs
from s2clientprotocol.sc2api_pb2 import Computer, LocalMap, InterfaceOptions, \
    Participant, PlayerSetup, RequestCreateGame, RequestJoinGame, VeryEasy
from s2clientprotocol.common_pb2 import Random

from lib.config import MAP_PATH, REPLAY_DIR


def main(ununsed_argv):
    run_config = run_configs.get()
    with run_config.start(full_screen=False) as controller:
        print('Starting map "{}"...'.format(MAP_PATH), file=sys.stderr)
        controller.create_game(RequestCreateGame(
            local_map=LocalMap(
                map_path=MAP_PATH,
                map_data=run_config.map_data(MAP_PATH)),
            player_setup=[
                PlayerSetup(type=Computer, race=Random, difficulty=VeryEasy),
                PlayerSetup(type=Computer, race=Random, difficulty=VeryEasy),
                PlayerSetup(type=Participant),
            ],
            realtime=False))

        print('Joining game...', file=sys.stderr)
        controller.join_game(RequestJoinGame(
            race=Random,
            # We just want to save the replay, so no special observations.
            options=InterfaceOptions()))

        print('Stepping through game...', file=sys.stderr)
        print('Remember that you have to manually configure the map settings '
              'ingame for now!', file=sys.stderr)
        obs = controller.observe()
        while not obs.player_result:
            # We just want to save the replay and don't care about observations,
            # so we use a large step_size for speed. But don't make it to large
            # because we need user interaction at the start.
            controller.step(16)
            obs = controller.observe()

        replay_path = os.path.join(REPLAY_DIR, 'SC2CombatGenerator.SC2Replay')
        print('Game completed. Saving replay to "{}".'.format(replay_path),
              file=sys.stderr)
        os.makedirs(REPLAY_DIR, exist_ok=True)
        with open(replay_path, 'wb') as file:
            file.write(controller.save_replay())

        print('Done.', file=sys.stderr)


def entry_point():
    app.run(main)


if __name__ == '__main__':
    app.run(main)
