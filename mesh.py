# import time
import pygame as pg
from camera import Layers
from world import Column
from trapezoid import SidesDrawer


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
    def __init__(self, sides_drawer: SidesDrawer, layers: Layers, scr_sizes):
        self.sides_drawer = sides_drawer
        self.layers = layers
        self.elements: list[list[Figure]] = []
        self.scr_rect = pg.Rect(0, 0, *scr_sizes)

    def create_mesh(self, columns):
        """:param columns: generator -> Column"""

        self.elements = []

        for column in columns:
            column: Column
            figures: list[Figure] = []

            # top sprites of first non-transparent block at column
            top_block = column.get_top_block()
            block = column.get_first_non_transparent()
            assert column.height_difference_are_set
            hd = column.height_difference
            hd2 = column.height_difference_2

            if block.z != top_block.z:
                x, y, z = column.x, column.y, block.z
                rect_size = self.layers.get_n_level_size(z)
                top_block_rect = self.layers.get_rect(x, y, z)
                if top_block_rect.colliderect(self.scr_rect):
                    if len(column.transparent_blocks) > 0:
                        sprite = block.get_top_sprite_fully_shaded(rect_size, z)
                    else:
                        sprite = block.get_top_sprite_resized_shaded(rect_size, (False,)*8, z)
                    top_figure = Figure(top_block_rect, sprite, (x, y, z), (x, y, z + 1))
                    figures.append(top_figure)

            # top sprites of top blocks at column
            x, y, z = column.x, column.y, top_block.z
            rect_size = self.layers.get_n_level_size(z)
            top_block_rect = self.layers.get_rect(x, y, z)
            if top_block_rect.colliderect(self.scr_rect):
                top_block_neighbors = column.get_top_block_neighbors()
                sprite = top_block.get_top_sprite_resized_shaded(rect_size, top_block_neighbors, z)
                top_figure = Figure(top_block_rect, sprite, (x, y, z), (x, y, z+1))
                figures.append(top_figure)

            # sides of blocks
            column_bottom_rect = self.layers.get_rect(x, y, 0)

            values = list(hd.values())+list(hd2.values())
            for i in range(max(values)):
                side_z = z - i
                block = column.get_block(side_z)
                top_rect = self.layers.get_rect(x, y, side_z)
                bottom_rect = self.layers.get_rect(x, y, side_z - 1)
                # bottom side
                if top_block_rect.bottom < column_bottom_rect.bottom:
                    if (not block.is_transparent and i < hd2['bottom']) or (block.is_transparent and i < hd['bottom']):
                        if i == hd2['bottom'] - 1:
                            sprite = block.get_side_sprite_shaded('bottom')
                            sprite_name = f"{block.__class__.__name__}_bottom_shaded"
                        else:
                            sprite = block.get_side_sprite('bottom')
                            sprite_name = f"{block.__class__.__name__}_bottom"

                        figure = self.create_bottom_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)

                # top side
                if top_block_rect.top > column_bottom_rect.top:
                    if (not block.is_transparent and i < hd2['top']) or (block.is_transparent and i < hd['top']):
                        if i == hd['top'] - 1:
                            sprite = block.get_side_sprite_shaded('top')
                            sprite_name = f"{block.__class__.__name__}_top_shaded"
                        else:
                            sprite = block.get_side_sprite('top')
                            sprite_name = f"{block.__class__.__name__}_top"

                        figure = self.create_top_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)

                # right side
                if top_block_rect.right < column_bottom_rect.right:
                    if (not block.is_transparent and i < hd2['right']) or (block.is_transparent and i < hd['right']):
                        if i == hd['right'] - 1:
                            sprite = block.get_side_sprite_shaded('right')
                            sprite_name = f"{block.__class__.__name__}_right_shaded"
                        else:
                            sprite = block.get_side_sprite('right')
                            sprite_name = f"{block.__class__.__name__}_right"
                        figure = self.create_right_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)

                # left side
                if top_block_rect.left > column_bottom_rect.left:
                    if (not block.is_transparent and i < hd2['left']) or (block.is_transparent and i < hd['left']):
                        if i == hd['left'] - 1:
                            sprite = column.get_block(side_z).get_side_sprite_shaded('left')
                            sprite_name = f"{block.__class__.__name__}_left_shaded"
                        else:
                            sprite = column.get_block(side_z).get_side_sprite('left')
                            sprite_name = f"{block.__class__.__name__}_left"
                        figure = self.create_left_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)

            self.elements.append(figures)

    def create_bottom_figure(self, x, y, z, sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> Figure | None:
        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.bottom - top_rect.bottom

        sizes = self.sides_drawer.get_hor_trapezoid_sizes(top+3, bottom+3, height, offset)
        rect_left = min(top_rect.left, bottom_rect.left)
        rect = pg.Rect((rect_left - 1, top_rect.bottom), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = self.sides_drawer.get_hor_trapezoid(sprite, sprite_name, top+3, bottom+3, height, offset)
            return Figure(rect, trapezoid_sprite, (x, y, z), (x, y + 1, z))

    def create_top_figure(self, x, y, z, sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> Figure | None:
        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.top - top_rect.top

        rect_left = min(bottom_rect.left, top_rect.left)
        sizes = self.sides_drawer.get_hor_trapezoid_sizes(top+1, bottom+1, height, offset)
        rect = pg.Rect((rect_left, bottom_rect.top), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = self.sides_drawer.get_hor_trapezoid(sprite, sprite_name, top+1, bottom+1, height, offset)
            return Figure(rect, trapezoid_sprite, (x, y, z), (x, y - 1, z))

    def create_right_figure(self, x, y, z, sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> Figure | None:
        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.right - top_rect.right
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = self.sides_drawer.get_vert_trapezoid_sizes(left+3, right+3, width, offset)
        rect = pg.Rect((top_rect.right, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = self.sides_drawer.get_vert_trapezoid(sprite, sprite_name, left+3, right+3, width, offset)
            return Figure(rect, trapezoid_sprite, (x, y, z), (x + 1, y, z))

    def create_left_figure(self, x, y, z, sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> Figure | None:
        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.left - top_rect.left
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = self.sides_drawer.get_vert_trapezoid_sizes(left+3, right+3, width, offset)
        rect = pg.Rect((bottom_rect.left, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid_sprite = self.sides_drawer.get_vert_trapezoid(sprite, sprite_name, left+3, right+3, width, offset)
            return Figure(rect, trapezoid_sprite, (x, y, z), (x - 1, y, z))

    def get_elements(self) -> list[list[Figure]]:
        return self.elements
