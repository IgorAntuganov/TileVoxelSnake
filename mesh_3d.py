import pygame as pg
from camera import CameraFrame, Layers
from world_class import Column, World
from render_order import RenderOrder
from sides_drawer import Figure, SidesDrawer
from constants import *


class SideCache:
    def __init__(self):
        self._cache: dict[tuple[int, int]: Figure] = {}

    def add(self, i: int, j: int, figures_lst: list[Figure], camera_xy: tuple[float, float]):
        start_rects = list([fig.rect.copy() for fig in figures_lst])
        item = (figures_lst, camera_xy, start_rects)
        key = (i, j)
        self._cache[key] = item

    def is_in(self, i: int, j: int) -> bool:
        return (i, j) in self._cache

    def get(self, i: int, j: int, camera_xy: tuple[float, float], layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, old_camera_xy, start_rects = self._cache.get(key)
        offset = old_camera_xy[0] - camera_xy[0], old_camera_xy[1] - camera_xy[1]
        for figure, start_rect in zip(figures_lst, start_rects):
            z = figure.origin_block[2]
            m = layers.get_n_level_size(z)
            m_offset = offset[0] * m, offset[1] * m
            new_rect = start_rect.move(m_offset)
            figure.reset_rect(new_rect)
        return figures_lst

    def pop(self,  i: int, j: int):
        if self.is_in(i, j):
            self._cache.pop((i, j))


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

    def check_if_in_screen(self, rect: pg.Rect) -> bool:
        return rect.colliderect(self.scr_rect)

    def create_mesh(self, world: World, frame: int):
        self.elements: list[list[Figure]] = []

        rend_order = self.render_order.get_order(self.camera.get_rect())
        counter = 0
        for i, j in rend_order:
            counter += 1
            column: Column
            column = world.get_column(i, j)
            figures: list[Figure] = []
            if column is None or not column.height_difference_are_set:
                continue

            # top sides of blocks
            non_transparent_already_rendered = False
            visible_blocks = column.get_blocks_with_visible_top_sprite()
            for m, block in enumerate(visible_blocks):
                x, y, z = block.x, block.y, block.z
                block_rect = self.layers.get_rect_for_block(x, y, z)
                if self.check_if_in_screen(block_rect):
                    rect_size = block_rect.size
                    if block.is_transparent:
                        if m == 0:
                            raise AssertionError('Bottom visible block must be non transparent')
                        else:
                            sprite = block.get_top_sprite_resized_shaded(rect_size, column.height_difference, z)
                    else:
                        assert not non_transparent_already_rendered
                        non_transparent_already_rendered = True
                        if len(visible_blocks) > 1:
                            sprite = block.get_top_sprite_fully_shaded(rect_size, column.height_difference, z)
                        else:
                            sprite = block.get_top_sprite_resized_shaded(rect_size, column.height_difference, z)

                    figure = Figure(block_rect, sprite, (x, y, z), (x, y, z + 1))
                    figures.append(figure)

            # cache for sides of blocks
            d = TRAPEZOIDS_IN_CACHE_DURATION
            if d > 1:
                if counter % d != frame % d and self.sides_cache.is_in(i, j):
                    figures_from_cache = self.sides_cache.get(i, j, self.camera.get_center(), self.layers)
                    figures += figures_from_cache
                    self.elements.append(figures)
                    continue
                self.sides_cache.pop(i, j)

            # sides of blocks
            top_block = column.get_top_block()
            x, y, z = column.x, column.y, top_block.z
            column_bottom_rect = self.layers.get_rect_for_block(x, y, 0)
            column_top_rect = self.layers.get_rect_for_block(x, y, z)

            full_hd = column.height_difference.full_full_height_diff
            nt_hd = column.height_difference.full_nt_height_diff

            figures_for_cache = []

            values = list(full_hd.values())+list(nt_hd.values())
            for k in range(max(values)):
                side_z = z - k
                block = column.get_block(side_z)
                top_rect = self.layers.get_rect_for_block(x, y, side_z)
                bottom_rect = self.layers.get_rect_for_block(x, y, side_z - 1)
                keys = []
                if column_top_rect.bottom < column_bottom_rect.bottom:
                    keys.append('south')
                if column_top_rect.top > column_bottom_rect.top:
                    keys.append('north')
                if column_top_rect.right < column_bottom_rect.right:
                    keys.append('east')
                if column_top_rect.left > column_bottom_rect.left:
                    keys.append('west')

                for key in keys:
                    if (not block.is_transparent and k < nt_hd[key]) or (block.is_transparent and k < full_hd[key]):
                        sprite, sprite_name = block.get_side_sprite(key, column.get_height_difference(), k)

                        figure = self.sides_drawer.create_figure(x, y, side_z, key,
                                                                 sprite, sprite_name,
                                                                 top_rect, bottom_rect)
                        if figure is not None:
                            figures.append(figure)
                            figures_for_cache.append(figure)

            if len(figures_for_cache) > 0:
                self.sides_cache.add(i, j, figures_for_cache, self.camera.get_center())
            self.elements.append(figures)

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
