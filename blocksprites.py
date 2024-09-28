import pygame as pg
from constants import *
from height_difference import HeightDiff9
import blockspritestools as bst


class BlockSprite:
    def __init__(self, path, angle=0, recolor_value=1.0, recolor_func=bst.recolor):
        image = pg.image.load(PATH_TO_BLOCKS+path).convert_alpha()
        assert image.get_height() == image.get_width()
        image = pg.transform.rotate(image, angle)
        image = pg.transform.scale_by(image, SPRITES_SCALE_FACTOR)
        self.image = recolor_func(image, recolor_value)


class BlockSpritesFabric:
    shade_maker = bst.CreaseShadowDrawer()
    scale_cache: dict[str: pg.Surface] = {}
    scale_shaded_cache: dict[str: pg.Surface] = {}
    shaded_sides_cache: dict[str: pg.Surface] = {}
    top_recolored_cache: dict[str: pg.Surface] = {}

    def __init__(self, block_name: str,
                 top: str,
                 bottom: str,
                 west: str,
                 north: str,
                 east: str,
                 south: str):
        self.block_name = block_name
        self._top = BlockSprite(top)
        self._bottom = BlockSprite(bottom)
        self._west = BlockSprite(west, 90, SUN_SIDES_RECOLOR['west'], bst.sun_sides_recolor)
        self._north = BlockSprite(north, 0, SUN_SIDES_RECOLOR['north'], bst.sun_sides_recolor)
        self._east = BlockSprite(east, 90, SUN_SIDES_RECOLOR['east'], bst.sun_sides_recolor)
        self._south = BlockSprite(south, 0, SUN_SIDES_RECOLOR['south'], bst.sun_sides_recolor)
        self._sides = [self._west, self._north, self._east, self._south]

    def get_top_height_recolored(self, z: int) -> pg.Surface:
        key = (self.block_name, 'recolored', z)
        if key not in self.top_recolored_cache:
            image = bst.height_recolor(self._top.image.copy(), z)
            self.top_recolored_cache[key] = image
        return self.top_recolored_cache[key].copy()

    def get_top_resized(self, size: tuple[int, int], z: int) -> pg.Surface:
        key = (self.block_name, 'not shaded', size, z)
        if key not in self.scale_shaded_cache:
            image = self.get_top_height_recolored(z)
            image = pg.transform.scale(image, size)
            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_top_resized_shaded(self, size: tuple[int, int],
                               height_diff: HeightDiff9,
                               z: int,
                               is_transparent: bool) -> pg.Surface:
        neighbors = height_diff.get_top_block_neighbors()
        if is_transparent:
            hd = height_diff.full_full_height_diff
        else:
            hd = height_diff.nt_nt_height_diff

        key = (self.block_name, *neighbors, *hd.values(), size, z)
        if key not in self.scale_shaded_cache:
            image = self.get_top_height_recolored(z)
            w, h = image.get_size()

            edges_image = bst.EdgesDrawer.get_edges_images(w, h, hd)
            image.blit(edges_image, (0, 0))

            image = pg.transform.scale(image, size)
            for i in range(4):
                is_shaded = neighbors[i]
                if is_shaded:
                    shade = self.shade_maker.get_shade(SIDES_NAMES[i], size)
                    image.blit(shade, (0, 0))
                next_is_shaded = neighbors[(i+1) % 4]
                if not (is_shaded or next_is_shaded) and neighbors[i+4]:
                    shade = self.shade_maker.get_corner_shade(DIAGONALS_NAMES[i], size)
                    image.blit(shade, (0, 0))

            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_top_resized_fully_shaded(self, size: tuple[int, int],
                                     height_diff: HeightDiff9,
                                     z: int,
                                     is_transparent: bool) -> pg.Surface:
        if is_transparent:
            hd = height_diff.full_full_height_diff
        else:
            hd = height_diff.nt_nt_height_diff

        key = (self.block_name, *hd.values(), 'fully shaded', size, z)

        if key not in self.scale_shaded_cache:
            image = self.get_top_height_recolored(z)

            w, h = image.get_size()
            edges_image = bst.EdgesDrawer.get_edges_images(w, h, hd)
            image.blit(edges_image, (0, 0))

            image = pg.transform.scale(image, size)
            shade = self.shade_maker.get_full_shade(size)
            image.blit(shade, (0, 0))
            self.scale_shaded_cache[key] = image.copy()
        return self.scale_shaded_cache[key]

    def get_side(self, side: str, height_diff: HeightDiff9, ind_from_top: int) -> tuple[pg.Surface, str]:
        full_nt_hd = height_diff.full_nt_height_diff
        n = SIDES_NAMES.index(side)
        right_side = SIDES_NAMES[(n+1) % 4]
        left_side = SIDES_NAMES[(n-1) % 4]
        left_diagonal = DIAGONALS_NAMES[n % 4]
        right_diagonal = DIAGONALS_NAMES[(n-1) % 4]
        key = f'{self.block_name}'

        if ind_from_top == full_nt_hd[side] - 1:
            if ind_from_top == full_nt_hd[left_side] - 1 and ind_from_top != full_nt_hd[right_side] - 1:
                key += f'{side} __left__'
            elif ind_from_top != full_nt_hd[left_side] - 1 and ind_from_top == full_nt_hd[right_side] - 1:
                key += f'{side} __right__'
            else:
                key += f'{side} __bottom__'

        else:
            key += f'{side}'

        if ind_from_top >= full_nt_hd[left_diagonal]:
            key += ' __left_diagonal__'
        if ind_from_top >= full_nt_hd[right_diagonal]:
            key += ' __right_diagonal__'
        if ind_from_top == full_nt_hd[left_diagonal] - 1 and ind_from_top < full_nt_hd[side] - 1:
            key += ' __left_diagonal_ends__'
        if ind_from_top == full_nt_hd[right_diagonal] - 1 and ind_from_top < full_nt_hd[side] - 1:
            key += ' __right_diagonal_ends__'

        if key in self.shaded_sides_cache:
            return self.shaded_sides_cache[key], f'{self.block_name} {key}'

        sprite = self._sides[n].image.copy()
        if '__bottom__' in key:
            shade = self.shade_maker.get_shade(side, sprite.get_size(), True)
            if side in ['north', 'west']:  # Undo the rotation of the top sprite shadow
                shade = pg.transform.rotate(shade, 180)
            sprite.blit(shade, (0, 0))

        if '__right__' in key:
            if side in ['east', 'south']:  # IDK, crazy rotations, brute forced
                diagonal = DIAGONALS_NAMES[(n - 1) % 4]
            else:
                diagonal = DIAGONALS_NAMES[(n - 2) % 4]
            shade = self.shade_maker.get_corner_shade(diagonal, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))

        if '__left__' in key:
            if side in ['east', 'south']:  # IDK, crazy rotations, brute forced
                diagonal = DIAGONALS_NAMES[n % 4]
            else:
                diagonal = DIAGONALS_NAMES[(n + 1) % 4]
            shade = self.shade_maker.get_corner_shade(diagonal, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))

        if '__left_diagonal__' in key:
            shade = self.shade_maker.get_shade(right_side, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))
        if '__right_diagonal__' in key:
            shade = self.shade_maker.get_shade(left_side, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))

        if '__left_diagonal_ends__' in key:
            if side in ['east', 'south']:  # IDK, crazy rotations, brute forced
                diagonal = DIAGONALS_NAMES[n % 4]
            else:
                diagonal = DIAGONALS_NAMES[(n - 3) % 4]
            shade = self.shade_maker.get_corner_shade(diagonal, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))

        if '__right_diagonal_ends__' in key:
            if side in ['east', 'south']:  # IDK, crazy rotations, brute forced
                diagonal = DIAGONALS_NAMES[(n - 1) % 4]
            else:
                diagonal = DIAGONALS_NAMES[(n - 2) % 4]
            shade = self.shade_maker.get_corner_shade(diagonal, sprite.get_size(), True)
            sprite.blit(shade, (0, 0))

        self.shaded_sides_cache[key] = sprite.copy()
        return sprite, f'{key}'
