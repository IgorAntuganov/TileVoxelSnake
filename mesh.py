# import time
import pygame as pg
from camera import Layers
from world import Column
from trapezoid import SidesDrawer
sides_drawer = SidesDrawer()
sides_drawer.set_debug_mode(False)
sides_drawer.set_using_anisotropic_filtration(True)
sides_drawer.set_fast_anisotropic(False)
sides_drawer.set_using_perspective(True)
sides_drawer.set_using_cache(True)


class Figure:
    def __init__(self, rect: pg.Rect,
                 sprite: pg.Surface,
                 origin_block: tuple[int, int, int],
                 directed_block: tuple[int, int, int]):
        self.rect = rect
        self.sprite = sprite
        self.origin_block = origin_block
        self.directed_block = directed_block


class TerrainMech:
    def __init__(self, layers: Layers, scr_sizes):
        self.layers = layers
        self.elements: list[list[Figure]] = []
        self.scr_rect = pg.Rect(0, 0, *scr_sizes)

    def create_mesh(self, columns):
        """:param columns: generator -> Column"""

        self.elements = []

        for column in columns:
            column: Column
            figures: list[Figure] = []

            # top sprites of blocks
            top_block = column.get_top_block()
            x, y, z = column.x, column.y, top_block.z
            hd = column.height_difference
            rect_size = self.layers.get_n_level_size(z)
            top_block_rect = self.layers.get_rect(x, y, z)
            if top_block_rect.colliderect(self.scr_rect):
                top_block_neighbors = column.get_top_block_neighbors()
                sprite = top_block.get_top_sprite_resized_shaded(rect_size, top_block_neighbors, z)
                top_figure = Figure(top_block_rect, sprite, (x, y, z), (x, y, z+1))
                figures.append(top_figure)

            # sides of blocks
            column_bottom_rect = self.layers.get_rect(x, y, 0)
            # bottom side
            if hd['bottom'] > 0:
                if top_block_rect.bottom < column_bottom_rect.bottom:
                    for i in range(hd['bottom']):
                        side_z = z - i
                        shaded = i == hd['bottom'] - 1
                        result = self.create_bottom_sprite(column, side_z, shaded)
                        if result is not None:
                            rect, sprite = result
                            figure = Figure(rect, sprite, (x, y, side_z), (x, y+1, side_z))
                            figures.append(figure)
            # top side
            if hd['top'] > 0:
                if top_block_rect.top > column_bottom_rect.top:
                    for i in range(hd['top']):
                        side_z = z - i
                        shaded = i == hd['top'] - 1
                        result = self.create_top_sprite(column, side_z, shaded)
                        if result is not None:
                            rect, sprite = result
                            figure = Figure(rect, sprite, (x, y, side_z), (x, y - 1, side_z))
                            figures.append(figure)

            # right side
            if hd['right'] > 0:
                if top_block_rect.right < column_bottom_rect.right:
                    for i in range(hd['right']):
                        side_z = z - i
                        shaded = i == hd['right'] - 1
                        result = self.create_right_sprite(column, side_z, shaded)
                        if result is not None:
                            rect, sprite = result
                            figure = Figure(rect, sprite, (x, y, side_z), (x + 1, y, side_z))
                            figures.append(figure)

            # left side
            if hd['left'] > 0:
                if top_block_rect.left > column_bottom_rect.left:
                    for i in range(hd['left']):
                        side_z = z - i
                        shaded = i == hd['left'] - 1
                        result = self.create_left_sprite(column, side_z, shaded)
                        if result is not None:
                            rect, sprite = result
                            figure = Figure(rect, sprite, (x, y, side_z), (x - 1, y, side_z))
                            figures.append(figure)
            self.elements.append(figures)

    def create_bottom_sprite(self, column, z, shaded) -> tuple[pg.Rect, pg.Surface] | None:
        x, y = column.x, column.y
        block_for_side = column.get_block(z)
        if not shaded:
            sprite = block_for_side.get_side_sprite('bottom')
        else:
            sprite = block_for_side.get_side_sprite_shaded('bottom')
        top_rect = self.layers.get_rect(x, y, z)
        bottom_rect = self.layers.get_rect(x, y, z - 1)

        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.bottom - top_rect.bottom

        sizes = sides_drawer.get_hor_trapezoid_sizes(top+3, bottom+3, height, offset)
        rect_left = min(top_rect.left, bottom_rect.left)
        rect = pg.Rect((rect_left - 1, top_rect.bottom), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = sides_drawer.get_hor_trapezoid(sprite, top+3, bottom+3, height, offset)
            figure = (rect, trapezoid_sprite)
            return figure

    def create_top_sprite(self, column, z, shaded) -> tuple[pg.Rect, pg.Surface] | None:
        x, y = column.x, column.y
        block_for_side = column.get_block(z)
        if not shaded:
            sprite = block_for_side.get_side_sprite('top')
        else:
            sprite = block_for_side.get_side_sprite_shaded('top')
        top_rect = self.layers.get_rect(x, y, z)
        bottom_rect = self.layers.get_rect(x, y, z - 1)

        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.top - top_rect.top

        rect_left = min(bottom_rect.left, top_rect.left)
        sizes = sides_drawer.get_hor_trapezoid_sizes(top+1, bottom+1, height, offset)
        rect = pg.Rect((rect_left, bottom_rect.top), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = sides_drawer.get_hor_trapezoid(sprite, top+1, bottom+1, height, offset)
            figure = (rect, trapezoid_sprite)
            return figure

    def create_right_sprite(self, column, z, shaded) -> tuple[pg.Rect, pg.Surface] | None:
        x, y = column.x, column.y
        block_for_side = column.get_block(z)
        if not shaded:
            sprite = block_for_side.get_side_sprite('right')
        else:
            sprite = block_for_side.get_side_sprite_shaded('right')
        top_rect = self.layers.get_rect(x, y, z)
        bottom_rect = self.layers.get_rect(x, y, z - 1)

        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.right - top_rect.right
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = sides_drawer.get_vert_trapezoid_sizes(left+3, right+3, width, offset)
        rect = pg.Rect((top_rect.right, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = sides_drawer.get_vert_trapezoid(sprite, left+3, right+3, width, offset)
            figure = (rect, trapezoid_sprite)
            return figure

    def create_left_sprite(self, column, z, shaded) -> tuple[pg.Rect, pg.Surface] | None:
        x, y = column.x, column.y
        block_for_side = column.get_block(z)
        if not shaded:
            sprite = block_for_side.get_side_sprite('left')
        else:
            sprite = block_for_side.get_side_sprite_shaded('left')
        top_rect = self.layers.get_rect(x, y, z)
        bottom_rect = self.layers.get_rect(x, y, z - 1)

        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.left - top_rect.left
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = sides_drawer.get_vert_trapezoid_sizes(left+3, right+3, width, offset)
        rect = pg.Rect((bottom_rect.left, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = sides_drawer.get_vert_trapezoid(sprite, left+3, right+3, width, offset)
            figure = (rect, trapezoid_sprite)
            return figure

    def get_elements_in_order(self) -> list[list[Figure]]:
        return self.elements
