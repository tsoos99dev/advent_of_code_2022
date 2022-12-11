from dataclasses import dataclass
from itertools import starmap

from calendar.calendar import Calendar


@dataclass
class Interval:
    start: int
    end: int

    def __contains__(self, interval):
        return interval.start >= self.start and interval.end <= self.end

    def overlaps(self, interval):
        s1 = self.start << 1
        e1 = self.end << 1

        s2 = interval.start << 1
        e2 = interval.end << 1

        l1 = (e1 - s1) >> 1
        l2 = (e2 - s2) >> 1
        l = l1 + l2

        m1 = s1 + l1
        m2 = s2 + l2
        d = abs(m2 - m1)
        return d <= l


@Calendar.register(day=4)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        pairings = self.puzzle_input.splitlines()

        def parse_range(range_string):
            return map(int, range_string.split('-'))

        pairing_ranges = map(
            lambda pairing: map(parse_range, pairing.split(',')),
            pairings
        )
        self.intervals = list(map(lambda ranges: list(starmap(Interval, ranges)), pairing_ranges))

    def part1(self):
        return sum(
            1
            for interval1, interval2 in self.intervals
            if interval1 in interval2 or interval2 in interval1
        )

    def part2(self):
        return sum(
            1
            for interval1, interval2 in self.intervals
            if interval1.overlaps(interval2)
        )
