from constants import *


class HeightDiff:
    def __init__(self, full_height_diff, nt_height_diff):
        self.full_height_diff = full_height_diff
        self.nt_height_diff = nt_height_diff

    def get_top_block_neighbors(self) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        return (self.full_height_diff['west'] < 0,
                self.full_height_diff['north'] < 0,
                self.full_height_diff['east'] < 0,
                self.full_height_diff['south'] < 0,
                self.full_height_diff['north_west'] < 0,
                self.full_height_diff['north_east'] < 0,
                self.full_height_diff['south_east'] < 0,
                self.full_height_diff['south_west'] < 0)

    @staticmethod
    def from_9_columns(columns_3x3: list[list[...]]):
        """left, top, right, bottom - adjacent Columns;
        top_left, top_right, bottom_left, bottom_right - diagonal Columns"""

        parent_column = columns_3x3[1][1]
        columns = {
            'west': columns_3x3[1][0],
            'north': columns_3x3[0][1],
            'east': columns_3x3[1][2],
            'south': columns_3x3[2][1],
            'north_west': columns_3x3[0][0],
            'north_east': columns_3x3[0][2],
            'south_west': columns_3x3[2][0],
            'south_east': columns_3x3[2][2]
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
