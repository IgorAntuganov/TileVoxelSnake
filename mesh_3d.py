import cProfile
import pygame as pg
from camera import CameraFrame, Layers
from world_class import Column, World
from world_region import Region
from render_order import RenderOrder
from sides_drawer import Figure, SidesDrawer
import blocks
from constants import *


class ColumnFiguresCache:
    def __init__(self):
        self._cache: dict[tuple[int, int]: tuple[list[Figure], list[pg.Rect]]] = {}
        self._infinite_top_cache: dict[tuple[int, int]: tuple[list[Figure], list[pg.Rect]]] = {}
        self._plains_cache: dict[tuple[int, int]: tuple[Figure, pg.Rect]] = {}

    def print_cache_sizes(self):
        print('Cache Sizes: -------------------')
        print('Cache:', len(self._cache))
        print('Infinite top cache:', len(self._infinite_top_cache))
        print('Plains cache:', len(self._plains_cache))

    def add(self, i: int, j: int, figures_lst: list[Figure], is_column_at_plain: bool):
        start_rects = list([fig.rect.copy() for fig in figures_lst])
        item = (figures_lst, start_rects)
        key = (i, j)

        if is_column_at_plain:
            plain_item = figures_lst[0], start_rects[0]
            self._plains_cache[(i, j)] = plain_item
        else:
            self._cache[key] = item

            only_top_figures_lst = []
            only_top_start_rects = []
            for k in range(len(figures_lst)):
                fig = figures_lst[k]
                start_rect = start_rects[k]
                if fig.is_not_side:
                    only_top_figures_lst.append(fig)
                    only_top_start_rects.append(start_rect)

            only_tops_item = (only_top_figures_lst, only_top_start_rects)
            self._infinite_top_cache[key] = only_tops_item

    def is_in_cache(self, i: int, j: int) -> bool:
        return (i, j) in self._cache

    def is_in_infinite_top_cache(self, i: int, j: int) -> bool:
        return (i, j) in self._infinite_top_cache

    def is_in_plains_cache(self, i: int, j: int) -> bool:
        return (i, j) in self._plains_cache

    def get(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figures = []
        figures_lst, start_rects = self._cache[key]
        for k, figure in enumerate(figures_lst):
            if figure.is_side:
                start_rect = start_rects[k]
                sizes = start_rect.size
                new_rect = layers.get_rect_for_side(figure.origin_block, figure.directed_block, sizes)
                figure.reset_rect(new_rect)
                figures.append(figure)
            elif figure.is_not_side:
                x, y, z = figure.origin_block
                top_left = layers.get_top_left_for_block(x, y, z)
                figure.set_top_left(top_left)
                figures.append(figure)
            else:
                raise AssertionError('figure must be side or not side (check directed and origin blocks)')

        return figures

    def get_top_figures(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, start_rects = self._infinite_top_cache[key]
        figures = []
        for figure, start_rect in zip(figures_lst, start_rects):
            x, y, z = figure.origin_block
            top_left = layers.get_top_left_for_block(x, y, z)
            old_top_left = figure.rect.topleft
            if top_left != old_top_left:
                figure.set_top_left(top_left)
                figures.append(figure)
        return figures

    def get_plain_figures(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figure, start_rect = self._plains_cache[key]
        x, y, z = figure.origin_block
        top_left = layers.get_top_left_for_block(x, y, z)
        figure.set_top_left(top_left)
        return [figure]

    def pop(self, i: int, j: int):
        if (i, j) in self._cache:
            self._cache.pop((i, j))

    def pop_edited(self, i: int, j: int):
        if (i, j) in self._infinite_top_cache:
            self._infinite_top_cache.pop((i, j))
        if (i, j) in self._plains_cache:
            self._plains_cache.pop((i, j))

    def clear(self):
        self._infinite_top_cache.clear()
        self._cache.clear()
        self._plains_cache.clear()


class RegionLODsCache:
    def __init__(self):
        self._cache: dict[tuple[int, int, int]] = {}

    def add(self, lod: pg.Surface, ind: tuple[int, int], base_level_size):
        key = (ind[0], ind[1], base_level_size)
        size = WORLD_CHUNK_SIZE * base_level_size
        resized = pg.transform.smoothscale(lod, (size, size))
        self._cache[key] = resized

    def is_in(self, ind, size):
        return (ind[0], ind[1], size) in self._cache

    def get(self, ind, size):
        return self._cache[(ind[0], ind[1], size)]

    def clear(self):
        self._cache.clear()


class FigureCreator:
    def __init__(self, layers: Layers, sides_drawer: SidesDrawer):
        self.layers = layers
        self.sides_drawer = sides_drawer

    def create_top_figures_for_column(self, column: Column) -> list[Figure]:
        figures = []
        non_transparent_already_rendered = False
        visible_blocks = column.get_blocks_with_visible_top_sprite()
        for m, block in enumerate(visible_blocks):
            if type(block) == blocks.Shadow:
                continue

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
                    sprite = block.get_top_sprite_fully_shaded(rect_size, column.height_difference, z, False)
                else:
                    sprite = block.get_top_sprite_resized_shaded(rect_size, column.height_difference, z)

            figure = Figure(block_rect, sprite, (x, y, z), (x, y, z + 1))
            figures.append(figure)
        return figures

    def create_side_figures_for_column(self, column: Column) -> list[Figure]:
        figures = []

        full_hd = column.height_difference.full_full_height_diff
        nt_hd = column.height_difference.full_nt_height_diff

        top_block = column.get_top_block()
        x, y, z = column.x, column.y, top_block.z
        column_top_rect = self.layers.get_rect_for_block(x, y, z)
        column_bottom_rect = self.layers.get_rect_for_block(x, y, 0)

        keys = []
        if column_top_rect.bottom < column_bottom_rect.bottom:
            keys.append('south')
        if column_top_rect.top > column_bottom_rect.top:
            keys.append('north')
        if column_top_rect.right < column_bottom_rect.right:
            keys.append('east')
        if column_top_rect.left > column_bottom_rect.left:
            keys.append('west')

        values = list(full_hd.values()) + list(nt_hd.values())
        max_value = max(values)
        last_bottom_rect = column_top_rect
        for k in range(max_value):
            side_z = z - k
            top_rect = last_bottom_rect
            bottom_rect = self.layers.get_rect_for_block(x, y, side_z - 1)

            block = column.get_block(side_z)
            if type(block) == blocks.Shadow:
                last_bottom_rect = bottom_rect
                continue

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
        return figures


class Mesh3D:
    def __init__(self, sides_drawer: SidesDrawer, camera: CameraFrame, scr_sizes):
        self.figures_creator = FigureCreator(camera.get_layers(), sides_drawer)
        self.camera = camera
        self.layers = camera.get_layers()
        self.scr_rect = pg.Rect(0, 0, *scr_sizes)
        self.render_order = RenderOrder()

        self.mouse_rect = None
        self.hovered_block = None
        self.directed_block = None
        self.mouse_hovering_sprite_expected: bool = False

        self.column_figures_cache = ColumnFiguresCache()
        self.region_LODs_cache = RegionLODsCache()

        self.pr = cProfile.Profile()

    def turn_on_cprofile(self, frame: int):
        if frame == 500 and PRINT_3D_MESH_CPROFILE:
            self.pr.enable()

    def check_cprofile_ends(self, frame: int):
        if frame == 2001 and PRINT_3D_MESH_CPROFILE:
            self.pr.create_stats()
            self.pr.print_stats(sort='cumtime')
            self.pr.print_stats(sort='tottime')
            self.pr.print_stats(sort='ncalls')

    def clear_cache(self):
        self.column_figures_cache.clear()
        self.region_LODs_cache.clear()

    def remove_edited_columns_from_cache(self, world: World):
        newly_set_height_columns = world.pop_newly_set_height_columns()
        recently_deleted_columns = world.pop_recently_deleted_columns()
        edited_columns = newly_set_height_columns.union(recently_deleted_columns)
        for i, j in edited_columns:
            self.column_figures_cache.pop(i, j)
            self.column_figures_cache.pop_edited(i, j)

    def is_column_in_screen(self, column: Column, screen_rect: pg.Rect) -> bool:
        invisible_block = column.get_first_invisible_block()
        x, y, z = column.x, column.y, invisible_block.z
        invisible_block_rect = self.layers.get_rect_for_block(x, y, z)
        return invisible_block_rect.colliderect(screen_rect)

    def blit_column_figures(self, figures: list[Figure],
                            scr: pg.Surface,
                            mouse_pos: tuple[int, int]):

        for figure in figures:
            rect, sprite = figure.rect, figure.sprite
            scr.blit(sprite, rect)

            if rect.collidepoint(mouse_pos):
                self.mouse_rect = rect.copy()
                self.hovered_block = figure.origin_block
                self.directed_block = figure.directed_block

    def draw_world_columns(self, world: World, frame: int, scr: pg.Surface):
        self.turn_on_cprofile(frame)
        self.check_cprofile_ends(frame)

        # self.column_figures_cache.print_cache_sizes()

        self.remove_edited_columns_from_cache(world)

        mouse_pos = pg.mouse.get_pos()
        screen_rect = scr.get_rect()

        d = COLUMN_FIGURES_IN_CACHE_DURATION
        no_sides_drawing = self.layers.base_level_size < NO_SIDES_LEVEL

        counter = 0
        rend_order = self.render_order.get_order(self.camera.get_rect())
        for i, j in rend_order:
            counter += 1

            if self.column_figures_cache.is_in_plains_cache(i, j):
                plain_figures = self.column_figures_cache.get_plain_figures(i, j, self.layers)
                self.blit_column_figures(plain_figures, scr, mouse_pos)
                continue

            column_figures_need_update = counter % d == frame % d
            if d > 1 and self.column_figures_cache.is_in_cache(i, j) and not no_sides_drawing:
                if not column_figures_need_update:
                    figures_from_cache = self.column_figures_cache.get(i, j, self.layers)
                    self.blit_column_figures(figures_from_cache, scr, mouse_pos)
                    continue
                else:
                    self.column_figures_cache.pop(i, j)

            infinite_top_figures: list[Figure] = []
            if self.column_figures_cache.is_in_infinite_top_cache(i, j):
                infinite_top_figures = self.column_figures_cache.get_top_figures(i, j, self.layers)
                if no_sides_drawing:
                    self.blit_column_figures(infinite_top_figures, scr, mouse_pos)
                    continue

            column = world.get_column(i, j)  # expensive
            if column is None or not column.height_difference_are_set:
                continue
            if not self.is_column_in_screen(column, screen_rect):
                continue

            figures: list[Figure] = []
            if len(infinite_top_figures) != 0:
                figures += infinite_top_figures
            else:
                figures += self.figures_creator.create_top_figures_for_column(column)

            if not no_sides_drawing:
                figures += self.figures_creator.create_side_figures_for_column(column)

            self.blit_column_figures(figures, scr, mouse_pos)

            if len(figures) > len(infinite_top_figures):
                self.column_figures_cache.add(i, j, figures, column.is_at_plain())

    def create_region_lod(self, region: Region) -> pg.Surface:
        size = WORLD_CHUNK_SIZE * self.layers.base_level_size
        lod = pg.Surface((size, size))
        left, top = region.get_rect().topleft
        for m in range(WORLD_CHUNK_SIZE):
            for n in range(WORLD_CHUNK_SIZE):
                i = left + m
                j = top + n
                if self.column_figures_cache.is_in_infinite_top_cache(i, j):
                    top_figures = self.column_figures_cache.get_top_figures(i, j, self.layers)
                else:
                    column = region.get_column(i, j)
                    top_figures = self.figures_creator.create_top_figures_for_column(column)
                x = m * self.layers.base_level_size
                y = n * self.layers.base_level_size
                for figure in top_figures:
                    lod.blit(figure.sprite, (x, y))
        return lod

    def draw_regions(self, world: World, scr: pg.Surface):
        camera_rect = self.camera.get_rect()
        left = camera_rect.left // WORLD_CHUNK_SIZE
        top = camera_rect.top // WORLD_CHUNK_SIZE
        width = camera_rect.width // WORLD_CHUNK_SIZE + 2
        height = camera_rect.height // WORLD_CHUNK_SIZE + 2

        for i in range(width):
            for j in range(height):
                ind = left + i, top + j
                if world.check_is_region_ready_by_ind(*ind):
                    if not self.region_LODs_cache.is_in(ind, self.layers.base_level_size):
                        region = world.get_region_by_ind(*ind)
                        lod = self.create_region_lod(region)
                        self.region_LODs_cache.add(lod, ind, self.layers.base_level_size)
                    lod = self.region_LODs_cache.get(ind, self.layers.base_level_size)

                    m = (left + i) * WORLD_CHUNK_SIZE
                    n = (top + j) * WORLD_CHUNK_SIZE
                    top_left_block = self.layers.get_top_left_for_block(m, n, 0)

                    x = int(top_left_block[0])
                    y = int(top_left_block[1])
                    scr.blit(lod, (x, y))
