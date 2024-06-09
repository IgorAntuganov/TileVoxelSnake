from world import *
from camera import *
from mesh import *

scr = pg.display.set_mode((1600, 900))
clock = pg.time.Clock()
camera = CameraFrame((5, 5), 1600//BASE_LEVEL_SIZE+3, 900//BASE_LEVEL_SIZE+4, (5, 5))
world = World()
world.test_fill()

while True:
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
        pressed_offset[1] -= .3
    if pressed[pg.K_DOWN]:
        pressed_offset[1] += .2
    if pressed[pg.K_LEFT]:
        pressed_offset[0] -= .2
    if pressed[pg.K_RIGHT]:
        pressed_offset[0] += .3
    camera.move(pressed_offset)

    # render
    scr.fill((0, 0, 0))
    column_cords = camera.get_rect()
    columns_to_draw = world.get_columns_in_rect(column_cords)
    layers = camera.get_layers()
    _mesh = Mech(columns_to_draw, layers)
    focus_in_frame = camera.get_focus_in_frame()
    for element in _mesh.get_elements_in_order(focus_in_frame):
        element.render(scr)
    clock.tick(120)
    pg.display.set_caption(str(clock.get_fps()))
    pg.display.update()
