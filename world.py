from blocks import *


class Column:
    def __init__(self, x, y, blocks: list[Block]):
        self.x = x
        self.y = y
        self.blocks = blocks


class World:
    def __init__(self):
        self.regions = {}
