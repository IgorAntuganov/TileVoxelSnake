# Settings
# visual setting

SCREEN_SIZE = 1536, 960  # 1344, 756; 1600, 900; 1536, 960;  800, 450
BASE_LEVEL_SIZE: int = 32  # size in pixels of top side of block at z = 0
LAYERS_OFFSET: float = 1  # difference in pixel between layers top side sprites sizes
MIN_BASE_LEVEL_SIZE = 1
MAX_BASE_LEVEL_SIZE = 64
BASE_LEVEL_STEP = 4
ONE_LEVEL_STEP_BEGINNING = 16
NO_SIDES_LEVEL = 24
REGION_DRAWING_LEVEL = 14


SUN_SIDES_RECOLOR = {
    'west': 1.2,
    'north': 1.05,
    'east': 0.95,
    'south': 0.8
}

# Ambient Occlusion shadows
SHADOW_RADIUS = 0.7  # 0 <= x <= 1
SHADOW_STRENGTH = 0.35  # 0 <= x <= 1

EXPOSED_EDGE_COLOR = (220, 210, 200)
HIDDEN_EDGE_COLOR = (200, 191, 182)
EDGES_ALPHA = 100
EDGE_THICKNESS = 2

HEIGHT_RECOLOR_OFFSET = 3
HEIGHT_RECOLOR_BASE = 1  # base value 1
HEIGHT_RECOLOR_STRENGTH = 0.35  # base value 0.3

MAX_FPS = 200
COLUMN_FIGURES_IN_CACHE_DURATION = 8  # base value: 1 (disabled), optimal: 8
# if more -> block sides will be rendered every n frames
# Cause artefacts if enabled and prefilling frames with black enabled

TRAPEZOID_KEYS_PRECISION = 3  # base value: 1, more -> more accurate trapezoids, more cache

REGIONS_DISTANCE_UPDATE_FREQ = 50
GARBAGE_COLLECTION_FREQ = 500

HOT_COLUMNS_CACHE_CAPACITY = 5000  # base value: 5000. Should be > n of columns on screen

# gameplay settings

START_PLAYER_STAMINA = 2
END_PLAYER_STAMINA = 10
STAMINA_LEVEL_UP_STEP = 1
START_PLAYER_COOLDOWN = 0.6  # in seconds
END_PLAYER_COOLDOWN = 0.2  # in seconds
COOLDOWN_LEVEL_UP_STEP = 0.05

BLOCK_INTERACTION_COOLDOWN = .5  # in seconds

BLOCKS_PER_MOVE = 2

CAMERA_SPEED = 8  # in blocks per second at start base level size

# Debug info

TRAPEZOIDS_CACHE_INFO = False
USE_TRAPEZOID_CACHE_ON_DISK = True
HEIGHT_GENERATING_INFO = False
NOT_ABSTRACT_BLOCKS_CLASSES_INFO = False
FILLING_COLUMNS_INFO = False
PREFILL_FRAME_WITH_BLACK = False
PRINT_3D_MESH_CPROFILE = False
DRAW_TILES = True

# Constants

PATH_TO_BLOCKS = 'sprites/blocks/'
PATH_TO_TILES = 'sprites/tiles/'

PATH_TO_CACHE = 'trapezoids_cache'
CACHE_KEYS_FILENAME = 'keys.pickle'

PATH_TO_SAVES = 'saves/'

SIDES_NAMES = ['west', 'north', 'east', 'south']
DIAGONALS_NAMES = ['north_west', 'north_east', 'south_east', 'south_west']

# Generation constants
PATH_TO_NOISE = 'saves/'

MAX_PRECALCULATED_LAYERS_HEIGHT = 50

MAX_HEIGHT = 20
HEIGHT_NOISE_TILE_SIZE = 64
HEIGHT_OCTAVES = [0, 2, 3]
START_HEIGHT_AREA = (-2, -2, 4, 4)

WORLD_CHUNK_SIZE = 32
LOADED_PARTS_PER_FRAME = 12
DRAW_SIDES_WITH_UNLOADED_REGIONS: bool = False

BIOME_NOISE_TILE_SIZE = 64
BIOME_OCTAVES = [0, 1, 2, 3]

TREES_CHUNK_SIZE = 128
TREES_IN_CHUNK = 450
TREE_AVOIDING_RADIUS = 4

TILES_CHUNK_SIZE = 32
TILES_IN_CHUNK = 6
TILE_AVOIDING_RADIUS = 3

WATER_LEVEL = 5
