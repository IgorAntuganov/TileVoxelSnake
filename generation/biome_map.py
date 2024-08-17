from abc import ABC, abstractmethod
from typing import Type
import pygame as pg
from generation.noise_grid import NoiseGrid
from generation.value_noise import ValueNoise
from constants import *
import blocks


class Biome(ABC):
    @staticmethod
    @abstractmethod
    def blocks_from_height(height) -> list[type]:
        pass


class Fields(Biome):
    @staticmethod
    def blocks_from_height(height) -> list[type]:
        _blocks = [blocks.Grass]
        for i in range(height - 1):
            if i < height // 2:
                _blocks.append(blocks.Dirt)
            else:
                _blocks.append(blocks.Stone)
        return _blocks


class Desert(Biome):
    @staticmethod
    def blocks_from_height(height) -> list[type]:
        _blocks = []
        for i in range(height):
            if i < height * 3 // 4:
                _blocks.append(blocks.Sand)
            else:
                _blocks.append(blocks.Stone)
        return _blocks


class Forest(Biome):
    @staticmethod
    def blocks_from_height(height) -> list[type]:
        _blocks = [blocks.ForestGrass]
        for i in range(height-1):
            if i < height // 2:
                _blocks.append(blocks.Dirt)
            else:
                _blocks.append(blocks.Stone)
        return _blocks


class BiomeMap:
    def __init__(self, world_folder: str, world_seed: int):
        self.world_seed = world_seed
        self.noise_grid = NoiseGrid(world_folder, 'biome', ValueNoise, BIOME_NOISE_TILE_SIZE, BIOME_OCTAVES)
        self.noise_grid.set_noise_at_rect(pg.Rect(*START_HEIGHT_AREA))

    def get_value(self, x, y) -> float:
        value = self.noise_grid.get_noise_point(x, y)
        return value

    def get_biome(self, x, y) -> Type[Desert] | Type[Forest] | Type[Fields]:
        value = self.get_value(x, y)
        if value < 0.4:
            return Desert
        elif value < 0.6:
            return Fields
        else:
            return Forest
