import pygame as pg
from constants import *
import math


def recolor(sprite: pg.Surface, coefficient: float) -> pg.Surface:
    for i in range(sprite.get_width()):
        for j in range(sprite.get_height()):
            pixel = sprite.get_at((i, j))
            pixel = [int(color_value * coefficient) for color_value in pixel]
            pixel = [min(255, color_value) for color_value in pixel]
            sprite.set_at((i, j), pixel)
    return sprite


def sun_sides_recolor(sprite: pg.Surface, coefficient: float) -> pg.Surface:
    normalized_coef = coefficient - 1
    for i in range(sprite.get_width()):
        for j in range(sprite.get_height()):
            pixel = sprite.get_at((i, j))
            if coefficient > 1:
                pixel[0] = min(255, int(pixel[0] * (1 + normalized_coef)))
                pixel[1] = min(255, int(pixel[1] * (1 + normalized_coef / 2)))
                pixel[2] = min(255, int(pixel[2] * 1))
            else:
                pixel[0] = min(255, int(pixel[0] * (1 + normalized_coef)))
                pixel[1] = min(255, int(pixel[1] * (1 + normalized_coef)))
                pixel[2] = min(255, int(pixel[2] * (1 + normalized_coef)))
            sprite.set_at((i, j), pixel)
    return sprite


def height_recolor(sprite: pg.Surface, z: int) -> pg.Surface:
    z -= HEIGHT_RECOLOR_OFFSET
    c = math.atan(z / (MAX_HEIGHT / 2)) * 2 / math.pi
    c = HEIGHT_RECOLOR_BASE + c * HEIGHT_RECOLOR_STRENGTH
    return recolor(sprite, c)


class CreaseShadowDrawer:
    def __init__(self, shade_radius=SHADOW_RADIUS, shade_strength=SHADOW_STRENGTH):
        """:param shade_radius: between 0 and 1, which part will be covered with shade
        :param shade_strength: between 0 and 1, shadow power at the darkest point (1 - full black)
        """
        self.cache = {}
        self.shade_radius = shade_radius
        self.shade_power = shade_strength

    def get_shade(self, nearby_block_side: str, size: tuple[int, int], is_side: bool = False) -> pg.Surface:
        if nearby_block_side in ['west', 'east']:
            size = size[::-1]

        if is_side:
            shade_radius = min(1, self.shade_radius * 2)
        else:
            shade_radius = self.shade_radius

        key = (*size, nearby_block_side, 'nearby')
        if key not in self.cache:
            shade = pg.Surface(size, pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            max_size = max(size)
            shade_size = int(max_size * shade_radius + 1)
            for i in range(shade_size):
                part = (i / shade_size) ** (1/SHADOW_POWER_FACTOR)
                power = int(start_power * (1 - part))
                shade_string = pg.Surface((max_size, 1), pg.SRCALPHA)
                shade_string.fill((0, 0, 0, power))
                shade.blit(shade_string, (0, i))

            angle = (1 - SIDES_NAMES.index(nearby_block_side)) * 90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]

    def get_corner_shade(self, side: str, size: tuple[int, int], is_side: bool = False) -> pg.Surface:
        if side == DIAGONALS_NAMES[1] or side == DIAGONALS_NAMES[3]:
            size = size[::-1]

        if is_side:
            shade_radius = min(1, self.shade_radius * 2)
        else:
            shade_radius = self.shade_radius

        key = (size, side, is_side, 'corner')
        if key not in self.cache:
            shade = pg.Surface(size, pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            if is_side:
                radius = int(max(size) * shade_radius)
            else:
                radius = int(max(size) * shade_radius)
            for i in range(radius):
                for j in range(radius):
                    part = ((i / radius) ** 2 + (j / radius) ** 2) ** .5  # distance from corner
                    part = part ** (1/SHADOW_POWER_FACTOR)
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


class EdgesDrawer:
    SPRITE = pg.Surface((1, 1), pg.SRCALPHA)
    SPRITE.fill(EDGE_COLOR)

    @classmethod
    def get_edges_images(cls, width: int, height: int, height_diff: dict[str: int]) -> pg.Surface:
        w, h = width, height
        t = EDGE_THICKNESS * SPRITES_SCALE_FACTOR
        edges_image = pg.Surface((width, height), pg.SRCALPHA)

        # sides
        if height_diff['west'] > 0:
            sprite = pg.transform.scale(cls.SPRITE, (t, h))
            edges_image.blit(sprite, (0, 0))
        if height_diff['north'] > 0:
            sprite = pg.transform.scale(cls.SPRITE, (w, t))
            edges_image.blit(sprite, (0, 0))
        if height_diff['east'] > 0:
            sprite = pg.transform.scale(cls.SPRITE, (t, h))
            edges_image.blit(sprite, (w - t, 0))
        if height_diff['south'] > 0:
            sprite = pg.transform.scale(cls.SPRITE, (w, t))
            edges_image.blit(sprite, (0, h - t))

        # corners
        sprite = pg.transform.scale(cls.SPRITE, (t, t))
        if height_diff['north_west'] > 0:
            edges_image.blit(sprite, (0, 0))
        if height_diff['north_east'] > 0:
            edges_image.blit(sprite, (w - t, 0))
        if height_diff['south_west'] > 0:
            edges_image.blit(sprite, (0, h - t))
        if height_diff['south_east'] > 0:
            edges_image.blit(sprite, (w - t, h - t))

        edges_image.set_alpha(EDGES_ALPHA)
        return edges_image
