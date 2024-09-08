import pygame as pg
from constants import *


class Layers:
    def __init__(self, base_level_size: int):
        self.base_level_size = base_level_size
        self.scr_size = SCREEN_SIZE
        self.center = (0, 0)

        self.n_level_size_dict: dict = {}
        self.define_n_level_size()
        self.x0_y0_dict: dict = {}
        self.define_n_level_x0_y0()

    def set_base_level_size(self, size: int):
        self.base_level_size = size
        self.define_n_level_size()

    def get_n_level_size(self, n: float | int) -> float:
        """:return size of blocks with z=n in pixels of screen"""
        layers_offset = (self.base_level_size / 32) ** 3
        difference = n * layers_offset
        return self.base_level_size + difference

    def define_n_level_size(self):
        self.n_level_size_dict = {}
        for z in range(MAX_PRECALCULATED_LAYERS_HEIGHT):
            self.n_level_size_dict[z] = (self.get_n_level_size(z))

    def getdict_n_level_size(self, n: int) -> float:
        if n in self.n_level_size_dict:
            return self.n_level_size_dict[n]
        return self.get_n_level_size(n)

    def set_center(self, center: tuple[float, float]):
        self.center = center
        self.define_n_level_x0_y0()

    def get_n_level_x0_y0(self, n: float | int) -> tuple[float, float]:
        """:return topleft coordinates of block with x=0, y=0 in pixels of screen"""
        size = self.getdict_n_level_size(n)
        offset_x = (-self.center[0]) * size + self.scr_size[0] / 2
        offset_y = (-self.center[1]) * size + self.scr_size[1] / 2
        return offset_x//1, offset_y//1

    def define_n_level_x0_y0(self):
        self.x0_y0_dict = {}
        for z in range(MAX_PRECALCULATED_LAYERS_HEIGHT):
            x0_y0 = self.get_n_level_x0_y0(z)
            self.x0_y0_dict[z] = x0_y0

    def getdict_n_level_x0_y0(self, n: int) -> tuple[float, float]:
        if n in self.x0_y0_dict:
            return self.x0_y0_dict[n]
        return self.get_n_level_x0_y0(n)

    def get_rect_for_block(self, x, y, z) -> pg.Rect:
        rect_size = self.getdict_n_level_size(z)
        x0, y0 = self.getdict_n_level_x0_y0(z)

        left = (x0 + x * rect_size) // 1
        right = (x0 + (x + 1) * rect_size) // 1
        top = (y0 + y * rect_size) // 1
        bottom = (y0 + (y + 1) * rect_size) // 1
        width = right - left
        height = bottom - top
        rect = pg.Rect(left, top, width, height)
        return rect

    def get_top_left_for_block(self, x, y, z) -> tuple[int, int]:
        rect_size = self.getdict_n_level_size(z)
        x0, y0 = self.getdict_n_level_x0_y0(z)

        left = (x0 + x * rect_size) // 1
        top = (y0 + y * rect_size) // 1
        return left, top

    def get_rect_for_side(self, origin_block: tuple[int, int, int],
                          directed_block: tuple[int, int, int],
                          sizes: tuple[int, int]) -> pg.Rect:
        orig_rect = self.get_rect_for_block(*origin_block)
        x, y, z = directed_block
        z -= 1
        dir_rect = self.get_rect_for_block(x, y, z)
        if origin_block[0] == directed_block[0] and origin_block[1] > directed_block[1]:  # north side
            left = min(orig_rect.left, dir_rect.left)
            top = dir_rect.bottom

        elif origin_block[0] == directed_block[0] and origin_block[1] < directed_block[1]:  # south side
            left = min(orig_rect.left, dir_rect.left) - 1  # -1: adjustment from sides_drawer
            top = orig_rect.bottom

        elif origin_block[0] > directed_block[0] and origin_block[1] == directed_block[1]:  # west side
            left = dir_rect.right
            top = min(orig_rect.top, dir_rect.top) - 1  # -1: adjustment from sides_drawer

        elif origin_block[0] < directed_block[0] and origin_block[1] == directed_block[1]:  # east side
            left = orig_rect.right
            top = min(orig_rect.top, dir_rect.top) - 1  # -1: adjustment from sides_drawer

        else:
            print(origin_block, directed_block)
            raise AssertionError('incorrect origin and directed blocks')

        rect = pg.Rect(left, top, *sizes)
        return rect


class CameraFrame:
    def __init__(self, center: tuple[float, float]):
        """All coordinates in blocks"""
        self.center = center
        self.scr_size = SCREEN_SIZE
        self.base_level_size = BASE_LEVEL_SIZE
        self.block_width = 0
        self.block_height = 0
        self.calculate_sizes_in_blocks()
        self.layers = Layers(BASE_LEVEL_SIZE)
        self.screen_rect = pg.Rect(0, 0, *SCREEN_SIZE)

    def get_base_level_size(self) -> int:
        return self.base_level_size

    def calculate_sizes_in_blocks(self):
        self.block_width = self.scr_size[0] // self.base_level_size
        self.block_height = self.scr_size[1] // self.base_level_size

    def zoom_in(self) -> bool:
        if self.base_level_size >= ONE_LEVEL_STEP_BEGINNING + BASE_LEVEL_STEP:
            self.base_level_size -= BASE_LEVEL_STEP
            self.layers.set_base_level_size(self.base_level_size)
            self.calculate_sizes_in_blocks()
            return True
        elif self.base_level_size >= MIN_BASE_LEVEL_SIZE + 1:
            self.base_level_size -= 1
            self.layers.set_base_level_size(self.base_level_size)
            self.calculate_sizes_in_blocks()
            return True
        return False

    def zoom_out(self) -> bool:
        if self.base_level_size <= ONE_LEVEL_STEP_BEGINNING - 1:
            self.base_level_size += 1
            self.layers.set_base_level_size(self.base_level_size)
            self.calculate_sizes_in_blocks()
            return True
        elif self.base_level_size <= MAX_BASE_LEVEL_SIZE - BASE_LEVEL_STEP:
            self.base_level_size += BASE_LEVEL_STEP
            self.layers.set_base_level_size(self.base_level_size)
            self.calculate_sizes_in_blocks()
            return True
        return False

    def move(self, offset: list[float, float] | tuple[float, float]):
        self.center = self.center[0]+offset[0], self.center[1]+offset[1]

    def set_center(self, center: list[float, float] | tuple[float, float]):
        self.center = list(center)

    def get_center(self) -> tuple[float, float]:
        return self.center

    def get_rect(self) -> pg.Rect:
        left = self.center[0] - self.block_width // 2
        top = self.center[1] - self.block_height // 2
        if left < 0:
            left -= 1
        if top < 0:
            top -= 1
        rect = pg.Rect(left, top, self.block_width + 1, self.block_height + 1)
        rect.normalize()
        return rect

    def get_layers(self) -> Layers:
        self.layers.set_center(self.center)
        return self.layers

    def update_layers(self):
        self.layers.set_center(self.center)

    def get_loading_chunk_distance(self) -> int:
        return int(max(self.get_rect().size) / 2) + WORLD_CHUNK_SIZE
