from camera import Layers
import blocks
from world_class import Column
from mesh_3d_figures import SimpleFigure, ManySpritesTopFigure
from mesh_3d_sides_drawer import SidesDrawer
import pygame as pg


class FigureCreator:
    def __init__(self, layers: Layers, sides_drawer: SidesDrawer):
        self.layers = layers
        self.sides_drawer = sides_drawer

    def create_top_figures_for_column(self, column: Column) -> list[SimpleFigure | ManySpritesTopFigure]:
        figures = []
        non_transparent_already_rendered = False
        visible_blocks = column.get_blocks_with_visible_top_sprite()
        for m, block in enumerate(visible_blocks):
            if type(block) == blocks.Shadow:
                continue

            x, y, z = block.x, block.y, block.z
            block_rect = self.layers.get_rect_for_block(x, y, z)

            rect_size = block_rect.size
            if block.is_transparent:
                if m == 0:
                    raise AssertionError('Bottom visible block must be non transparent')
                else:
                    sprite = block.get_top_sprite_resized_shaded(rect_size, column.height_difference, z)
            else:
                assert not non_transparent_already_rendered
                non_transparent_already_rendered = True
                if len(visible_blocks) > 1:
                    sprite = block.get_top_sprite_fully_shaded(rect_size, column.height_difference, z, False)
                else:
                    sprite = block.get_top_sprite_resized_shaded(rect_size, column.height_difference, z)

            if type(block) == blocks.Grass:
                sprites = [pg.transform.rotate(sprite, 90*i) for i in range(4)]
                figure = ManySpritesTopFigure(block_rect, sprites, (x, y, z), (x, y, z + 1))
            else:
                figure = SimpleFigure(block_rect, sprite, (x, y, z), (x, y, z + 1))
            figures.append(figure)
        return figures

    def create_side_figures_for_column(self, column: Column) -> list[SimpleFigure]:
        figures = []

        full_hd = column.height_difference.full_full_height_diff
        nt_hd = column.height_difference.full_nt_height_diff

        top_block = column.get_top_block()
        x, y, z = column.x, column.y, top_block.z
        column_top_rect = self.layers.get_rect_for_block(x, y, z)
        column_bottom_rect = self.layers.get_rect_for_block(x, y, 0)

        keys = []
        if column_top_rect.bottom < column_bottom_rect.bottom:
            keys.append('south')
        if column_top_rect.top > column_bottom_rect.top:
            keys.append('north')
        if column_top_rect.right < column_bottom_rect.right:
            keys.append('east')
        if column_top_rect.left > column_bottom_rect.left:
            keys.append('west')

        values = list(full_hd.values()) + list(nt_hd.values())
        max_value = max(values)
        last_bottom_rect = column_top_rect
        for k in range(max_value):
            side_z = z - k
            top_rect = last_bottom_rect
            bottom_rect = self.layers.get_rect_for_block(x, y, side_z - 1)

            block = column.get_block(side_z)
            if type(block) == blocks.Shadow:
                last_bottom_rect = bottom_rect
                continue

            for key in keys:
                non_transparent_side = not block.is_transparent and k < nt_hd[key]
                transparent_side = block.is_transparent and k < full_hd[key]
                if non_transparent_side or transparent_side:
                    sprite, sprite_name = block.get_side_sprite(key, column.get_height_difference(), k)

                    figure = self.sides_drawer.create_figure(x, y, side_z, key,
                                                             sprite, sprite_name,
                                                             top_rect, bottom_rect)
                    if figure is not None:
                        figures.append(figure)
            last_bottom_rect = bottom_rect
        return figures