from abc import ABC, abstractmethod
import pygame as pg


class Sprite:
    pass


class Block(ABC):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.top_rect = pg.Rect((1, 1, 1, 1))
        self.bottom_rect = pg.Rect((1, 1, 1, 1))
        self.neighbors = []

    def get_xyz(self):
        return self.x, self.y, self.z

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_bottom_size_in_pixels(self, size: list[int | float]):
        self.bottom_rect.inflate_ip(size)

    def set_top_size_in_pixels(self, size: list[int | float]):
        self.top_rect.inflate_ip(size)

    def set_bottom_topleft(self, top_left: list[int | float]):
        self.bottom_rect.topleft = top_left

    def set_top_topleft(self, top_left: list[int | float]):
        self.top_rect.topleft = top_left

    def set_shade(self):
        pass

    def set_neighbors(self, left: bool, top: bool, right: bool, bottom: bool):
        self.neighbors = [left, top, right, bottom]

    @abstractmethod
    def get_sprites(self) -> list[Sprite]:
        pass


class Air(Block):
    def get_sprites(self) -> list[Sprite]:
        return []


class FullBlock(Block):
    def get_sprites(self) -> list[Sprite]:
        pass


class Grass(FullBlock):
    pass


class Dirt(FullBlock):
    pass


class Stone(FullBlock):
    pass
