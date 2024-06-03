import pygame as pg


class SidesDrawer:
    def __init__(self):
        self.cache = {}

    def get_hor_trapezoid(self, texture: pg.Surface,
                          top_width: int,
                          bot_width: int,
                          height: int,
                          offset: int) -> pg.Surface:
        """
        :param texture
        :param top_width
        :param bot_width:
        :param height: can be negative if top below bottom on screen
        :param offset: difference by x between the upper-left and lower-left corners
        """
        widths_diff = top_width - bot_width
        if offset > 0:
            im_width = max(top_width, bot_width+offset)
        else:
            im_width = max(top_width-offset, bot_width)
        im_height = abs(height)

        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        for i in range(im_height):
            part = i/im_height
            if offset > 0:
                im_x = int(offset * part)
            else:
                im_x = int(abs(offset) * (1-part))
            str_width = int(top_width - widths_diff * part)
            pixel_string = self.get_pixel_string_fast(texture, str_width, part)
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



def test():
    s = SidesDrawer()

    grass = pg.image.load('grass.png')
    clock = pg.time.Clock()
    scr = pg.display.set_mode((1600, 900))
    top = 50
    bot = 30
    h = 20
    off = 20

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
        pressed = pg.key.get_pressed()
        if pressed[pg.K_q] and top >= 5:
            top -= 5
        if pressed[pg.K_w]:
            top += 5
        if pressed[pg.K_a] and bot >= 5:
            bot -= 5
        if pressed[pg.K_s]:
            bot += 5
        if pressed[pg.K_e]:
            h -= 5
        if pressed[pg.K_d]:
            h += 5
        if pressed[pg.K_r]:
            off += 5
        if pressed[pg.K_f]:
            off -= 5

        scr.fill((0, 0, 0))
        trap = s.get_hor_trapezoid(grass, top, bot, h, off)
        scr.blit(trap, (100, 100))
        clock.tick(60)
        fps = clock.get_fps()
        pg.display.set_caption(str(fps))
        print(len(s.cache))
        pg.display.update()


if __name__ == '__main__':
    test()