import cProfile
import pygame as pg
from camera import CameraFrame, Layers
from world_class import Column, World
from render_order import RenderOrder
from sides_drawer import Figure, SidesDrawer
from constants import *


class ColumnFiguresCache:
    def __init__(self):
        self._cache: dict[tuple[int, int]: Figure] = {}
        self._top_cache: dict[tuple[int, int]: Figure] = {}

    def add(self, i: int, j: int, figures_lst: list[Figure], camera_xy: tuple[float, float]):
        start_rects = list([fig.rect.copy() for fig in figures_lst])
        item = (figures_lst, camera_xy, start_rects)
        key = (i, j)
        self._cache[key] = item

        only_top_figures_lst = []
        only_top_start_rects = []
        for k in range(len(figures_lst)):
            fig = figures_lst[k]
            start_rect = start_rects[k]
            if fig.is_not_side:
                only_top_figures_lst.append(fig)
                only_top_start_rects.append(start_rect)

        only_tops_item = (only_top_figures_lst, camera_xy, only_top_start_rects)
        self._top_cache[key] = only_tops_item

    def is_in_cache(self, i: int, j: int) -> bool:
        return (i, j) in self._cache

    def is_in_top_cache(self, i: int, j: int) -> bool:
        return (i, j) in self._top_cache

    def get(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, old_camera_xy, start_rects = self._cache[key]
        for k, figure in enumerate(figures_lst):
            if figure.is_side:
                start_rect = start_rects[k]
                sizes = start_rect.size
                new_rect = layers.get_rect_for_side(figure.origin_block, figure.directed_block, sizes)
                figure.reset_rect(new_rect)
            elif figure.is_not_side:
                x, y, z = figure.origin_block
                top_left = layers.get_top_left_for_block(x, y, z)
                figure.set_top_left(top_left)
            else:
                raise AssertionError('figure must be side or not side (check directed and origin blocks)')

        return figures_lst

    def get_top_figures(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, old_camera_xy, start_rects = self._top_cache[key]
        for figure, start_rect in zip(figures_lst, start_rects):
            x, y, z = figure.origin_block
            top_left = layers.get_top_left_for_block(x, y, z)
            figure.set_top_left(top_left)
        return figures_lst

    def pop(self, i: int, j: int):
        if (i, j) in self._cache:
            self._cache.pop((i, j))

    def pop_top(self, i: int, j: int):
        if (i, j) in self._top_cache:
            self._top_cache.pop((i, j))

    def clear(self):
        self._top_cache.clear()
        self._cache.clear()


class Mesh3D:
    def __init__(self, sides_drawer: SidesDrawer, camera: CameraFrame, scr_sizes):
        self.sides_drawer = sides_drawer
        self.camera = camera
        self.layers = camera.get_layers()
        self.scr_rect = pg.Rect(0, 0, *scr_sizes)
        self.render_order = RenderOrder()

        self.mouse_rect = None
        self.hovered_block = None
        self.directed_block = None

        self.column_figures_cache = ColumnFiguresCache()

        self.pr = cProfile.Profile()

    def check_if_in_screen(self, rect: pg.Rect) -> bool:
        return rect.colliderect(self.scr_rect)

    def clear_cache(self):
        self.column_figures_cache.clear()

    def create_mesh(self, world: World, frame: int, scr: pg.Surface):
        if frame == 500 and PRINT_3D_MESH_CPROFILE:
            self.pr.enable()
        newly_set_height_columns = world.pop_newly_set_height_columns()
        recently_deleted_columns = world.pop_recently_deleted_columns()
        for i, j in recently_deleted_columns:
            self.column_figures_cache.pop(i, j)
            self.column_figures_cache.pop_top(i, j)

        mouse_pos = pg.mouse.get_pos()
        screen_rect = scr.get_rect()
        rend_order = self.render_order.get_order(self.camera.get_rect())
        camera_xy = self.camera.get_center()

        counter = 0

        for i, j in rend_order:
            figures: list[Figure] = []
            top_figures_from_cache = []
            if (i, j) in newly_set_height_columns:
                self.column_figures_cache.pop_top(i, j)

            counter += 1
            d = COLUMN_FIGURES_IN_CACHE_DURATION
            top_d = d * TOP_FIGURES_DURATION_MULTIPLAYER
            if d > 1:
                if self.column_figures_cache.is_in_cache(i, j):
                    if counter % d != frame % d:
                        figures_from_cache = self.column_figures_cache.get(i, j, self.layers)
                        figures += figures_from_cache
                        collide_screen = self.blit_column_figures(figures, scr, mouse_pos, screen_rect)
                        if not collide_screen:
                            self.column_figures_cache.pop(i, j)
                            self.column_figures_cache.pop_top(i, j)
                            self.column_figures_cache.add(i, j, [], camera_xy)
                        continue
                    else:
                        self.column_figures_cache.pop(i, j)

                if self.column_figures_cache.is_in_top_cache(i, j):
                    if counter % top_d == frame % top_d:
                        self.column_figures_cache.pop_top(i, j)
                    else:
                        top_figures_from_cache = self.column_figures_cache.get_top_figures(i, j, self.layers)

            column: Column
            column = world.get_column(i, j)

            if column is None or not column.height_difference_are_set:
                continue

            invisible_block = column.get_first_invisible_block()
            x, y, z = column.x, column.y, invisible_block.z
            invisible_block_rect = self.layers.get_rect_for_block(x, y, z)

            if not invisible_block_rect.colliderect(screen_rect):
                continue

            # top sides of blocks
            if len(top_figures_from_cache) != 0:
                figures += top_figures_from_cache
            else:
                non_transparent_already_rendered = False
                visible_blocks = column.get_blocks_with_visible_top_sprite()
                for m, block in enumerate(visible_blocks):
                    x, y, z = block.x, block.y, block.z
                    block_rect = self.layers.get_rect_for_block(x, y, z)

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

            # sides of blocks

            full_hd = column.height_difference.full_full_height_diff
            nt_hd = column.height_difference.full_nt_height_diff

            top_block = column.get_top_block()
            x, y, z = column.x, column.y, top_block.z
            column_top_rect = self.layers.get_rect_for_block(x, y, z)
            column_bottom_rect = self.layers.get_rect_for_block(x, y, 0)

            values = list(full_hd.values())+list(nt_hd.values())
            max_value = max(values)
            if max_value > 0:

                keys = []
                if column_top_rect.bottom < column_bottom_rect.bottom:
                    keys.append('south')
                if column_top_rect.top > column_bottom_rect.top:
                    keys.append('north')
                if column_top_rect.right < column_bottom_rect.right:
                    keys.append('east')
                if column_top_rect.left > column_bottom_rect.left:
                    keys.append('west')

                last_bottom_rect = column_top_rect
                for k in range(max_value):
                    side_z = z - k
                    block = column.get_block(side_z)
                    top_rect = last_bottom_rect
                    bottom_rect = self.layers.get_rect_for_block(x, y, side_z - 1)

                    for key in keys:
                        non_transparent_side = not block.is_transparent and k < nt_hd[key]
                        transparent_side = block.is_transparent and k < full_hd[key]
                        if non_transparent_side or transparent_side:
                            sprite, sprite_name = block.get_side_sprite(key, column.get_height_difference(), k)

                            figure = self.sides_drawer.create_figure(x, y, side_z, key,
                                                                     sprite, sprite_name,
                                                                     top_rect, bottom_rect)
                            if figure is not None:
                                figures.append(figure)
                    last_bottom_rect = bottom_rect

            if len(figures) > 0:
                collide_screen = self.blit_column_figures(figures, scr, mouse_pos, screen_rect)
                if collide_screen:
                    self.column_figures_cache.add(i, j, figures, camera_xy)

        if frame == 2000 and PRINT_3D_MESH_CPROFILE:
            self.pr.create_stats()
            self.pr.print_stats(sort='cumtime')
            self.pr.print_stats(sort='tottime')
            self.pr.print_stats(sort='ncalls')

    def blit_column_figures(self, figures: list[Figure],
                            scr: pg.Surface,
                            mouse_pos: tuple[int, int],
                            screen_rect: pg.Rect) -> bool:
        collide_screen = False

        for figure in figures:
            rect, sprite = figure.rect, figure.sprite
            if screen_rect.colliderect(rect):
                scr.blit(sprite, rect)
                collide_screen = True

            if rect.collidepoint(mouse_pos):
                self.mouse_rect = rect.copy()
                self.hovered_block = figure.origin_block
                self.directed_block = figure.directed_block

        return collide_screen
