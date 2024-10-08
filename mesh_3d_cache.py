import pygame as pg
from mesh_3d_figures import Figure
from camera import Layers
from constants import *


class ColumnFiguresCache:
    def __init__(self):
        self._cache: dict[tuple[int, int]: tuple[list[Figure], list[pg.Rect]]] = {}
        self._infinite_top_cache: dict[tuple[int, int]: tuple[list[Figure], list[pg.Rect]]] = {}
        self._plains_cache: dict[tuple[int, int]: tuple[Figure, pg.Rect]] = {}

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

    def get_moved_top_figures(self, i: int, j: int, layers: Layers) -> list[Figure]:
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

    def get_top_figures(self, i: int, j: int, layers: Layers) -> list[Figure]:
        key = (i, j)
        figures_lst, start_rects = self._infinite_top_cache[key]
        figures = []
        for figure, start_rect in zip(figures_lst, start_rects):
            x, y, z = figure.origin_block
            top_left = layers.get_top_left_for_block(x, y, z)
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
