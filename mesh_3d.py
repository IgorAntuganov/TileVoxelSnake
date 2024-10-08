import cProfile
import pygame as pg
from camera import CameraFrame
from world_class import Column, World
from world_region import Region
from render_order import RenderOrder
from mesh_3d_sides_drawer import SidesDrawer
from mesh_3d_figures import ManySpritesTopFigure, Figure, SimpleFigure
from mesh_3d_cache import ColumnFiguresCache, RegionLODsCache
from mesh_3d_figure_creator import FigureCreator
from constants import *


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
                            tick: int,
                            mouse_pos: tuple[int, int]):

        for figure in figures:
            if type(figure) is SimpleFigure:
                figure: SimpleFigure
                rect, sprite = figure.rect, figure.sprite
                scr.blit(sprite, rect)
            elif type(figure) is ManySpritesTopFigure:
                figure: ManySpritesTopFigure
                rect = figure.rect
                sprite = figure.get_sprite(tick)
                scr.blit(sprite, rect)
            else:
                raise TypeError

            if rect.collidepoint(mouse_pos):
                self.mouse_rect = rect.copy()
                self.hovered_block = figure.origin_block
                self.directed_block = figure.directed_block

    def draw_world_columns(self, world: World, frame: int, scr: pg.Surface):
        tick = frame // 12 % ANIMATION_TICKS_AMOUNT

        self.turn_on_cprofile(frame)
        self.check_cprofile_ends(frame)

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
                self.blit_column_figures(plain_figures, scr, tick, mouse_pos)
                continue

            column_figures_need_update = counter % d == frame % d
            if d > 1 and self.column_figures_cache.is_in_cache(i, j) and not no_sides_drawing:
                if not column_figures_need_update:
                    figures_from_cache = self.column_figures_cache.get(i, j, self.layers)
                    self.blit_column_figures(figures_from_cache, scr, tick, mouse_pos)
                    continue
                else:
                    self.column_figures_cache.pop(i, j)

            infinite_top_figures: list[Figure] = []
            if self.column_figures_cache.is_in_infinite_top_cache(i, j):
                if no_sides_drawing:
                    infinite_top_figures = self.column_figures_cache.get_top_figures(i, j, self.layers)
                    self.blit_column_figures(infinite_top_figures, scr, tick, mouse_pos)
                    continue
                infinite_top_figures = self.column_figures_cache.get_moved_top_figures(i, j, self.layers)

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

            self.blit_column_figures(figures, scr, tick, mouse_pos)

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
                    top_figures = self.column_figures_cache.get_moved_top_figures(i, j, self.layers)
                else:
                    column = region.get_column(i, j)
                    top_figures = self.figures_creator.create_top_figures_for_column(column)
                x = m * self.layers.base_level_size
                y = n * self.layers.base_level_size
                for figure in top_figures:
                    if type(figure) == SimpleFigure:
                        figure: SimpleFigure
                        lod.blit(figure.sprite, (x, y))
                    elif type(figure) == ManySpritesTopFigure:
                        figure: ManySpritesTopFigure
                        lod.blit(figure.get_sprite_for_lod(), (x, y))
                    else:
                        raise TypeError
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
