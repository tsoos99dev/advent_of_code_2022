import math
import operator
from dataclasses import dataclass, field, astuple
from functools import partial
from itertools import islice, takewhile, count, accumulate, chain, pairwise, starmap, repeat, zip_longest
from pprint import pprint
from typing import Protocol, Callable, Optional, Iterable

from calendar.calendar import Calendar
from itertoolsx import takewhile_inclusive, prepend, tail, flatten


@dataclass(frozen=True)
class Vector:
    x: int
    y: int

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(scalar * self.x, scalar * self.y)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __iter__(self):
        return iter(astuple(self))


@Calendar.register(day=9)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        def parse_move(move: str) -> Iterable[Vector]:
            direction, steps = move.strip().split(' ')
            unit_vector = unit_vectors[direction]
            return repeat(unit_vector, int(steps))

        unit_vectors: dict[str, Vector] = {
            'L': Vector(-1, 0),
            'R': Vector(1, 0),
            'U': Vector(0, -1),
            'D': Vector(0, 1)
        }

        moves = list(chain.from_iterable(map(parse_move, self.puzzle_input.strip().splitlines())))
        self.head_positions = list(accumulate(moves, initial=Vector(0, 0)))

    @staticmethod
    def get_node_position(current_head_position: Vector, current_node_position: Vector) -> Vector:
        dx, dy = current_head_position - current_node_position
        tx = (abs(dx - 1) - abs(dx + 1)) // 2 * (1 - (abs(abs(dy) - abs(dx)) + abs(dy) - abs(dx)) // 2)
        ty = (abs(dy - 1) - abs(dy + 1)) // 2 * (1 - (abs(abs(dx) - abs(dy)) + abs(dx) - abs(dy)) // 2)
        return current_head_position + Vector(tx, ty)

    def update_tail_positions(self, current_tail_positions: Iterable[Vector], current_head_position: Vector):
        return tuple(islice(accumulate(current_tail_positions, self.get_node_position, initial=current_head_position), 1, None))

    def get_tail_positions(self, n: int):
        initial_tail_positions = (Vector(0, 0),) * n
        return tuple(islice(accumulate(self.head_positions, self.update_tail_positions, initial=initial_tail_positions), 1, None))

    def part1(self):
        tail_positions = self.get_tail_positions(1)
        return len(set(flatten(map(lambda positions: tail(1, positions), tail_positions))))

    def part2(self):
        tail_positions = self.get_tail_positions(9)
        return len(set(flatten(map(lambda positions: tail(1, positions), tail_positions))))

