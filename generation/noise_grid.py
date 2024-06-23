import os
import pygame as pg
from constants import HEIGHT_GENERATING_INFO
from generation.value_noise import ValueNoise
from generation.perlin_noise import PerlinNoise
from generation.abc_noise import Noise, DataNoiseTile


class NoiseGrid:
    def __init__(self, world_folder: str,
                 unique_name: str,
                 noise_type: type,
                 tile_size: int,
                 octaves: int | list[int] | None):
        """
        :param noise_type: ValueNoise or PerlinNoise
        :param tile_size: literally
        :param octaves: octaves in noise
        """
        self.unique_name = unique_name
        self.folder = world_folder + f'{self.unique_name} noise/'

        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)

        assert noise_type in [PerlinNoise, ValueNoise]
        self.noise_type = noise_type
        self.tile_size = tile_size
        self.octaves = octaves
        self.grid: dict[tuple[int, int]: Noise] = {}

    def merge_tile_with_neighbors(self, tile, tile_i, tile_j):
        if (tile_i, tile_j - 1) in self.grid:
            left_tile = self.grid[(tile_i, tile_j - 1)]
            tile.set_left_neighbor(left_tile.get_values())

        if (tile_i, tile_j + 1) in self.grid:
            right_tile = self.grid[(tile_i, tile_j + 1)]
            tile.set_right_neighbor(right_tile.get_values())

        if (tile_i - 1, tile_j) in self.grid:
            top_tile = self.grid[(tile_i - 1, tile_j)]
            tile.set_top_neighbor(top_tile.get_values())

        if (tile_i + 1, tile_j) in self.grid:
            bottom_tile = self.grid[(tile_i + 1, tile_j)]
            tile.set_bottom_neighbor(bottom_tile.get_values())

        if (tile_i + 1, tile_j + 1) in self.grid:
            bottom_right_tile = self.grid[(tile_i + 1, tile_j + 1)]
            tile.set_bottom_right_neighbor(bottom_right_tile.get_values())

    def get_save_file_path(self, i, j) -> str:
        return self.folder + f'{i}_{j}.pickle'

    def check_if_tile_saved(self, i, j) -> bool:
        return os.path.isfile(self.get_save_file_path(i, j))

    def create_tile(self, i, j) -> Noise:
        if HEIGHT_GENERATING_INFO:
            print('generating noise tile', i, j)
        new_tile: DataNoiseTile = self.noise_type((self.tile_size, self.tile_size),
                                                  self.octaves)
        new_tile.calculate_values()
        self.merge_tile_with_neighbors(new_tile, i, j)
        new_tile.calculate_points()
        new_tile.calculate_normalized_points()
        path = self.get_save_file_path(i, j)
        new_tile.save_to_file(path)
        return new_tile

    def load_tile(self, i, j) -> Noise:
        if HEIGHT_GENERATING_INFO:
            print('loading noise tile', i, j)
        loaded_tile: DataNoiseTile = self.noise_type((self.tile_size, self.tile_size),
                                                     self.octaves)
        path = self.get_save_file_path(i, j)
        loaded_tile.update_with_save_file(path)
        return loaded_tile

    def get_or_create_tile(self, i, j) -> Noise:
        if (i, j) not in self.grid:
            if self.check_if_tile_saved(i, j):
                self.grid[(i, j)] = self.load_tile(i, j)
            else:
                self.grid[(i, j)] = self.create_tile(i, j)
        return self.grid[(i, j)]

    def get_texture(self, rect: pg.Rect, print_progress=False) -> pg.Surface:
        texture = pg.Surface((rect.width * self.tile_size, rect.height * self.tile_size))
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if print_progress:
                    print(i, j)
                tex_i = (i - rect.left) * self.tile_size
                tex_j = (j - rect.top) * self.tile_size
                tile = self.get_or_create_tile(i, j)
                tile_texture = tile.work(get_texture=True)
                texture.blit(tile_texture, (tex_i, tex_j))
        return texture

    def set_noise_at_rect(self, rect: pg.Rect, print_progress=False):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if print_progress:
                    print(i, j)
                tile = self.get_or_create_tile(i, j)
                tile.work()

    def get_noise_point(self, i, j) -> float:
        tile_i = i // self.tile_size
        tile_j = j // self.tile_size
        tile = self.get_or_create_tile(tile_i, tile_j)
        x = i % self.tile_size
        y = j % self.tile_size
        point = tile.get_normalized_points()[y][x]
        return point
