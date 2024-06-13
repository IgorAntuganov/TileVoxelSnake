from abc import ABC, abstractmethod
import pygame as pg
PATH_TO_SPRITES = 'sprites/'
PATH_TO_BLOCKS = 'sprites/blocks/'

SIDES = ['left', 'top', 'right', 'bottom']
DIAGONALS = ['top_left', 'top_right', 'bottom_left', 'bottom_right']


class ShadowSprites:
    def __init__(self, shade_radius=0.6, shade_power=0.3):
        """:param shade_radius: between 0 and 1, which part will be covered with shade
        :param shade_power: between 0 and 1, shadow power at the darkest point (1 - full black)
        """
        self.cache = {}
        self.shade_radius = shade_radius
        self.shade_power = shade_power

    def get_shade(self, side: str, size: int) -> pg.Surface:
        key = (size, side, 'nearby')
        if key not in self.cache:
            shade = pg.Surface((size, size), pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            for i in range(int(size*self.shade_radius)):
                part = i / int(size*self.shade_radius)
                power = int(start_power*(1-part))
                shade_string = pg.Surface((size, 1), pg.SRCALPHA)
                shade_string.fill((0, 0, 0, power))
                shade.blit(shade_string, (0, i))

            angle = (1-SIDES.index(side))*90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]

    def get_diagonal_shade(self, side: str, size: int) -> pg.Surface:
        key = (size, side, 'diagonal')
        if key not in self.cache:
            shade = pg.Surface((size, size), pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            radius = int(size * self.shade_radius)
            for i in range(radius):
                for j in range(radius):
                    part = ((i/radius)**2 + (j/radius)**2)**.5
                    part = min(1.0, part)
                    power = int(start_power * (1 - part))
                    shade_string = pg.Surface((1, 1), pg.SRCALPHA)
                    shade_string.fill((0, 0, 0, power))
                    shade.blit(shade_string, (i, j))

            angle = (-DIAGONALS.index(side)) * 90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]


class BlockSprite:
    def __init__(self, path, angle=0):
        self.image = pg.image.load(PATH_TO_BLOCKS+path).convert()
        self.image = pg.transform.rotate(self.image, angle)


class BlockSpritesDict:
    shade_maker = ShadowSprites()

    def __init__(self, top: str,
                 bottom: str,
                 side1: str,
                 side2: str,
                 side3: str,
                 side4: str):
        self.scale_cache = {}
        self.scale_shaded_cache = {}
        self._top = BlockSprite(top)
        self._bottom = BlockSprite(bottom)
        self._side1 = BlockSprite(side1, 90)
        self._side2 = BlockSprite(side2)
        self._side3 = BlockSprite(side3, 90)
        self._side4 = BlockSprite(side4)
        self._sides = [self._side1, self._side2, self._side3, self._side4]

    def get_top_resized(self, size: int) -> pg.Surface:
        key = f'top{size}'
        if key not in self.scale_cache:
            image = pg.transform.scale(self._top.image, (size, size))
            self.scale_cache[key] = image
        return self.scale_cache[key]

    def get_top_resized_shaded(self, size: int,
                               neighbors: tuple[bool, bool, bool, bool, bool, bool, bool, bool]) -> pg.Surface:
        key = (*neighbors, size)
        if key not in self.scale_shaded_cache:
            image = pg.transform.scale(self._top.image, (size, size))
            for i in range(4):
                is_shaded = neighbors[i]
                if is_shaded:
                    shade = self.shade_maker.get_shade(SIDES[i], size)
                    image.blit(shade, (0, 0))
                next_is_shaded = neighbors[(i+1) % 4]
                if not (is_shaded or next_is_shaded) and neighbors[i+4]:
                    shade = self.shade_maker.get_diagonal_shade(DIAGONALS[i], size)
                    image.blit(shade, (0, 0))
            self.scale_shaded_cache[key] = image
        return self.scale_shaded_cache[key]

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

    def get_top_sprite_resized_shaded(self, size: int,
                                      neighbors: tuple[bool, bool, bool, bool, bool, bool, bool, bool]) -> pg.Surface:
        return self.sprites.get_top_resized_shaded(size, neighbors)

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
