# import time
import pygame as pg
from camera import Layers
from world import Column
from trapezoid import SidesDrawer
sides_drawer = SidesDrawer()
sides_drawer.set_debug_mode(False)
sides_drawer.set_fast_anisotropic(False)
sides_drawer.set_using_perspective(True)
sides_drawer.set_using_cache(True)


class TerrainMech:
    def __init__(self, columns, layers: Layers):
        """columns: generator -> Column"""
        # total_time = 0

        last_x = None
        # two-dim list of figures list, figure: tuple[pg.Rect, pg.Surface]
        self.elements: list[list[list[tuple[pg.Rect, pg.Surface]]]] = []
        r = []
        for column in columns:
            column: Column
            # start = time.time()
            # total_time += time.time() - start

            # top sprites of blocks
            top_block = column.get_top_block()
            x, y, z = column.x, column.y, top_block.z
            rect_size = layers.get_n_level_size(z)
            rect = layers.get_rect(x, y, z)
            sprite = top_block.get_top_sprite_resized(rect_size)
            top_figure = (rect, sprite)

            # sides of blocks
            sides_figures: list[tuple[pg.Rect, pg.Surface]] = []
            hd = column.height_difference
            # bottom side
            if hd['bottom'] > 0:
                top_rect = layers.get_rect(x, y, z)
                bottom_rect = layers.get_rect(x, y, 0)
                if top_rect.bottom < bottom_rect.bottom:
                    for i in range(hd['bottom']):
                        side_z = z - i
                        block_for_side = column.get_block(side_z)
                        bottom_sprite = block_for_side.get_side_sprite('bottom')
                        top_rect = layers.get_rect(x, y, side_z)
                        bottom_rect = layers.get_rect(x, y, side_z-1)

                        left_top = top_rect.bottomleft
                        right_top = top_rect.bottomright
                        left_bottom = bottom_rect.bottomleft
                        right_bottom = bottom_rect.bottomright

                        top = right_top[0] - left_top[0]
                        bottom = right_bottom[0] - left_bottom[0]
                        offset = left_bottom[0] - left_top[0]
                        height = left_bottom[1] - left_top[1]
                        trapezoid_sprite = sides_drawer.get_hor_trapezoid(bottom_sprite, top, bottom,  height, offset)

                        rect_left = min(left_top[0], left_bottom[0])
                        rect = pg.Rect((rect_left, left_top[1]), trapezoid_sprite.get_rect().size)
                        figure = (rect, trapezoid_sprite)
                        sides_figures.append(figure)

            if last_x is not None and last_x != top_block.x:
                self.elements.append(r)
                r = []
            last_x = top_block.x
            r.append([top_figure, *sides_figures])
        self.elements.append(r)
        # print('total', int(1/total_time) if total_time != 0 else None, total_time)

    def get_elements_in_order(self, focus_in_frame: tuple[int, int]) -> list[list[tuple[pg.Rect, pg.Surface]]]:
        ordered: list[list[tuple[pg.Rect, pg.Surface]]] = []
        width = len(self.elements[0])
        height = len(self.elements)
        i, j = focus_in_frame
        ordered.append(self.elements[i][j])
        r = 0
        # Adding rhombuses sides
        while len(ordered) != width * height:
            r += 1
            # from top to right ------------
            x, y = i, j + r
            top_right = []
            for n in range(r):
                i1, j1 = x + n, y - n
                if 0 <= i1 < len(self.elements) and 0 <= j1 < len(self.elements[0]):
                    top_right.append(self.elements[i1][j1])
            ordered += top_right
            # from left to top ------------
            x, y = i - r, j
            left_top = []
            for n in range(r):
                i1, j1 = x + n, y + n
                if 0 <= i1 < len(self.elements) and 0 <= j1 < len(self.elements[0]):
                    left_top.append(self.elements[i1][j1])
            ordered += left_top
            # from bottom to left ------------
            x, y = i, j - r
            bottom_left = []
            for n in range(r):
                i1, j1 = x - n, y + n
                if 0 <= i1 < len(self.elements) and 0 <= j1 < len(self.elements[0]):
                    bottom_left.append(self.elements[i1][j1])
            ordered += bottom_left
            # from right to bottom ------------
            x, y = i + r, j
            right_bottom = []
            for n in range(r):
                i1, j1 = x - n, y - n
                if 0 <= i1 < len(self.elements) and 0 <= j1 < len(self.elements[0]):
                    right_bottom.append(self.elements[i1][j1])
            ordered += right_bottom

        return ordered[::-1]
