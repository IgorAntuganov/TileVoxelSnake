import pygame as pg
from constants import PATH_TO_PLAYER, PLAYER_SIZE
from camera import Layers


class Player:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.angle = 0
        self.part_of_block = PLAYER_SIZE
        self.sprite = pg.image.load(PATH_TO_PLAYER+'1.png').convert_alpha()
        # self.sprite = pg.transform.scale(self.sprite, (PLAYER_SIZE, PLAYER_SIZE))

    def get_sprite(self, layers: Layers) -> pg.Surface:
        rect = layers.get_rect(int(self.x), int(self.y), int(self.z))
        actual_size = rect.width * PLAYER_SIZE, rect.height * PLAYER_SIZE
        sprite = pg.transform.scale(self.sprite, actual_size)
        return pg.transform.rotate(sprite, self.angle)

    def get_rect(self, layers: Layers) -> pg.Rect:
        rect = layers.get_rect(int(self.x), int(self.y), int(self.z))
        actual_size = rect.width * PLAYER_SIZE, rect.height * PLAYER_SIZE
        top_left = rect.centerx - actual_size[0] // 2, rect.centery - actual_size[1] // 2
        return pg.Rect(top_left, actual_size)

    def move(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z
