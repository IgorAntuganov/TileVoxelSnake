import pygame as pg
from generation.noise_grid import NoiseGrid
from generation.perlin_noise import PerlinNoise
from generation.constants import *


class HeightMap:
    def __init__(self, world_folder: str, world_seed: int):
        self.noise_grid = NoiseGrid(world_folder, 'height', PerlinNoise, HEIGHT_NOISE_TILE_SIZE, HEIGHT_OCTAVES)
        self.noise_grid.set_noise_at_rect(pg.Rect(*START_HEIGHT_AREA))

    def get_height(self, x, y) -> int:
        value = self.noise_grid.get_noise_point(x, y)
        value = max(0.0, value-0.1)
        value = int(value*MAX_HEIGHT)
        return value
