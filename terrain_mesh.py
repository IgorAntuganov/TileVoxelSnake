import pygame as pg
from camera import CameraFrame
from world import Column, World
from render_order import RenderOrder
from sides_drawer import Figure, SidesDrawer


class TerrainMech:
    def __init__(self, sides_drawer: SidesDrawer, camera: CameraFrame, scr_sizes):
        self.sides_drawer = sides_drawer
        self.camera = camera
        self.layers = camera.get_layers()
        self.elements: list[list[Figure]] = []
        self.scr_rect = pg.Rect(0, 0, *scr_sizes)
        self.render_order = RenderOrder()

        self.mouse_rect = None
        self.hovered_block = None
        self.directed_block = None

    def create_mesh(self, world: World):
        self.elements = []

        for i, j in self.render_order.get_order(self.camera.get_rect()):
            column: Column
            column = world.get_column(i, j)
            figures: list[Figure] = []

            # top sprites of first non-transparent block at column
            top_block = column.get_top_block()
            block = column.get_first_non_transparent()
            # assert column.height_difference_are_set
            if not column.height_difference_are_set:
                rect = self.layers.get_rect(column.x, column.y, 0)
                red = pg.Surface(rect.size)
                red.fill((255, 20, 20))
                self.elements.append([Figure(rect, red, (0, 0, 0), (0, 0, 0))])
                continue
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

                        figure = self.sides_drawer.create_bottom_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
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

                        figure = self.sides_drawer.create_top_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
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
                        figure = self.sides_drawer.create_right_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
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
                        figure = self.sides_drawer.create_left_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)

            self.elements.append(figures)

    def get_elements(self) -> list[list[Figure]]:
        return self.elements

    def draw_terrain(self, scr: pg.Surface):
        for column_figures in self.elements:
            for figure in column_figures:
                rect, sprite = figure.rect, figure.sprite
                if self.camera.screen_rect.colliderect(rect):
                    scr.blit(sprite, rect)

                if rect.collidepoint(pg.mouse.get_pos()):
                    self.mouse_rect = rect.copy()
                    self.hovered_block = figure.origin_block
                    self.directed_block = figure.directed_block
