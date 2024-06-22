from abc import ABC, abstractmethod

import pygame as pg

from constants import SIDES_NAMES, NOT_ABSTRACT_BLOCKS_CLASSES_INFO
from blocksprites import BlockSpritesDict

# Abstract classes: -----------------------------------


class Block(ABC):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def copy_to_x_y(self, x, y):
        return type(self)(x, y, self.z)

    # For creating blocks in Column
    def __call__(self, *args, **kwargs):
        return type(self)(*args, **kwargs)


class FullBlock(Block, ABC):
    debug_sprite = 'debug.png'

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.debug_sprite] * 6)

    def get_top_sprite_resized_shaded(self, size: int,
                                      neighbors: tuple[bool, bool, bool, bool, bool, bool, bool, bool],
                                      z: int) -> pg.Surface:
        return self.sprites.get_top_resized_shaded(size, neighbors, z)

    def get_side_sprite(self, side: str):
        assert side in SIDES_NAMES
        return self.sprites.get_side(SIDES_NAMES.index(side))

    def get_side_sprite_shaded(self, side: str) -> pg.Surface:
        assert side in SIDES_NAMES
        size = self.sprites.side_sprite_sizes
        return self.sprites.get_side_shaded(side, size)


class SingleSpriteBlock(FullBlock, ABC):
    @property
    @abstractmethod
    def sprite(self):
        return 'debug2.png'

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.sprite] * 6)

# Block classes: -----------------------------------


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


class Sand(SingleSpriteBlock):
    sprite = 'sand.png'


class DebugBlock(SingleSpriteBlock):
    sprite = 'debug.png'


# Loading sprites and define blocks_class_dict -------------------

def is_abstract(cls):
    if len(cls.__abstractmethods__) == 0:
        return False  # a concrete implementation of an abstract class
    return True  # an abstract class


checking_classes: list[type] = [Block]
non_abc_classes: list[type] = []
while len(checking_classes) != 0:
    new_checking_classes = []
    for checking_class in checking_classes:
        for child_class in checking_class.__subclasses__():
            if not is_abstract(child_class):
                non_abc_classes.append(child_class)
            new_checking_classes.append(child_class)

    checking_classes = new_checking_classes

if NOT_ABSTRACT_BLOCKS_CLASSES_INFO:
    print('non abstract blocks:')
    for _class in non_abc_classes:
        print(_class.__name__)


blocks_classes_dict = {_class.__name__: _class for _class in non_abc_classes}
reversed_blocks_classes_dict = {_class: _class.__name__ for _class in non_abc_classes}

for _class in blocks_classes_dict.values():
    _class.load_sprites()
