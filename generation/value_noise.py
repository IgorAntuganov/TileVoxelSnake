import random

import pygame as pg
import time
from generation.interpolations import *
from generation.abc_noise import DataNoiseTile


class ValueNoise(DataNoiseTile):
    def random_value(self, k, x, y):
        return random.random() * 2 - 1

    def _calculate_points(self, print_progress=False):
        for k in self.octaves:
            region: list[list[float]] = self.values[k]
            k1 = 2 ** k
            for i in range(self.width):
                if print_progress:
                    print(f'{k+1}/{len(self.octaves)}, {i+1}/{self.width}')
                for j in range(self.height):
                    if self.width // k1 and self.height // k1 != 0:
                        x = i // (self.width // k1)
                        y = j // (self.height // k1)
                    else:
                        continue

                    top_left = region[x][y]
                    top_right = region[x + 1][y]
                    bottom_left = region[x][y + 1]
                    bottom_right = region[x + 1][y + 1]

                    xf = i % (self.width // k1) / (self.width // k1)
                    yf = j % (self.height // k1) / (self.height // k1)

                    top = interpolate_sigmoid(top_left, top_right, xf)
                    bottom = interpolate_sigmoid(bottom_left, bottom_right, xf)
                    value = interpolate_sigmoid(top, bottom, yf)
                    value = value / k1 / 2
                    self.points[j][i] += value
