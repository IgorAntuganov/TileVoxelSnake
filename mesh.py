import pygame as pg
from camera import Layers
# import time


class TerrainMech:
    def __init__(self, columns, layers: Layers):
        """columns: generator -> Column"""
        # total_time = 0

        last_x = None
        self.elements: list[list[tuple[pg.Rect, pg.Surface]]] = []
        r = []
        for column in columns:
            # start = time.time()
            top_block = column.get_top_block()
            # total_time += time.time() - start
            z = top_block.z
            rect_size = layers.get_n_level_size(z)
            x0, y0 = layers.get_n_level_x0_y0(z)
            left = x0 + top_block.x * rect_size
            top = y0 + top_block.y * rect_size
            rect = pg.Rect(left, top, rect_size, rect_size)
            sprite = top_block.get_top_sprite_resized(rect_size)
            figure = (rect, sprite)
            if last_x is not None and last_x != top_block.x:
                self.elements.append(r)
                r = []
            last_x = top_block.x
            r.append(figure)
        self.elements.append(r)
        # print('total', int(1/total_time) if total_time != 0 else None, total_time)

    def get_elements_in_order(self, focus_in_frame: tuple[int, int]) -> list[tuple[pg.Rect, pg.Surface]]:
        ordered: list[tuple[pg.Rect, pg.Surface]] = []
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
