from blocks import *
from constants import *


class Column:
    def __init__(self, x, y, blocks: list[type]):
        """
        :param blocks: blocks from top to bottom as types !Transparent can't follow non-transparent blocks!
        """
        self.x = x
        self.y = y
        self.blocks: list[Block | FullBlock | SingleSpriteBlock] = []  # from top to bottom
        self.transparent_blocks: list[Block] = []  # from top to bottom
        for i in range(len(blocks)):
            block = blocks[i](x, y, len(blocks)-i-1)
            if not block.is_transparent:
                self.blocks.append(block)
            else:
                assert len(self.blocks) == 0
                self.transparent_blocks.append(block)

        self.visible_blocks_are_set = False
        self.blocks_with_visible_top_sprite = []
        self.define_blocks_with_visible_top_sprite()

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
        self.height_difference_2 = self.height_difference.copy()
        self.height_difference_are_set = False

        if FILLING_COLUMNS_INFO:
            print('new column created', self.x, self.y)
            for block in self.blocks + self.transparent_blocks:
                print(block.z, block.__class__.__name__)

    @property
    def nt_height(self):
        return len(self.blocks)

    @property
    def full_height(self):
        return len(self.blocks) + len(self.transparent_blocks)

    @property
    def transparent_height(self):
        return len(self.transparent_blocks)

    def get_top_block(self) -> Block:
        if len(self.transparent_blocks) != 0:
            return self.transparent_blocks[0]
        if self.nt_height > 0:
            return self.blocks[0]
        return DebugBlock(self.x, self.y, 0)

    def get_block(self, z) -> Block | FullBlock:
        if self.nt_height > 0:
            if self.nt_height > z:
                return self.blocks[-z-1]
            elif len(self.transparent_blocks) > 0:
                ind = - z + self.nt_height - 1
                return self.transparent_blocks[ind]
        return DebugBlock(self.x, self.y, z)

    def get_first_non_transparent(self) -> Block:
        if self.nt_height > 0:
            return self.blocks[0]
        return DebugBlock(self.x, self.y, 0)

    def get_blocks_with_visible_top_sprite(self) -> list[Block]:
        assert self.visible_blocks_are_set
        return self.blocks_with_visible_top_sprite[::-1]

    def define_blocks_with_visible_top_sprite(self):
        # print('defing')
        self.blocks_with_visible_top_sprite = []
        if self.transparent_height > 0:
            top_block = self.transparent_blocks[0]
            self.blocks_with_visible_top_sprite.append(top_block)
            last = top_block
            for i in range(1, self.transparent_height):
                block = self.transparent_blocks[i]
                if type(block) != type(last):
                    self.blocks_with_visible_top_sprite.append(block)
                last = block
        if len(self.blocks) > 0:
            self.blocks_with_visible_top_sprite.append(self.blocks[0])
        self.visible_blocks_are_set = True

    # Adding and removing blocks -------
    def remove_top_block(self):
        if len(self.transparent_blocks) > 0:
            self.transparent_blocks = self.transparent_blocks[1:]
        else:
            self.blocks = self.blocks[1:]
        self.height_difference_are_set = False
        self.visible_blocks_are_set = False
        self.define_blocks_with_visible_top_sprite()
        if FILLING_COLUMNS_INFO:
            print('removing block')
            print(self.x, self.y, len(self.blocks), len(self.transparent_blocks))

    def add_block_on_top(self, block_type: type):
        z = len(self.blocks) + len(self.transparent_blocks)
        block = block_type(self.x, self.y, z)
        if not block.is_transparent:
            if len(self.transparent_blocks) != 0:
                print(self.x, self.y, self.blocks, self.transparent_blocks, block_type)
            assert len(self.transparent_blocks) == 0
            self.blocks.insert(0, block)
        else:
            self.transparent_blocks.insert(0, block)
        self.height_difference_are_set = False
        self.visible_blocks_are_set = False
        self.define_blocks_with_visible_top_sprite()
        if FILLING_COLUMNS_INFO:
            print('adding block')
            print(self.x, self.y, len(self.blocks), len(self.transparent_blocks))
            print('block z', block.z, 'height', self.nt_height)
            for block in self.transparent_blocks + self.blocks:
                print(block.z, block.__class__.__name__)

    # Working with height difference -----
    def set_height_difference(self, left, top, right, bottom, top_left, top_right, bottom_left, bottom_right):
        """left, top, right, bottom - adjacent Columns;
        top_left, top_right, bottom_left, bottom_right - diagonal Columns"""

        columns = {
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom,
            'top_left': top_left,
            'top_right': top_right,
            'bottom_left': bottom_left,
            'bottom_right': bottom_right
        }

        for key in columns:
            self.height_difference[key] = self.full_height - columns[key].full_height
            self.height_difference_2[key] = self.full_height - columns[key].nt_height

        if FILLING_COLUMNS_INFO:
            print('set diffs', self.x, self.y, self.height_difference, self.height_difference_2)
        self.height_difference_are_set = True

    def get_height_difference(self) -> dict[str: int]:
        assert self.height_difference_are_set is True
        return self.height_difference

    def get_height_difference_2(self) -> dict[str: int]:
        assert self.height_difference_are_set is True
        return self.height_difference_2

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

    def copy_to_x_y(self, x, y, height_difference_are_set=False):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        new_column = Column(x, y, new_blocks)
        new_column.height_difference_are_set = height_difference_are_set
        return new_column

    @staticmethod
    def from_pickle(data: dict):
        x, y = data['x'], data['y']
        height_diff = data['hd']
        height_diff_2 = data['hd2']
        height_diff_are_set = data['hd_are_set']
        blocks = []
        for block in data['transparent_blocks']:
            block_class = blocks_classes_dict[block]
            blocks.append(block_class)
        for block in data['blocks']:
            block_class = blocks_classes_dict[block]
            blocks.append(block_class)

        pickle_column = Column(x, y, blocks)

        pickle_column.height_difference = height_diff
        pickle_column.height_difference_2 = height_diff_2
        pickle_column.height_difference_are_set = height_diff_are_set
        pickle_column.define_blocks_with_visible_top_sprite()
        return pickle_column

    def to_pickle(self) -> dict:
        disk_data = {
            'x': self.x,
            'y': self.y,
            'hd': self.height_difference,
            'hd2': self.height_difference_2,
            'hd_are_set': self.height_difference_are_set,
            'blocks': [],
            'transparent_blocks': []
        }
        for block in self.blocks:
            block_name = reversed_blocks_classes_dict[type(block)]
            disk_data['blocks'].append(block_name)
        for block in self.transparent_blocks:
            block_name = reversed_blocks_classes_dict[type(block)]
            disk_data['transparent_blocks'].append(block_name)
        return disk_data


NOT_FOUND_COLUMN = Column(0, 0, [Shadow])
NOT_FOUND_COLUMN.set_height_difference(*[NOT_FOUND_COLUMN]*8)
NOT_FOUND_COLUMN2 = Column(0, 0, [TransparentDebugBlock])
NOT_FOUND_COLUMN2.set_height_difference(*[NOT_FOUND_COLUMN2]*8)
