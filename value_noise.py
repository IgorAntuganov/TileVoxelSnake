import pygame as pg
import random
import time
from interpolations import *


class ValueNoise:
    def __init__(self, sizes: tuple[int, int], octaves: None | int = None):
        self.sizes = sizes
        self.width, self.height = sizes
        if octaves is not None:
            self.octaves = octaves
        else:
            self.octaves = int(math.log(max(sizes), 2))
        self.values: list[list[list[float]]] = []
        self.points: list[list[float]] = [[0] * self.width for _ in range(self.height)]
        self.texture: None | pg.Surface = None

    def set_values(self):
        for k in range(self.octaves):
            region = []
            f = 2 ** (k+1)
            for x in range(f + 1):
                row = []
                for y in range(f + 1):
                    value = 2 * random.random() ** .5 - 1
                    row.append(value)
                region.append(row)
            self.values.append(region)

    def get_values(self) -> list[list[list[float]]]:
        return self.values

    def set_points(self, print_progress=False):
        for k in range(self.octaves):
            region: list[list[float]] = self.values[k]
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
                    top_left = region[x][y]
                    top_right = region[x + 1][y]
                    bottom_left = region[x][y + 1]
                    bottom_right = region[x + 1][y + 1]

                    xf = i % (self.width // k1) / (self.width // k1)
                    yf = j % (self.height // k1) / (self.height // k1)

                    top = interpolate_sigmoid(top_left, top_right, xf)
                    bottom = interpolate_sigmoid(bottom_left, bottom_right, xf)
                    value = interpolate_sigmoid(top, bottom, yf)
                    value = value / k1
                    self.points[j][i] += value

    def get_points(self) -> list[list[float]]:
        return self.points

    def get_texture(self) -> pg.Surface:
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
    noise = ValueNoise((width1, height1))
    noise.set_values()
    noise.set_points(print_progress=True)
    texture = noise.get_texture()
    pg.image.save(texture, f'perlin_test_images/value{file_name}.png')
    scr = pg.display.set_mode((width1, height1))
    scr.blit(texture, (0, 0))
    pg.display.update()
    while True:
        [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
