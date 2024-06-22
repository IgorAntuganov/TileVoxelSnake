from blocks import *
from render_order import RenderOrder
from generation.height_map import HeightMap
from constants import HEIGHT_GENERATING_INFO, PATH_TO_SAVES
from generation.constants import CHUNK_LOADING_PART_SIZE, WORLD_CHUNK_SIZE
LOADING_PARTS_COUNT = WORLD_CHUNK_SIZE // CHUNK_LOADING_PART_SIZE
LOADING_PARTS_TOTAL_COUNT = (WORLD_CHUNK_SIZE // CHUNK_LOADING_PART_SIZE) ** 2


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

    @staticmethod
    def from_height(x, y, height):
        blocks = [Grass if height > 5 else Sand]
        for i in range(height-1):
            if i < height // 2:
                blocks.append(Dirt)
            else:
                blocks.append(Stone)
        return Column(x, y, blocks)

    @staticmethod
    def from_pickle(data):
        pass

    def to_pickle(self):
        pass

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


NOT_FOUND_COLUMN = Column(0, 0, [DebugBlock])
NOT_FOUND_COLUMN.set_height_difference(*[NOT_FOUND_COLUMN]*8)


class Region:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.center_x = x + size//2
        self.center_y = y + size//2
        self.size = size
        self.columns: list[list[None | Column]] = [[None] * size for _ in range(size)]

        self.part_size = self.size // CHUNK_LOADING_PART_SIZE
        assert self.part_size * CHUNK_LOADING_PART_SIZE == self.size
        self.filled_parts = 0
        self.full_filled = False

    @staticmethod
    def check_distance(center_x, center_y, frame_x, frame_y, r) -> bool:
        # distance = ((frame_x-x) ** 2 + (frame_y-y) ** 2) ** .5
        distance = max(abs(frame_x - center_x), abs(frame_y - center_y))
        return distance < r

    def get_next_part_rect(self) -> pg.Rect:
        i = self.filled_parts // LOADING_PARTS_COUNT
        j = self.filled_parts % LOADING_PARTS_COUNT
        x = self.x + i * CHUNK_LOADING_PART_SIZE
        y = self.y + j * CHUNK_LOADING_PART_SIZE
        self.filled_parts += 1
        return pg.Rect(x, y, CHUNK_LOADING_PART_SIZE, CHUNK_LOADING_PART_SIZE)

    def check_if_fully_filled(self) -> bool:
        return self.filled_parts == LOADING_PARTS_TOTAL_COUNT

    def check_region_distance(self, frame_x, frame_y, r) -> bool:
        return self.check_distance(self.center_x, self.center_y, frame_x, frame_y, r)

    def get_column(self, x, y) -> Column:
        x -= self.x
        y -= self.y
        column = self.columns[y][x]
        if column is not None:
            return column
        else:
            return NOT_FOUND_COLUMN.copy_to_x_y(x, y, True)

    def set_column(self, x: int, y: int, column: Column):
        x -= self.x
        y -= self.y
        self.columns[y][x] = column

    def get_rect(self) -> pg.Rect:
        return pg.Rect(self.x, self.y, self.size, self.size)


class World:
    def __init__(self, load_distance: int, seed: int = 0, name: str = 'test wrold'):
        self.regions: dict[tuple[int, int]: Region] = {}

        self.loading_regions: list[Region] = []
        self.loading_regions_ind = 0
        self.next_loading_regions: list[Region] = []

        self.name = name
        self.folder = PATH_TO_SAVES + f'{name}/'
        self.height_map = HeightMap(self.folder, seed)
        self.load_distance = load_distance
        self.preload_start_area()

        self.DEFAULT_ADDED_BLOCK: type = Grass

        self.render_order = RenderOrder()

    def add_region(self, x2, y2):
        region = Region(x2 * WORLD_CHUNK_SIZE, y2 * WORLD_CHUNK_SIZE, WORLD_CHUNK_SIZE)
        self.regions[(x2, y2)] = region
        self.loading_regions.append(region)

    def get_region(self, x, y) -> Region:
        x2 = x // WORLD_CHUNK_SIZE
        y2 = y // WORLD_CHUNK_SIZE
        return self.regions[(x2, y2)]

    def check_is_region(self, x, y):
        x2 = x // WORLD_CHUNK_SIZE
        y2 = y // WORLD_CHUNK_SIZE
        return (x2, y2) in self.regions

    def get_column(self, x, y) -> Column:
        if self.check_is_region(x, y):
            region = self.get_region(x, y)
            column = region.get_column(x, y)
            return column
        else:
            return NOT_FOUND_COLUMN.copy_to_x_y(x, y, True)

    def set_column(self, x, y, column):
        region = self.get_region(x, y)
        region.set_column(x, y, column)

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

    def set_columns_in_rect(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                height = self.height_map.get_height(i, j)
                new_column = Column.from_height(i, j, height)
                self.set_column(i, j, new_column)
        bigger_rect = pg.Rect(rect.left-1, rect.top-1, rect.width+2, rect.height+2)
        self.set_columns_h_diff_in_rect(bigger_rect)

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

    def check_regions_distance(self, frame_x: int, frame_y: int):
        # removing too far regions
        for key in list(self.regions.keys()):
            r: Region = self.regions[key]
            if not r.check_region_distance(frame_x, frame_y, self.load_distance * 1.5):
                if HEIGHT_GENERATING_INFO:
                    print('deleting too far region', key)
                self.regions.pop(key)
        # adding nearby regions
        left = (frame_x - self.load_distance) // WORLD_CHUNK_SIZE
        right = (frame_x + self.load_distance) // WORLD_CHUNK_SIZE
        top = (frame_y - self.load_distance) // WORLD_CHUNK_SIZE
        bottom = (frame_y + self.load_distance) // WORLD_CHUNK_SIZE
        for i in range(left, right+1):
            for j in range(top, bottom+1):
                center_x = i * WORLD_CHUNK_SIZE + WORLD_CHUNK_SIZE // 2
                center_y = j * WORLD_CHUNK_SIZE + WORLD_CHUNK_SIZE // 2
                if (i, j) not in self.regions and \
                        Region.check_distance(frame_x, frame_y, center_x, center_y, self.load_distance):
                    if HEIGHT_GENERATING_INFO:
                        print('add nearby region', i, j, center_x, center_y)
                    self.add_region(i, j)
        if HEIGHT_GENERATING_INFO:
            print('regions after checking: ')
            for key in sorted(list(self.regions.keys())):
                print(key, end=' ')
            print()

    def load_regions_partly(self):
        if len(self.loading_regions) != 0:
            if self.loading_regions_ind >= len(self.loading_regions):
                self.loading_regions_ind = 0
                self.loading_regions = self.next_loading_regions
                self.next_loading_regions = []

        if len(self.loading_regions) != 0:  # (after swap)
            loading_region = self.loading_regions[self.loading_regions_ind]
            rect = loading_region.get_next_part_rect()
            self.set_columns_in_rect(rect)
            if not loading_region.check_if_fully_filled():
                self.next_loading_regions.append(loading_region)
            self.loading_regions_ind += 1

    def preload_start_area(self, frame_x=0, frame_y=0):
        self.check_regions_distance(frame_x, frame_y)

    def get_columns_in_rect_generator(self, rect: pg.Rect):
        for i, j in self.render_order.get_order(rect):
            yield self.get_column(i, j)
