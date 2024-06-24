import time
import pygame as pg
import pickle
import os
from constants import PATH_TO_CACHE, CACHE_KEYS_FILENAME


class TrapeziodTexturer:
    def __init__(self):
        folder = PATH_TO_CACHE
        cache_file = folder + '/' + CACHE_KEYS_FILENAME
        if not os.path.isdir(folder):
            os.mkdir(folder)

        if not os.path.isfile(cache_file):
            pickle.dump({}, open(cache_file, 'wb'))
        with open(cache_file, 'rb') as file:
            self.keys = pickle.load(file)

        self._textures_cache = {}
        for filename in os.listdir(folder):
            if filename == CACHE_KEYS_FILENAME:
                continue
            file_path = folder + '/' + filename
            image = pg.image.load(file_path).convert_alpha()
            key = filename.split('.')[0]
            self._textures_cache[key] = image

        self._lines_cache = {}
        self._print_cache_size = False

    def set_print_cache_size(self, using: bool):
        self._print_cache_size = using

    def create_cache(self):
        start = time.time()
        for key in self.keys:
            is_hor, texture_name, size, part, next_part = key
            texture = self._textures_cache[texture_name]
            if is_hor:
                image = self.get_pixel_string_with_anisotropic(texture, size, part, next_part)
                self._lines_cache[key] = image
            else:
                image = self.get_pixel_column_with_anisotropic(texture, size, part, next_part)
                self._lines_cache[key] = image
        if self._print_cache_size:
            t = time.time() - start
            print('cache created by keys from disk:', len(self._lines_cache.keys()), 'time consuming:', t)

    def save_cache(self):
        folder = PATH_TO_CACHE
        cache_file = folder + '/' + CACHE_KEYS_FILENAME
        with open(cache_file, 'wb') as file:
            keys = list(self._lines_cache.keys())
            pickle.dump(keys, file)

        for key in self._textures_cache:
            file_path = folder + '/' + key + '.png'
            image = self._textures_cache[key]
            pg.image.save(image, file_path)

    def add_texture_to_cache(self, texture: pg.Surface, texture_name: str):
        if texture_name not in self._textures_cache:
            pg.image.save(texture, f'{PATH_TO_CACHE}/{texture_name}.png')
            self._textures_cache[texture_name] = texture

    @staticmethod
    def get_hor_trapezoid_sizes(top_width, bot_width, height, offset):
        if offset > 0:
            im_width = max(top_width, bot_width+offset)
        else:
            im_width = max(top_width-offset, bot_width)
        im_height = abs(height)
        return im_width, im_height

    def get_hor_trapezoid(self, texture: pg.Surface,
                          texture_name: str,
                          top_width: int,
                          bot_width: int,
                          height: int,
                          offset: int) -> pg.Surface:
        """
        :param texture: source texture
        :param texture_name: code name of texture for saving cache in file
        :param top_width: width where will be top of texture
        :param bot_width: width where will be bottom of texture
        :param height: can be negative if top below bottom on screen
        :param offset: difference by x between the upper-left and lower-left corners
        """
        self.add_texture_to_cache(texture, texture_name)

        im_width, im_height = self.get_hor_trapezoid_sizes(top_width, bot_width, height, offset)
        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        for i in range(im_height):
            i1 = i - .5
            part = i1/im_height
            next_part = (i1+1)/im_height

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

            z1 = bot_width/top_width
            part = part / (part + (1 - part) / z1)
            next_part = next_part / (next_part + (1 - next_part) / z1)

            part = round(part, 10)
            next_part = round(next_part, 10)
            part = max(0, part)  # Fixing black strings with a small trapezoid height

            args = texture, str_width, part, next_part
            key = (True, texture_name, str_width, part, next_part)
            if key in self._lines_cache:
                pixel_string = self._lines_cache[key]
            else:
                pixel_string = self.get_pixel_string_with_anisotropic(*args)
                self._lines_cache[key] = pixel_string.copy()
                if self._print_cache_size:
                    print('in cache:', len(self._lines_cache))

            image.blit(pixel_string, (str_x, str_y))
        return image

    @staticmethod
    def get_pixel_string_with_anisotropic(texture: pg.Surface, width, part1, part2) -> pg.Surface:
        texture_y_1 = part1 * texture.get_height()
        texture_y_2 = part2 * texture.get_height()

        pstring = pg.Surface((texture.get_width(), 1), pg.SRCALPHA)
        for k in range(int(texture_y_1), int(texture_y_2)+1):
            crop = pg.Surface((texture.get_width(), 1), pg.SRCALPHA)
            crop.blit(texture, (0, -k))
            y_diff = abs(texture_y_1 - texture_y_2)
            if k != int(texture_y_1):
                crop.set_alpha(int(255 / y_diff))
            pstring.blit(crop, (0, 0))

        if width < texture.get_width():
            resized = pg.transform.smoothscale(pstring, (width, 1))
        else:
            resized = pg.transform.scale(pstring, (width, 1))
        return resized

    @staticmethod
    def get_vert_trapezoid_sizes(left_height, right_height, width, offset):
        if offset > 0:
            im_height = max(left_height, right_height + offset)
        else:
            im_height = max(left_height - offset, right_height)
        im_width = abs(width)
        return im_width, im_height

    def get_vert_trapezoid(self, texture: pg.Surface,
                           texture_name: str,
                           left_height: int,
                           right_height: int,
                           width: int,
                           offset: int) -> pg.Surface:
        """
        :param texture: source texture
        :param texture_name: code name of texture for saving cache in file
        :param left_height: height where will be left side of texture
        :param right_height: height where will be right side of texture
        :param width: can be negative if left side righter on screen than right side
        :param offset: difference by y between the upper-left and upper-right corners
        """
        self.add_texture_to_cache(texture, texture_name)

        im_width, im_height = self.get_vert_trapezoid_sizes(left_height, right_height, width, offset)
        image = pg.Surface((im_width, im_height), pg.SRCALPHA)

        for i in range(im_width):
            i1 = i - .5
            part = i1 / im_width
            next_part = (i1 + 1) / im_width

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

            z1 = (right_height / left_height)
            part = part / (part + (1 - part) / z1)
            next_part = next_part / (next_part + (1 - next_part) / z1)

            part = round(part, 10)
            next_part = round(next_part, 10)
            part = max(0, part)  # Fixing black columns with a small trapezoid width
            args = texture, col_height, part, next_part
            key = (False, texture_name, col_height, part, next_part)
            if key in self._lines_cache:
                pixel_column = self._lines_cache[key]
            else:
                pixel_column = self.get_pixel_column_with_anisotropic(*args)
                self._lines_cache[key] = pixel_column.copy()
                if self._print_cache_size:
                    print('in cache:', len(self._lines_cache))

            image.blit(pixel_column, (str_x, str_y))

        return image

    @staticmethod
    def get_pixel_column_with_anisotropic(texture: pg.Surface, height, part1, part2) -> pg.Surface:
        texture_x_1 = part1 * texture.get_width()
        texture_x_2 = part2 * texture.get_width()

        pstring = pg.Surface((1, texture.get_height()), pg.SRCALPHA)
        for k in range(int(texture_x_1), int(texture_x_2 + 1)):
            crop = pg.Surface((1, texture.get_height()), pg.SRCALPHA)
            crop.blit(texture, (-k, 0))
            x_diff = abs(texture_x_1 - texture_x_2)
            if k != int(texture_x_1):
                crop.set_alpha(int(255 / x_diff))
            pstring.blit(crop, (0, 0))

        if height < texture.get_height():
            resized = pg.transform.smoothscale(pstring, (1, height))
        else:
            resized = pg.transform.scale(pstring, (1, height))
        return resized
