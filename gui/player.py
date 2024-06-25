from abc import ABC, abstractmethod
import time
import pygame as pg
from constants import PATH_TO_TILES, START_PLAYER_STAMINA, START_PLAYER_COOLDOWN
from camera import Layers


class Tile(ABC):
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
        self.sprites: dict[str: pg.Surface] = {}
        self.sprites_loaded = False
        self.last_location: tuple[int, int, int] = x, y, z

    @property
    @abstractmethod
    def load_sprites(self):
        pass

    def get_sprite(self, layers: Layers, buried: bool = False) -> pg.Surface:
        if not self.sprites_loaded:
            self.load_sprites()
            self.sprites_loaded = True
        rect = layers.get_rect(int(self.x), int(self.y), int(self.z))
        if buried:
            sprite = self.sprites['buried']
        else:
            sprite = self.sprites['exposed']
        sprite = pg.transform.scale(sprite, rect.size)
        return sprite

    def get_rect(self, layers: Layers) -> pg.Rect:
        rect = layers.get_rect(int(self.x), int(self.y), int(self.z))
        return pg.Rect(rect)

    def move(self, x, y, z):
        self.last_location = self.x, self.y, self.z
        self.x += x
        self.y += y
        self.z += z


class Player(Tile):
    def __init__(self, x: int, y: int, z: int):
        super().__init__(x, y, z)
        self.angle: int = 0
        self.stamina: int = 0
        self.max_stamina: int = START_PLAYER_STAMINA
        self.stamina_cooldown = START_PLAYER_COOLDOWN
        self.stamina_cooldown_start: float = time.time()

    def load_sprites(self):
        ready_sprite = pg.image.load(PATH_TO_TILES + 'player_ready.png').convert_alpha()
        no_stamina_sprite = pg.image.load(PATH_TO_TILES + 'no_stamina.png').convert_alpha()
        self.sprites['ready'] = ready_sprite
        self.sprites['no_stamina'] = no_stamina_sprite

    def get_sprite(self, layers: Layers, buried=False) -> pg.Surface:
        if not self.sprites_loaded:
            self.load_sprites()
            self.sprites_loaded = True
        rect = layers.get_rect(int(self.x), int(self.y), int(self.z))
        if self.stamina != 0:
            sprite = self.sprites['ready']
        else:
            sprite = self.sprites['no_stamina']
        sprite = pg.transform.scale(sprite, rect.size)
        assert self.angle in [0, 90, 180, 270]
        return pg.transform.rotate(sprite, self.angle)

    def spend_stamina(self, full: bool = False):
        if full:
            self.stamina = 0
        else:
            self.stamina -= 1
        if self.stamina == 0:
            self.stamina_cooldown_start = time.time()

    def update_cooldown(self):
        if time.time() - self.stamina_cooldown_start > self.stamina_cooldown:
            self.stamina = self.max_stamina

    def fall(self, height: int):
        self.z = height


class ColoredTile(Tile, ABC):
    sprite = 'debug_tile.png'

    def load_sprites(self):
        exposed = pg.image.load(PATH_TO_TILES + self.sprite).convert_alpha()
        buried = exposed.copy()
        shadow = pg.Surface(buried.get_rect().size)
        shadow.fill((0, 0, 0))
        shadow.set_alpha(200)
        buried.blit(shadow, (0, 0))
        self.sprites['buried'] = buried
        self.sprites['exposed'] = exposed


class RedTile(ColoredTile):
    sprite = 'red_tile.png'


class GreenTile(ColoredTile):
    sprite = 'green_tile.png'


class YellowTile(ColoredTile):
    sprite = 'yellow_tile.png'


class BlueTile(ColoredTile):
    sprite = 'blue_tile.png'


class VioletTile(ColoredTile):
    sprite = 'violet_tile.png'
