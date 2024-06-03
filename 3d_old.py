import pygame as pg
import pickle

scr_size = (1280, 720)
scr_size = (800, 600)
scr_size = (1920, 1080)
scr_size = (1536, 960)
x, y = -200, -200
FPS = 60
using_cache = False
back_color = (0, 0, 0)
brown_color = (50, 50, 30)
green_color = (90, 131, 55)
red_color = (255, 0, 0)
dirt_color = (121, 85, 58)
size1 = 48
size2 = 51
size3 = 57
sides_scale_factor = 1  # 2 is best
smooth_sides = False
twice_up_height_in_blocks = 3
mouse_slope_factor = 100
using_mouse_slope = False
using_anisotropic_filtration = True
max_anisotropic_filtration = 4
using_shadows = True
shadow_radius = size1 // 2
render_smaller_resolution = False
render_sides_every_n_frame = 2

move2 = move1 = 1
move1 = size1 * 6 // FPS
move2 = size1 * 8 // FPS

twice_size_equals = 1

fix_lane_width = 3
up_blocks = [
    (1, 1),
    (1, 2),
    (2, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (4, 5),
    (4, 6),
    (6, 4),
    (6, 6),
    (-10, -10),
    (-9, -9),
    (-11, -10),
    (-12, -9)
]
twice_up_blocks = [
(10, 10),
(10 - 1, 10 - 1),
(10 - 1, 10),
(10, 10 - 1),
(10 - 4, 10),
(5, 5),
(5, 7),
(3, 5),
(-5, -5),
(10, 10 + 5),
(9, 9 + 5),
(11, 10 + 5),
(12, 9 + 5),
(-30, -30),
] + [(25, i) for i in range(-20, 20)]
for j in range(20):
    twice_up_blocks += [(50 + j, 2 * i + j % 2) for i in range(-20, 20)]
    up_blocks += [(50 + j, 2 * i + j % 2 + 1) for i in range(0, 20)]

for i in range(100):
    for j in range(100):
        if (50 - i) ** 2 + (50 - j) ** 2 < 250:
            twice_up_blocks.append((i - 40, j))

twice_up_blocks = set(twice_up_blocks)
up_blocks = set(up_blocks)
all_up_blocks = twice_up_blocks.copy()
all_up_blocks.update(up_blocks)

if render_smaller_resolution:
    true_screen = pg.display.set_mode(scr_size, pg.SRCALPHA)
    screen = pg.Surface((scr_size[0]//2, scr_size[1]//2))
    size1 = size1//2
    size2 = size2//2
    size3 = size3//2
    center_x = scr_size[0] // 4
    center_y = scr_size[1] // 4
else:
    true_screen = None
    screen = pg.display.set_mode(scr_size)
    center_x = scr_size[0] // 2
    center_y = scr_size[1] // 2

if render_sides_every_n_frame != 1:
    sides_screen = pg.Surface(scr_size, pg.SRCALPHA)
else:
    sides_screen = None

grass = pg.image.load('grass.png')
dirt = pg.image.load('dirt.png')
'''grass = pg.Surface((32, 32))
grass.blit(grass1, (0, 0))
grass.blit(grass1, (16, 0))
grass.blit(grass1, (16, 16))
grass.blit(grass1, (0, 16))'''
sprite1 = pg.transform.scale(grass, (size1, size1))
sprite2 = pg.transform.scale(grass, (size2, size2))
sprite3 = pg.transform.scale(grass, (size3, size3))
sprite4 = sprite1.copy()
sprite4.fill((0, 255, 20))
black_sprite = pg.Surface((size1, size1))
black_sprite.fill(brown_color)
black_sprites = {}

sprite1_top_shadow = pg.Surface((size1, size1), pg.SRCALPHA)
for i in range(size1):
    for j in range(size1):
        k = 1 - (1 * j / shadow_radius)
        pixel = pg.Surface((1, 1), pg.SRCALPHA)
        pixel.fill((0, 0, 0))
        pixel.set_alpha(int(k * 55))
        sprite1_top_shadow.blit(pixel, (i, j))
sprite1_right_shadow = pg.transform.rotate(sprite1_top_shadow, 270)
sprite1_bottom_shadow = pg.transform.rotate(sprite1_top_shadow, 180)
sprite1_left_shadow = pg.transform.rotate(sprite1_top_shadow, 90)

sprite1_top_left_shadow = pg.Surface((size1, size1), pg.SRCALPHA)
for i in range(size1):
    for j in range(size1):
        f = (i + j)
        k = 1 - (1 * f / shadow_radius)
        pixel = pg.Surface((1, 1), pg.SRCALPHA)
        pixel.fill((0, 0, 0))
        pixel.set_alpha(int(k * 55))
        sprite1_top_left_shadow.blit(pixel, (i, j))
sprite1_top_right_shadow = pg.transform.rotate(sprite1_top_left_shadow, 270)
sprite1_bottom_right_shadow = pg.transform.rotate(sprite1_top_left_shadow, 180)
sprite1_bottom_left_shadow = pg.transform.rotate(sprite1_top_left_shadow, 90)

for k, sprite in enumerate([sprite2, sprite3]):
    for i in range(sprite.get_rect().width):
        for j in range(sprite.get_rect().height):
            pixel = sprite.get_at((i, j))
            coefficient = 1 + 0.2 * ((k + 1) ** .7)
            new_pixel = pixel[0] * coefficient, pixel[1] * coefficient, pixel[2] * coefficient
            new_pixel = min(new_pixel[0], 255), min(new_pixel[1], 255), min(new_pixel[2], 255)
            new_pixel = list(map(int, new_pixel))
            sprite.set_at((i, j), new_pixel)
width = screen.get_width() // size1 + 1
height = screen.get_height() // size1 + 1
clock = pg.time.Clock()
print(width, height)

x_plus = x_minus = y_plus = y_minus = False

tilted = {}
lines = {}

cache_key_divider = 1


class SidesSprites:
    def __init__(self):
        self.cache = {}

    def fill_cache(self):
        try:
            keys = pickle.load(open('keys.pickle', 'rb'))
        except FileNotFoundError:
            keys = []
            pickle.dump(keys, open('keys.pickle', 'wb'))
        keys.sort()
        for i, key in enumerate(keys):
            print(f'{i + 1} of {len(keys)}, {key}')
            x1, y1, x2, y2, size1, size2 = key
            self.get(x1 * cache_key_divider, y1 * cache_key_divider, x2 * cache_key_divider, y2 * cache_key_divider,
                     size1, size2, info=False)

    def get(self, x_1, y_1, x_2, y_2, size_1, size_2, _block_tall, info=True):

        key = (
        x_1 // cache_key_divider, y_1 // cache_key_divider, x_2 // cache_key_divider, y_2 // cache_key_divider, size_1,
        size_2)
        if key in self.cache:
            return self.cache[key]

        spr_width = size_2 + abs(x_1 - x_2)
        spr_height = size_2 + abs(y_1 - y_2)
        side_sprite = pg.Surface((spr_width, spr_height), pg.SRCALPHA)

        if x_2 < x_1 and y_2 >= y_1:
            x_4 = abs(x_2 - x_1)
            y_3 = abs(y_2 - y_1)
            x_3 = y_4 = 0
            side = 1
        elif x_2 >= x_1 and y_2 > y_1:
            x_3 = abs(x_2 - x_1)
            y_3 = abs(y_2 - y_1)
            x_4 = y_4 = 0
            side = 2
        elif x_2 >= x_1 and y_2 <= y_1:
            x_3 = abs(x_2 - x_1)
            y_4 = abs(y_2 - y_1)
            x_4 = y_3 = 0
            side = 3
        elif x_2 < x_1 and y_2 <= y_1:
            x_4 = abs(x_2 - x_1)
            y_4 = abs(y_2 - y_1)
            x_3 = y_3 = 0
            side = 4
        else:
            x_3 = y_3 = x_4 = y_4 = 0
            side = 0

        def copy_texture_line(sprite: pg.Surface, x1, y1, x2, y2, percent, side, anisotropic_filtering, block_tall):
            length = int(max(abs(x1 - x2), abs(y1 - y2)))
            anisotropic_filtering = min(anisotropic_filtering, max_anisotropic_filtration)
            '''for i in range(length):
                pixel_ind = int(16*i/length)
                origin = dirt if percent > 0.25 else grass
                pixel = origin.get_at((line, pixel_ind))
                x, y = x1 + (x2-x1) * (i/length), y1 + (y2-y1) * (i/length)
                sprite.set_at((int(x), int(y)), pixel)'''

            if abs(x1 - x2) != 0:
                width = abs(x1 - x2) + 3
                height = anisotropic_filtering
            else:
                width = anisotropic_filtering
                height = abs(y1 - y2) + 3
            '''width = int(1+abs(x1-x2))
            height = int(1+abs(y1-y2))'''

            k = int(percent * block_tall * 16) % 16
            key = (width, height, k, side, anisotropic_filtering, using_shadows, block_tall)
            if key not in lines:
                if using_anisotropic_filtration:
                    pixel_line = pg.Surface((width, height))
                    # pixel_line.fill((0, 250, 250))
                    for j in range(anisotropic_filtering):
                        for i in range(length + 3):
                            pixel_ind = int(16 * i / length) % 16
                            k1 = (k + j) % 16
                            origin = dirt if percent * block_tall > .25 else grass
                            pixel = origin.get_at((k1, pixel_ind))
                            multiplayers = [0.7, 0.9, 1.1, 1.3]
                            multi = multiplayers[side - 1]
                            # shadow
                            if using_shadows:
                                critical_percent = 1-0.7/block_tall
                                if percent > critical_percent:
                                    multi *= 1-(percent-critical_percent)/(1-critical_percent) / 3
                            pixel = list(map(lambda x: int(x * multi), pixel))

                            pixel = list(map(lambda x: min(255, x), pixel))
                            pixel = list(map(lambda x: max(0, x), pixel))

                            x, y = int(abs(x1 - x2) * i / length), int(abs(y1 - y2) * i / length)
                            if abs(x1 - x2) != 0:
                                y += j
                            else:
                                x += j
                            #print(x, y, width, height, block_tall)
                            pixel_line.set_at((x, y), pixel)

                    # pixel_line = pg.transform.smoothscale(pixel_line, (width, height))
                    if abs(x1 - x2) != 0:
                        width = int(abs(x1 - x2)) + 3
                        actual_pixel_line = pg.Surface((width, 1), pg.SRCALPHA)
                        for i in range(width):
                            sum_pixel = [0, 0, 0]
                            for j in range(anisotropic_filtering):
                                pixel = pixel_line.get_at((i, j))
                                sum_pixel[0] += pixel[0]
                                sum_pixel[1] += pixel[1]
                                sum_pixel[2] += pixel[2]
                            sum_pixel = list(map(lambda x: min(int(x / anisotropic_filtering), 255), sum_pixel))
                            actual_pixel_line.set_at((i, 0), sum_pixel)
                        pixel_line = actual_pixel_line
                    else:
                        height = int(abs(y1 - y2)) + 3
                        actual_pixel_line = pg.Surface((1, height), pg.SRCALPHA)
                        for i in range(height):
                            sum_pixel = [0, 0, 0]
                            for j in range(anisotropic_filtering):
                                pixel = pixel_line.get_at((j, i))
                                sum_pixel[0] += pixel[0]
                                sum_pixel[1] += pixel[1]
                                sum_pixel[2] += pixel[2]
                            sum_pixel = list(map(lambda x: min(int(x / anisotropic_filtering), 255), sum_pixel))
                            actual_pixel_line.set_at((0, i), sum_pixel)
                        pixel_line = actual_pixel_line

                else:
                    if abs(x1 - x2) != 0:
                        width = abs(x1 - x2) + 3
                        height = 1
                    else:
                        width = 1
                        height = abs(y1 - y2) + 3
                    pixel_line = pg.Surface((width, height))
                    pixel_line.fill((0, 255, 255))
                    for i in range(length + 3):
                        pixel_ind = int(16 * i / length) % 16
                        pixel = dirt.get_at((k, pixel_ind))
                        multiplayers = [0.7, 0.9, 1.1, 1.3]
                        multi = multiplayers[side - 1]
                        pixel = list(map(lambda x: int(min(x * multi, 255)), pixel))
                        x, y = int(abs(x1 - x2) * i / length), int(abs(y1 - y2) * i / length)
                        pixel_line.set_at((x, y), pixel)

                lines[key] = pixel_line
                print(len(lines))
            pixel_line = lines[key]
            sprite.blit(pixel_line, (x1, y1))

        '''def side_texture(sprite: pg.Surface, x1, y1, x2, y2):
            tilted_key = (y1, y2)
            if tilted_key not in tilted:
                tilted_sprite = pg.Surface((size1, size1+abs(y1-y2)), pg.SRCALPHA)
                for k in range(size1):
                    offset = int(k/size1*(abs(y1-y2)))
                    r = int(size3 - (size1- size3) * k / 16)
                    for j in range(r):
                        pixel = dirt.get_at((int(k/size1*16), int(j/r*16)))
                        tilted_sprite.set_at((k, j+offset), pixel)
                tilted[tilted_key] = tilted_sprite
            tilted_sprite = tilted[tilted_key]
            #resized = pg.transform.scale(tilted_sprite, (abs(x1-x2), size3+abs(y1-y2)))
            resized = tilted_sprite
            sprite.blit(resized, (0, 0))
            sprite.blit(resized, (size1, 0))

        side_texture(side_sprite, x_3, y_3, x_4, y_4)'''

        r1 = int(abs(x_3 - x_4)) + 2
        for k in range(0, r1, 1):
            x5 = x_4 + (x_3 - x_4) * k / r1
            y5 = y_4 + (y_3 - y_4) * k / r1
            size = int(size_2 - (size_2 - size_1) * k / r1)
            correct_x5 = x5 if x_2 < x_1 else x5 + size
            # color = brown_color if (k>r1/10) else green_color
            # pg.draw.line(side_sprite, color, (correct_x5, y5), (correct_x5, y5+size))
            #
            if side in [1, 4]:
                m = 1
            else:
                m = 4
            a_f = 2 + int(16 * (_block_tall-1) / r1)
            copy_texture_line(side_sprite, correct_x5, y5, correct_x5, y5 + size, k / r1, m, a_f, _block_tall)

        r2 = int(abs(y_3 - y_4)) + 2
        for k in range(0, r2, 1):
            x5 = x_4 + (x_3 - x_4) * k / r2
            y5 = y_4 + (y_3 - y_4) * k / r2
            size = int(size_2 - (size_2 - size_1) * k / r2)
            correct_y5 = y5 if y_2 < y_1 else y5 + size
            # color = brown_color if (k>r2/10) else green_color
            # pg.draw.line(side_sprite, color, (x5, correct_y5), (x5+size, correct_y5))
            if y_1 <= y_2 <= y_1 + (size_2 - size_1) / sides_scale_factor:  # incorrect drawing fix
                continue
            if side in [1, 2]:
                m = 3
            else:
                m = 2
            a_f = 2 + round(16 * (_block_tall-1) / r2)
            copy_texture_line(side_sprite, x5, correct_y5, x5 + size, correct_y5, k / r2, m, a_f, _block_tall)

            ''' r = int(abs(x_3-x_4)+abs(y_3-y_4))
            if r == 0:
                return side_sprite

            for k in range(int(r*1.1)+3):
                x5 = x_4+(x_3 - x_4) * k / r
                y5 = y_4+(y_3 - y_4) * k / r
                size = int(size_2 - (size_2 - size_1) * k/r)
                #size = max(size, 1)
                if size not in black_sprites:
                    try:
                        black_sprite1 = pg.transform.scale(black_sprite, (size, size))
                    finally:
                        print(size, size_2, size_1, k, r)
                    black_sprites[size] = black_sprite1
                black_sprite1 = black_sprites[size]
                #black_sprite1.fill((10, (255-k)%255, 10))
                side_sprite.blit(black_sprite1, (x5, y5))'''
        if using_cache:
            self.cache[key] = side_sprite
            if info:
                print(len(self.cache), key, spr_width, spr_height, x_3, y_3, x_4, y_4)
        return side_sprite


twice_up_sides = SidesSprites()
twice_up_sides.fill_cache()


def from_corners_order(start1: int, end1: int, start2: int, end2: int) -> list[tuple[int, ...]]:
    # start1 left
    # end1 right
    # start2 top
    # end2 bottom
    indexes = [
        [start1, start2],
        [start1, end2 - 1],
        [end1 - 1, start2],
        [end1 - 1, end2 - 1]
    ]
    ans = [tuple(lst) for lst in indexes]
    ans_set = set([tuple(lst) for lst in indexes])
    width1 = end1 - start1
    height1 = end2 - start2
    while len(ans) != (width1 * height1):
        new_indexes = []
        for index in indexes:
            for offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                m, n = index[0] + offset[0], index[1] + offset[1]
                if start1 <= m < end1 and start2 <= n < end2 and (m, n) not in ans_set:
                    ans_set.add((m, n))
                    ans.append((m, n))
                    new_indexes.append((m, n))
        indexes = new_indexes

    return ans


frame = 0
sides_sprites_cache = {}
sides_sprites_cache1 = {}
while True:
    events = pg.event.get()
    frame += 1
    for event in events:
        if event.type == pg.QUIT:
            keys = twice_up_sides.cache.keys()
            pickle.dump(list(keys), open('keys.pickle', 'wb'))
            exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                y_plus = True
            if event.key == pg.K_s:
                y_minus = True
            if event.key == pg.K_a:
                x_plus = True
            if event.key == pg.K_d:
                x_minus = True
        if event.type == pg.KEYUP:
            if event.key == pg.K_w:
                y_plus = False
            if event.key == pg.K_s:
                y_minus = False
            if event.key == pg.K_a:
                x_plus = False
            if event.key == pg.K_d:
                x_minus = False
            if event.key == pg.K_e:
                using_shadows = not using_shadows

            if event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]:
                lines = {}
                if event.key == pg.K_LEFT:
                    size3 += 1
                elif event.key == pg.K_RIGHT:
                    size3 -= 1
                elif event.key == pg.K_DOWN:
                    size3 += 1
                    size1 += 1
                else:
                    size3 -= 1
                    size1 -= 1
                sprite3 = pg.transform.scale(grass, (size3, size3))
                for i in range(sprite3.get_rect().width):
                    for j in range(sprite3.get_rect().height):
                        pixel = sprite3.get_at((i, j))
                        coefficient = 1 + 0.2 * ((3) ** .7)
                        new_pixel = pixel[0] * coefficient, pixel[1] * coefficient, pixel[2] * coefficient
                        new_pixel = min(new_pixel[0], 255), min(new_pixel[1], 255), min(new_pixel[2], 255)
                        new_pixel = list(map(int, new_pixel))
                        sprite3.set_at((i, j), new_pixel)
                sprite1 = pg.transform.scale(grass, (size1, size1))
                width = scr_size[0] // size1 + 1
                height = scr_size[1] // size1 + 1

    old_coords = x, y
    if y_plus:
        if x_plus or x_minus:
            y += move1
        else:
            y += move2
    if y_minus:
        if x_plus or x_minus:
            y -= move1
        else:
            y -= move2
    if x_plus:
        if y_plus or y_minus:
            x -= move1
        else:
            x -= move2
    if x_minus:
        if y_plus or y_minus:
            x += move1
        else:
            x += move2
    if clock.get_fps() != 0:
        FPS_DIFF = FPS / clock.get_fps()
        x_offset = old_coords[0] - x
        x_offset *= FPS_DIFF
        x_offset = round(x_offset)
        y_offset = old_coords[1] - y
        y_offset *= FPS_DIFF
        y_offset = round(y_offset)
        x, y = old_coords[0] - x_offset, old_coords[1] - y_offset
        '''x, y = x//2, y//2
        x, y = x*2, y*2'''

    pg.display.set_caption(f'center:({x}, {y}) {round(clock.get_fps(), 3)}FPS')
    print("FPS:", round(clock.get_fps(), 3))

    #screen.fill(back_color)
    sides_screen = pg.Surface(scr_size, pg.SRCALPHA)

    center_i = x // size1 - width // 2
    center_j = -y // size1 - height // 2
    corners_size = size1
    ij_list = from_corners_order(-x // corners_size, (-x // corners_size) + width + 2, y // corners_size, height + y // corners_size + 2)
    #print(ij_list[:4])

    for i, j in ij_list:
        i1, j1 = -i + width // 2, j - height // 2
        # bottom blocks
        if (i1, j1) not in up_blocks and (i1, j1) not in twice_up_blocks:
            x1 = (width // 2 - i) * size1 - x + center_x
            y1 = (height // 2 - j) * size1 + y + center_y
            screen.blit(sprite1, (x1, y1))
            # shadows
            if using_shadows:
                if (i1, j1 + 1) in all_up_blocks:
                    screen.blit(sprite1_top_shadow, (x1, y1))
                if (i1, j1 - 1) in all_up_blocks:
                    screen.blit(sprite1_bottom_shadow, (x1, y1))
                if (i1 + 1, j1) in all_up_blocks:
                    screen.blit(sprite1_right_shadow, (x1, y1))
                if (i1 - 1, j1) in all_up_blocks:
                    screen.blit(sprite1_left_shadow, (x1, y1))

                if (i1 + 1, j1 + 1) in all_up_blocks and not (
                        (i1, j1 + 1) in all_up_blocks or (i1 + 1, j1) in all_up_blocks):
                    screen.blit(sprite1_top_right_shadow, (x1, y1))
                if (i1 - 1, j1 + 1) in all_up_blocks and not (
                        (i1, j1 + 1) in all_up_blocks or (i1 - 1, j1) in all_up_blocks):
                    screen.blit(sprite1_top_left_shadow, (x1, y1))
                if (i1 - 1, j1 - 1) in all_up_blocks and not (
                        (i1, j1 - 1) in all_up_blocks or (i1 - 1, j1) in all_up_blocks):
                    screen.blit(sprite1_bottom_left_shadow, (x1, y1))
                if (i1 + 1, j1 - 1) in all_up_blocks and not (
                        (i1, j1 - 1) in all_up_blocks or (i1 + 1, j1) in all_up_blocks):
                    screen.blit(sprite1_bottom_right_shadow, (x1, y1))

        # top blocks sides
        if (i1, j1) in up_blocks:
            x1 = (width // 2 - i - x / size1) * size2 + center_x
            y1 = (height // 2 - j + y / size1) * size2 + center_y
            x2 = (width // 2 - i) * size1 - x + center_x
            y2 = (height // 2 - j) * size1 + y + center_y

            if x1 < screen.get_width() / 2 and y1 < screen.get_height() / 2:
                coordinates = (x1, y1)
            elif x1 >= screen.get_width() / 2 and y1 < screen.get_height() / 2:
                coordinates = (x2, y1)
            elif x1 >= screen.get_width() / 2 and y1 >= screen.get_height() / 2:
                coordinates = (x2, y2)
            else:
                coordinates = (x1, y2)

            if not frame % render_sides_every_n_frame == 0:
                if (i1, j1) in sides_sprites_cache1:
                    sprite = sides_sprites_cache1[(i1, j1)]
                    screen.blit(sprite, coordinates)
            else:
                args = x1, y1, x2, y2, size1, size2, 1
                args = list(map(lambda x: x // sides_scale_factor, args))
                sprite = twice_up_sides.get(*args)
                if smooth_sides:
                    sprite = pg.transform.smoothscale_by(sprite, sides_scale_factor)
                else:
                    sprite = pg.transform.scale_by(sprite, sides_scale_factor)
                screen.blit(sprite, coordinates)
                sides_sprites_cache1[(i1, j1)] = sprite


        # top blocks
        if (i1, j1) in up_blocks:
            x1 = (width // 2 - i - x / size1) * size2 + center_x
            y1 = (height // 2 - j + y / size1) * size2 + center_y
            screen.blit(sprite2, (x1, y1))

        # twice top blocks sides
        if (i1, j1) in twice_up_blocks:
            x1 = (width // 2 - i - x / size1) * size3 + center_x
            y1 = (height // 2 - j + y / size1) * size3 + center_y
            x2 = (width // 2 - i) * size1 - x + center_x
            y2 = (height // 2 - j) * size1 + y + center_y
            if x1 < screen.get_width() / 2 and y1 < screen.get_height() / 2:
                coordinates = (x1, y1)
            elif x1 >= screen.get_width() / 2 and y1 < screen.get_height() / 2:
                coordinates = (x2, y1)
            elif x1 >= screen.get_width() / 2 and y1 >= screen.get_height() / 2:
                coordinates = (x2, y2)
            else:
                coordinates = (x1, y2)
            if not frame % render_sides_every_n_frame == 0:
                if (i1, j1) in sides_sprites_cache:
                    sprite = sides_sprites_cache[(i1, j1)]

                    screen.blit(sprite, coordinates)

            if frame % render_sides_every_n_frame == 0:
                if not ((i1 + 1, j1) in twice_up_blocks and (i1 - 1, j1) in twice_up_blocks and (
                i1, j1 + 1) in twice_up_blocks and (i1, j1 - 1) in twice_up_blocks):

                    args = x1, y1, x2, y2, size1, size3, twice_up_height_in_blocks
                    args = list(map(lambda x: x // sides_scale_factor, args))
                    sprite = twice_up_sides.get(*args)
                    if smooth_sides:
                        sprite = pg.transform.smoothscale_by(sprite, sides_scale_factor)
                    else:
                        sprite = pg.transform.scale_by(sprite, sides_scale_factor)
                    if x1 < screen.get_width() / 2 and y1 < screen.get_height() / 2:
                        coordinates = (x1, y1)
                    elif x1 >= screen.get_width() / 2 and y1 < screen.get_height() / 2:
                        coordinates = (x2, y1)
                    elif x1 >= screen.get_width() / 2 and y1 >= screen.get_height() / 2:
                        coordinates = (x2, y2)
                    else:
                        coordinates = (x1, y2)

                    screen.blit(sprite, coordinates)
                    sides_sprites_cache[(i1, j1)] = sprite

                '''r = int(abs(x1-x2)+abs(y1-y2))
                for k in range(r-1):
                x3 = x2 + (x1 - x2) * k / r
                y3 = y2 + (y1 - y2) * k / r
                size = int(size1 + (size3 - size1) * k/r)
                if size not in black_sprites:
                    sprite = pg.transform.scale(black_sprite, (size, size))
                    black_sprites[size] = sprite
                sprite = black_sprites[size]
                screen.blit(sprite, (x3, y3))'''

                '''# fix gap between blocks
                pg.draw.line(screen, dirt_color, (x1+size3-1, y1), (x2+size1-1, y2), fix_lane_width)
                pg.draw.line(screen, dirt_color, (x1, y1+size3-1), (x2, y2+size1-1), fix_lane_width)

                pg.draw.line(screen, dirt_color, (x1, y1), (x2, y2), fix_lane_width)
                pg.draw.line(screen, dirt_color, (x1+size3-1, y1+size3-1), (x2+size1-1, y2+size1-1), fix_lane_width)'''

        # twice top blocks
        if (i1, j1) in twice_up_blocks:
            x1 = (width // 2 - i - x / size1) * size3 + center_x
            y1 = (height // 2 - j + y / size1) * size3 + center_y
            if using_mouse_slope:
                mouse_offset_x = (center_x - pg.mouse.get_pos()[0]) // mouse_slope_factor
                mouse_offset_y = (center_y - pg.mouse.get_pos()[1]) // mouse_slope_factor
                x1 -= mouse_offset_x
                y1 -= mouse_offset_y
            screen.blit(sprite3, (x1, y1))

    if render_smaller_resolution:
        scaled = pg.transform.scale_by(screen, 2)
        true_screen.blit(scaled, (0, 0))

    if render_sides_every_n_frame != 1:
        #sides_screen.blit(screen, (0, 0))
        screen.blit(sides_screen, (0, 0))

    clock.tick(FPS)
    pg.display.update()
