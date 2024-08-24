import pygame as pg
from world_column import Column
from gui.objects import Tile


class Region:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.center_x = x + size//2
        self.center_y = y + size//2
        self.size = size
        self.columns_dict: dict[tuple[int, int]: Column] = {}
        self.tiles: dict[tuple[int, int]: Tile] = {}

        self.filled = False

    @staticmethod
    def check_distance(center_x, center_y, frame_x, frame_y, r) -> bool:
        distance = max(abs(frame_x - center_x), abs(frame_y - center_y))
        return distance < r

    def check_if_fully_filled(self) -> bool:
        return self.filled

    def check_region_distance(self, frame_x, frame_y, r) -> bool:
        return self.check_distance(self.center_x, self.center_y, frame_x, frame_y, r)

    def get_distance_to_point(self, frame_x, frame_y):
        distance = max(abs(frame_x - self.center_x), abs(frame_y - self.center_y))
        return distance

    def get_column(self, x, y) -> Column | None:
        x -= self.x
        y -= self.y
        if (x, y) in self.columns_dict:
            return self.columns_dict[(x, y)]

    def set_column(self, x: int, y: int, column: Column):
        x -= self.x
        y -= self.y
        assert (x, y) not in self.columns_dict
        assert len(self.columns_dict) < self.size**2
        self.columns_dict[(x, y)] = column

    def set_tile(self, x, y, tile: Tile):
        self.tiles[(x, y)] = tile

    def get_tiles(self) -> list[Tile]:
        return list(self.tiles.values())

    def set_tile_as_taken(self, tile: Tile):
        self.tiles.pop((tile.x, tile.y))

    def get_rect(self) -> pg.Rect:
        return pg.Rect(self.x, self.y, self.size, self.size)
