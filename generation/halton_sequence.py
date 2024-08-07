import os
import pickle
import random


def halton_sequence(b):
    n, d = 0, 1
    while True:
        x = d - n
        if x == 1:
            n = 1
            d *= b
        else:
            y = d // b
            while x <= y:
                y //= b
            n = (b + 1) * y - x
        yield n / d


class HaltonSequence:
    def __init__(self, size: int, seed):
        self.size = size
        self.h1 = halton_sequence(2)
        self.h2 = halton_sequence(3)
        for _ in range(17 * seed):
            next(self.h1)
            next(self.h2)

    def get_n_points(self, n: int) -> list[tuple[int, int]]:
        points = []
        for _ in range(n):
            for _ in range(673-1):
                next(self.h1)
                next(self.h2)
            a = next(self.h1)
            b = next(self.h2)
            x = int(a*self.size) % self.size
            y = int(b*self.size) % self.size
            points.append((x, y))
        random.shuffle(points)
        return points


class HaltonPoints:
    def __init__(self, path_to_saves: str,
                 unique_name: str,
                 chunk_size: int,
                 points_per_chunk: int,
                 avoiding_radius: int = 2):
        self.path = path_to_saves + unique_name + '/'
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        self.points_per_chunk = points_per_chunk
        self.chunk_size = chunk_size
        self.avoiding_distance = avoiding_radius
        self.chunks: dict[tuple[int, int]: list[tuple[int, int]]] = {}
        self.load_chunks()

    def load_chunks(self):
        for filename in os.listdir(self.path):
            with open(self.path + filename, 'rb') as file:
                data = pickle.load(file)
                x, y, points = data
                self.chunks[(x, y)] = points

    def add_and_save_chunk(self, chunk_x, chunk_y, points):
        self.chunks[(chunk_x, chunk_y)] = set(points)
        data = chunk_x, chunk_y, points
        filename = f'{chunk_x}_{chunk_y}.pickle'
        with open(self.path + filename, 'wb') as file:
            pickle.dump(data, file)

    def get_points_for_chunk(self, chunk_x, chunk_y) -> set[tuple[int, int]]:
        if (chunk_x, chunk_y) not in self.chunks:
            seed = (chunk_x * 17 + chunk_y * 11) % 25
            hs = HaltonSequence(self.chunk_size - self.avoiding_distance, seed)
            points = hs.get_n_points(self.points_per_chunk)
            moved_points = set()
            for x, y in points:
                x1 = x + self.chunk_size * chunk_x
                y1 = y + self.chunk_size * chunk_y
                moved_points.add((x1, y1))

            if self.avoiding_distance != 0:

                points_around = set()
                if (chunk_x-1, chunk_y) in self.chunks:
                    points_around.update(self.chunks[(chunk_x-1, chunk_y)])
                if (chunk_x+1, chunk_y) in self.chunks:
                    points_around.update(self.chunks[(chunk_x+1, chunk_y)])
                if (chunk_x, chunk_y-1) in self.chunks:
                    points_around.update(self.chunks[(chunk_x, chunk_y-1)])
                if (chunk_x, chunk_y+1) in self.chunks:
                    points_around.update(self.chunks[(chunk_x, chunk_y+1)])

                filtered_points = set()
                for x, y in moved_points:
                    found = False
                    for i in range(x-self.avoiding_distance, x + self.avoiding_distance + 1):
                        for j in range(y-self.avoiding_distance, y + self.avoiding_distance + 1):
                            if (i, j) in filtered_points or (i, j) in points_around:
                                found = True
                                break
                    if not found:
                        filtered_points.add((x, y))
                self.add_and_save_chunk(chunk_x, chunk_y, filtered_points)
            else:
                self.add_and_save_chunk(chunk_x, chunk_y, moved_points)
        return self.chunks[(chunk_x, chunk_y)]

    def get_points_by_point(self, point_x, point_y) -> set[tuple[int, int]]:
        chunk_x = point_x // self.chunk_size
        chunk_y = point_y // self.chunk_size
        return self.get_points_for_chunk(chunk_x, chunk_y)
