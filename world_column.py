from constants import *
import blocks
from height_difference import HeightDiff


class Column:
    def __init__(self, x, y, _blocks: list[type]):
        """
        :param _blocks: blocks from top to bottom as types !Transparent can't follow non-transparent blocks!
        """
        self.x = x
        self.y = y
        self.blocks: list[blocks.Block | blocks.FullBlock | blocks.SingleSpriteBlock] = []  # from top to bottom
        self.transparent_blocks: list[blocks.Block] = []  # from top to bottom
        for i in range(len(_blocks)):
            block = _blocks[i](x, y, len(_blocks)-i-1)
            if not block.is_transparent:
                self.blocks.append(block)
            else:
                assert len(self.blocks) == 0
                self.transparent_blocks.append(block)

        self.visible_blocks_are_set: bool = False
        self.blocks_with_visible_top_sprite = []
        self.define_blocks_with_visible_top_sprite()

        self.height_difference: HeightDiff | None = None
        self.height_difference_are_set: bool = False

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

    def get_top_block(self) -> blocks.Block:
        if len(self.transparent_blocks) != 0:
            return self.transparent_blocks[0]
        if self.nt_height > 0:
            return self.blocks[0]
        return blocks.DebugBlock(self.x, self.y, 0)

    def get_block(self, z) -> blocks.Block | blocks.FullBlock:
        if self.nt_height > 0:
            if self.nt_height > z:
                return self.blocks[-z-1]
            elif len(self.transparent_blocks) > 0:
                ind = - z + self.nt_height - 1
                return self.transparent_blocks[ind]
        return blocks.DebugBlock(self.x, self.y, z)

    def get_first_non_transparent(self) -> blocks.Block:
        if self.nt_height > 0:
            return self.blocks[0]
        return blocks.DebugBlock(self.x, self.y, 0)

    def get_blocks_with_visible_top_sprite(self) -> list[blocks.Block]:
        """return blocks from top to bottom"""
        assert self.visible_blocks_are_set
        return self.blocks_with_visible_top_sprite

    def define_blocks_with_visible_top_sprite(self):
        blocks_with_visible_top_sprite = []
        if self.transparent_height > 0:
            top_block = self.transparent_blocks[0]
            blocks_with_visible_top_sprite.append(top_block)
            last = top_block
            for i in range(1, self.transparent_height):
                block = self.transparent_blocks[i]
                if type(block) != type(last):
                    blocks_with_visible_top_sprite.append(block)
                last = block
        if len(self.blocks) > 0:
            blocks_with_visible_top_sprite.append(self.blocks[0])
        self.blocks_with_visible_top_sprite = blocks_with_visible_top_sprite[::-1]
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
    def set_height_difference(self, columns_3x3: list[...]):
        self.height_difference = HeightDiff.from_9_columns(columns_3x3)

        if FILLING_COLUMNS_INFO:
            print('set diffs', self.x, self.y, self.height_difference)
        self.height_difference_are_set = True

    def get_height_difference(self) -> dict[str: int]:
        assert self.height_difference_are_set
        return self.height_difference

    def get_top_block_neighbors(self) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        assert self.height_difference_are_set
        return self.height_difference.get_top_block_neighbors()

    def copy_to_x_y(self, x, y, height_difference_are_set=False):
        new_blocks = [block.copy_to_x_y(x, y) for block in self.blocks]
        new_column = Column(x, y, new_blocks)
        new_column.height_difference_are_set = height_difference_are_set
        return new_column

    @staticmethod
    def from_pickle(data: dict):
        x, y = data['x'], data['y']
        height_diff = HeightDiff.from_pickle(data['hd'])
        height_diff_are_set = data['hd_are_set']
        _blocks = []
        for block in data['transparent_blocks']:
            block_class = blocks.blocks_classes_dict[block]
            _blocks.append(block_class)
        for block in data['blocks']:
            block_class = blocks.blocks_classes_dict[block]
            _blocks.append(block_class)

        pickle_column = Column(x, y, _blocks)

        pickle_column.height_difference = height_diff
        pickle_column.height_difference_are_set = height_diff_are_set
        pickle_column.define_blocks_with_visible_top_sprite()
        return pickle_column

    def to_pickle(self) -> dict:
        disk_data = {
            'x': self.x,
            'y': self.y,
            'hd': self.height_difference.to_pickle(),
            'hd_are_set': self.height_difference_are_set,
            'blocks': [],
            'transparent_blocks': []
        }
        for block in self.blocks:
            block_name = blocks.reversed_blocks_classes_dict[type(block)]
            disk_data['blocks'].append(block_name)
        for block in self.transparent_blocks:
            block_name = blocks.reversed_blocks_classes_dict[type(block)]
            disk_data['transparent_blocks'].append(block_name)
        return disk_data
