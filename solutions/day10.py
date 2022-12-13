import math
import operator
from dataclasses import dataclass, field, astuple
from functools import partial
from itertools import islice, takewhile, count, accumulate, chain, pairwise, starmap, repeat, zip_longest
from pprint import pprint
from typing import Protocol, Callable, Optional, Iterable

from calendar.calendar import Calendar
from itertoolsx import takewhile_inclusive, prepend, tail, flatten, batched


@Calendar.register(day=10)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        def parse_instruction(instruction: str) -> Iterable[int]:
            match instruction.strip().split(' '):
                case ['noop']:
                    return [0]
                case ['addx', n]:
                    return [0, int(n)]

        self.register_values = list(accumulate(flatten(map(parse_instruction, self.puzzle_input.strip().splitlines())), initial=1))

    def part1(self):
        return sum(i * self.register_values[i-1] for i in range(20, 221, 40))

    def part2(self):
        pixels = map(
            lambda row: "".join(starmap(
                lambda col_id, sprite_pos: '#' if col_id in range(sprite_pos - 1, sprite_pos + 2) else '.',
                enumerate(row)
            )),
            batched(self.register_values, 40)
        )

        return "\n".join(pixels)

