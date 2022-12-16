from dataclasses import dataclass

from calendar.calendar import Calendar


@Calendar.register(day=1)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        ...

    def part1(self):
        ...

    def part2(self):
        ...

