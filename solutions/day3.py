from dataclasses import dataclass
from functools import reduce

from calendar.calendar import Calendar
from itertoolsx import batched


@Calendar.register(day=3)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.rucksacks = self.puzzle_input.splitlines()

    @staticmethod
    def get_priority(item: str):
        return ord(item) - ord('a') + 1 if item.islower() else ord(item) - ord('A') + 27

    def part1(self):
        misplaced_items = [
            set(reduce(set.intersection, map(set, batched(rucksack, len(rucksack) // 2)))).pop()
            for rucksack in self.rucksacks
        ]

        return sum(self.get_priority(item) for item in misplaced_items)

    def part2(self):
        badges = [
            set(reduce(set.intersection, map(set, group))).pop()
            for group in batched(self.rucksacks, 3)
        ]

        return sum(self.get_priority(badge) for badge in badges)


