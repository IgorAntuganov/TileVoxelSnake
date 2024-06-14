from abc import ABC, abstractmethod
import pygame as pg

from constants import SIDES_NAMES
from blocksprites import BlockSpritesDict


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

    # For creating blocks in Column
    def __call__(self, *args, **kwargs):
        return type(self)(*args, **kwargs)


class FullBlock(Block):
    debug_sprite = 'debug.png'

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.debug_sprite] * 6)

    def get_top_sprite_resized(self, size: int) -> pg.Surface:
        return self.sprites.get_top_resized(size)

    def get_top_sprite_resized_shaded(self, size: int,
                                      neighbors: tuple[bool, bool, bool, bool, bool, bool, bool, bool]) -> pg.Surface:
        return self.sprites.get_top_resized_shaded(size, neighbors)

    def get_side_sprite(self, side: str):
        assert side in SIDES_NAMES
        return self.sprites.get_side(SIDES_NAMES.index(side))

    def get_side_sprite_shaded(self, side: str) -> pg.Surface:
        assert side in SIDES_NAMES
        size = self.sprites.side_sprite_sizes
        return self.sprites.get_side_shaded(side, size)


class SingleSpriteBlock(FullBlock):
    sprite = 'debug2.png'

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.sprite] * 6)

# BLOCKS: -----------------------------------


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
