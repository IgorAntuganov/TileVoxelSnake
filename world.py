from blocks import *


class Column:
    def __init__(self, x, y, blocks: list[Block]):
        """:param blocks: blocks from top to bottom"""
        self.x = x
        self.y = y
        self.blocks = blocks

    def copy_to_x_y(self, x, y):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        return Column(x, y, new_blocks)

    def get_first_not_air(self):
        for block in self.blocks:
            if type(block) != Air:
                return block
        return DebugBlock(self.x, self.y, 0)


class World:
    def __init__(self):
        # self.regions: dict[(int, int): list[list[Column]]] = {}
        self.columns = {}
        self.not_found_column = Column(0, 0, [Air(0, 0, 0)])

    def test_fill(self):
        blocks1 = [Air(0, 0, 5), Air(0, 0, 4), Air(0, 0, 3), Dirt(0, 0, 2), Dirt(0, 0, 1), Stone(0, 0, 0)]
        blocks2 = [Air(0, 0, 5), Grass(0, 0, 4), Dirt(0, 0, 3), Dirt(0, 0, 2), Stone(0, 0, 1), Stone(0, 0, 0)]
        test_column_1 = Column(0, 0, blocks1)
        test_column_2 = Column(0, 0, blocks2)
        for i in range(-50, 51):
            for j in range(-50, 51):
                if i % 2 == j % 2 and not(abs(i) < 10 and abs(j) < 10):
                    column = test_column_1
                else:
                    column = test_column_2
                self.columns[(i, j)] = column.copy_to_x_y(i, j)

    def get_columns_in_rect(self, rect: pg.Rect) -> list[list[Column]]:
        # self.regions
        columns = []
        for i in range(rect.left, rect.right):
            row = []
            for j in range(rect.top, rect.bottom):
                if (i, j) in self.columns:
                    row.append(self.columns[(i, j)])
                else:
                    row.append(self.not_found_column.copy_to_x_y(i, j))
            columns.append(row)
        return columns
