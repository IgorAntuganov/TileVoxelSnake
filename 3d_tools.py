import pygame as pg
import time


class SidesDrawer:
    """
    perspective_correctness: adjust texture with perspective effect
    perspective_const: should be > 0, 1 is base value, maybe 0.5 is best
    debug_background: fill background with red for debugging
    """
    def __init__(self):
        self._cache = {}
        self._perspective_correctness = True
        self._perspective_const = 1
        self._debug_background = True
        self._anisotropic_filtration = True

    def set_using_perspective(self, using: bool):
        self._perspective_correctness = using

    def set_perspective_const(self, n: int | float):
        self._perspective_const = n

    def set_debug_mode(self, mode: bool):
        self._debug_background = mode

    def set_using_anisotropic_filtration(self, mode: bool):
        self._anisotropic_filtration = mode

    def get_hor_trapezoid(self, texture: pg.Surface,
                          top_width: int,
                          bot_width: int,
                          height: int,
                          offset: int) -> pg.Surface:
        """
        :param texture: source texture
        :param top_width: width where will be top of texture
        :param bot_width: width where will be bottom of texture
        :param height: can be negative if top below bottom on screen
        :param offset: difference by x between the upper-left and lower-left corners
        """
        if offset > 0:
            im_width = max(top_width, bot_width+offset)
        else:
            im_width = max(top_width-offset, bot_width)
        im_height = abs(height)
        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        if self._debug_background:
            image.fill((255, 0, 0))

        for i in range(im_height):
            if self._anisotropic_filtration:
                i1 = i - .5
                part = i1/im_height
                next_part = (i1+1)/im_height
            else:
                part = i/im_height
                next_part = -1

            # calculating str_x, str_y and str_width
            if offset > 0:
                str_x = int(offset * part)
                right_top = top_width
                right_bottom = offset + bot_width
            else:
                str_x = int(abs(offset) * (1-part))
                right_top = top_width + abs(offset)
                right_bottom = bot_width
            rights_diffs = right_top - right_bottom
            str_width = int(right_top - rights_diffs * part) - str_x
            if str_width < 1:
                continue
            if height > 0:
                str_y = i
            else:
                str_y = im_height-i-1

            if self._perspective_correctness:
                z1 = (bot_width/top_width) ** self._perspective_const
                part = part / (part + (1 - part) / z1)
                next_part = next_part / (next_part + (1 - next_part) / z1)

            # getting string of pixels
            if self._anisotropic_filtration:
                pixel_string = self.get_pixel_string_with_anisotropic(texture, str_width, part, next_part)
            else:
                pixel_string = self.get_pixel_string_fast(texture, str_width, part)

            image.blit(pixel_string, (str_x, str_y))
        return image

    def get_pixel_string(self, texture, width, part) -> pg.Surface:
        key = width, part
        if key in self._cache:
            return self._cache[key]

        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        for i in range(width):
            x_part = i / width
            texture_x = int(x_part * texture.get_width())
            pixel = texture.get_at((texture_x, texture_y))
            pstring.set_at((i, 0), pixel)
        self._cache[key] = pstring
        return pstring

    @staticmethod
    def get_pixel_string_fast(texture, width, part) -> pg.Surface:
        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        crop = pg.Surface((texture.get_width(), 1))
        crop.blit(texture, (0, -texture_y))
        resized = pg.transform.scale(crop, (width, 1))
        pstring.blit(resized, (0, 0))
        return pstring

    @staticmethod
    def get_pixel_string_with_anisotropic(texture, width, part1, part2) -> pg.Surface:
        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y_1 = part1 * texture.get_height()
        texture_y_2 = part2 * texture.get_height()
        for k in range(int(texture_y_1), int(texture_y_2)+1):
            crop = pg.Surface((texture.get_width(), 1))
            crop.blit(texture, (0, -k))
            if width < texture.get_width():
                resized = pg.transform.smoothscale(crop, (width, 1))
            else:
                resized = pg.transform.scale(crop, (width, 1))

            y_diff = abs(texture_y_1 - texture_y_2)
            if k != int(texture_y_1):
                resized.set_alpha(int(255/y_diff))
            pstring.blit(resized, (0, 0))
        return pstring


def test():
    s = SidesDrawer()

    grass_png = pg.image.load('grass.png')
    test_width = 256
    test_height = 256
    grass = pg.Surface((test_width, test_height))
    grass.fill((255, 255, 255))
    for i in range(test_width//16):
        for j in range(test_height//16):
            grass.blit(grass_png, (i*16, j*16))
    clock = pg.time.Clock()
    scr = pg.display.set_mode((1600, 900))
    top = test_width
    bot = test_width
    h = test_height
    off = 0
    pc = 1
    last_pc = time.time()

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        pressed = pg.key.get_pressed()
        if pressed[pg.K_q] and top > 5:
            top -= 5
        if pressed[pg.K_w]:
            top += 5
        if pressed[pg.K_a] and bot > 5:
            bot -= 5
        if pressed[pg.K_s]:
            bot += 5
        if pressed[pg.K_e]:
            h -= 5 if abs(h) > 20 else 1
        if pressed[pg.K_d]:
            h += 5 if abs(h) > 20 else 1
        if pressed[pg.K_r]:
            off += 2
        if pressed[pg.K_f]:
            off -= 2
        if pressed[pg.K_UP] and time.time() - last_pc > .2:
            pc += .1
            print(pc)
            last_pc = time.time()
        if pressed[pg.K_DOWN] and time.time() - last_pc > .2 and pc > 0.1:
            pc -= .1
            print(pc)
            last_pc = time.time()
        if pressed[pg.K_z]:
            s.set_using_perspective(False)
        if pressed[pg.K_x]:
            s.set_using_perspective(True)
        if pressed[pg.K_c]:
            s.set_using_anisotropic_filtration(False)
        if pressed[pg.K_v]:
            s.set_using_anisotropic_filtration(True)

        scr.fill((0, 0, 0))
        s.set_perspective_const(pc)
        off1 = off+(top-bot)//2
        trap = s.get_hor_trapezoid(grass, top, bot, h, off1)

        x = (1600-trap.get_width())//2
        y = (900-trap.get_height())//2
        scr.blit(trap, (x, y))
        clock.tick(240)
        fps = clock.get_fps()
        pg.display.set_caption('fps:' + str(fps))
        pg.display.update()


if __name__ == '__main__':
    test()
