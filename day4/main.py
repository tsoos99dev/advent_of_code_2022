from dataclasses import dataclass
from enum import Enum
from functools import reduce
from itertools import product, cycle, tee, islice, groupby

from collections import deque
from pprint import pprint
from typing import Iterable


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


def main():
    with open('input.txt', encoding='utf-8') as file:
        pairings = file.read().splitlines()
        pairing_ranges = [pairing.split(',') for pairing in pairings]
        interval_strings = [
            [prange.split('-') for prange in ranges]
            for ranges in pairing_ranges
        ]
        intervals = [
            [
                Interval(int(prange[0]), int(prange[1]))
                for prange in ranges
            ]
            for ranges in interval_strings
        ]

        # Part 1
        print(sum(
            1
            for pairing_intervals in intervals
            if pairing_intervals[0] in pairing_intervals[1] or pairing_intervals[1] in pairing_intervals[0]
        ))

        # Part 2
        print(sum(
            1
            for pairing_intervals in intervals
            if pairing_intervals[0].overlaps(pairing_intervals[1])
        ))


if __name__ == '__main__':
    main()