# Settings

BASE_LEVEL_SIZE = 32  # size in pixels of top side of block at z = 0
LAYERS_OFFSET = 1  # only int > 0, difference in pixel between layers top side sprites sizes
# OPTIMAL VALUES: (32, 1) (48, 2) (64, 3)
# (32, 1) looks the best but have freezes

SHADOW_RADIUS = 0.5  # 0 <= x <= 1
SHADOW_STRENGTH = 0.2  # 0 <= x <= 1

HEIGHT_RECOLOR_STRENGTH = 0.3

TRAPEZOIDS_CACHE_INFO = False
HEIGHT_GENERATING_INFO = False
SET_FPS_CAPTION = False
PRINT_FPS = False
NOT_ABSTRACT_BLOCKS_CLASSES_INFO = True

# Constants

PATH_TO_SPRITES = 'sprites/'
PATH_TO_BLOCKS = 'sprites/blocks/'

PATH_TO_CACHE = 'trapezoids_cache'
CACHE_KEYS_FILENAME = 'keys.pickle'

PATH_TO_SAVES = 'saves/'

SIDES_NAMES = ['left', 'top', 'right', 'bottom']
DIAGONALS_NAMES = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
