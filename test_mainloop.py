# import time
import pygame as pg
pg.init()
scr = pg.display.set_mode((1536, 960))

from world import *
from camera import *
from mesh import *

clock = pg.time.Clock()
camera = CameraFrame((0, 0), 1536//BASE_LEVEL_SIZE, 960//BASE_LEVEL_SIZE, (0, 0))
layers = camera.get_layers()
world = World()
world.test_fill()
terr_mesh = TerrainMech(layers)
frame = 0

while True:
    frame += 1
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
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
    # times.append(time.time())  # 5
    focus_in_frame = camera.get_focus_in_frame()
    # times.append(time.time())  # 6
    ordered = terr_mesh.get_elements_in_order(focus_in_frame)
    # times.append(time.time())  # 7
    mouse_rect = None
    for column_figures in ordered:
        for element in column_figures:
            rect, sprite = element
            if camera.screen_rect.colliderect(rect):
                scr.blit(sprite, rect)
        rect = column_figures[0][0]
        if rect.collidepoint(pg.mouse.get_pos()):
            mouse_rect = rect.copy()

    if mouse_rect is not None:
        pg.draw.rect(scr, (255-(60-mouse_rect.width)*10, 0, 0), mouse_rect)

    # times.append(time.time())  # 8
    pg.display.set_caption(str(clock.get_fps()))

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
    clock.tick(1000)
