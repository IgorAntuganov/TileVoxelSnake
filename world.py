from blocks import *


class Column:
    def __init__(self, x, y, blocks: list[Block]):
        """:param blocks: blocks from top to bottom"""
        self.x = x
        self.y = y
        self.blocks = blocks
        self.height = len(blocks)
        self.neighbors = []

    def copy_to_x_y(self, x, y):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        return Column(x, y, new_blocks)

    def get_top_block(self):
        return self.blocks[0]


class World:
    def __init__(self):
        # self.regions: dict[(int, int): list[list[Column]]] = {}
        self.columns = {}
        self.not_found_column: Column = Column(0, 0, [DebugBlock(0, 0, 0)])

    def test_fill(self):
        blocks1 = [Dirt(0, 0, 2), Dirt(0, 0, 1), Stone(0, 0, 0)]
        blocks2 = [Grass(0, 0, 4), Dirt(0, 0, 3), Dirt(0, 0, 2), Stone(0, 0, 1), Stone(0, 0, 0)]
        test_column_1 = Column(0, 0, blocks1)
        test_column_2 = Column(0, 0, blocks2)
        for i in range(-30, 151):
            for j in range(-150, 151):
                if (i % 2 == j % 2 and not(abs(i) < 10 and abs(j) < 10)) or i > 1 and j > 1:
                    column = test_column_1
                else:
                    column = test_column_2
                self.columns[(i, j)] = column.copy_to_x_y(i, j)

    def get_columns_in_rect_generator(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if (i, j) in self.columns:
                    yield self.columns[(i, j)]
                else:
                    yield self.not_found_column.copy_to_x_y(i, j)
