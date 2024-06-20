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
        angle = random.random() * math.pi * 2
        x = math.cos(angle)
        y = math.sin(angle)
        return Vector(x, y)


class InfPerlinNoise:
    def __init__(self, sizes: tuple[int, int], multi: float = 1.0):
        self.sizes = sizes
        self.width, self.height = sizes
        self.multi = multi
        self.values: list[list[Vector]] = []
        # self.points: list[list[float]] = [[0] * self.width for _ in range(self.height)]
        self.texture: None | pg.Surface = None
        self.values_are_set = False

    def random_value(self, x, y):
        return Vector.random_vector()

    def set_values(self):
        for x in range(self.height + 1):
            row = []
            for y in range(self.width + 1):
                value = self.random_value(x, y)
                row.append(value)
            self.values.append(row)
        self.values_are_set = True

    def get_values(self) -> list[list[Vector]]:
        return self.values

    '''def set_top_neighbor(self, top_neighbor_values: list[list[list[float]]]):
        for self_region, neighbor_region in zip(self.values, top_neighbor_values):
            for j in range(len(self_region)//2):
                self_region[j] = neighbor_region[len(self_region)//2 + j][:]
        # for i in range(len(self.values)):
        #     self.values[i] = top_neighbor_values[i]

    def set_left_neighbor(self, left_neighbor_values):
        for self_region, neighbor_region in zip(self.values, left_neighbor_values):
            for self_row, neighbor_row in zip(self_region, neighbor_region):
                for j in range(len(self_row) // 2):
                    self_row[j] = neighbor_row[len(self_row) // 2 + j]'''

    def get_texture(self, width, height) -> pg.Surface:
        assert self.values_are_set
        if self.texture is None:
            texture = pg.Surface((width, height))
            part_width = width // self.width
            part_height = height // self.height
            print(part_width, part_height)
            for i in range(width):
                for j in range(height):
                    x = i // part_width
                    y = j // part_height

                    # corner vectors
                    top_left_corner = self.values[x][y]
                    top_right_corner = self.values[x + 1][y]
                    bottom_left_corner = self.values[x][y + 1]
                    bottom_right_corner = self.values[x + 1][y + 1]

                    xf = (i % part_width) / part_width
                    yf = (j % part_height) / part_height

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
                    value *= self.multi
                    value = (value + 1) / 2

                    color = int(value*255)
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


def test():
    file_name = f'{int(time.time())}'
    start = 0
    end = 9
    noises = [InfPerlinNoise((2**i, 2**i), 1/(2**(i-5))) for i in range(start, end)]
    for noise in noises:
        noise.set_values()
    width1, height1 = 512, 512
    textures = []
    for noise in noises:
        texture = noise.get_texture(width1, height1)
        textures.append(texture)
    image = pg.transform.average_surfaces(textures)
    '''for i in range(width1):
        for j in range(height1):
            pixel = image.get_at((i, j))
            color = pixel[0]
            color = 128 + (color - 128) * (end-start)
            pixel = [color] * 3
            image.set_at((i, j), pixel)'''
    pg.image.save(image, f'perlin_test_images/infperlin{file_name}.png')
    scr = pg.display.set_mode((width1, height1))
    scr.blit(image, (0, 0))
    pg.display.update()
    while True:
        [exit() for event in pg.event.get() if event.type == pg.QUIT]


if __name__ == '__main__':
    test()
