import pygame as pg
from world import World
from camera import CameraFrame
from blocks import *
from trapezoid import TrapeziodTexturer
from gui.player import Player


class EventHandler:
    def __init__(self, world: World, camera: CameraFrame, sides_drawer: TrapeziodTexturer):
        self.world = world
        self.camera = camera
        self.sides_drawer = sides_drawer

    def handle(self, player: Player, fps: float):
        events = pg.event.get()
        mouse_left_click = False
        mouse_right_click = False
        for event in events:
            if event.type == pg.QUIT:
                self.sides_drawer.save_cache()
                exit()
            if event.type == pg.KEYDOWN:
                offset = [0, 0, 0]
                if event.key == pg.K_w:
                    offset[1] -= 1
                if event.key == pg.K_s:
                    offset[1] += 1
                if event.key == pg.K_a:
                    offset[0] -= 1
                if event.key == pg.K_d:
                    offset[0] += 1
                if event.key == pg.K_q:
                    offset[2] += 1
                if event.key == pg.K_e:
                    offset[2] -= 1
                player.move(*offset)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_left_click = True
                if event.button == 3:
                    mouse_right_click = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    self.world.DEFAULT_ADDED_BLOCK = Grass
                if event.key == pg.K_2:
                    self.world.DEFAULT_ADDED_BLOCK = Dirt
                if event.key == pg.K_3:
                    self.world.DEFAULT_ADDED_BLOCK = Stone
                if event.key == pg.K_4:
                    self.world.DEFAULT_ADDED_BLOCK = Sand
                if event.key == pg.K_5:
                    self.world.DEFAULT_ADDED_BLOCK = OakLog
                if event.key == pg.K_6:
                    self.world.DEFAULT_ADDED_BLOCK = Leaves
                if event.key == pg.K_7:
                    self.world.DEFAULT_ADDED_BLOCK = Shadow
                if event.key == pg.K_8:
                    self.world.DEFAULT_ADDED_BLOCK = DebugBlock
        pressed_offset = [0, 0]
        pressed = pg.key.get_pressed()
        if pressed[pg.K_UP]:
            pressed_offset[1] -= .19
        if pressed[pg.K_DOWN]:
            pressed_offset[1] += .195
        if pressed[pg.K_LEFT]:
            pressed_offset[0] -= .19
        if pressed[pg.K_RIGHT]:
            pressed_offset[0] += .195
        if fps != 0:
            pressed_offset = pressed_offset[0] / fps * 60, pressed_offset[1] / fps * 60
        self.camera.move(pressed_offset)
