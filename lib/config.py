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

SCREEN_RESOLUTION = 84
MINIMAP_RESOLUTION = 64

REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

MAP_PATH = os.path.join(REPO_DIR, 'CombatGenerator-v1.SC2Map')

REPLAY_DIR = os.path.join(REPO_DIR, 'replays')

REPLAYS_PARSED_DIR = os.path.join(REPO_DIR, 'replays_parsed')
