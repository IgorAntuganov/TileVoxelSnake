from constants import *


class HeightDiff:
    def __init__(self, full_height_diff, nt_height_diff):
        self.full_height_diff = full_height_diff
        self.nt_height_diff = nt_height_diff

    def get_top_block_neighbors(self) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        return (self.full_height_diff['left'] < 0,
                self.full_height_diff['top'] < 0,
                self.full_height_diff['right'] < 0,
                self.full_height_diff['bottom'] < 0,
                self.full_height_diff['top_left'] < 0,
                self.full_height_diff['top_right'] < 0,
                self.full_height_diff['bottom_right'] < 0,
                self.full_height_diff['bottom_left'] < 0)

    @staticmethod
    def from_9_columns(parent_column,
                       left, top, right, bottom,
                       top_left, top_right, bottom_left, bottom_right
                       ):
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
        full_height_diff = {}
        nt_height_diff = {}

        for key in columns:
            column = columns[key]
            if column is not None:
                full_height_diff[key] = parent_column.full_height - column.full_height
                nt_height_diff[key] = parent_column.full_height - column.nt_height
            else:
                if DRAW_SIDES_WITH_UNLOADED_REGIONS:
                    value = parent_column.full_height
                else:
                    value = 0
                full_height_diff[key] = value
                nt_height_diff[key] = value
        return HeightDiff(full_height_diff, nt_height_diff)

    @staticmethod
    def from_pickle(data):
        full_height_diff, nt_height_diff = data
        hd = HeightDiff(full_height_diff, nt_height_diff)
        return hd

    def to_pickle(self):
        data = self.full_height_diff, self.nt_height_diff
        return data
