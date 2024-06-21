import time
import os
import pygame as pg
from constants import HEIGHT_GENERATING_INFO
from generation._NU_value_noise import ValueNoise
from generation.perlin_noise import PerlinNoise
from generation.abc_noise import Noise, DataNoiseTile
from generation.constants import PATH_TO_NOISE


class NoiseGrid:
    def __init__(self, world_seed: int,
                 unic_name: str,
                 noise_type: type,
                 tile_size: int,
                 octaves: int | list[int] | None):
        """
        :param noise_type: ValueNoise or PerlinNoise
        :param tile_size: literally
        :param octaves: octaves in noise
        """
        self.world_seed = world_seed
        self.unic_name = unic_name
        assert noise_type in [PerlinNoise, ValueNoise]
        self.noise_type = noise_type
        self.tile_size = tile_size
        self.octaves = octaves
        self.grid: dict[tuple[int, int]: Noise] = {}
        self.load_from_disk()

    def load_from_disk(self):
        folder = PATH_TO_NOISE + f'world {self.world_seed}/'
        if not os.path.isdir(folder):
            os.mkdir(folder)
        file_name_start = DataNoiseTile.get_file_name(self.unic_name)
        for file in os.listdir(folder):
            if file.startswith(file_name_start):
                without_pickle = file.split('.')[0]
                i, j = without_pickle.split('_')[-2:]
                i, j = int(i), int(j)
                self.load_and_finish_calculating_tile(i, j)

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

    def load_and_finish_calculating_tile(self, i, j):
        new_tile = self.noise_type(self.world_seed,
                                   self.unic_name,
                                   i, j,
                                   (self.tile_size, self.tile_size),
                                   self.octaves)
        if not new_tile.loaded:
            if HEIGHT_GENERATING_INFO:
                print('generating noise tile', i, j)
            new_tile.calculate_values()
            self.merge_tile_with_neighbors(new_tile, i, j)
            new_tile.calculate_points()
            new_tile.calculate_normalized_points()
            new_tile.save_to_file()
        self.grid[(i, j)] = new_tile

    def get_or_create_tile(self, i, j) -> Noise:
        if (i, j) not in self.grid:
            self.load_and_finish_calculating_tile(i, j)
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


def test():
    file_name = f'{int(time.time())}'
    size = 256
    noise = NoiseGrid(0, 'SavingTest', PerlinNoise, size, list(range(5)))
    rect = pg.Rect(-1, -1, 4, 4)
    # rect = pg.Rect(0, 0, 2, 2)
    texture = noise.get_texture(rect, True)
    pg.image.save(texture, f'perlin_test_images/grid{file_name}.png')
    if texture.get_height() < 1080:
        scr = pg.display.set_mode(texture.get_size())
        scr.blit(texture, (0, 0))
        pg.display.update()
        while True:
            [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
