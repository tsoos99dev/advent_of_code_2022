from dataclasses import dataclass

from calendar.calendar import Calendar
from search import a_star, PathNotFoundError


@dataclass(frozen=True)
class MapTile:
    x_coord: int
    y_coord: int
    height: str


@Calendar.register(day=12)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.tiles: dict[tuple[int, int], MapTile] = {}

        # self.puzzle_input = """
        #     Sabqponm
        #     abcryxxl
        #     accszExk
        #     acctuvwj
        #     abdefghi
        # """

        for row_ind, row in enumerate(self.puzzle_input.strip().split()):
            for col_ind, height in enumerate(row):
                def create_tile(_height: str):
                    return MapTile(col_ind, row_ind, _height)

                match height:
                    case 'S':
                        tile = create_tile('a')
                        self.start_node = tile
                    case 'E':
                        tile = create_tile('z')
                        self.goal_node = tile
                    case _:
                        tile = create_tile(height)

                self.tiles[col_ind, row_ind] = tile

    def decode(self, height: str) -> int:
        return ord(height) - ord('a')

    def get_neighbours(self, tile: MapTile):
        surrounding_tiles = [
            self.tiles.get((tile.x_coord - 1, tile.y_coord), None),
            self.tiles.get((tile.x_coord + 1, tile.y_coord), None),
            self.tiles.get((tile.x_coord, tile.y_coord - 1), None),
            self.tiles.get((tile.x_coord, tile.y_coord + 1), None)
        ]

        return [
            neighbour
            for neighbour in surrounding_tiles
            if neighbour is not None and self.decode(neighbour.height) - self.decode(tile.height) <= 1
        ]

    def tile_heuristic(self, tile: MapTile):
        return float(abs(self.goal_node.x_coord - tile.x_coord) + abs(self.goal_node.y_coord - tile.y_coord))

    def part1(self):
        path = a_star(self.start_node, self.goal_node, self.get_neighbours, self.tile_heuristic, lambda t1, t2: 1)
        return path.length

    def part2(self):
        all_paths = []

        for start_node in filter(lambda tile: tile.height == 'a', self.tiles.values()):
            try:
                path = a_star(start_node, self.goal_node, self.get_neighbours, self.tile_heuristic, lambda t1, t2: 1)
            except PathNotFoundError:
                continue

            all_paths.append(path)

        return min(path.length for path in all_paths)
