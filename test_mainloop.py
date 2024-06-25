import gc
gc.disable()
import time

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
pg.init()
scr = pg.display.set_mode((1536, 960))
pg.display.set_caption('Voxels')

from constants import TRAPEZOIDS_CACHE_INFO, SET_FPS_CAPTION, PRINT_FPS
from world import *
from camera import *
from terrain_mesh import *
from trapezoid import TrapeziodTexturer
from sides_drawer import SidesDrawer
from gui.ui_mesh import UIMesh
from events_handler import EventHandler
from gui.player import Player

trap_drawer = TrapeziodTexturer()
trap_drawer.set_print_cache_size(TRAPEZOIDS_CACHE_INFO)
trap_drawer.create_cache()
sides_drawer = SidesDrawer(trap_drawer, scr.get_rect())

clock = pg.time.Clock()
camera_frame = CameraFrame((0, 0), 1536 // BASE_LEVEL_SIZE, 960 // BASE_LEVEL_SIZE, (0, 0))
layers = camera_frame.get_layers()

load_distance = int(max(camera_frame.get_rect().size) / 2) + WORLD_CHUNK_SIZE
world = World()
world_filler = WorldFiller(world, load_distance)

terr_mesh = TerrainMech(sides_drawer, camera_frame, (1536, 960))
ui_mesh = UIMesh(camera_frame, (1536, 960))

events_handler = EventHandler(world, camera_frame, trap_drawer)

player = Player(0, 0, 0)

frame = 0
last_frame_end = time.time()

while True:
    frame += 1
    frame_time = round(time.time() - last_frame_end, 5)
    fps = round(clock.get_fps(), 2)

    for _ in range(5):
        world_filler.load_chucks_by_part()
    if frame % 50 == 0:
        if PRINT_FPS:
            print('check regions')
        world_filler.update_regions_by_distance(*camera_frame.get_rect().center)

    if frame % 300 == 0:
        gc.collect()
        if PRINT_FPS:
            print('garbage collection')

    scr.fill((0, 0, 0))
    camera_frame.update_layers()
    terr_mesh.create_mesh(world)
    terr_mesh.draw_terrain(scr)

    ui_mesh.create_ui_mesh(player, terr_mesh.mouse_rect)
    ui_mesh.draw_ui(scr)

    events_handler.handle(player, fps)

    if SET_FPS_CAPTION:
        pg.display.set_caption(str(camera_frame.get_rect().center) + ' fps: ' + str(fps)  + ' ft: ' + str(frame_time))
    if PRINT_FPS:
        print(str(camera_frame.get_rect().center) + ' fps: ' + str(fps) + ' ft: ' + str(frame_time) +
              ('' if frame_time < 0.03 else ' --- '))
    last_frame_end = time.time()

    pg.display.update()
    clock.tick(60)
