from abc import ABC, abstractmethod

import pygame as pg

from constants import SIDES_NAMES, NOT_ABSTRACT_BLOCKS_CLASSES_INFO
from blocksprites import BlockSpritesDict
from height_difference import HeightDiff9

# Abstract classes: -----------------------------------


class Block(ABC):
    debug_sprite = 'debug.png'

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_xyz(self) -> tuple[int, int, int]:
        return self.x, self.y, self.z

    @property
    @abstractmethod
    def is_transparent(self) -> bool:
        pass

    def copy_to_x_y(self, x, y):
        return type(self)(x, y, self.z)

    # For creating blocks in Column
    def __call__(self, *args, **kwargs):
        return type(self)(*args, **kwargs)

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(cls.__name__, *[cls.debug_sprite] * 6)

    def get_top_sprite_resized_shaded(self, size: tuple[int, int],
                                      height_diff: HeightDiff9,
                                      z: int) -> pg.Surface:
        return self.sprites.get_top_resized_shaded(size, height_diff, z)

    def get_top_sprite_fully_shaded(self, size: tuple[int, int], z: int):
        return self.sprites.get_top_resized_fully_shaded(size, z)

    def get_side_sprite(self, side: str, height_diff: HeightDiff9, ind_from_top: int) -> tuple[pg.Surface, str]:
        """:param ind_from_top: 0 if side of first/top block of column, 1 if second, etc."""
        assert side in SIDES_NAMES
        return self.sprites.get_side(side, height_diff, ind_from_top)


class FullBlock(Block, ABC):
    debug_sprite = 'debug.png'

    @property
    def is_transparent(self) -> bool:
        return False


class SingleSpriteBlock(FullBlock, ABC):
    @property
    @abstractmethod
    def sprite(self) -> str:
        pass

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(cls.__name__, *[cls.sprite] * 6)


class SingleSideSpriteBlock(FullBlock, ABC):
    @property
    @abstractmethod
    def top_sprite(self) -> str:
        pass

    @property
    @abstractmethod
    def side_sprite(self) -> str:
        pass

    @property
    @abstractmethod
    def bottom_sprite(self) -> str:
        pass

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(cls.__name__, cls.top_sprite, cls.bottom_sprite, *[cls.side_sprite] * 4)


# Block classes: -----------------------------------

class Grass(SingleSideSpriteBlock):
    top_sprite = 'grass.png'
    side_sprite = 'grass_side.png'
    bottom_sprite = 'dirt.png'


class ForestGrass(SingleSideSpriteBlock):
    top_sprite = 'forest_grass1.png'
    side_sprite = 'podzol_side.png'
    bottom_sprite = 'dirt.png'


class OakLog(SingleSideSpriteBlock):
    top_sprite = bottom_sprite = 'oak_log_top.png'
    side_sprite = 'oak_log_side.png'


class Leaves(SingleSpriteBlock):
    sprite = 'leaves.png'

    @property
    def is_transparent(self) -> bool:
        return True


class Shadow(SingleSpriteBlock):
    sprite = 'air.png'

    @property
    def is_transparent(self) -> bool:
        return True

    def get_side_sprite(self, side: str, height_diff: HeightDiff9, ind_from_top: int) -> tuple[pg.Surface, str]:
        assert side in SIDES_NAMES
        return self.sprites.get_side(side, height_diff, -10000000000)

    def get_top_sprite_resized_shaded(self, size: tuple[int, int],
                                      neighbors: tuple[bool, bool, bool, bool, bool, bool, bool, bool],
                                      z: int) -> pg.Surface:
        return self.sprites.get_top_resized(size, z)


class Water(SingleSpriteBlock):
    sprite = 'water.png'

    @property
    def is_transparent(self) -> bool:
        return True


class Glass(SingleSpriteBlock):
    sprite = 'glass.png'

    @property
    def is_transparent(self) -> bool:
        return True


class Dirt(SingleSpriteBlock):
    sprite = 'dirt.png'


class Stone(SingleSpriteBlock):
    sprite = 'stone.png'


class Sand(SingleSpriteBlock):
    sprite = 'sand.png'


class DebugBlock(SingleSpriteBlock):
    sprite = 'debug.png'


class TransparentDebugBlock(SingleSpriteBlock):
    sprite = 'debug.png'

    @property
    def is_transparent(self) -> bool:
        return True


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


blocks_classes_dict = {_class.__name__: _class for _class in non_abc_classes}
reversed_blocks_classes_dict = {_class: _class.__name__ for _class in non_abc_classes}

if NOT_ABSTRACT_BLOCKS_CLASSES_INFO:
    print('non abstract blocks:')
    for _class in non_abc_classes:
        print(_class.__name__)

    print(blocks_classes_dict)
    print(reversed_blocks_classes_dict)


for _class in blocks_classes_dict.values():
    _class.load_sprites()
