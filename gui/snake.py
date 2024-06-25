from gui.objects import Player, Tile


class Snake:
    def __init__(self, player: Player):
        self.player = player
        self.body: list[Tile] = []

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

    def add_tile(self, tile: Tile):
        self.body.append(tile)

    def is_ready_for_level_up(self) -> bool:
        current_level = self.player.level
        return len(self.body) > current_level

    def level_up(self):
        self.player.level_up()
        self.body = []
