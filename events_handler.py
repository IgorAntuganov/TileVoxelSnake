import pygame as pg
from world import World
from camera import CameraFrame
from blocks import *
from trapezoid import TrapeziodTexturer
from gui.tiles import Player
from constants import CAMERA_SPEED, BLOCKS_PER_MOVE


class EventHandler:
    def __init__(self, world: World, camera: CameraFrame, sides_drawer: TrapeziodTexturer):
        self.world = world
        self.camera = camera
        self.sides_drawer = sides_drawer

    def handle(self, player: Player, fps: float):
        events = pg.event.get()
        mouse_left_click = False
        mouse_right_click = False

        player_move = [0, 0, 0]

        for event in events:
            if event.type == pg.QUIT:
                self.sides_drawer.save_cache()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    player_move[1] -= 1
                    continue
                if event.key == pg.K_s:
                    player_move[1] += 1
                    continue
                if event.key == pg.K_a:
                    player_move[0] -= 1
                    continue
                if event.key == pg.K_d:
                    player_move[0] += 1
                    continue
                if event.key == pg.K_SPACE:
                    player_move[2] += 1
                    continue

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
            pressed_offset[1] -= 1
        if pressed[pg.K_DOWN]:
            pressed_offset[1] += 1
        if pressed[pg.K_LEFT]:
            pressed_offset[0] -= 1
        if pressed[pg.K_RIGHT]:
            pressed_offset[0] += 1
        if fps != 0:
            pressed_offset = pressed_offset[0] / fps * CAMERA_SPEED, pressed_offset[1] / fps * CAMERA_SPEED
        self.camera.move(pressed_offset)

        if player.stamina > 0 and any(player_move):
            for _ in range(BLOCKS_PER_MOVE):
                next_position = player.x + player_move[0], player.y + player_move[1]
                next_column = self.world.get_column(*next_position)
                if next_column.full_height - 1 <= player.z:
                    player.move(*player_move[:2], 0)
            player.spend_stamina(False)

            column_under_player = self.world.get_column(player.x, player.y)
            height = column_under_player.full_height - 1

            if player.z - height < 1:
                player.move(0, 0, player_move[2])

            if player_move[2] != 1:
                player.fall(height)

        elif player.stamina == 0:
            column_under_player = self.world.get_column(player.x, player.y)
            height = column_under_player.full_height - 1
            player.fall(height)
            player.update_cooldown()
        column_under_player = self.world.get_column(player.x, player.y)
        height = column_under_player.full_height - 1
        if player.z < height:
            player.fall(height)

