import gc
gc.disable()

import time
import pygame as pg
pg.init()
scr = pg.display.set_mode((1536, 960))
pg.display.set_caption('Voxels')

from world import *
from camera import *
from mesh import *
from trapezoid import SidesDrawer
from constants import TRAPEZOIDS_CACHE_INFO, SET_FPS_CAPTION, PRINT_FPS

sides_drawer = SidesDrawer()
sides_drawer.set_print_cache_size(TRAPEZOIDS_CACHE_INFO)
sides_drawer.create_cache()

clock = pg.time.Clock()
camera_frame = CameraFrame((0, 0), 1536 // BASE_LEVEL_SIZE, 960 // BASE_LEVEL_SIZE, (0, 0))
layers = camera_frame.get_layers()
load_distance = int(max(camera_frame.get_rect().size) / 2) + WORLD_CHUNK_SIZE
world = World()
world_filler = WorldFiller(world, load_distance)
terr_mesh = TerrainMech(sides_drawer, layers, (1536, 960))

frame = 0
last_frame_end = time.time()

while True:
    frame += 1
    events = pg.event.get()
    mouse_left_click = False
    mouse_right_click = False
    for event in events:
        if event.type == pg.QUIT:
            sides_drawer.save_cache()
            exit()
        if event.type == pg.KEYDOWN:
            offset = [0, 0]
            if event.key == pg.K_w:
                offset[1] -= .3
            if event.key == pg.K_s:
                offset[1] += .2
            if event.key == pg.K_a:
                offset[0] -= .2
            if event.key == pg.K_d:
                offset[0] += .3
            camera_frame.move(offset)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_click = True
            if event.button == 3:
                mouse_right_click = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                world.DEFAULT_ADDED_BLOCK = Grass
            if event.key == pg.K_2:
                world.DEFAULT_ADDED_BLOCK = Dirt
            if event.key == pg.K_3:
                world.DEFAULT_ADDED_BLOCK = Stone
            if event.key == pg.K_4:
                world.DEFAULT_ADDED_BLOCK = Sand
            if event.key == pg.K_5:
                world.DEFAULT_ADDED_BLOCK = OakLog
            if event.key == pg.K_6:
                world.DEFAULT_ADDED_BLOCK = Leaves
            if event.key == pg.K_7:
                world.DEFAULT_ADDED_BLOCK = Shadow
            if event.key == pg.K_8:
                world.DEFAULT_ADDED_BLOCK = DebugBlock
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
    if clock.get_fps() != 0:
        pressed_offset = pressed_offset[0] / clock.get_fps() * 60, pressed_offset[1] / clock.get_fps() * 60
    camera_frame.move(pressed_offset)

    for _ in range(5):
        world_filler.load_chucks_by_part()
    if frame % 50 == 0:
        if PRINT_FPS:
            print('check regions')
        world_filler.check_regions_distance(*camera_frame.get_rect().center)

    if frame % 300 == 0:
        gc.collect()
        if PRINT_FPS:
            print('garbage collection')

    scr.fill((0, 0, 0))
    camera_frame.update_layers()
    terr_mesh.create_mesh(world, camera_frame)
    ordered = terr_mesh.get_elements()
    mouse_rect = None
    block_to_add = None
    block_to_delete = None

    for column_figures in ordered:
        for figure in column_figures:
            rect, sprite = figure.rect, figure.sprite
            if camera_frame.screen_rect.colliderect(rect):
                scr.blit(sprite, rect)

            if rect.collidepoint(pg.mouse.get_pos()):
                mouse_rect = rect.copy()
                if mouse_left_click:
                    block_to_delete = figure.origin_block

                elif mouse_right_click:
                    block_to_add = figure.directed_block

    if block_to_delete is not None:
        world.remove_block_and_save_changes(block_to_delete)
    if block_to_add is not None:
        world.add_block_and_save_changes(block_to_add)
    if mouse_rect is not None:
        sprite = pg.Surface(mouse_rect.size)
        sprite.fill((200, 200, 200))
        sprite.set_alpha(120)
        scr.blit(sprite, mouse_rect.topleft)

    frame_time = round(time.time() - last_frame_end, 5)
    fps = str(round(clock.get_fps(), 2))
    if SET_FPS_CAPTION:
        pg.display.set_caption(str(camera_frame.get_rect().center) + ' fps: ' + fps + ' ft: ' + str(frame_time))
    if PRINT_FPS:
        print(str(camera_frame.get_rect().center) + ' fps: ' + fps + ' ft: ' + str(frame_time) +
              ('' if frame_time < 0.03 else ' --- '))
    last_frame_end = time.time()

    pg.display.update()
    clock.tick(60)
