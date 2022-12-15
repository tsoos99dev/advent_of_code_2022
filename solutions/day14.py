import curses
import math
import queue
from curses import wrapper
from dataclasses import dataclass
from itertools import pairwise, accumulate, starmap, takewhile, repeat, chain
from queue import LifoQueue
from typing import Iterable, Protocol, Optional

from calendar.calendar import Calendar
from itertoolsx import flatten, iter_except
from mathx import Vector


class RockLine(Protocol):
    def contains(self, point: Vector) -> bool:
        ...


@dataclass
class HorizontalRockLine:
    start: Vector
    end: Vector

    def contains(self, point: Vector) -> bool:
        return point.y == self.start.y and self.start.x <= point.x <= self.end.x


@dataclass
class VerticalRockLine:
    start: Vector
    end: Vector

    def contains(self, point: Vector) -> bool:
        return point.x == self.start.x and self.start.y <= point.y <= self.end.y


@Calendar.register(day=14)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     498,4 -> 498,6 -> 496,6
        #     503,4 -> 502,4 -> 502,9 -> 494,9
        # """

        def parse_position(position_data: str) -> Vector:
            return Vector(*map(int, position_data.strip().split(',')))

        def parse_rock_line_endpoints(start: Vector, end: Vector) -> RockLine:
            if start.x == end.x:
                return VerticalRockLine(
                    Vector(start.x, min(start.y, end.y)),
                    Vector(end.x, max(start.y, end.y))
                )

            return HorizontalRockLine(
                Vector(min(start.x, end.x), start.y),
                Vector(max(start.x, end.x), end.y)
            )

        def parse_rock_lines(line: str):
            return list(pairwise(map(parse_position, line.strip().split('->'))))

        self.start_position = Vector(500, 0)
        rock_lines_data = self.puzzle_input.strip().splitlines()
        rock_line_endpoints = list(flatten(map(parse_rock_lines, rock_lines_data)))
        self.rock_lines = list(starmap(parse_rock_line_endpoints, rock_line_endpoints))
        self.bottom_edge = int(max(map(lambda coordinate: coordinate.y, flatten(rock_line_endpoints))))

    def fall_down(self, sand_positions: set[Vector], start_position: Vector) -> Iterable[set[Vector]]:
        return starmap(
            lambda positions, current_position: set(chain(positions, [current_position])),
            zip(repeat(sand_positions), takewhile(
                lambda position: position,
                accumulate(repeat(sand_positions), self.update_pos, initial=start_position)
            ))
        )

    def simulate(self):
        sand_path: LifoQueue[Vector] = LifoQueue()
        world_map: dict[Vector, bool] = {}
        sand_pile: set[Vector] = set()

        fall_vectors = [Vector(0, 1), Vector(-1, 1), Vector(1, 1)]

        def update_pos(current_position: Vector) -> Optional[Vector]:
            potential_positions = map(lambda direction: direction + current_position, fall_vectors)
            for position in potential_positions:
                state = world_map.get(position, None)
                if state is None:
                    state = any(map(lambda rock_line: rock_line.contains(position), self.rock_lines))
                    world_map[position] = state

                if state:
                    continue

                return position

            return None

        sand_path.put_nowait(self.start_position)

        for start_position in iter_except(sand_path.get_nowait, queue.Empty):
            current_position = start_position

            while True:
                new_position = update_pos(current_position)
                if not new_position:
                    break

                if new_position.y > self.bottom_edge:
                    return

                sand_path.put_nowait(current_position)
                current_position = new_position

            world_map[current_position] = True
            sand_pile.add(current_position)

            yield sand_pile.copy()

    def display(self, simulation: list[set[Vector]]):
        def inner(stdscr):
            pad_width = curses.COLS
            pad_height = self.bottom_edge
            curses.curs_set(False)
            stdscr.clear()
            stdscr.refresh()
            # stdscr.nodelay(True)

            sim_pad = curses.newpad(pad_height, pad_width)
            sim_pad.scrollok(True)
            pad_x = 0
            pad_y = 0

            def pad_refresh():
                sim_pad.refresh(pad_y, pad_x, 0, 0, curses.LINES - 1, curses.COLS - 1)

            current_frame_ind = 0

            def draw_frame():
                # Draw air
                for i in range(pad_height):
                    sim_pad.hline(i, 0, '.', pad_width)

                # Draw rocks
                # for coordinate in self.rock_coordinates:
                #     sim_pad.addch(int(coordinate.y), int(coordinate.x - self.boundary.position.x), '#')

                # Draw source
                # sim_pad.addch(int(self.start_position.y), int(self.start_position.x - self.boundary.position.x), '+')

                # Draw sand
                current_frame = simulation[current_frame_ind]
                for sand_position in current_frame:
                    sim_pad.addch(int(sand_position.y), int(sand_position.x - self.boundary.position.x), 'o')

                pad_refresh()

            draw_frame()

            while True:
                key = stdscr.getch()

                match key:
                    case curses.KEY_UP:
                        pad_y = max(0, pad_y - 1)
                        draw_frame()
                    case curses.KEY_DOWN:
                        pad_y = min(pad_height - curses.LINES, pad_y + 1)
                        draw_frame()
                    case curses.KEY_LEFT:
                        pad_x = max(0, pad_x - 1)
                        draw_frame()
                    case curses.KEY_RIGHT:
                        pad_x = min(pad_width - curses.COLS, pad_x + 1)
                        draw_frame()
                    case 10:
                        current_frame_ind = min(current_frame_ind + 1, len(simulation) - 1)
                        draw_frame()

        wrapper(inner)

    def part1(self):
        simulation = list(self.simulate())
        return len(simulation[-1])

    def part2(self):
        self.bottom_edge += 2
        floor = HorizontalRockLine(
            Vector(-math.inf, self.bottom_edge),
            Vector(math.inf, self.bottom_edge)
        )

        self.rock_lines.append(floor)
        simulation = list(self.simulate())
        return len(simulation[-1])