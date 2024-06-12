from blocks import *


class Column:
    def __init__(self, x, y, blocks: list[FullBlock]):
        """:param blocks: blocks from top to bottom"""
        self.x = x
        self.y = y
        self.blocks = blocks
        self.height = len(blocks)
        self.height_difference: dict[str: int] = {
            'left': 0,
            'top': 0,
            'right': 0,
            'bottom': 0
        }
        self.height_difference_are_set = False

    def copy_to_x_y(self, x, y):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        return Column(x, y, new_blocks)

    def get_top_block(self) -> FullBlock:
        return self.blocks[0]

    def get_block(self, z) -> FullBlock:
        return self.blocks[-z-1]

    def set_height_difference(self, left, top, right, bottom):
        """left, top, right, bottom - adjacent Columns"""
        self.height_difference['left'] = self.height - left.height
        self.height_difference['top'] = self.height - top.height
        self.height_difference['right'] = self.height - right.height
        self.height_difference['bottom'] = self.height - bottom.height
        self.height_difference_are_set = True

    def get_height_difference(self) -> dict[str: int]:
        assert self.height_difference_are_set is True
        return self.height_difference


class World:
    def __init__(self):
        # self.regions: dict[(int, int): list[list[Column]]] = {}
        self.columns = {}
        self.not_found_column: Column = Column(0, 0, [DebugBlock(0, 0, 0)])

    def test_fill(self):
        blocks1 = [Stone(0, 0, 2), Dirt(0, 0, 1), Stone(0, 0, 0)]
        blocks2 = [Grass(0, 0, 3),  Dirt(0, 0, 2), Stone(0, 0, 1), Stone(0, 0, 0)]
        test_column_1 = Column(0, 0, blocks1)
        test_column_2 = Column(0, 0, blocks2)
        for i in range(-30, 151):
            for j in range(-150, 51):
                if (i % 2 == j % 2 and not(abs(i) < 10 and abs(j) < 10)) or i > 1 and j > 1:
                    column = test_column_1
                else:
                    column = test_column_2
                self.columns[(i, j)] = column.copy_to_x_y(i, j)
        self.set_columns_h_diff_in_rect(pg.Rect(-40, -160, 200, 240))

    def get_column(self, x, y) -> Column:
        if (x, y) in self.columns:
            return self.columns[(x, y)]
        else:
            return self.not_found_column.copy_to_x_y(x, y)

    def set_columns_h_diff_in_rect(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                column = self.get_column(i,   j)
                left   = self.get_column(i-1, j)
                top    = self.get_column(i,   j-1)
                right  = self.get_column(i+1, j)
                bottom = self.get_column(i,   j+1)
                column.set_height_difference(left, top, right, bottom)

    def get_columns_in_rect_generator(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if (i, j) in self.columns:
                    yield self.columns[(i, j)]
                else:
                    yield self.not_found_column.copy_to_x_y(i, j)
