from abc import ABC
import pygame as pg


class Figure(ABC):
    is_side = None
    is_not_side = None

    def reset_rect(self, rect: pg.Rect):
        self.rect = rect

    def set_top_left(self, topleft: tuple[int, int]):
        self.rect.topleft = topleft


class SimpleFigure(Figure):
    def __init__(self, rect: pg.Rect,
                 sprite: pg.Surface,
                 origin_block: tuple[int, int, int],
                 directed_block: tuple[int, int, int]):
        self.rect: pg.Rect = rect
        self.sprite = sprite
        self.origin_block = origin_block
        self.directed_block = directed_block
        self.is_side = self.origin_block[0] != self.directed_block[0] or self.origin_block[1] != self.directed_block[1]
        self.is_not_side = self.origin_block[0] == self.directed_block[0] and self.origin_block[1] == \
                           self.directed_block[1]


class ManySpritesTopFigure(Figure):
    def __init__(self, rect: pg.Rect,
                 sprites: list[pg.Surface],
                 origin_block: tuple[int, int, int],
                 directed_block: tuple[int, int, int]):
        self.rect: pg.Rect = rect
        assert len(sprites) > 0
        self.sprites = sprites
        self.origin_block = origin_block
        self.directed_block = directed_block
        self.is_side = False
        self.is_not_side = True

    def get_sprite(self, ind: int) -> pg.Surface:
        ind = ind % len(self.sprites)
        return self.sprites[ind]

    def get_sprite_for_lod(self) -> pg.Surface:
        return self.sprites[0]
