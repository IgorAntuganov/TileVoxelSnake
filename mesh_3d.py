import pygame as pg
from camera import CameraFrame, Layers
from world import Column, World
from render_order import RenderOrder
from sides_drawer import Figure, SidesDrawer
from constants import TRAPEZOIDS_IN_CACHE_DURATION


def ceil(n: float) -> int:
    return int(n+0.99999999999999999999)


class SideCache:
    def __init__(self):
        self.cache: dict[tuple[int, int]: Figure] = {}

    def add(self, i: int, j: int, figures_lst: list[Figure], camera_xy: tuple[float, float]):
        start_rects = list([fig.rect.copy() for fig in figures_lst])
        item = (figures_lst, camera_xy, start_rects)
        key = (i, j)
        self.cache[key] = item

    def isin(self, i: int, j: int) -> bool:
        return (i, j) in self.cache

    def get(self, i: int, j: int, camera_xy: tuple[float, float], layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, old_camera_xy, start_rects = self.cache.get(key)
        offset = old_camera_xy[0] - camera_xy[0], old_camera_xy[1] - camera_xy[1]
        for figure, start_rect in zip(figures_lst, start_rects):
            z = figure.origin_block[2]
            m = layers.get_n_level_size(z)
            m_offset = offset[0] * m, offset[1] * m
            new_rect = start_rect.move(m_offset)
            figure.reset_rect(new_rect)
        return figures_lst

    def pop(self,  i: int, j: int):
        if self.isin(i, j):
            self.cache.pop((i, j))


class Mesh3D:
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

        self.sides_cache = SideCache()

    def create_mesh(self, world: World, frame: int):
        self.elements = []

        rend_order = self.render_order.get_order(self.camera.get_rect())
        counter = 0
        for i, j in rend_order:
            counter += 1
            column: Column
            column = world.get_column(i, j)
            figures: list[Figure] = []

            if not column.height_difference_are_set:
                rect = self.layers.get_rect_for_block(column.x, column.y, 0)
                red = pg.Surface(rect.size)
                red.fill((255, 20, 20))
                self.elements.append([Figure(rect, red, (0, 0, 0), (0, 0, 0))])
                continue

            # top sprites of first non-transparent block at column
            top_block = column.get_top_block()
            block = column.get_first_non_transparent()
            hd = column.height_difference
            hd2 = column.height_difference_2

            if block.z != top_block.z:
                x, y, z = column.x, column.y, block.z
                top_block_rect = self.layers.get_rect_for_block(x, y, z)
                rect_size = max(top_block_rect.size)
                if top_block_rect.colliderect(self.scr_rect):
                    if len(column.transparent_blocks) > 0:
                        sprite = block.get_top_sprite_fully_shaded(rect_size, z)
                    else:
                        sprite = block.get_top_sprite_resized_shaded(rect_size, (False,)*8, z)
                    top_figure = Figure(top_block_rect, sprite, (x, y, z), (x, y, z + 1))
                    figures.append(top_figure)

            # top sprites of top blocks at column
            x, y, z = column.x, column.y, top_block.z
            top_block_rect = self.layers.get_rect_for_block(x, y, z)
            rect_size = max(top_block_rect.size)
            if top_block_rect.colliderect(self.scr_rect):
                top_block_neighbors = column.get_top_block_neighbors()
                sprite = top_block.get_top_sprite_resized_shaded(rect_size, top_block_neighbors, z)
                top_figure = Figure(top_block_rect, sprite, (x, y, z), (x, y, z+1))
                figures.append(top_figure)

            # sides of blocks
            d = TRAPEZOIDS_IN_CACHE_DURATION
            if d > 1:
                if counter % d != frame % d and self.sides_cache.isin(i, j):
                    figures_from_cache = self.sides_cache.get(i, j, self.camera.get_center(), self.layers)
                    figures += figures_from_cache
                    self.elements.append(figures)
                    continue

            self.sides_cache.pop(i, j)

            figures_for_cache = []

            column_bottom_rect = self.layers.get_rect_for_block(x, y, 0)

            values = list(hd.values())+list(hd2.values())
            for k in range(max(values)):
                side_z = z - k
                block = column.get_block(side_z)
                top_rect = self.layers.get_rect_for_block(x, y, side_z)
                bottom_rect = self.layers.get_rect_for_block(x, y, side_z - 1)
                # bottom side
                if top_block_rect.bottom < column_bottom_rect.bottom:
                    if (not block.is_transparent and k < hd2['bottom']) or (block.is_transparent and k < hd['bottom']):
                        if k == hd2['bottom'] - 1:
                            sprite = block.get_side_sprite_shaded('bottom')
                            sprite_name = f"{block.__class__.__name__}_bottom_shaded"
                        else:
                            sprite = block.get_side_sprite('bottom')
                            sprite_name = f"{block.__class__.__name__}_bottom"

                        figure = self.sides_drawer.create_bottom_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)
                            figures_for_cache.append(figure)

                # top side
                if top_block_rect.top > column_bottom_rect.top:
                    if (not block.is_transparent and k < hd2['top']) or (block.is_transparent and k < hd['top']):
                        if k == hd['top'] - 1:
                            sprite = block.get_side_sprite_shaded('top')
                            sprite_name = f"{block.__class__.__name__}_top_shaded"
                        else:
                            sprite = block.get_side_sprite('top')
                            sprite_name = f"{block.__class__.__name__}_top"

                        figure = self.sides_drawer.create_top_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)
                            figures_for_cache.append(figure)

                # right side
                if top_block_rect.right < column_bottom_rect.right:
                    if (not block.is_transparent and k < hd2['right']) or (block.is_transparent and k < hd['right']):
                        if k == hd['right'] - 1:
                            sprite = block.get_side_sprite_shaded('right')
                            sprite_name = f"{block.__class__.__name__}_right_shaded"
                        else:
                            sprite = block.get_side_sprite('right')
                            sprite_name = f"{block.__class__.__name__}_right"
                        figure = self.sides_drawer.create_right_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)
                            figures_for_cache.append(figure)

                # left side
                if top_block_rect.left > column_bottom_rect.left:
                    if (not block.is_transparent and k < hd2['left']) or (block.is_transparent and k < hd['left']):
                        if k == hd['left'] - 1:
                            sprite = column.get_block(side_z).get_side_sprite_shaded('left')
                            sprite_name = f"{block.__class__.__name__}_left_shaded"
                        else:
                            sprite = column.get_block(side_z).get_side_sprite('left')
                            sprite_name = f"{block.__class__.__name__}_left"
                        figure = self.sides_drawer.create_left_figure(x, y, side_z, sprite, sprite_name, top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)
                            figures_for_cache.append(figure)

            if len(figures_for_cache) > 0:
                self.sides_cache.add(i, j, figures_for_cache, self.camera.get_center())
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
