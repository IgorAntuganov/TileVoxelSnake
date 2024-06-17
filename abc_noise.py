from abc import ABC, abstractmethod
import math
import pygame as pg


class Noise(ABC):
    def __init__(self, sizes: tuple[int, int], octaves: None | int | list[int] = None):
        self.sizes = sizes
        self.width, self.height = sizes
        self.octaves: list[int]
        if octaves is not None:
            if type(octaves) == int:
                self.octaves = list(range(octaves))
            else:
                self.octaves = octaves
        else:
            octaves = int(math.log(max(sizes), 2))
            self.octaves = list(range(octaves))
        self.values: list[list[list[...]]] = []
        self.points: list[list[float]] = [[0] * self.width for _ in range(self.height)]
        self.texture: None | pg.Surface = None
        self.points_are_set = False

    @abstractmethod
    def random_value(self, k, x, y):
        pass

    def set_values(self):
        for _ in range(min(self.octaves)):
            self.values.append([])
        for k in self.octaves:
            region = []
            f = 2 ** (k+1)
            for x in range(f + 1):
                row = []
                for y in range(f + 1):
                    value = self.random_value(k, x, y)
                    row.append(value)
                region.append(row)
            self.values.append(region)

    def get_values(self) -> list[list[list[float]]]:
        return self.values

    def set_top_neighbor(self, top_neighbor_values: list[list[list[float]]]):
        for self_region, neighbor_region in zip(self.values, top_neighbor_values):
            pass

    def set_left_neighbor(self, left_neighbor_values):
        '''for self_region, neighbor_region in zip(self.values, left_neighbor_values):
            for self_row, neighbor_row in zip(self_region, neighbor_region):
                self_row[0] = neighbor_row[0]'''
        pass

    @abstractmethod
    def set_points(self, print_progress=False):
        pass

    def get_points(self) -> list[list[float]]:
        assert self.points_are_set
        return self.points

    def get_texture(self) -> pg.Surface:
        assert self.points_are_set
        if self.texture is None:
            texture = pg.Surface((self.width, self.height))
            for i in range(self.width):
                for j in range(self.height):
                    value = self.points[j][i]
                    value = value * 2 ** min(self.octaves)
                    value = (value + 1) / 2
                    color = int(value * 255)
                    color = color % 510
                    if color > 255:
                        color = 509 - color

                    texture.set_at((i, j), [color] * 3)

                    # if color % 3 == 0:
                    #     texture.set_at((i, j), [color, 0, 0])
                    # elif color % 3 == 1:
                    #     texture.set_at((i, j), [0, color, 0])
                    # else:
                    #     texture.set_at((i, j), [0, 0, color])

            self.texture = texture
        return self.texture

    def work(self) -> pg.Surface:
        self.set_values()
        self.set_points()
        return self.get_texture()
