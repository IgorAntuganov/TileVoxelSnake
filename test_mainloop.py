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
camera = CameraFrame((0, 0), 1536//BASE_LEVEL_SIZE, 960//BASE_LEVEL_SIZE, (0, 0))
layers = camera.get_layers()
load_distance = int(max(camera.get_rect().size)/2) + WORLD_CHUNK_SIZE
world = World(load_distance)
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
            camera.move(offset)
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
                world.DEFAULT_ADDED_BLOCK = Air
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
    camera.move(pressed_offset)

    world.load_regions_partly()
    if frame % 25 == 0:
        world.check_regions_distance(*camera.get_rect().center)

    # render
    # times = [time.time()]
    scr.fill((0, 0, 0))
    # times.append(time.time())  # 1
    column_cords = camera.get_rect()
    # times.append(time.time())  # 2
    columns_to_draw = world.get_columns_in_rect_generator(column_cords)
    # times.append(time.time())  # 3
    camera.update_layers()
    # times.append(time.time())  # 4
    terr_mesh.create_mesh(columns_to_draw)
    # times.append(time.time())  # 6
    ordered = terr_mesh.get_elements()
    # times.append(time.time())  # 7
    mouse_rect = None
    block_to_add = None
    block_to_delete = None

    for column_figures in ordered:
        for figure in column_figures:
            rect, sprite = figure.rect, figure.sprite
            if camera.screen_rect.colliderect(rect):
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

    # times.append(time.time())  # 8
    frame_time = round(time.time() - last_frame_end, 5)
    fps = str(round(clock.get_fps(), 2))
    if SET_FPS_CAPTION:
        pg.display.set_caption(str(camera.get_rect().center) + ' fps: ' + fps + ' ft: ' + str(frame_time))
    if PRINT_FPS:
        print(str(camera.get_rect().center) + ' fps: ' + fps + ' ft: ' + str(frame_time))
    last_frame_end = time.time()
    # if frame % 25 == 0:
    #     print(' - ' * 30)
    #     print(len(ordered), 'blocks on screen')
    #     for i in range(1, len(times)):
    #         t = round(times[i]-times[i-1], 10)
    #         if t == 0:
    #             print(i, t)
    #         else:
    #             print(i, round(1/t), t)

    pg.display.update()
    clock.tick(60)
