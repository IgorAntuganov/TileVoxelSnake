import os
import pickle
import pygame as pg
import blocks
from generation.height_map import HeightMap
from generation.biome_map import BiomeMap, Forest
from generation.halton_sequence import HaltonPoints
from generation.structures import Tree1, Tree2
from constants import *
from gui.objects import tiles_types, Tile
from world_column import Column
from world_region import Region


class ChangedColumnsCatalog:
    def __init__(self, path: str):
        self.folder = path
        if not os.path.isdir(path):
            os.mkdir(path)
        self.columns: dict[tuple[int, int]: Column] = {}

    def get_column_file_name(self, column: Column):
        return self.folder + f'{column.x}_{column.y}.pickle'

    def load(self):
        for file_name in os.listdir(self.folder):
            path = self.folder + file_name
            with open(path, 'rb') as file:
                data = pickle.load(file)
                column = Column.from_pickle(data)
                i, j = column.x, column.y
                self.columns[(i, j)] = column

    def check_if_column_was_changed(self, i, j) -> bool:
        return (i, j) in self.columns

    def get_changed_column(self, i, j) -> Column:
        return self.columns[(i, j)]

    def add_changed_column(self, column: Column):
        path = self.get_column_file_name(column)
        with open(path, 'wb') as file:
            pickle.dump(column.to_pickle(), file)


class TakenTilesCatalog:
    def __init__(self, path):
        self.folder = path
        self.file = self.folder + 'taken_tile.pickle'
        if not os.path.isdir(path):
            os.mkdir(path)
        self.taken = set()
        if not os.path.isfile(self.file):
            with open(self.file, 'wb') as file:
                pickle.dump(self.taken, file)

    def load(self):
        with open(self.file, 'rb') as file:
            self.taken = pickle.load(file)

    def add_tile(self, tile: Tile):
        self.taken.add((tile.x, tile.y, tile.z))
        with open(self.file, 'wb') as file:
            pickle.dump(self.taken, file)

    def check_if_already_taken(self, tile: Tile) -> bool:
        return (tile.x, tile.y, tile.z) in self.taken


class World:
    def __init__(self, name: str = 'test wrld'):
        self.name = name

        self.regions: dict[tuple[int, int]: Region] = {}
        self.loading_regions: list[Region] = []

        self.folder = PATH_TO_SAVES + f'{name}/'
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)
        path_to_changed_columns = self.folder + 'changed columns/'
        self.changed_columns = ChangedColumnsCatalog(path_to_changed_columns)
        self.changed_columns.load()

        path_to_taken_tiles = self.folder + 'taken tiles/'
        self.taken_tiles = TakenTilesCatalog(path_to_taken_tiles)
        self.taken_tiles.load()

        self.DEFAULT_ADDED_BLOCK: type = blocks.Glass

    def add_region(self, x2, y2):
        region = Region(x2 * WORLD_CHUNK_SIZE, y2 * WORLD_CHUNK_SIZE, WORLD_CHUNK_SIZE)
        self.regions[(x2, y2)] = region
        self.loading_regions.append(region)

    def get_region(self, x, y) -> Region:
        x2 = x // WORLD_CHUNK_SIZE
        y2 = y // WORLD_CHUNK_SIZE
        return self.regions[(x2, y2)]

    def check_is_region(self, x, y):
        x2 = x // WORLD_CHUNK_SIZE
        y2 = y // WORLD_CHUNK_SIZE
        return (x2, y2) in self.regions

    def get_column(self, x, y) -> Column | None:
        if self.check_is_region(x, y):
            region = self.get_region(x, y)
            column = region.get_column(x, y)
            return column
        '''else:
            if FILLING_COLUMNS_INFO:
                print('not is region, copying not fount column')
            return NOT_FOUND_COLUMN2.copy_to_x_y(x, y, True)'''

    def set_column(self, x, y, column: Column):
        region = self.get_region(x, y)
        region.set_column(x, y, column)

    def add_tile(self, x, y, tile: Tile):
        region = self.get_region(x, y)
        region.set_tile(x, y, tile)

    def get_all_tiles(self) -> list[Tile]:
        tiles = []
        for region in self.regions.values():
            tiles += region.get_tiles()
        return tiles

    def set_tile_as_taken(self, tile: Tile):
        region = self.get_region(tile.x, tile.y)
        region.set_tile_as_taken(tile)
        self.taken_tiles.add_tile(tile)

    def add_block_and_save_changes(self, block: tuple[int, int, int], _type: None | type = None):
        x, y, z = block
        if _type is None:
            _type = self.DEFAULT_ADDED_BLOCK
        column = self.get_column(x, y)
        column.add_block_on_top(_type)
        rect = pg.Rect(x - 1, y - 1, 3, 3)
        self.set_columns_h_diff_in_rect(rect)
        self.changed_columns.add_changed_column(column)

    def remove_block_and_save_changes(self, block: tuple[int, int, int]):
        x, y, z = block
        column = self.get_column(x, y)
        column.remove_top_block()
        rect = pg.Rect(x-1, y-1, 3, 3)
        self.set_columns_h_diff_in_rect(rect)
        self.changed_columns.add_changed_column(column)

    def set_columns_h_diff_in_rect(self, rect: pg.Rect):
        if FILLING_COLUMNS_INFO:
            print('start setting h diffs -----------------------------------')
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                column = self.get_column(i, j)
                if column is None:
                    continue
                if FILLING_COLUMNS_INFO:
                    print('setting for column', i, j)
                left   = self.get_column(i-1, j)
                top    = self.get_column(i,   j-1)
                right  = self.get_column(i+1, j)
                bottom = self.get_column(i,   j+1)
                top_left     = self.get_column(i-1, j-1)
                top_right    = self.get_column(i+1, j-1)
                bottom_left  = self.get_column(i-1, j+1)
                bottom_right = self.get_column(i+1, j+1)
                column.set_height_difference(left, top, right, bottom, top_left, top_right, bottom_left, bottom_right)


