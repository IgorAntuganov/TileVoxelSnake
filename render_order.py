import pygame as pg


class RenderOrder:
    def __init__(self):
        self._size_cache = {}
        self._order_cache = {}

    def create_order(self, rect: pg.Rect) -> list[tuple[int, int]]:
        ordered: list[tuple[int, int]] = []

        width = rect.width
        height = rect.height
        key = (width, height)
        if key in self._size_cache:
            return self._size_cache[key]

        i, j = (width-1) // 2, (height-1) // 2
        ordered.append((i, j))
        r = 0
        # Adding rhombuses sides
        while len(ordered) != width * height:
            r += 1
            # from top to right ------------
            x, y = i, j + r
            top_right = []
            for n in range(r):
                i1, j1 = x + n, y - n
                if 0 <= i1 < width and 0 <= j1 < height:
                    top_right.append((i1, j1))
            ordered += top_right
            # from left to top ------------
            x, y = i - r, j
            left_top = []
            for n in range(r):
                i1, j1 = x + n, y + n
                if 0 <= i1 < width and 0 <= j1 < height:
                    left_top.append((i1, j1))
            ordered += left_top
            # from bottom to left ------------
            x, y = i, j - r
            bottom_left = []
            for n in range(r):
                i1, j1 = x - n, y + n
                if 0 <= i1 < width and 0 <= j1 < height:
                    bottom_left.append((i1, j1))
            ordered += bottom_left
            # from right to bottom ------------
            x, y = i + r, j
            right_bottom = []
            for n in range(r):
                i1, j1 = x - n, y - n
                if 0 <= i1 < width and 0 <= j1 < height:
                    right_bottom.append((i1, j1))
            ordered += right_bottom

        ordered = ordered[::-1]
        self._size_cache[key] = ordered
        return ordered

    def get_order(self, rect: pg.Rect) -> list[tuple[int, int]]:
        if len(self._order_cache) > 100:
            self._order_cache.clear()

        key2 = *rect.topleft, *rect.bottomright
        if key2 in self._order_cache:
            return self._order_cache[key2]

        offset = rect.topleft
        offset_x, offset_y = offset
        width = rect.width
        height = rect.height
        key = (width, height)
        if key in self._size_cache:
            order = self._size_cache[key]
        else:
            order = self.create_order(rect)

        order_with_offset = []
        for i, j in order:
            coords = i + offset_x, j + offset_y
            order_with_offset.append(coords)
        self._order_cache[key2] = order_with_offset
        return order_with_offset
