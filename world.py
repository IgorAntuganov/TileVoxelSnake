from blocks import *


class Column:
    def __init__(self, x, y, blocks: list[type]):
        """:param blocks: blocks from top to bottom as types (ex: [Grass, Dirt, Dirt, Stone])"""
        self.x = x
        self.y = y
        self.blocks: list[Block | FullBlock | SingleSpriteBlock] = []
        for i in range(len(blocks)):
            block = blocks[i](x, y, len(blocks)-i-1)
            self.blocks.append(block)
        self.height = len(blocks)
        self.height_difference: dict[str: int] = {
            'left': 0,
            'top': 0,
            'right': 0,
            'bottom': 0,
            'top_left': 0,
            'top_right': 0,
            'bottom_left': 0,
            'bottom_right': 0
        }
        self.height_difference_are_set = False

    def copy_to_x_y(self, x, y, height_difference_are_set=False):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        new_column = Column(x, y, new_blocks)
        new_column.height_difference_are_set = height_difference_are_set
        return new_column

    def get_top_block(self) -> FullBlock:
        return self.blocks[0]

    def get_block(self, z) -> FullBlock:
        return self.blocks[-z-1]

    def set_height_difference(self, left, top, right, bottom, top_left, top_right, bottom_left, bottom_right):
        """left, top, right, bottom - adjacent Columns;
        top_left, top_right, bottom_left, bottom_right - diagonal Columns"""
        self.height_difference['left'] = self.height - left.height
        self.height_difference['top'] = self.height - top.height
        self.height_difference['right'] = self.height - right.height
        self.height_difference['bottom'] = self.height - bottom.height
        self.height_difference['top_left'] = self.height - top_left.height
        self.height_difference['top_right'] = self.height - top_right.height
        self.height_difference['bottom_left'] = self.height - bottom_left.height
        self.height_difference['bottom_right'] = self.height - bottom_right.height
        self.height_difference_are_set = True

    def get_height_difference(self) -> dict[str: int]:
        assert self.height_difference_are_set is True
        return self.height_difference

    def get_top_block_neighbors(self) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        assert self.height_difference_are_set is True
        return (self.height_difference['left'] < 0,
                self.height_difference['top'] < 0,
                self.height_difference['right'] < 0,
                self.height_difference['bottom'] < 0,
                self.height_difference['top_left'] < 0,
                self.height_difference['top_right'] < 0,
                self.height_difference['bottom_right'] < 0,
                self.height_difference['bottom_left'] < 0)


class World:
    def __init__(self):
        # self.regions: dict[(int, int): list[list[Column]]] = {}
        self.columns = {}
        self.not_found_column: Column = Column(0, 0, [DebugBlock])
        self.not_found_column.set_height_difference(*[self.not_found_column]*8)

    def test_fill(self):
        blocks1 = [Stone, Dirt, Stone]
        blocks2 = [Grass,  Dirt, Stone, Stone]
        test_column_1 = Column(0, 0, blocks1)
        test_column_2 = Column(0, 0, blocks2)
        for i in range(-30, 151):
            for j in range(-150, 51):
                if (i % 2 == j % 2 and not(abs(i) < 10 and abs(j) < 10)) or i > 1 and j > 1:
                    column = test_column_1
                else:
                    column = test_column_2
                self.columns[(i, j)] = column.copy_to_x_y(i, j)
        for i in range(6, 9):
            for j in range(6, 9):
                self.columns[(i, j)] = test_column_2.copy_to_x_y(i, j)
        self.columns[(20, 20)] = Column(20, 20, [Stone for _ in range(8)])
        self.columns[(30, 20)] = Column(30, 20, [Grass for _ in range(8)])
        self.set_columns_h_diff_in_rect(pg.Rect(-50, -160, 200, 240))

    def get_column(self, x, y) -> Column:
        if (x, y) in self.columns:
            return self.columns[(x, y)]
        else:
            return self.not_found_column.copy_to_x_y(x, y, True)

    def set_columns_h_diff_in_rect(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                column = self.get_column(i,   j)
                left   = self.get_column(i-1, j)
                top    = self.get_column(i,   j-1)
                right  = self.get_column(i+1, j)
                bottom = self.get_column(i,   j+1)
                top_left     = self.get_column(i-1, j-1)
                top_right    = self.get_column(i+1, j-1)
                bottom_left  = self.get_column(i-1, j+1)
                bottom_right = self.get_column(i+1, j+1)
                column.set_height_difference(left, top, right, bottom, top_left, top_right, bottom_left, bottom_right)
                if (i, j) not in self.columns and any(column.get_top_block_neighbors()):
                    self.columns[(i, j)] = column

    def get_columns_in_rect_generator(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if (i, j) in self.columns:
                    yield self.columns[(i, j)]
                else:
                    yield self.not_found_column.copy_to_x_y(i, j, True)
