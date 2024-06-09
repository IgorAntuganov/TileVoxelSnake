# import time
import pygame as pg
pg.init()
scr = pg.display.set_mode((1536, 960))

from world import *
from camera import *
from mesh import *

clock = pg.time.Clock()
camera = CameraFrame((0, 0), 1536//BASE_LEVEL_SIZE, 960//BASE_LEVEL_SIZE, (0, 0))
world = World()
world.test_fill()
# frame = 0

while True:
    # frame += 1
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
    camera.move(pressed_offset)

    # render
    # times = [time.time()]
    scr.fill((0, 0, 0))
    # times.append(time.time())
    column_cords = camera.get_rect()
    # times.append(time.time())
    columns_to_draw = world.get_columns_in_rect(column_cords)
    # times.append(time.time())
    layers = camera.get_layers()
    # times.append(time.time())
    _mesh = Mech(columns_to_draw, layers)
    # times.append(time.time())
    focus_in_frame = camera.get_focus_in_frame()
    # times.append(time.time())
    ordered = _mesh.get_elements_in_order(focus_in_frame)
    # times.append(time.time())
    for element in ordered:
        element.render(scr)
    # times.append(time.time())
    pg.display.set_caption(str(clock.get_fps()))

    '''if frame % 25 == 0:
        print(' - ' * 30)
        print(len(ordered))
        for i in range(1, len(times)):
            t = round(times[i]-times[i-1], 10)
            if t == 0:
                print(i, t)
            else:
                print(i, round(1/t), t)'''

    pg.display.update()
    clock.tick(120)
