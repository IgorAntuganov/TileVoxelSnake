from abc import ABC, abstractmethod
import pygame as pg
PATH_TO_SPRITES = 'sprites/'
PATH_TO_BLOCKS = 'sprites/blocks/'

SIDES = ['left', 'top', 'right', 'bottom']

class BlockSprite:
    def __init__(self, path):
        self.image = pg.image.load(PATH_TO_BLOCKS+path).convert()


class BlockSpritesDict:
    def __init__(self, top: BlockSprite,
                 bottom: BlockSprite,
                 side1: BlockSprite,
                 side2: BlockSprite,
                 side3: BlockSprite,
                 side4: BlockSprite):
        self.scale_cache = {}
        self._top = top
        self._bottom = bottom
        self._side1 = side1
        self._side2 = side2
        self._side3 = side3
        self._side4 = side4
        self._sides = [side1, side2, side3, side4]

    def get_top_resized(self, size) -> pg.Surface:
        key = f'top{size}'
        if key not in self.scale_cache:
            image = pg.transform.scale(self._top.image, (size, size))
            self.scale_cache[key] = image
        return self.scale_cache[key]

    def get_side(self, n) -> pg.Surface:
        return self._sides[n].image

    def get_side_resized(self, n, size) -> pg.Surface:
        pass


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

    '''def set_bottom_size_in_pixels(self, size: list[int | float]):
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
        self.neighbors = [left, top, right, bottom]'''

    def copy_to_x_y(self, x, y):
        return type(self)(x, y, self.z)


class FullBlock(Block):
    debug_sprite = BlockSprite('debug.png')

    @classmethod
    @abstractmethod
    def load_sprites(cls):
        cls.sprites = BlockSpritesDict(*[cls.debug_sprite] * 6)

    def get_top_sprite_resized(self, size: int) -> pg.Surface:
        return self.sprites.get_top_resized(size)

    def get_side_sprite_resized(self, n: int, size: int):
        assert 0 <= n < 4
        return self.sprites.get_side_resized(n, size)

    def get_side_sprite(self, side: str):
        assert side in SIDES
        return self.sprites.get_side(SIDES.index(side))


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


class DebugBlock(SingleSpriteBlock):
    sprite = BlockSprite('debug.png')


load_list = [Grass, Dirt, Stone, DebugBlock]
for c in load_list:
    c.load_sprites()
