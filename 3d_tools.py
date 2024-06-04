import pygame as pg
import time


class SidesDrawer:
    def __init__(self):
        self.cache = {}

    def get_hor_trapezoid(self, texture: pg.Surface,
                          top_width: int,
                          bot_width: int,
                          height: int,
                          offset: int,
                          fill_red: bool = False,
                          perspective_const: float = 1) -> pg.Surface:
        """
        :param texture
        :param top_width
        :param bot_width:
        :param height: can be negative if top below bottom on screen
        :param offset: difference by x between the upper-left and lower-left corners
        :param fill_red: fill background with red (for debugging)
        :param perspective_const: should be > 0, 1 is base value, maybe 0.5 is best
        """
        if offset > 0:
            im_width = max(top_width, bot_width+offset)
        else:
            im_width = max(top_width-offset, bot_width)
        im_height = abs(height)

        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        if fill_red:
            image.fill((255, 0, 0))

        for i in range(im_height):
            part = i/im_height
            if offset > 0:
                im_x = int(offset * part)
                right_top = top_width
                right_bottom = offset + bot_width
            else:
                im_x = int(abs(offset) * (1-part))
                right_top = top_width + abs(offset)
                right_bottom = bot_width
            rights_diffs = right_top - right_bottom
            str_width = int(right_top - rights_diffs * part) - im_x

            z1 = (bot_width/top_width) ** perspective_const
            part_with_perspective = part / (part + (1 - part) / z1)

            pixel_string = self.get_pixel_string_fast(texture, str_width, part_with_perspective)

            if height > 0:
                im_y = i
            else:
                im_y = im_height-i-1
            image.blit(pixel_string, (im_x, im_y))
        return image

    def get_pixel_string(self, texture, width, part) -> pg.Surface:
        key = width, part
        if key in self.cache:
            return self.cache[key]

        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        for i in range(width):
            x_part = i / width
            texture_x = int(x_part * texture.get_width())
            pixel = texture.get_at((texture_x, texture_y))
            pstring.set_at((i, 0), pixel)
        self.cache[key] = pstring
        return pstring

    def get_pixel_string_fast(self, texture, width, part) -> pg.Surface:
        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        crop = pg.Surface((texture.get_width(), 1))
        crop.blit(texture, (0, -texture_y))
        resized = pg.transform.scale(crop, (width, 1))
        pstring.blit(resized, (0, 0))
        return pstring

    def get_double_pixel_string_fast(self, texture, width, part) -> pg.Surface:
        pstring = pg.Surface((width, 1), pg.SRCALPHA)
        texture_y = int(part * texture.get_height())
        crop = pg.Surface((texture.get_width(), 1))
        crop.blit(texture, (0, -texture_y))
        #crop.set_alpha(128)
        crop2 = pg.Surface((texture.get_width(), 1))
        crop2.blit(texture, (0, -texture_y+1))
        crop2.set_alpha(128)
        crop.blit(crop2, (0, 0))
        resized = pg.transform.smoothscale(crop, (width, 1))
        pstring.blit(resized, (0, 0))
        return pstring


def test():
    s = SidesDrawer()

    grass_png = pg.image.load('grass.png')
    test_width = 64
    test_height = 64
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
            off += 5
        if pressed[pg.K_f]:
            off -= 5
        if pressed[pg.K_UP] and time.time() - last_pc > .2:
            pc += .1
            print(pc)
            last_pc = time.time()
        if pressed[pg.K_DOWN] and time.time() - last_pc > .2 and pc > 0.1:
            pc -= .1
            print(pc)
            last_pc = time.time()

        scr.fill((0, 0, 0))
        trap = s.get_hor_trapezoid(grass, top, bot, h, off, perspective_const=pc)

        scr.blit(trap, (0, 0))
        clock.tick(120)
        fps = clock.get_fps()
        pg.display.set_caption('fps:' + str(fps))
        pg.display.update()


if __name__ == '__main__':
    test()
