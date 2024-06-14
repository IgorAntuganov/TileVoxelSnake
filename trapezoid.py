import pygame as pg
import time


class SidesDrawer:
    """
    using_cache: use cache for pixel strings, may take many GBs of RAM
    perspective_correctness: adjust texture with perspective effect
    perspective_const: should be > 0, 1 is base value, maybe 0.5 is best
    debug_background: fill background with red for debugging
    fast_anisotropic: using set_alpha() if True, else more accurate average_surface()
    """
    def __init__(self):
        self._cache = {}
        self._using_cache = False
        self._perspective_correctness = True
        self._perspective_const = 1
        self._debug_background = True
        self._anisotropic_filtration = True
        self._fast_anisotropic = True

    def set_using_cache(self, using: bool):
        self._using_cache = using

    def set_using_perspective(self, using: bool):
        self._perspective_correctness = using

    def set_perspective_const(self, n: int | float):
        self._perspective_const = n

    def set_debug_mode(self, mode: bool):
        self._debug_background = mode

    def set_using_anisotropic_filtration(self, mode: bool):
        self._anisotropic_filtration = mode

    def set_fast_anisotropic(self, mode: bool):
        self._fast_anisotropic = mode

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
                next_part = 0

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

    @staticmethod
    def get_pixel_string_fast(texture, width, part) -> pg.Surface:
        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        crop = pg.Surface((texture.get_width(), 1))
        crop.blit(texture, (0, -texture_y))
        resized = pg.transform.scale(crop, (width, 1))
        pstring.blit(resized, (0, 0))
        return pstring

    def get_pixel_string_with_anisotropic(self, texture: pg.Surface, width, part1, part2) -> pg.Surface:
        part1 = round(part1, 10)
        part2 = round(part2, 10)
        part1 = max(0, part1)  # Fixing black strings with a small trapezoid height
        key = (True, texture.__hash__(), width, part1, part2)
        if self._using_cache and key in self._cache:
            return self._cache[key]

        texture_y_1 = part1 * texture.get_height()
        texture_y_2 = part2 * texture.get_height()

        if self._fast_anisotropic:
            pstring = pg.Surface((texture.get_width(), 1), pg.SRCALPHA)
            surfaces = []  # for PyCharm
        else:
            pstring = None  # for PyCharm
            surfaces = []

        for k in range(int(texture_y_1), int(texture_y_2)+1):
            crop = pg.Surface((texture.get_width(), 1))
            crop.blit(texture, (0, -k))
            if self._fast_anisotropic:
                y_diff = abs(texture_y_1 - texture_y_2)
                if k != int(texture_y_1):
                    crop.set_alpha(int(255/y_diff))
                pstring.blit(crop, (0, 0))
            else:
                surfaces.append(crop)
        if not self._fast_anisotropic:
            pstring = pg.transform.average_surfaces(surfaces)

        if width < texture.get_width():
            resized = pg.transform.smoothscale(pstring, (width, 1))
        else:
            resized = pg.transform.scale(pstring, (width, 1))

        if self._using_cache:
            self._cache[key] = resized
            print('in cache:', len(self._cache))
        return resized

    def get_vert_trapezoid(self, texture: pg.Surface,
                           left_height: int,
                           right_height: int,
                           width: int,
                           offset: int) -> pg.Surface:
        """
        :param texture: source texture
        :param left_height: height where will be left side of texture
        :param right_height: height where will be right side of texture
        :param width: can be negative if left side righter on screen than right side
        :param offset: difference by y between the upper-left and upper-right corners
        """
        if offset > 0:
            im_height = max(left_height, right_height + offset)
        else:
            im_height = max(left_height - offset, right_height)
        im_width = abs(width)
        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        if self._debug_background:
            image.fill((255, 0, 0))

        for i in range(im_width):
            if self._anisotropic_filtration:
                i1 = i - .5
                part = i1 / im_width
                next_part = (i1 + 1) / im_width
            else:
                part = i / im_width
                next_part = -1

            # calculating str_x, str_y and col_height
            if offset > 0:
                str_y = int(offset * part)
                bottom_left = left_height
                bottom_right = offset + right_height
            else:
                str_y = int(abs(offset) * (1 - part))
                bottom_left = left_height + abs(offset)
                bottom_right = right_height
            bottom_diffs = bottom_left - bottom_right
            col_height = int(bottom_left - bottom_diffs * part) - str_y
            if col_height < 1:
                continue

            if width > 0:
                str_x = i
            else:
                str_x = im_width - i - 1

            if self._perspective_correctness:
                z1 = (right_height / left_height) ** self._perspective_const
                part = part / (part + (1 - part) / z1)
                next_part = next_part / (next_part + (1 - next_part) / z1)

            # getting column of pixels
            if self._anisotropic_filtration:
                pixel_column = self.get_pixel_column_with_anisotropic(texture, col_height, part, next_part)
            else:
                pixel_column = self.get_pixel_column_fast(texture, col_height, part)

            image.blit(pixel_column, (str_x, str_y))

        return image

    @staticmethod
    def get_pixel_column_fast(texture, height, part) -> pg.Surface:
        pstring = pg.Surface((1, height), pg.SRCALPHA)
        texture_x = int(part * texture.get_width())
        crop = pg.Surface((1, texture.get_height()))
        crop.blit(texture, (-texture_x, 0))
        resized = pg.transform.scale(crop, (1, height))
        pstring.blit(resized, (0, 0))
        return pstring

    def get_pixel_column_with_anisotropic(self, texture: pg.Surface, height, part1, part2) -> pg.Surface:
        part1 = round(part1, 10)
        part2 = round(part2, 10)
        part1 = max(0, part1)  # Fixing black columns with a small trapezoid width
        key = (False, texture.__hash__(), height, part1, part2)
        if self._using_cache and key in self._cache:
            return self._cache[key]

        texture_x_1 = part1 * texture.get_width()
        texture_x_2 = part2 * texture.get_width()

        if self._fast_anisotropic:
            pstring = pg.Surface((1, texture.get_height()), pg.SRCALPHA)
            surfaces = []  # for PyCharm
        else:
            pstring = None  # for PyCharm
            surfaces = []

        for k in range(int(texture_x_1), int(texture_x_2+1)):
            crop = pg.Surface((1, texture.get_height()))
            crop.blit(texture, (-k, 0))
            if self._fast_anisotropic:
                x_diff = abs(texture_x_1 - texture_x_2)
                if k != int(texture_x_1):
                    crop.set_alpha(int(255/x_diff))
                pstring.blit(crop, (0, 0))
            else:
                surfaces.append(crop)
        if not self._fast_anisotropic:
            pstring = pg.transform.average_surfaces(surfaces)

        if height < texture.get_height():
            resized = pg.transform.smoothscale(pstring, (1, height))
        else:
            resized = pg.transform.scale(pstring, (1, height))

        if self._using_cache:
            self._cache[key] = resized
            print('in cache:', len(self._cache))
        return resized


def test():
    s = SidesDrawer()

    grass_png = pg.image.load('sprites/blocks/grass_side.png')
    test_width = 16
    test_height = 16
    texture = pg.Surface((test_width, test_height))
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
    last_k = time.time()
    k = 0
    pixel_offset_in_seconds = 60

    while True:
        if time.time() - last_k > 1/pixel_offset_in_seconds:
            k += 1
            last_k = time.time()
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
        if pressed[pg.K_b]:
            s.set_fast_anisotropic(False)
        if pressed[pg.K_n]:
            s.set_fast_anisotropic(True)

        scr.fill((0, 0, 0))
        s.set_perspective_const(pc)
        off1 = off+(top-bot)//2
        h = int(max(top, bot)*min(top/bot, bot/top))
        texture.blit(grass, (0, k % test_height))
        texture.blit(grass, (0, (k % test_height) - test_height))
        trap = s.get_vert_trapezoid(grass, top, bot, h, off1)

        x = (1600-trap.get_width())//2
        y = (900-trap.get_height())//2
        scr.blit(trap, (x, y))
        clock.tick(240)
        fps = clock.get_fps()
        pg.display.set_caption('fps:' + str(fps))
        pg.display.update()


if __name__ == '__main__':
    test()
