from dataclasses import dataclass

from calendar.calendar import Calendar
from itertoolsx import window, first


@Calendar.register(day=6)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.buffer = self.puzzle_input.strip()

        print(self.buffer)

    @staticmethod
    def first_distinct(buffer, n) -> tuple[int, tuple[str]]:
        ind, marker = first(enumerate(window(buffer, n)), pred=lambda i_w: len(set(i_w[1])) == n)
        return ind + n, marker

    def part1(self):
        return self.first_distinct(self.buffer, 4)

    def part2(self):
        return self.first_distinct(self.buffer, 14)


