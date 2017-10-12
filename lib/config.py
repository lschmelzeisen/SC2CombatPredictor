import os

SCREEN_RESOLUTION = 84
MINIMAP_RESOLUTION = 64

REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

MAP_PATH = os.path.join(REPO_DIR, 'CombatGenerator-v1.SC2Map')

REPLAY_DIR = os.path.join(REPO_DIR, 'replays')

REPLAYS_PARSED_DIR = os.path.join(REPO_DIR, 'replays_parsed')
