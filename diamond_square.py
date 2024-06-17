import random

import pygame as pg
import math
import time


class DiamondSquare:
    def __init__(self, sizes: tuple[int, int], octaves: None | int | list[int] = None):
        """:param sizes: Must be 2**n + 1 !!!
        """
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
        self.points: list[list[float]] = [[0] * self.width for _ in range(self.height)]

        self.points[0][0] = random.random() * 2 - 1
        self.points[0][-1] = random.random() * 2 - 1
        self.points[-1][0] = random.random() * 2 - 1
        self.points[-1][-1] = random.random() * 2 - 1

        self.points_are_set = False
        self.texture: None | pg.Surface = None

    def set_values(self, print_progress=False):
        for k in self.octaves:
            k1 = 2 ** k
            _width = ((self.width-1) // k1)
            _height = ((self.height-1) // k1)
            # diamond part
            for i in range(k1):
                if print_progress:
                    print(f'{k}/{max(self.octaves)} {i+1}/{k1*2}')
                for j in range(k1):
                    x, y = i * _width, j * _height
                    x1, y1 = (i+1) * _width, (j+1) * _height
                    center_x = (x + x1) // 2
                    center_y = (y + y1) // 2
                    top_left = self.points[y][x]
                    top_right = self.points[y][x1]
                    bottom_left = self.points[y1][x]
                    bottom_right = self.points[y1][x1]
                    value = sum([top_right, top_left, bottom_right, bottom_left]) / 4
                    value += (random.random() * 2 - 1) / k1
                    self.points[center_y][center_x] = value

            # square part
            for i in range(k1):
                if print_progress:
                    print(f'{k}/{max(self.octaves)} {i+k1+1}/{k1*2}')
                for j in range(k1):
                    x, y = i * _width, j * _height
                    x1, y1 = (i + 1) * _width, (j + 1) * _height
                    center_x = (x + x1) // 2
                    center_y = (y + y1) // 2
                    if i == 0 or j == 0:
                        points = [
                            (center_x, y),  # top
                            (x, center_y),  # left
                            (center_x, y1),  # bottom
                            (x1, center_y)  # right
                        ]
                    else:
                        points = [
                            (center_x, y1),  # bottom
                            (x1, center_y)  # right
                        ]
                    rx = center_x - x
                    ry = center_y - y
                    offsets = [
                        (0, -ry),  # top
                        (rx, 0),  # right
                        (0, ry),  # bottom
                        (-rx, 0)  # left
                    ]
                    for p in points:
                        value = 0
                        m = 0
                        for offset in offsets:
                            ind_i = p[0] + offset[0]
                            ind_j = p[1] + offset[1]
                            if 0 <= ind_i < self.width and 0 <= ind_j < self.height:
                                value += self.points[ind_j][ind_i]
                                m += 1
                        value = value / m
                        value += (random.random() * 2 - 1) / k1
                        p_i, p_j = p
                        self.points[p_j][p_i] = value
        self.points_are_set = True

    def get_values(self):
        return self.points

    def get_texture(self):
        assert self.points_are_set
        if self.texture is None:
            texture = pg.Surface((self.width, self.height))
            for i in range(self.width):
                for j in range(self.height):
                    power = len(self.octaves)
                    value = self.points[j][i] / power
                    value = (value + 1) / 2
                    color = int(value * 255 * 2 ** (power / 2))
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

    def work(self):
        pass


def test():
    power = 10
    width, height = 2 ** power, 2 ** power
    noise = DiamondSquare((width+1, height+1), list(range(3, power)))
    noise.set_values(True)
    print('texturing...')
    texture = noise.get_texture()
    file_name = f'{int(time.time())}'
    pg.image.save(texture, f'perlin_test_images/diamond_square{file_name}.png')
    print('done')
    if height < 1080:
        scr = pg.display.set_mode((width, height))
        scr.blit(texture, (0, 0))
        pg.display.update()
        while True:
            [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
