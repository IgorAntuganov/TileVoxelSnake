import pygame as pg
from constants import BASE_LEVEL_SIZE, MIN_BASE_LEVEL_SIZE, MAX_BASE_LEVEL_SIZE, SCREEN_SIZE, BASE_LEVEL_STEP, \
    WORLD_CHUNK_SIZE


class Layers:
    def __init__(self, base_level_size: int):
        self.base_level_size = base_level_size
        self.scr_size = SCREEN_SIZE
        self.center = (0, 0)

    def get_base_level_size(self) -> int:
        return self.base_level_size

    def set_base_level_size(self, size: int):
        self.base_level_size = size

    def set_center(self, focus: tuple[float, float]):
        self.center = focus

    def get_n_level_size(self, n: float | int) -> float:
        """:return size of blocks with z=n in pixels of screen"""
        layers_offset = (self.base_level_size / 32) ** 3
        difference = n * layers_offset
        return self.base_level_size + difference

    def get_n_level_x0_y0(self, n: float | int) -> tuple[float, float]:
        """:return topleft coordinates of block with x=0, y=0 in pixels of screen"""
        size = self.get_n_level_size(n)
        offset_x = (-self.center[0]) * size + self.scr_size[0] / 2
        offset_y = (-self.center[1]) * size + self.scr_size[1] / 2
        return offset_x, offset_y

    def get_rect_for_block(self, x: int, y: int, z: int) -> pg.Rect:
        rect_size = self.get_n_level_size(z)
        x0, y0 = self.get_n_level_x0_y0(z)
        left = x0 + x * rect_size
        right = x0 + (x+1) * rect_size
        top = y0 + y * rect_size
        bottom = y0 + (y+1) * rect_size
        width = bottom - top
        height = right - left
        args = list([int(x) for x in [left, top, width+.999, height+.999]])
        rect = pg.Rect(*args)
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
        if self.base_level_size >= MIN_BASE_LEVEL_SIZE + BASE_LEVEL_STEP:
            self.base_level_size -= BASE_LEVEL_STEP
            self.layers.set_base_level_size(self.base_level_size)
            self.calculate_sizes_in_blocks()
            return True
        return False

    def zoom_out(self) -> bool:
        if self.base_level_size <= MAX_BASE_LEVEL_SIZE - BASE_LEVEL_STEP:
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
        return int(max(self.get_rect().size) / 2) + WORLD_CHUNK_SIZE // 3
