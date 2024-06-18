from abc import ABC, abstractmethod
import math
import pygame as pg


class Noise(ABC):
    def __init__(self, sizes: tuple[int, int], octaves: None | int | list[int] = None):
        """:param sizes: must be 2**n !!!"""
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
        self.normalized_points: list[list[float]] = [[0] * self.width for _ in range(self.height)]
        self.texture: None | pg.Surface = None
        self.values_are_set = False
        self.points_are_set = False
        self.normalized_points_are_set = False

    @abstractmethod
    def random_value(self, k, x, y):
        pass

    def calculate_values(self):
        for _ in range(min(self.octaves)):
            self.values.append([])
        for k in self.octaves:
            region = []
            f = 2 ** k
            for x in range(f + 1):
                row = []
                for y in range(f + 1):
                    value = self.random_value(k, x, y)
                    row.append(value)
                region.append(row)
            self.values.append(region)
        self.values_are_set = True

    def get_values(self) -> list[list[list[float]]]:
        return self.values

    @abstractmethod
    def _calculate_points(self, print_progress):
        pass

    def calculate_points(self, print_progress=False):
        assert self.values_are_set
        self._calculate_points(print_progress)
        self.points_are_set = True

    def get_points(self) -> list[list[float]]:
        assert self.points_are_set
        return self.points

    def calculate_normalized_points(self):
        assert self.points_are_set
        for i in range(self.width):
            for j in range(self.height):
                value = self.points[j][i]
                value = value * 2 ** min(self.octaves)
                value = (value + 1) / 2
                self.normalized_points[j][i] = value
        self.normalized_points_are_set = True

    def get_normalized_points(self):
        assert self.normalized_points_are_set
        return self.normalized_points_are_set

    def get_texture(self) -> pg.Surface:
        assert self.normalized_points_are_set
        if self.texture is None:
            texture = pg.Surface((self.width, self.height))
            for i in range(self.width):
                for j in range(self.height):
                    value = self.normalized_points[j][i]
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

    def work(self, get_texture=True) -> pg.Surface | None:
        if not self.values_are_set:
            self.calculate_values()
        if not self.points_are_set:
            self.calculate_points()
        if not self.normalized_points_are_set:
            self.calculate_normalized_points()
        if get_texture:
            return self.get_texture()


class NoiseTile(Noise, ABC):
    def set_top_neighbor(self, top_neighbor_values: list[list[list[float]]]):
        for self_region, neighbor_region in zip(self.values, top_neighbor_values):
            for i in range(len(self_region)):
                self_region[0][i] = neighbor_region[-1][i]

    def set_bottom_neighbor(self, top_neighbor_values: list[list[list[float]]]):
        for self_region, neighbor_region in zip(self.values, top_neighbor_values):
            for i in range(len(self_region)):
                self_region[-1][i] = neighbor_region[0][i]

    def set_left_neighbor(self, left_neighbor_values):
        for self_region, neighbor_region in zip(self.values, left_neighbor_values):
            for self_row, neighbor_row in zip(self_region, neighbor_region):
                self_row[0] = neighbor_row[-1]

    def set_right_neighbor(self, right_neighbor_values):
        for self_region, neighbor_region in zip(self.values, right_neighbor_values):
            for self_row, neighbor_row in zip(self_region, neighbor_region):
                self_row[-1] = neighbor_row[0]

    def set_bottom_right_neighbor(self, bottom_right_neighbor_values):
        for self_region, neighbor_region in zip(self.values, bottom_right_neighbor_values):
            self_region[-1][-1] = neighbor_region[0][0]
