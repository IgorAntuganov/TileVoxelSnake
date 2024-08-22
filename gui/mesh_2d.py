import pygame as pg
from camera import CameraFrame
from gui.objects import Player
from gui.snake import Snake
from world_class import World
from constants import *


class UIFigure:
    def __init__(self, sprite: pg.Surface, rect: pg.Rect, z: int):
        self.sprite = sprite
        self.rect = rect
        self.z = z


class Mesh2D:
    def __init__(self, camera: CameraFrame, sizes: tuple[int, int]):
        self.camera = camera
        self.sizes = sizes
        self.elements = []

    def create_ui_mesh(self, world: World, player: Player, snake: Snake, hovered_block_rect: pg.Rect | None):
        self.elements = []
        layers = self.camera.get_layers()

        if hovered_block_rect is not None:
            hovered_block_sprite = pg.Surface(hovered_block_rect.size, pg.SRCALPHA)
            hovered_block_sprite.fill((255, 255, 255, 120))
            hovered_block_figure = UIFigure(hovered_block_sprite, hovered_block_rect, 100000)
            self.elements.append(hovered_block_figure)

        player_sprite = player.get_sprite(layers)
        player_rect = player.get_rect(layers)
        player_figure = UIFigure(player_sprite, player_rect, player.z)
        for tile in snake.get_body():
            sprite = tile.get_sprite(layers).copy()
            sprite.set_alpha(150)
            rect = tile.get_rect(layers)
            tile_figure = UIFigure(sprite, rect, tile.z)
            self.elements.append(tile_figure)

        for tile in world.get_all_tiles():
            column_under_tile = world.get_column(tile.x, tile.y)
            buried = tile.z+1 < column_under_tile.full_height
            tile_figure = UIFigure(tile.get_sprite(layers, buried), tile.get_rect(layers), tile.z)
            if DRAW_TILES:
                self.elements.append(tile_figure)

        self.elements.append(player_figure)
        self.elements.sort(key=lambda fig: fig.z)

    def draw_ui(self, scr: pg.Surface):
        for figure in self.elements:
            scr.blit(figure.sprite, figure.rect)
