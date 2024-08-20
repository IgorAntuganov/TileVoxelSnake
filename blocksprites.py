import math
import pygame as pg
from constants import *
from height_difference import HeightDiff


def recolor(sprite: pg.Surface, coefficient: float) -> pg.Surface:
    for i in range(sprite.get_width()):
        for j in range(sprite.get_height()):
            pixel = sprite.get_at((i, j))
            pixel = [int(color_value*coefficient) for color_value in pixel]
            pixel = [min(255, color_value) for color_value in pixel]
            sprite.set_at((i, j), pixel)
    return sprite


def sun_sides_recolor(sprite: pg.Surface, coefficient: float) -> pg.Surface:
    normalized_coef = coefficient - 1
    for i in range(sprite.get_width()):
        for j in range(sprite.get_height()):
            pixel = sprite.get_at((i, j))
            if coefficient > 1:
                pixel[0] = min(255, int(pixel[0]*(1+normalized_coef)))
                pixel[1] = min(255, int(pixel[1]*(1+normalized_coef/2)))
                pixel[2] = min(255, int(pixel[2]*1))
            else:
                pixel[0] = min(255, int(pixel[0]*(1+normalized_coef)))
                pixel[1] = min(255, int(pixel[1]*(1+normalized_coef)))
                pixel[2] = min(255, int(pixel[2]*(1+normalized_coef)))
            sprite.set_at((i, j), pixel)
    return sprite


def height_recolor(sprite: pg.Surface, z: int) -> pg.Surface:
    z -= HEIGHT_RECOLOR_OFFSET
    c = math.atan(z/(MAX_HEIGHT/2)) * 2 / math.pi
    c = HEIGHT_RECOLOR_BASE + c * HEIGHT_RECOLOR_STRENGTH
    return recolor(sprite, c)


class ShadowSprites:
    def __init__(self, shade_radius=SHADOW_RADIUS, shade_strength=SHADOW_STRENGTH):
        """:param shade_radius: between 0 and 1, which part will be covered with shade
        :param shade_strength: between 0 and 1, shadow power at the darkest point (1 - full black)
        """
        self.cache = {}
        self.shade_radius = shade_radius
        self.shade_power = shade_strength

    def get_shade(self, nearby_block_side: str, size: tuple[int, int], is_side: bool = False) -> pg.Surface:
        if is_side:
            shade_radius = min(1, self.shade_radius * 2)
        else:
            shade_radius = self.shade_radius

        key = (size, nearby_block_side, 'nearby')
        if key not in self.cache:
            shade = pg.Surface(size, pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            max_size = max(size)
            for i in range(int(max_size*shade_radius)):
                part = i / int(max_size*shade_radius)
                power = int(start_power*(1-part))
                shade_string = pg.Surface((max_size, 1), pg.SRCALPHA)
                shade_string.fill((0, 0, 0, power))
                shade.blit(shade_string, (0, i))

            angle = (1 - SIDES_NAMES.index(nearby_block_side)) * 90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]

    def get_diagonal_shade(self, side: str, size: tuple[int, int]) -> pg.Surface:
        key = (size, side, 'diagonal')
        if key not in self.cache:
            shade = pg.Surface(size, pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            radius = int(max(size) * self.shade_radius)
            for i in range(radius):
                for j in range(radius):
                    part = ((i/radius)**2 + (j/radius)**2)**.5
                    part = min(1.0, part)
                    power = int(start_power * (1 - part))
                    shade_string = pg.Surface((1, 1), pg.SRCALPHA)
                    shade_string.fill((0, 0, 0, power))
                    shade.blit(shade_string, (i, j))

            angle = (-DIAGONALS_NAMES.index(side)) * 90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]

    def get_full_shade(self, size: tuple[int, int]) -> pg.Surface:
        key = (size, 'full')
        if key not in self.cache:
            shade = pg.Surface(size, pg.SRCALPHA)
            power = 255 * self.shade_power
            shade.fill((0, 0, 0, power))
            self.cache[key] = shade
        return self.cache[key]


class BlockSprite:
    def __init__(self, path, angle=0, recolor_value=1.0, recolor_func=recolor):
        self.image = pg.image.load(PATH_TO_BLOCKS+path).convert_alpha()
        assert self.image.get_height() == self.image.get_width()
        self.image = pg.transform.rotate(self.image, angle)
        self.image = pg.transform.scale_by(self.image, 2)  # For more accurate trapezoids, doesn't reduce fps
        self.image = recolor_func(self.image, recolor_value)


class BlockSpritesDict:
    shade_maker = ShadowSprites()

    def __init__(self, top: str,
                 bottom: str,
                 west: str,
                 north: str,
                 east: str,
                 south: str):
        self.scale_cache = {}
        self.scale_shaded_cache = {}
        self.shaded_sides_cache = {}
        self._top = BlockSprite(top)
        self._bottom = BlockSprite(bottom)
        self._west = BlockSprite(west, 90, SUN_SUN_RECOLOR['west'], recolor_func=sun_sides_recolor)
        self._north = BlockSprite(north, 0, SUN_SUN_RECOLOR['north'], recolor_func=sun_sides_recolor)
        self._east = BlockSprite(east, 90, SUN_SUN_RECOLOR['east'], recolor_func=sun_sides_recolor)
        self._south = BlockSprite(south, 0, SUN_SUN_RECOLOR['south'], recolor_func=sun_sides_recolor)
        self._sides = [self._west, self._north, self._east, self._south]

    def get_top_resized(self, size: tuple[int, int], z: int):
        key = ('not shaded', size, z)
        if key not in self.scale_shaded_cache:
            image = pg.transform.scale(self._top.image, size)
            image = height_recolor(image, z)
            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_top_resized_shaded(self, size: tuple[int, int],
                               height_diff: HeightDiff,
                               z: int) -> pg.Surface:
        neighbors = height_diff.get_top_block_neighbors()
        key = (*neighbors, size, z)
        if key not in self.scale_shaded_cache:
            image = pg.transform.scale(self._top.image, size)
            image = height_recolor(image, z)
            for i in range(4):
                is_shaded = neighbors[i]
                if is_shaded:
                    shade = self.shade_maker.get_shade(SIDES_NAMES[i], size)
                    image.blit(shade, (0, 0))
                next_is_shaded = neighbors[(i+1) % 4]
                if not (is_shaded or next_is_shaded) and neighbors[i+4]:
                    shade = self.shade_maker.get_diagonal_shade(DIAGONALS_NAMES[i], size)
                    image.blit(shade, (0, 0))
            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_top_resized_fully_shaded(self, size: tuple[int, int], z: int):
        key = ('fully shaded', size, z)
        if key not in self.scale_shaded_cache:
            image = pg.transform.scale(self._top.image, size)
            image = height_recolor(image, z)
            shade = self.shade_maker.get_full_shade(size)
            image.blit(shade, (0, 0))
            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_side(self, side: str) -> pg.Surface:
        n = SIDES_NAMES.index(side)
        return self._sides[n].image

    def get_side_shaded(self, side: str) -> pg.Surface:
        key = side
        n = SIDES_NAMES.index(side)
        sprite = self._sides[n].image.copy()
        if key in self.shaded_sides_cache:
            return self.shaded_sides_cache[key]
        shade = self.shade_maker.get_shade(side, sprite.get_size(), True)
        if side in ['north', 'west']:  # Undo the rotation of the top sprite shadow
            shade = pg.transform.rotate(shade, 180)

        sprite.blit(shade, (0, 0))
        self.shaded_sides_cache[key] = sprite.copy()
        return sprite
