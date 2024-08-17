from abc import ABC, abstractmethod
import blocks


class Structure(ABC):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.blocks: list[blocks.Block] = []  # in removing order
        self.create_blocks()

    @abstractmethod
    def create_blocks(self):
        pass

    def get_blocks_sorted(self) -> list[blocks.Block]:
        return sorted(self.blocks, key=lambda block: block.z, reverse=False)

    def check_if_exist(self) -> bool:
        return len(self.blocks) != 0

    def check_collision(self, x, y, z) -> bool:
        for block in self.blocks:
            if block.x == x and block.y == y and block.z == z:
                return True
        return False

    def pop_block(self) -> list[tuple[int, int, int]]:
        removing_blocks = [self.blocks.pop().get_xyz()]
        while type(removing_blocks[-1]) == blocks.Shadow:
            removing_blocks.append(self.blocks.pop().get_xyz())
        return removing_blocks


class Tree1(Structure):
    def create_blocks(self):
        for i in range(5):
            self.blocks.append(blocks.OakLog(self.x, self.y, self.z+i))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z))
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z+1))
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z+2))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Leaves(self.x + i, self.y + j, self.z+3))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Leaves(self.x + i, self.y + j, self.z+4))
        self.blocks.append(blocks.Leaves(self.x-1, self.y, self.z+5))
        self.blocks.append(blocks.Leaves(self.x+1, self.y, self.z+5))
        self.blocks.append(blocks.Leaves(self.x, self.y+1, self.z+5))
        self.blocks.append(blocks.Leaves(self.x, self.y-1, self.z+5))
        self.blocks.append(blocks.Leaves(self.x, self.y, self.z+6))


class Tree2(Structure):
    def create_blocks(self):
        for i in range(6):
            self.blocks.append(blocks.OakLog(self.x, self.y, self.z+i))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z))
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z+1))
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z+2))
                    self.blocks.append(blocks.Shadow(self.x + i, self.y + j, self.z+3))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Leaves(self.x + i, self.y + j, self.z+4))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if not (i == 0 and j == 0) and not (i in (-2, 2) and j in (-2, 2)):
                    self.blocks.append(blocks.Leaves(self.x + i, self.y + j, self.z+5))
        self.blocks.append(blocks.Leaves(self.x-1, self.y, self.z+6))
        self.blocks.append(blocks.Leaves(self.x+1, self.y, self.z+6))
        self.blocks.append(blocks.Leaves(self.x, self.y+1, self.z+6))
        self.blocks.append(blocks.Leaves(self.x, self.y-1, self.z+6))
        self.blocks.append(blocks.Leaves(self.x, self.y, self.z+7))
