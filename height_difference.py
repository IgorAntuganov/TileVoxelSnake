from constants import *


class HeightDiff9:
    def __init__(self, full_height_diff, full_nt_height_diff, nt_nt_height_diff):
        self.full_full_height_diff = full_height_diff
        self.full_nt_height_diff = full_nt_height_diff
        self.nt_nt_height_diff = nt_nt_height_diff

        self.top_block_neighbors = tuple(bool(self.full_full_height_diff[key] < 0) for key in SIDES_NAMES+DIAGONALS_NAMES)
        self.full_full_edges = tuple(bool(self.full_full_height_diff[key] > 0) for key in SIDES_NAMES+DIAGONALS_NAMES)
        self.nt_full_edges = tuple(bool(self.nt_nt_height_diff[key] > 0) for key in SIDES_NAMES + DIAGONALS_NAMES)

    def get_top_block_neighbors(self) -> tuple[bool]:
        return self.top_block_neighbors

    def get_full_full_edges(self) -> tuple[bool]:
        return self.full_full_edges

    def get_nt_full_edges(self) -> tuple[bool]:
        return self.nt_full_edges

    @staticmethod
    def from_9_columns(columns_3x3: list[list[...]]):
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
        full_full_height_diff = {}
        full_nt_height_diff = {}
        nt_nt_height_diff = {}

        for key in columns:
            column = columns[key]
            if column is not None:
                full_full_height_diff[key] = parent_column.full_height - column.full_height
                full_nt_height_diff[key] = parent_column.full_height - column.nt_height
                nt_nt_height_diff[key] = parent_column.nt_height - column.nt_height
            else:
                if DRAW_SIDES_WITH_UNLOADED_REGIONS:
                    value = parent_column.full_height
                else:
                    value = 0
                full_full_height_diff[key] = value
                full_nt_height_diff[key] = value
                nt_nt_height_diff[key] = value
        return HeightDiff9(full_full_height_diff, full_nt_height_diff, nt_nt_height_diff)

    @staticmethod
    def from_pickle(data):
        full_height_diff, nt_height_diff, nt_nt_height_diff = data
        hd = HeightDiff9(full_height_diff, nt_height_diff, nt_nt_height_diff)
        return hd

    def to_pickle(self):
        data = self.full_full_height_diff, self.full_nt_height_diff, self.nt_nt_height_diff
        return data
