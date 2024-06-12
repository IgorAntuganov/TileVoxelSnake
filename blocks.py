from abc import ABC, abstractmethod
import pygame as pg
PATH_TO_SPRITES = 'sprites/'
PATH_TO_BLOCKS = 'sprites/blocks/'

SIDES = ['left', 'top', 'right', 'bottom']


class BlockSprite:
    def __init__(self, path, angle=0):
        self.image = pg.image.load(PATH_TO_BLOCKS+path).convert()
        self.image = pg.transform.rotate(self.image, angle)


class BlockSpritesDict:
    def __init__(self, top: str,
                 bottom: str,
                 side1: str,
                 side2: str,
                 side3: str,
                 side4: str):
        self.scale_cache = {}
        self._top = BlockSprite(top)
        self._bottom = BlockSprite(bottom)
        self._side1 = BlockSprite(side1, 90)
        self._side2 = BlockSprite(side2)
        self._side3 = BlockSprite(side3, 90)
        self._side4 = BlockSprite(side4)
        self._sides = [self._side1, self._side2, self._side3, self._side4]

    def get_top_resized(self, size) -> pg.Surface:
        key = f'top{size}'
        if key not in self.scale_cache:
            image = pg.transform.scale(self._top.image, (size, size))
            self.scale_cache[key] = image
        return self.scale_cache[key]

    def get_top_resized_shaded(self, size, neighbors) -> pg.Surface:
        pass

    def get_side(self, n) -> pg.Surface:
        return self._sides[n].image


class Block(ABC):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_xyz(self):
        return self.x, self.y, self.z

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def copy_to_x_y(self, x, y):
        return type(self)(x, y, self.z)


class FullBlock(Block):
    debug_sprite = 'debug.png'

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.debug_sprite] * 6)

    def get_top_sprite_resized(self, size: int) -> pg.Surface:
        return self.sprites.get_top_resized(size)

    def get_side_sprite(self, side: str):
        assert side in SIDES
        return self.sprites.get_side(SIDES.index(side))


class SingleSpriteBlock(FullBlock):
    sprite = 'debug2.png'

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.sprite] * 6)


class Grass(FullBlock):
    top_sprite = 'grass.png'
    side_sprite = 'grass_side.png'
    bottom_sprite = 'dirt.png'

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(cls.top_sprite, cls.bottom_sprite, *[cls.side_sprite] * 4)


class Dirt(SingleSpriteBlock):
    sprite = 'dirt.png'


class Stone(SingleSpriteBlock):
    sprite = 'stone.png'


class DebugBlock(SingleSpriteBlock):
    sprite = 'debug.png'


load_list = [Grass, Dirt, Stone, DebugBlock]
for c in load_list:
    c.load_sprites()
