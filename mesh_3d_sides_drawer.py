import pygame as pg
from trapezoid import TrapezoidDrawer
from mesh_3d_figures import SimpleFigure
from constants import *


class SidesDrawer:
    def __init__(self, trap_drawer: TrapezoidDrawer, scr_rect: pg.Rect):
        self.trap_drawer = trap_drawer
        self.scr_rect = scr_rect
        self.functions = {
            'north': self.create_north_figure,
            'west': self.create_west_figure,
            'south': self.create_south_figure,
            'east': self.create_east_figure,
        }

    def create_figure(self, x, y, z, key, sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> SimpleFigure | None:
        assert key in SIDES_NAMES
        func = self.functions[key]
        return func(x, y, z, sprite, sprite_name, top_rect, bottom_rect)

    def create_south_figure(self, x, y, z,
                            sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> SimpleFigure | None:
        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.bottom - top_rect.bottom

        sizes = self.trap_drawer.get_hor_trapezoid_sizes(top + 3, bottom + 3, height, offset)
        rect_left = min(top_rect.left, bottom_rect.left)
        rect = pg.Rect((rect_left - 1, top_rect.bottom), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid = self.trap_drawer.get_hor_trapezoid(sprite, sprite_name, top + 3, bottom + 3, height, offset)
            return SimpleFigure(rect, trapezoid, (x, y, z), (x, y + 1, z))

    def create_north_figure(self, x, y, z,
                            sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> SimpleFigure | None:
        top = top_rect.right - top_rect.left
        bottom = bottom_rect.right - bottom_rect.left
        offset = bottom_rect.left - top_rect.left
        height = bottom_rect.top - top_rect.top

        rect_left = min(bottom_rect.left, top_rect.left)
        sizes = self.trap_drawer.get_hor_trapezoid_sizes(top + 1, bottom + 1, height, offset)
        rect = pg.Rect((rect_left, bottom_rect.top), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid = self.trap_drawer.get_hor_trapezoid(sprite, sprite_name, top + 1, bottom + 1, height, offset)
            return SimpleFigure(rect, trapezoid, (x, y, z), (x, y - 1, z))

    def create_east_figure(self, x, y, z,
                           sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> SimpleFigure | None:
        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.right - top_rect.right
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = self.trap_drawer.get_vert_trapezoid_sizes(left + 3, right + 3, width, offset)
        rect = pg.Rect((top_rect.right, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid = self.trap_drawer.get_vert_trapezoid(sprite, sprite_name, left + 3, right + 3, width, offset)
            return SimpleFigure(rect, trapezoid, (x, y, z), (x + 1, y, z))

    def create_west_figure(self, x, y, z,
                           sprite: pg.Surface, sprite_name, top_rect, bottom_rect) -> SimpleFigure | None:
        left = top_rect.bottom - top_rect.top
        right = bottom_rect.bottom - bottom_rect.top
        width = bottom_rect.left - top_rect.left
        offset = bottom_rect.top - top_rect.top

        rect_top = min(bottom_rect.top, top_rect.top)
        sizes = self.trap_drawer.get_vert_trapezoid_sizes(left + 3, right + 3, width, offset)
        rect = pg.Rect((bottom_rect.left, rect_top - 1), sizes)

        if rect.colliderect(self.scr_rect):
            trapezoid = self.trap_drawer.get_vert_trapezoid(sprite, sprite_name, left + 3, right + 3, width, offset)
            return SimpleFigure(rect, trapezoid, (x, y, z), (x - 1, y, z))
