from dataclasses import dataclass
from itertools import islice

from calendar.calendar import Calendar
from itertoolsx import isplit


@Calendar.register(day=1)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        lines = self.puzzle_input.splitlines()
        elf_inventories = isplit(lines, '')

        self.total_calories = [
            sum(int(calorie) for calorie in inventory)
            for inventory in elf_inventories
        ]

    def part1(self):
        return max(self.total_calories)

    def part2(self):
        return sum(islice(sorted(self.total_calories, reverse=True), 3))

