# Settings
# visual setting

BASE_LEVEL_SIZE = 32  # size in pixels of top side of block at z = 0
LAYERS_OFFSET = 1  # only int > 0, difference in pixel between layers top side sprites sizes
# OPTIMAL VALUES: (32, 1) (48, 2) (64, 3)
# (32, 1) looks the best but have freezes

SHADOW_RADIUS = 0.5  # 0 <= x <= 1
SHADOW_STRENGTH = 0.2  # 0 <= x <= 1

HEIGHT_RECOLOR_STRENGTH = 0.3

MAX_FPS = 200
TRAPEZOIDS_IN_CACHE_DURATION = 5  # base value: 1
# if more block sides will be rendered every n frames (cause artefacts if value is big)
# 2: +15% FPS, 3: +30% FPS, 5: +67% FPS, 25: +96% FPS

# gameplay settings

START_PLAYER_STAMINA = 2
END_PLAYER_STAMINA = 10
STAMINA_LEVEL_UP_STEP = 1
START_PLAYER_COOLDOWN = 0.6  # in seconds
END_PLAYER_COOLDOWN = 0.2  # in seconds
COOLDOWN_LEVEL_UP_STEP = 0.05

BLOCK_INTERACTION_COOLDOWN = 2  # in seconds

BLOCKS_PER_MOVE = 2

CAMERA_SPEED = 8  # in blocks per second

# Debug info

TRAPEZOIDS_CACHE_INFO = False
HEIGHT_GENERATING_INFO = False
SET_FPS_CAPTION = False
NOT_ABSTRACT_BLOCKS_CLASSES_INFO = False
FILLING_COLUMNS_INFO = False

# Constants

PATH_TO_BLOCKS = 'sprites/blocks/'
PATH_TO_TILES = 'sprites/tiles/'

PATH_TO_CACHE = 'trapezoids_cache'
CACHE_KEYS_FILENAME = 'keys.pickle'

PATH_TO_SAVES = 'saves/'

SIDES_NAMES = ['left', 'top', 'right', 'bottom']
DIAGONALS_NAMES = ['top_left', 'top_right', 'bottom_left', 'bottom_right']


# Generation constants
PATH_TO_NOISE = 'saves/'

MAX_HEIGHT = 20
HEIGHT_NOISE_TILE_SIZE = 64
HEIGHT_OCTAVES = [0, 2, 3]
START_HEIGHT_AREA = (-2, -2, 4, 4)
WORLD_CHUNK_SIZE = 12

BIOME_NOISE_TILE_SIZE = 64
BIOME_OCTAVES = [0, 1, 2, 3]

TREES_CHUNK_SIZE = 128
TREES_IN_CHUNK = 350
TREE_AVOIDING_RADIUS = 6

TILES_CHUNK_SIZE = 32
TILES_IN_CHUNK = 6
TILE_AVOIDING_RADIUS = 3

WATER_LEVEL = 5
