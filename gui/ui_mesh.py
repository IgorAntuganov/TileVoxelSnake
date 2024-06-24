import pygame as pg
from camera import CameraFrame
from gui.player import Player


class UIFigure:
    def __init__(self, sprite: pg.Surface, rect: pg.Rect):
        self.sprite = sprite
        self.rect = rect


class UIMesh:
    def __init__(self, camera: CameraFrame, sizes: tuple[int, int]):
        self.camera = camera
        self.sizes = sizes
        self.elements = []

    def create_ui_mesh(self, player: Player, hovered_block_rect: pg.Rect | None):
        self.elements = []
        layers = self.camera.get_layers()

        if hovered_block_rect is not None:
            hovered_block_sprite = pg.Surface(hovered_block_rect.size, pg.SRCALPHA)
            hovered_block_sprite.fill((255, 255, 255, 120))
            hovered_block_figure = UIFigure(hovered_block_sprite, hovered_block_rect)
            self.elements.append(hovered_block_figure)

        player_figure = UIFigure(player.get_sprite(layers), player.get_rect(layers))
        self.elements.append(player_figure)

    def draw_ui(self, scr: pg.Surface):
        for figure in self.elements:
            scr.blit(figure.sprite, figure.rect)
