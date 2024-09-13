CREATING_MESH = True
import gc
gc.disable()
import time

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
pg.init()
from constants import SCREEN_SIZE
scr = pg.display.set_mode(SCREEN_SIZE, vsync=1)
pg.display.set_caption('Voxels')

from constants import *
import world_class
import camera
import mesh_3d
from trapezoid import TrapezoidDrawer
from sides_drawer import SidesDrawer
from gui.mesh_2d import Mesh2D
from events_handler import EventHandler, InfoScreen
from gui.objects import Player
from gui.snake import Snake

trap_drawer = TrapezoidDrawer()
trap_drawer.set_print_cache_size(TRAPEZOIDS_CACHE_INFO)
trap_drawer.create_cache(scr)
sides_drawer = SidesDrawer(trap_drawer, scr.get_rect())

clock = pg.time.Clock()
camera_frame = camera.CameraFrame((0, 0))
layers = camera_frame.get_layers()

world = world_class.World()
world_filler = world_class.WorldFiller(world, camera_frame.get_loading_chunk_distance())

terr_mesh = mesh_3d.Mesh3D(sides_drawer, camera_frame, SCREEN_SIZE)
ui_mesh = Mesh2D(camera_frame, SCREEN_SIZE)

events_handler = EventHandler(world, camera_frame, trap_drawer, terr_mesh)
info_screens: list[InfoScreen] = []

player = Player(0, 0, 0)
snake = Snake(player)

frame = 0
last_frame_end = time.time()

while True:
    frame += 1
    frame_time = round(time.time() - last_frame_end, 5)
    fps = round(clock.get_fps(), 2)

    camera_center = camera_frame.get_rect().center
    for _ in range(LOADED_PARTS_PER_FRAME):
        world_filler.load_chucks_by_part(*camera_center)
    if frame % REGIONS_DISTANCE_UPDATE_FREQ == 0:
        load_dist = camera_frame.get_loading_chunk_distance()
        world_filler.update_regions_by_distance(*camera_center, load_dist)

    if frame % GARBAGE_COLLECTION_FREQ == 0:
        gc.collect()

    if PREFILL_FRAME_WITH_BLACK:
        scr.fill((0, 0, 0))

    info_screen, CREATING_MESH = events_handler.handle(player, snake, fps, terr_mesh.hovered_block,
                                                       terr_mesh.directed_block)
    if info_screen is not None:
        info_screens.append(info_screen)

    camera_frame.update_layers()
    if CREATING_MESH:
        if layers.base_level_size > REGION_DRAWING_LEVEL:
            terr_mesh.draw_world_columns(world, frame, scr)
        else:
            terr_mesh.draw_regions(world, scr)

    if layers.base_level_size > REGION_DRAWING_LEVEL:
        ui_mesh.create_ui_mesh(world, player, snake, terr_mesh.mouse_rect)
        ui_mesh.draw_ui(scr)

    new_info_screens = []
    for info_screen in info_screens:
        info_screen.render(scr)
        if not info_screen.is_ends():
            new_info_screens.append(info_screen)
    info_screens = new_info_screens

    caption = str(camera_frame.get_rect().center) + ' FPS: ' + str(fps) + ' level: ' + str(player.level)
    caption += ' stamina:' + str(player.max_stamina)
    caption += ' cooldown:' + str(round(player.stamina_cooldown, 2))
    caption += ' block size:' + str(camera_frame.get_base_level_size())

    pg.display.set_caption(caption)

    last_frame_end = time.time()

    pg.display.flip()
    clock.tick(MAX_FPS)
