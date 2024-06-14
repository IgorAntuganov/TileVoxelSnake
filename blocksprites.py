import pygame as pg
from constants import SHADOW_STRENGTH, SHADOW_RADIUS, SIDES_NAMES, DIAGONALS_NAMES, PATH_TO_BLOCKS


class ShadowSprites:
    def __init__(self, shade_radius=SHADOW_RADIUS, shade_strength=SHADOW_STRENGTH):
        """:param shade_radius: between 0 and 1, which part will be covered with shade
        :param shade_strength: between 0 and 1, shadow power at the darkest point (1 - full black)
        """
        self.cache = {}
        self.shade_radius = shade_radius
        self.shade_power = shade_strength

    def get_shade(self, nearby_block_side: str, size: int, is_side: bool = False) -> pg.Surface:
        if is_side:
            shade_radius = min(1, self.shade_radius * 2)
        else:
            shade_radius = self.shade_radius

        key = (size, nearby_block_side, 'nearby')
        if key not in self.cache:
            shade = pg.Surface((size, size), pg.SRCALPHA)
            shade.fill((0, 0, 0, 0))
            start_power = 255 * self.shade_power
            for i in range(int(size*shade_radius)):
                part = i / int(size*shade_radius)
                power = int(start_power*(1-part))
                shade_string = pg.Surface((size, 1), pg.SRCALPHA)
                shade_string.fill((0, 0, 0, power))
                shade.blit(shade_string, (0, i))

            angle = (1 - SIDES_NAMES.index(nearby_block_side)) * 90
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

            angle = (-DIAGONALS_NAMES.index(side)) * 90
            shade = pg.transform.rotate(shade, angle)
            self.cache[key] = shade
        return self.cache[key]


class BlockSprite:
    def __init__(self, path, angle=0):
        self.image = pg.image.load(PATH_TO_BLOCKS+path).convert()
        self.image = pg.transform.rotate(self.image, angle)
        self.image = pg.transform.scale_by(self.image, 2)  # For more accurate trapezoids, doesn't reduce fps


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
        self.shaded_sides_cache = {}
        self._top = BlockSprite(top)
        self._bottom = BlockSprite(bottom)
        self._side1 = BlockSprite(side1, 90)
        self._side2 = BlockSprite(side2)
        self._side3 = BlockSprite(side3, 90)
        self._side4 = BlockSprite(side4)
        self._sides = [self._side1, self._side2, self._side3, self._side4]
        self.side_sprite_sizes = self._side1.image.get_width()

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
                    shade = self.shade_maker.get_shade(SIDES_NAMES[i], size)
                    image.blit(shade, (0, 0))
                next_is_shaded = neighbors[(i+1) % 4]
                if not (is_shaded or next_is_shaded) and neighbors[i+4]:
                    shade = self.shade_maker.get_diagonal_shade(DIAGONALS_NAMES[i], size)
                    image.blit(shade, (0, 0))
            self.scale_shaded_cache[key] = image
        return self.scale_shaded_cache[key]

    def get_side(self, n) -> pg.Surface:
        return self._sides[n].image

    def get_side_shaded(self, side: str, size: int) -> pg.Surface:
        key = side
        if key in self.shaded_sides_cache:
            return self.shaded_sides_cache[key]
        shade = self.shade_maker.get_shade(side, size, True)
        if side in ['top', 'left']:  # Undo the rotation of the top sprite shadow
            shade = pg.transform.rotate(shade, 180)
        n = SIDES_NAMES.index(side)
        sprite = self._sides[n].image.copy()
        sprite.blit(shade, (0, 0))
        self.shaded_sides_cache[key] = sprite
        return sprite
