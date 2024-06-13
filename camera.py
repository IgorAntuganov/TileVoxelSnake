import pygame as pg
BASE_LEVEL_SIZE = 48


class Layers:
    def __init__(self, base_level_size: int):
        self.base_level_size = base_level_size
        self.focus = (0, 0)
        self.focus_on_screen = (0, 0)

    def set_base_level_size(self, size: int):
        self.base_level_size = size

    def set_focus(self, focus: tuple[float, float]):
        self.focus = focus

    def set_focus_on_screen(self, focus: tuple[int, int]):
        self.focus_on_screen = focus

    def get_n_level_size(self, n: int) -> int:
        """:return size of blocks with z=n in pixels of screen"""
        difference = n * 4
        #difference = max(self.base_level_size*difference, n//2)
        return int(self.base_level_size + difference)

    def get_n_level_x0_y0(self, n: int) -> tuple[int, int]:
        """:return topleft coordinates of block with x=0, y=0 in pixels of screen"""
        size = self.get_n_level_size(n)
        offset_x = (-self.focus[0]) * size + self.focus_on_screen[0]
        offset_y = (-self.focus[1]) * size + self.focus_on_screen[1]
        return offset_x, offset_y

    def get_rect(self, x, y, z) -> pg.Rect:
        rect_size = self.get_n_level_size(z)
        x0, y0 = self.get_n_level_x0_y0(z)
        left = x0 + x * rect_size
        top = y0 + y * rect_size
        rect = pg.Rect(left, top, rect_size, rect_size)
        return rect


class CameraFrame:
    def __init__(self, center: tuple[float, float], width: float, height: float, focus: tuple[float, float]):
        """All coordinates in blocks"""
        self.center = center
        self.width = width
        self.height = height
        self.focus = focus
        self.layers = Layers(BASE_LEVEL_SIZE)
        # !!!
        self.focus_on_screen = (768, 480)
        self.screen_rect = pg.Rect(0, 0, 1536, 960)

    def move(self, offset: list[float, float] | tuple[float, float]):
        self.center = self.center[0]+offset[0], self.center[1]+offset[1]
        self.focus = self.focus[0]+offset[0], self.focus[1]+offset[1]

    def set_center(self, center: list[float, float] | tuple[float, float]):
        self.center = list(center)

    def get_rect(self) -> pg.Rect:
        left = self.center[0] - self.width // 2
        top = self.center[1] - self.height // 2
        if left < 0:
            left -= 1
        if top < 0:
            top -= 1
        rect = pg.Rect(left, top, self.width+1, self.height+1)
        rect.normalize()
        return rect

    def get_layers(self) -> Layers:
        self.layers.set_focus(self.focus)
        self.layers.set_focus_on_screen(self.focus_on_screen)
        return self.layers

    def update_layers(self):
        self.layers.set_focus(self.focus)
        self.layers.set_focus_on_screen(self.focus_on_screen)

    def get_focus_in_frame(self) -> tuple[int, int]:
        focus = int(self.focus[0]), int(self.focus[1])
        rect = self.get_rect()
        x = focus[0] - rect.left
        y = focus[1] - rect.top
        return x, y
