from dataclasses import dataclass
from itertools import islice

from calendar.calendar import Calendar
from itertoolsx import takewhile_inclusive


@Calendar.register(day=8)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.tree_grid = [
            list(map(int, row.strip()))
            for row in self.puzzle_input.strip().splitlines()
        ]

    def is_visible(self, i, j):
        height = self.tree_grid[i][j]

        visible_from_above = all(
            height > row[j]
            for row in islice(self.tree_grid, i)
        )

        visible_from_below = all(
            height > row[j]
            for row in islice(self.tree_grid, i + 1, None)
        )

        visible_from_left = all(
            height > current_height
            for current_height in islice(self.tree_grid[i], j)
        )

        visible_from_right = all(
            height > current_height
            for current_height in islice(self.tree_grid[i], j + 1, None)
        )

        return visible_from_above or visible_from_below or visible_from_left or visible_from_right

    def scenic_score(self, i, j):
        height = self.tree_grid[i][j]

        top_score = sum(
            1
            for _ in takewhile_inclusive(
                lambda row: row[j] < height,
                reversed(list(islice(self.tree_grid, i)))
            )
        )

        bottom_score = sum(
            1
            for _ in takewhile_inclusive(
                lambda row: row[j] < height,
                islice(self.tree_grid, i + 1, None)
            )
        )

        left_score = sum(
            1
            for _ in takewhile_inclusive(
                lambda current_height: current_height < height,
                reversed(list(islice(self.tree_grid[i], j)))
            )
        )

        right_score = sum(
            1
            for _ in takewhile_inclusive(
                lambda current_height: current_height < height,
                islice(self.tree_grid[i], j + 1, None)
            )
        )

        return top_score * bottom_score * left_score * right_score

    def part1(self):
        return sum(
            1
            for i, row in enumerate(self.tree_grid)
            for j, height in enumerate(row)
            if self.is_visible(i, j)
        )

    def part2(self):
        return max(
            self.scenic_score(i, j)
            for i, row in enumerate(self.tree_grid)
            for j, height in enumerate(row)
        )