class WorldFiller:
    def __init__(self, world: World, seed: int = 0, ):
        self.world = world

        name = world.name
        self.folder = PATH_TO_SAVES + f'{name}/'
        self.height_map = HeightMap(self.folder, seed)

        self.biome_map = BiomeMap(self.folder, seed)

        self.tree_generator = HaltonPoints(self.folder, 'trees', TREES_CHUNK_SIZE, TREES_IN_CHUNK, TREE_AVOIDING_RADIUS)
        self.blocks_to_add_stash: dict[tuple[int, int]: list[blocks.Block]] = {}

        self.tile_generator = HaltonPoints(self.folder, 'tiles', TILES_CHUNK_SIZE, TILES_IN_CHUNK, TILE_AVOIDING_RADIUS)

        self.current_loading_iterator = None
        self.loading_region: None | Region = None

    def set_block_to_add_during_generation(self, block):
        if (block.x, block.y) not in self.blocks_to_add_stash:
            self.blocks_to_add_stash[(block.x, block.y)] = [block]
        else:
            self.blocks_to_add_stash[(block.x, block.y)].append(block)

    def check_stash_for_column(self, column, i, j):
        if (i, j) in self.blocks_to_add_stash:
            blocks_from_stash: list[blocks.Block] = self.blocks_to_add_stash[(i, j)]
            blocks_from_stash.sort(key=lambda b: b.z)
            while blocks_from_stash[0].z > column.nt_height + len(column.transparent_blocks):
                if blocks_from_stash[0].is_transparent:
                    column.add_block_on_top(blocks.Shadow)
                else:
                    column.add_block_on_top(type(column.get_top_block()))
            for block in blocks_from_stash:
                if not block.z <= column.nt_height + len(column.transparent_blocks):
                    column.add_block_on_top(type(block))
            self.blocks_to_add_stash.pop((i, j))
        self.world.set_columns_h_diff_in_rect(pg.Rect(i-1, j-1, 3, 3))

    def add_stash_blocks_to_rect_generator(self, rect: pg.Rect):
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                checking_column = self.world.get_column(i, j)
                self.check_stash_for_column(checking_column, i, j)
            yield

    def set_columns_in_rect_generator(self, rect: pg.Rect):
        structures = []
        for i in range(rect.left, rect.right):
            for j in range(rect.top, rect.bottom):
                if self.world.changed_columns.check_if_column_was_changed(i, j):
                    new_column = self.world.changed_columns.get_changed_column(i, j)
                else:
                    height = self.height_map.get_height(i, j)
                    biome = self.biome_map.get_biome(i, j)
                    _blocks = biome.blocks_from_height(height)

                    if len(_blocks) < WATER_LEVEL:
                        for _ in range(WATER_LEVEL - len(_blocks)):
                            _blocks = [blocks.Water] * (WATER_LEVEL - len(_blocks)) + _blocks

                    new_column = Column(i, j, _blocks)

                    if biome is Forest and len(_blocks) > WATER_LEVEL:
                        trees = self.tree_generator.get_points_by_point(i, j)
                        if (i, j) in trees:
                            if i + j % 3 == 0:
                                structures.append(Tree2(i, j, new_column.nt_height))
                            else:
                                structures.append(Tree1(i, j, new_column.nt_height))

                    if len(_blocks) > WATER_LEVEL:
                        tiles = self.tile_generator.get_points_by_point(i, j)
                        if (i, j) in tiles:
                            z_offset = ((i+j) % 3) - 1
                            tile_type = tiles_types[(i+j) % len(tiles_types)]
                            tile = tile_type(i, j, len(_blocks)-1 + z_offset)
                            if not self.world.taken_tiles.check_if_already_taken(tile):
                                self.world.add_tile(i, j, tile)

                self.world.set_column(i, j, new_column)
            yield

        for _ in self.add_stash_blocks_to_rect_generator(rect):
            yield

        for structure in structures:
            for block in structure.get_blocks_sorted():
                i, j = block.x, block.y
                if rect.collidepoint(i, j):
                    editing_column = self.world.get_column(i, j)
                    height_diff = editing_column.nt_height + len(editing_column.transparent_blocks) - structure.z
                    if type(block) is blocks.Shadow:
                        for i in range(max(0, -height_diff - 1)):
                            editing_column.add_block_on_top(blocks.Shadow)
                    if height_diff >= block.z - structure.z:
                        continue
                    editing_column.add_block_on_top(type(block))
                else:
                    self.set_block_to_add_during_generation(block)
            yield

        bigger_rect = pg.Rect(rect.left - 1, rect.top - 1, rect.width + 2, rect.height + 2)
        self.world.set_columns_h_diff_in_rect(bigger_rect)
        yield

    def update_regions_by_distance(self, frame_x: int, frame_y: int, load_distance: int):
        # removing too far regions
        for key in list(self.world.regions.keys()):
            r: Region = self.world.regions[key]
            if not r.check_region_distance(frame_x, frame_y, load_distance * 1.5):
                if HEIGHT_GENERATING_INFO:
                    print('deleting too far region', key)
                self.world.regions.pop(key)
        # adding nearby regions
        left = (frame_x - load_distance) // WORLD_CHUNK_SIZE
        right = (frame_x + load_distance) // WORLD_CHUNK_SIZE
        top = (frame_y - load_distance) // WORLD_CHUNK_SIZE
        bottom = (frame_y + load_distance) // WORLD_CHUNK_SIZE
        for i in range(left, right+1):
            for j in range(top, bottom+1):
                center_x = i * WORLD_CHUNK_SIZE + WORLD_CHUNK_SIZE // 2
                center_y = j * WORLD_CHUNK_SIZE + WORLD_CHUNK_SIZE // 2
                if (i, j) not in self.world.regions and \
                        Region.check_distance(frame_x, frame_y, center_x, center_y, load_distance):
                    if HEIGHT_GENERATING_INFO:
                        print('add nearby region', i, j, center_x, center_y)
                    self.world.add_region(i, j)
        if HEIGHT_GENERATING_INFO:
            print('regions after checking: ')
            for key in sorted(list(self.world.regions.keys())):
                print(key, end=' ')
            print()

    def select_loading_region(self, frame_x: int, frame_y: int) -> Region:
        regions = self.world.loading_regions
        selected = min(regions, key=lambda r: r.get_distance_to_point(frame_x, frame_y))
        self.world.loading_regions.remove(selected)
        return selected

    def load_chucks_by_part(self, frame_x: int, frame_y: int):
        if len(self.world.loading_regions) > 0 and self.current_loading_iterator is None:
            if self.current_loading_iterator is None:
                self.loading_region = self.select_loading_region(frame_x, frame_y)
                rect = self.loading_region.get_rect().copy()
                self.current_loading_iterator = self.set_columns_in_rect_generator(rect)
        elif self.current_loading_iterator is not None:
            if not self.world.check_is_region(self.loading_region.x, self.loading_region.y):
                self.loading_region = None
                self.current_loading_iterator = None
            else:
                try:
                    next(self.current_loading_iterator)
                except StopIteration:
                    self.loading_region.filled = True
                    self.check_stash()
                    self.current_loading_iterator = None
                    self.loading_region = None

    def check_stash(self):
        if len(self.blocks_to_add_stash) > 0:
            for x, y in list(self.blocks_to_add_stash.keys()):
                if self.world.check_is_region(x, y):
                    region = self.world.get_region(x, y)
                    if region.filled:
                        column = self.world.get_column(x, y)
                        self.check_stash_for_column(column, x, y)

    def preload_start_area(self, frame_x: int, frame_y: int, load_dist: int):
        pass
