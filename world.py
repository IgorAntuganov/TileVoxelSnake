from blocks import *
from render_order import RenderOrder
from generation.height_map import HeightMap


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
        self._figures: list[tuple[pg.Rect, pg.Surface, tuple[int, int, int]]] = []

    @classmethod
    def from_height(cls, x, y, height):
        blocks = [Grass]
        for i in range(height-1):
            if i < height // 2:
                blocks.append(Dirt)
            else:
                blocks.append(Stone)
        return Column(x, y, blocks)

    def set_figures(self, figures: list[tuple[pg.Rect, pg.Surface, tuple[int, int, int]]]):
        self._figures = figures

    def get_figures(self) -> list[tuple[pg.Rect, pg.Surface, tuple[int, int, int]]]:
        return self._figures

    def copy_to_x_y(self, x, y, height_difference_are_set=False):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        new_column = Column(x, y, new_blocks)
        new_column.height_difference_are_set = height_difference_are_set
        return new_column

    def get_top_block(self) -> FullBlock:
        if self.height > 0:
            return self.blocks[0]
        return DebugBlock(self.x, self.y, 0)

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

    def remove_top_block(self):
        self.blocks = self.blocks[1:]
        self.height -= 1
        self.height_difference_are_set = False

    def add_block_on_top(self, block_type: type):
        block = block_type(self.x, self.y, self.height)
        self.blocks.insert(0, block)
        self.height += 1
        self.height_difference_are_set = False


class World:
    def __init__(self, seed=0):
        self.columns = {}
        self.not_found_column: Column = Column(0, 0, [DebugBlock])
        self.not_found_column.set_height_difference(*[self.not_found_column]*8)
        self.DEFAULT_ADDED_BLOCK: type = Stone

        self.render_order = RenderOrder()

        self.height_map = HeightMap(seed)
        self.test_fill_with_height_map()

    def get_column(self, x, y) -> Column:
        if (x, y) in self.columns:
            return self.columns[(x, y)]
        else:
            return self.not_found_column.copy_to_x_y(x, y, True)

    def get_columns_in_rect_generator(self, rect: pg.Rect):
        for i, j in self.render_order.get_order(rect):
            if (i, j) in self.columns:
                yield self.columns[(i, j)]
            else:
                yield self.not_found_column.copy_to_x_y(i, j, True)

    def add_block(self, block: tuple[int, int, int], _type: None | type = None):
        x, y, z = block
        if _type is None:
            _type = self.DEFAULT_ADDED_BLOCK
        column = self.get_column(x, y)
        column.add_block_on_top(_type)
        rect = pg.Rect(x - 1, y - 1, 3, 3)
        self.set_columns_h_diff_in_rect(rect)

    def remove_block(self, block: tuple[int, int, int]):
        x, y, z = block
        column = self.get_column(x, y)
        column.remove_top_block()
        rect = pg.Rect(x-1, y-1, 3, 3)
        self.set_columns_h_diff_in_rect(rect)

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

    def test_fill_with_height_map(self):
        for i in range(-200, 201):
            for j in range(-200, 201):
                height = self.height_map.get_height(i, j)
                new_column = Column.from_height(i, j, height)
                self.columns[(i, j)] = new_column
        self.set_columns_h_diff_in_rect(pg.Rect(-201, -201, 402, 402))

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
        self.columns[(40, 20)] = Column(40, 20, [Grass, Grass, Stone, Stone, Stone, Stone, Stone])
        self.columns[(23, 35)] = Column(23, 35, [Grass, Grass, Grass, Grass, Grass, Grass, Grass, Grass])
        self.columns[(22, 35)] = Column(22, 35, [Grass, Grass, Grass, Grass, Grass, Grass, Grass])
        self.columns[(21, 35)] = Column(21, 35, [Grass, Grass, Grass, Grass, Grass, Grass])
        self.columns[(20, 35)] = Column(20, 35, [Grass, Grass, Grass, Grass, Grass])
        self.columns[(19, 36)] = Column(19, 36, [Grass, Grass, Grass, Grass])
        self.columns[(20, 36)] = Column(20, 36, [Grass, Grass, Grass, Grass])
        self.columns[(21, 36)] = Column(21, 36, [Grass, Grass, Grass, Grass])
        self.columns[(19, 37)] = Column(19, 37, [Grass, Grass, Grass])
        self.columns[(20, 37)] = Column(20, 37, [Grass, Grass, Grass])
        self.columns[(21, 37)] = Column(21, 37, [Grass, Grass, Grass])
        self.columns[(19, 38)] = Column(19, 38, [Grass, Grass])
        self.columns[(20, 38)] = Column(20, 38, [Grass, Grass])
        self.columns[(21, 38)] = Column(21, 38, [Grass, Grass])
        self.columns[(19, 39)] = Column(19, 39, [Grass])
        self.columns[(20, 39)] = Column(20, 39, [Grass])
        self.columns[(21, 39)] = Column(21, 39, [Grass])
        self.columns[(19, 40)] = Column(19, 40, [Grass])
        self.columns[(20, 40)] = Column(20, 40, [Grass])
        self.columns[(21, 40)] = Column(21, 40, [Grass])
        self.set_columns_h_diff_in_rect(pg.Rect(-50, -160, 200, 240))
