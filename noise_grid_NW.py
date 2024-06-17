import pygame as pg
from value_noise import ValueNoise
from perlin_noise import PerlinNoise
from abc_noise import Noise
# from diamond_square import DiamondSquare
import time


class NoiseGrid:
    def __init__(self, noise_type: type, tile_size: int, octaves: int | list[int] | None):
        self.noise_type = noise_type
        self.tile_size = tile_size
        self.octaves = octaves
        self.grid: dict[tuple[int, int]: Noise] = {}

    def add_tile(self, i, j):
        new_tile = self.noise_type((self.tile_size, self.tile_size), self.octaves)
        new_tile.set_values()

        if (i, j-1) in self.grid:
            top_tile = self.grid[(i, j-1)]
            print('set top for', i, j)
            new_tile.set_top_neighbor(top_tile.get_values())

        if (i-1, j) in self.grid:
            left_tile = self.grid[(i-1, j)]
            print('set left for', i, j)
            new_tile.set_left_neighbor(left_tile.get_values())

        # bottom tile
        # right tile

        new_tile.set_points()

        self.grid[(i, j)] = new_tile

    def get_tile(self, i, j) -> Noise:
        if (i, j) not in self.grid:
            self.add_tile(i, j)
        return self.grid[(i, j)]

    def get_texture(self, rect: pg.Rect) -> pg.Surface:
        texture = pg.Surface((rect.width * self.tile_size, rect.height * self.tile_size))
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                print(i, j)
                tex_i = (i - rect.left) * self.tile_size
                tex_j = (j - rect.top) * self.tile_size
                tile = self.get_tile(i, j)
                tile_texture = tile.get_texture()
                texture.blit(tile_texture, (tex_i, tex_j))
        return texture


def test():
    file_name = f'{int(time.time())}'
    size = 128
    noise = NoiseGrid(PerlinNoise, size, 1)
    rect = pg.Rect(0, 0, 2, 2)
    texture = noise.get_texture(rect)
    pg.image.save(texture, f'perlin_test_images/grid{file_name}.png')
    scr = pg.display.set_mode(texture.get_size())
    scr.blit(texture, (0, 0))
    pg.display.update()
    while True:
        [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
