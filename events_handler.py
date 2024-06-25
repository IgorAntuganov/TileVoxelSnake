import pygame as pg
from world import World
from camera import CameraFrame
from blocks import *
from trapezoid import TrapeziodTexturer
from gui.objects import Player
from gui.snake import Snake
from constants import CAMERA_SPEED, BLOCKS_PER_MOVE


class InfoScreen:
    def __init__(self, image: pg.Surface, remaining_frames: int):
        self.image = image
        self.remaining_frames = remaining_frames

    def render(self, scr: pg.Surface):
        scr.blit(self.image, (0, 0))
        self.remaining_frames -= 1

    def is_ends(self) -> bool:
        return self.remaining_frames < 1


class EventHandler:
    def __init__(self, world: World, camera: CameraFrame, sides_drawer: TrapeziodTexturer):
        self.world = world
        self.camera = camera
        self.sides_drawer = sides_drawer

    def handle(self, player: Player, snake: Snake, fps: float) -> InfoScreen | None:
        events = pg.event.get()
        mouse_left_click = False
        mouse_right_click = False

        camera_move = [0, 0]
        player_move = [0, 0, 0]

        for event in events:
            if event.type == pg.QUIT:
                self.sides_drawer.save_cache()
                exit()
            if event.type == pg.KEYDOWN:
                if not any(player_move):
                    if event.key == pg.K_w:
                        player_move[1] -= 1
                    if event.key == pg.K_s:
                        player_move[1] += 1
                    if event.key == pg.K_a:
                        player_move[0] -= 1
                    if event.key == pg.K_d:
                        player_move[0] += 1
                    if event.key == pg.K_SPACE:
                        player_move[2] += 1

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

        pressed = pg.key.get_pressed()
        if pressed[pg.K_UP]:
            camera_move[1] -= 1
        if pressed[pg.K_DOWN]:
            camera_move[1] += 1
        if pressed[pg.K_LEFT]:
            camera_move[0] -= 1
        if pressed[pg.K_RIGHT]:
            camera_move[0] += 1
        if fps != 0:
            camera_move = camera_move[0] / fps * CAMERA_SPEED, camera_move[1] / fps * CAMERA_SPEED
        self.camera.move(camera_move)

        zero_stamina_move = False
        if player.stamina > 0 and any(player_move):
            player.spend_stamina(False)
            if player_move[0] or player_move[1]:
                for _ in range(BLOCKS_PER_MOVE):
                    next_position = player.x + player_move[0], player.y + player_move[1]
                    next_column = self.world.get_column(*next_position)
                    if next_column.full_height - 1 <= player.z:
                        height = next_column.full_height - 1
                        player.fall(height)
                        snake.move_horizontally(*player_move[:2])

            column_under_player = self.world.get_column(player.x, player.y)
            height = column_under_player.full_height - 1
            if player.z - height < 1:
                snake.move_player_vertically(player_move[2])

        elif player.stamina == 0:
            column_under_player = self.world.get_column(player.x, player.y)
            height = column_under_player.full_height - 1
            player.fall(height)
            if any(player_move):
                zero_stamina_move = True
                player.init_cooldown()
            player.update_cooldown()

        all_tiles = self.world.get_all_tiles()
        for tile in all_tiles:
            if player.x == tile.x and player.y == tile.y and player.z == tile.z:
                snake.add_tile(tile)
                self.world.set_tile_as_taken(tile)

        if snake.is_ready_for_level_up():
            snake.level_up()
            info_image = pg.Surface((1536, 960), pg.SRCALPHA)
            info_image.fill((0, 255, 0))
            info_image.set_alpha(60)
            return InfoScreen(info_image, 20)

        if zero_stamina_move:
            info_image = pg.Surface((1536, 960), pg.SRCALPHA)
            info_image.fill((255, 0, 0))
            info_image.set_alpha(60)
            return InfoScreen(info_image, 3)

        return None
