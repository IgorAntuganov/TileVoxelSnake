import pygame as pg
from generation.noise_grid import NoiseGrid
from generation.perlin_noise import PerlinNoise
from generation.constants import *


class HeightMap:
    def __init__(self, world_seed: int):
        self.noise_grid = NoiseGrid(world_seed, 'height', PerlinNoise, HEIGHT_TILE_SIZE, HEIGHT_OCTAVES)
        self.noise_grid.set_noise_at_rect(pg.Rect(*START_HEIGHT_AREA))

    def get_height(self, x, y) -> int:
        value = self.noise_grid.get_noise_point(x, y)
        value = int(value*MAX_HEIGHT)
        value = max(1, value-5)
        return value
