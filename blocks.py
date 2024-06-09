from abc import ABC, abstractmethod
import pygame as pg
PATH_TO_SPRITES = 'sprites/'
PATH_TO_BLOCKS = 'sprites/blocks/'


class BlockSprite:
    def __init__(self, path):
        self.image = pg.image.load(PATH_TO_BLOCKS+path)


class BlockSpritesDict:
    def __init__(self, top: BlockSprite,
                 bottom: BlockSprite,
                 side1: BlockSprite,
                 side2: BlockSprite,
                 side3: BlockSprite,
                 side4: BlockSprite):
        self.top = top
        self.bottom = bottom
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3
        self.side4 = side4


class Block(ABC):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.top_rect = pg.Rect((1, 1, 1, 1))
        self.bottom_rect = pg.Rect((1, 1, 1, 1))
        self.neighbors = []

    def get_xyz(self):
        return self.x, self.y, self.z

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_bottom_size_in_pixels(self, size: list[int | float]):
        self.bottom_rect.inflate_ip(size)

    def set_top_size_in_pixels(self, size: list[int | float]):
        self.top_rect.inflate_ip(size)

    def set_bottom_topleft(self, top_left: list[int | float]):
        self.bottom_rect.topleft = top_left

    def set_top_topleft(self, top_left: list[int | float]):
        self.top_rect.topleft = top_left

    def set_shade(self):
        pass

    def set_neighbors(self, left: bool, top: bool, right: bool, bottom: bool):
        self.neighbors = [left, top, right, bottom]

    @abstractmethod
    def get_sprites(self) -> list[BlockSprite]:
        pass

    def copy_to_x_y(self, x, y):
        return type(self)(x, y, self.z)


class Air(Block):
    def get_sprites(self) -> list[BlockSprite]:
        return []


class FullBlock(Block):
    debug_sprite = BlockSprite('debug.png')

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.debug_sprite] * 6)

    def get_sprites(self) -> list[BlockSprite]:
        return [self.sprites.top,
                self.sprites.bottom,
                self.sprites.side1,
                self.sprites.side2,
                self.sprites.side3,
                self.sprites.side4]


class SingleSpriteBlock(FullBlock):
    sprite = BlockSprite('debug2.png')

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.sprite] * 6)


class Grass(FullBlock):
    top_sprite = BlockSprite('grass.png')
    side_sprite = BlockSprite('grass_side.png')
    bottom_sprite = BlockSprite('dirt.png')

    @classmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(cls.top_sprite, cls.bottom_sprite, *[cls.side_sprite] * 4)


class Dirt(SingleSpriteBlock):
    sprite = BlockSprite('dirt.png')


class Stone(SingleSpriteBlock):
    sprite = BlockSprite('stone.png')


def test():
    pass


if __name__ == '__main__':
    test()
