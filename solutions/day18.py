import queue
from dataclasses import dataclass
from itertools import starmap
from queue import Queue

from calendar.calendar import Calendar
from itertoolsx import quantify, iter_except

Coordinate = tuple[int, ...]


@Calendar.register(day=18)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     2,2,2
        #     1,2,2
        #     3,2,2
        #     2,1,2
        #     2,3,2
        #     2,2,1
        #     2,2,3
        #     2,2,4
        #     2,2,6
        #     1,2,5
        #     3,2,5
        #     2,1,5
        #     2,3,5
        # """

        def parse_coordinate(data: str) -> Coordinate:
            return tuple(map(int, data.strip().split(',')))

        self.lava_coordinates = list(map(parse_coordinate, self.puzzle_input.strip().splitlines()))

        self.surfaces: dict[Coordinate, int] = {}

        for coordinate in self.lava_coordinates:
            surface = self.construct_surface(coordinate)
            for surface_coordinate, direction in surface.items():
                self.surfaces[surface_coordinate] = self.surfaces.get(surface_coordinate, 0) + direction

    def construct_surface(self, coordinate: Coordinate):
        x, y, z = coordinate
        return {
            (2 * x + 1, 2 * y, 2 * z): +1,
            (2 * x - 1, 2 * y, 2 * z): -1,
            (2 * x, 2 * y + 1, 2 * z): +1,
            (2 * x, 2 * y - 1, 2 * z): -1,
            (2 * x, 2 * y, 2 * z + 1): +1,
            (2 * x, 2 * y, 2 * z - 1): -1
        }

    def part1(self):
        return quantify(self.surfaces.values(), pred=lambda surface: surface != 0)

    def part2(self):
        min_x = min(starmap(lambda x, y, z: x, self.lava_coordinates)) - 5
        max_x = max(starmap(lambda x, y, z: x, self.lava_coordinates)) + 5
        min_y = min(starmap(lambda x, y, z: y, self.lava_coordinates)) - 5
        max_y = max(starmap(lambda x, y, z: y, self.lava_coordinates)) + 5
        min_z = min(starmap(lambda x, y, z: z, self.lava_coordinates)) - 5
        max_z = max(starmap(lambda x, y, z: z, self.lava_coordinates)) + 5

        volume: set[Coordinate] = set()

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                for z in range(min_z, max_z):
                    volume.add((x, y, z))

        start = (min_x, min_y, min_z)
        filled_coordinates: set[Coordinate] = {start}

        steam_envelope: Queue[Coordinate] = Queue()
        steam_envelope.put_nowait(start)

        for coordinate in iter_except(steam_envelope.get_nowait, queue.Empty):
            x, y, z = coordinate
            neighbours = [
                (x + 1, y, z),
                (x - 1, y, z),
                (x, y + 1, z),
                (x, y - 1, z),
                (x, y, z + 1),
                (x, y, z - 1)
            ]

            for neighbour in neighbours:
                if neighbour in self.lava_coordinates:
                    continue

                nx, ny, nz = neighbour

                if nx < min_x or nx > max_x:
                    continue

                if ny < min_y or ny > max_y:
                    continue

                if nz < min_z or nz > max_z:
                    continue

                if neighbour in filled_coordinates:
                    continue

                filled_coordinates.add(neighbour)
                steam_envelope.put_nowait(neighbour)

        air_pockets = volume - filled_coordinates - set(self.lava_coordinates)

        for coordinate in air_pockets:
            surface = self.construct_surface(coordinate)
            for surface_coordinate, direction in surface.items():
                self.surfaces[surface_coordinate] = self.surfaces.get(surface_coordinate, 0) + direction

        return quantify(self.surfaces.values(), pred=lambda surface: surface != 0)



