import pygame as pg
import time
import random
from generation.interpolations import *
from generation.abc_noise import DataNoiseTile


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scalar(self, vect) -> float:
        vect: Vector
        return self.x * vect.x + self.y * vect.y

    @classmethod
    def random_vector(cls):
        angle = random.random() * math.pi * 2
        x = math.cos(angle)
        y = math.sin(angle)
        return Vector(x, y)


class PerlinNoise(DataNoiseTile):
    def random_value(self, k, x, y):
        return Vector.random_vector()

    def _calculate_points(self, print_progress=False):
        for k in self.octaves:
            region: list[list[Vector]] = self.values[k]
            k1 = 2 ** k
            for i in range(self.width):
                if print_progress:
                    print(f'{k+1}/{len(self.octaves)}, {i+1}/{self.width}')
                for j in range(self.height):
                    x = i // (self.width // k1)
                    y = j // (self.height // k1)

                    # corner vectors
                    top_left_corner = region[x][y]
                    top_right_corner = region[x + 1][y]
                    bottom_left_corner = region[x][y + 1]
                    bottom_right_corner = region[x + 1][y + 1]

                    # offset vectors
                    xf = i % (self.width // k1) / (self.width // k1)
                    yf = j % (self.height // k1) / (self.height // k1)

                    top_left_offset = Vector(xf, yf)
                    top_right_offset = Vector(xf-1, yf)
                    bottom_left_offset = Vector(xf, yf-1)
                    bottom_right_offset = Vector(xf-1, yf-1)

                    # scalars
                    top_left = top_left_corner.scalar(top_left_offset)
                    top_right = top_right_corner.scalar(top_right_offset)
                    bottom_left = bottom_left_corner.scalar(bottom_left_offset)
                    bottom_right = bottom_right_corner.scalar(bottom_right_offset)

                    top = interpolate_sigmoid(top_left, top_right, xf)
                    bottom = interpolate_sigmoid(bottom_left, bottom_right, xf)
                    value = interpolate_sigmoid(top, bottom, yf)

                    value = value / (2 ** k)
                    self.points[j][i] += value

    def get_points(self) -> list[list[float]]:
        assert self.points_are_set
        return self.points


def test():
    file_name = f'{int(time.time())}'
    width1, height1 = 512, 512
    noise = PerlinNoise((width1, height1), list(range(2, 9)))
    noise.calculate_values()
    noise.calculate_points(print_progress=True)
    texture = noise.get_texture()
    pg.image.save(texture, f'perlin_test_images/perlin{file_name}.png')
    scr = pg.display.set_mode((width1, height1))
    scr.blit(texture, (0, 0))
    pg.display.update()
    while True:
        [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
