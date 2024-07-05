from gui.objects import Player, Tile, EmptyTile


class Snake:
    def __init__(self, player: Player):
        self.player = player
        self.length = player.level + 1
        self.filled_with_color = False
        xyz = player.x, player.y, player.z
        self.body: list[Tile] = [EmptyTile(*xyz) for _ in range(self.length)]

    def move_horizontally(self, x: int, y: int):
        self.player.move(x, y, 0)
        previous_tiles: list[Player | Tile] = [self.player] + self.body[:-1]
        for tile, prev_tile in zip(self.body, previous_tiles):
            point = prev_tile.last_location
            tile.move_to_point(*point)

    def move_player_vertically(self, z: int):
        self.player.move(0, 0, z)

    def get_body(self) -> list[Tile]:
        return self.body

    def add_tile(self, new_tile: Tile):
        assert not self.filled_with_color
        for i, tile in enumerate(self.body):
            if type(tile) == EmptyTile:
                new_tile.x, new_tile.y, new_tile.z = tile.x, tile.y, tile.z
                self.body = self.body[:i] + [new_tile] + self.body[i+1:]
                if i == self.length - 1:
                    self.filled_with_color = True
                break

    def is_ready_for_level_up(self) -> bool:
        return self.filled_with_color

    def level_up(self):
        self.player.level_up()
        self.filled_with_color = False
        self.length += 1

        new_body = []
        for tile in self.body:
            empty = EmptyTile(tile.x, tile.y, tile.z)
            new_body.append(empty)
        tile = self.body[-1]
        extra_tile = EmptyTile(tile.x, tile.y, tile.z)
        new_body.append(extra_tile)
        self.body = new_body
