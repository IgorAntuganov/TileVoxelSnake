import pygame as pg
import random
import time
from interpolations import *


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scalar(self, vect) -> float:
        vect: Vector
        return self.x * vect.x + self.y * vect.y

    @classmethod
    def random_vector(cls):
        x = random.random() * 2 - 1
        y = random.random() * 2 - 1
        return Vector(x, y)


class PerlinNoise:
    def __init__(self, sizes: tuple[int, int], octaves: None | int = None):
        self.sizes = sizes
        self.width, self.height = sizes
        if octaves is not None:
            self.octaves = octaves
        else:
            self.octaves = int(math.log(max(sizes), 2))
        self.values: list[list[list[Vector]]] = []
        self.points: list[list[float]] = [[0] * self.width for _ in range(self.height)]
        self.points_are_set = False
        self.texture: None | pg.Surface = None

    def set_values(self):
        for k in range(self.octaves):
            region = []
            f = 2 ** (k+1)
            for x in range(f + 1):
                row = []
                for y in range(f + 1):
                    value = Vector.random_vector()
                    row.append(value)
                region.append(row)
            self.values.append(region)

    def get_values(self) -> list[list[list[Vector]]]:
        return self.values

    def set_points(self, print_progress=False):
        for k in range(1, self.octaves):
            region: list[list[Vector]] = self.values[k]
            k1 = 2 ** k
            for i in range(self.width):
                if print_progress:
                    print(f'{k+1}/{self.octaves}, {i+1}/{self.width}')
                for j in range(self.height):
                    if self.width // k1 and self.height // k1 != 0:
                        x = i // (self.width // k1)
                        y = j // (self.height // k1)
                    else:
                        continue
                    x -= k1 // 2
                    y -= k1 // 2

                    # corner vectors
                    top_left_corner = region[x][y]
                    top_right_corner = region[x + 1][y]
                    bottom_left_corner = region[x][y + 1]
                    bottom_right_corner = region[x + 1][y + 1]

                    xf = i % (self.width // k1) / (self.width // k1)
                    yf = j % (self.height // k1) / (self.height // k1)

                    # offset vectors
                    top_left_offset = Vector(xf, yf)
                    top_right_offset = Vector(xf-1, yf)
                    bottom_left_offset = Vector(xf, yf-1)
                    bottom_right_offset = Vector(xf-1, yf-1)

                    top_left = top_left_corner.scalar(top_left_offset)
                    top_right = top_right_corner.scalar(top_right_offset)
                    bottom_left = bottom_left_corner.scalar(bottom_left_offset)
                    bottom_right = bottom_right_corner.scalar(bottom_right_offset)

                    top = interpolate_sigmoid(top_left, top_right, xf)
                    bottom = interpolate_sigmoid(bottom_left, bottom_right, xf)
                    value = interpolate_sigmoid(top, bottom, yf)
                    # value = sum([top_left, top_right, bottom_left, bottom_right]) / 4
                    value = value / k1
                    self.points[j][i] += value
        self.points_are_set = True

    def get_points(self) -> list[list[float]]:
        assert self.points_are_set
        return self.points

    def get_texture(self) -> pg.Surface:
        assert self.points_are_set
        if self.texture is None:
            texture = pg.Surface((self.width, self.height))
            for i in range(self.width):
                for j in range(self.height):
                    value = self.points[j][i] / self.octaves
                    value = (value + 1) / 2
                    color = int(value * 255 * 2 ** (self.octaves / 2))
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


def test():
    file_name = f'{int(time.time())}'
    width1, height1 = 512, 512
    noise = PerlinNoise((width1, height1))
    noise.set_values()
    noise.set_points(print_progress=True)
    texture = noise.get_texture()
    pg.image.save(texture, f'perlin_test_images/perlin{file_name}.png')
    scr = pg.display.set_mode((width1, height1))
    scr.blit(texture, (0, 0))
    pg.display.update()
    while True:
        [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
