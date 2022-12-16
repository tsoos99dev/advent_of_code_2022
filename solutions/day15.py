import re
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial, reduce
from itertools import starmap, pairwise
from typing import Iterable, Protocol, Optional

from calendar.calendar import Calendar
from itertoolsx import flatten, first
from mathx import Vector


@dataclass
class Interval:
    """Half open interval [start, end)"""
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start

    def overlaps(self, other: 'Interval') -> bool:
        return self.start < other.end or other.start < self.end

    def __contains__(self, other) -> bool:
        if isinstance(other, int):
            return self.start <= other < self.end

        return self.start <= other.start and other.end <= self.end

    def __iter__(self):
        return iter(range(self.start, self.end))


class Device(Protocol):
    position: Vector

    def coverage(self, row: int) -> Optional[Interval]:
        ...


@dataclass(frozen=True)
class Beacon:
    position: Vector

    def coverage(self, row: int) -> Optional[Interval]:
        if row != self.position.y:
            return None

        return Interval(int(self.position.x), int(self.position.x + 1))


@dataclass(frozen=True)
class Sensor:
    position: Vector
    beacon_distance: int

    def coverage(self, row: int) -> Optional[Interval]:
        row_dist = int(abs(row - self.position.y))
        radius = max(0, self.beacon_distance - row_dist)
        start = int(self.position.x) - radius
        end = int(self.position.x) + radius

        if end == start:
            return None

        return Interval(start, end + 1)


def merge(intervals: Iterable[Interval]):
    sorted_intervals = sorted(intervals, key=lambda interval: interval.start)

    def merge_inner(intervals: list[Interval], next_interval: Interval):
        previous_interval = intervals.pop()
        if next_interval.start <= previous_interval.end:
            intervals.append(Interval(previous_interval.start, max(previous_interval.end, next_interval.end)))
        else:
            intervals.extend([previous_interval, next_interval])

        return intervals

    return reduce(merge_inner, sorted_intervals[1:], sorted_intervals[:1])


def get_combined_coverage_at(row: int, *_, devices: set[Device]) -> list[Interval]:
    device_coverage = list(filter(None, map(lambda device: device.coverage(row), devices)))
    combined_coverage = merge(device_coverage)
    return combined_coverage


def find_distress_beacon_at(row: int, *_, devices: set[Device], search_interval: Interval) -> Optional[Vector]:
    coverage = get_combined_coverage_at(row, devices=devices)
    possible_cols = flatten(map(lambda interval: (interval.start - 1, interval.end), coverage))
    distress_beacon_col = first(possible_cols, pred=lambda interval: interval in search_interval)

    if not distress_beacon_col:
        return None

    return Vector(distress_beacon_col, row)


@Calendar.register(day=15)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     Sensor at x=2, y=18: closest beacon is at x=-2, y=15
        #     Sensor at x=9, y=16: closest beacon is at x=10, y=16
        #     Sensor at x=13, y=2: closest beacon is at x=15, y=3
        #     Sensor at x=12, y=14: closest beacon is at x=10, y=16
        #     Sensor at x=10, y=20: closest beacon is at x=10, y=16
        #     Sensor at x=14, y=17: closest beacon is at x=10, y=16
        #     Sensor at x=8, y=7: closest beacon is at x=2, y=10
        #     Sensor at x=2, y=0: closest beacon is at x=2, y=10
        #     Sensor at x=0, y=11: closest beacon is at x=2, y=10
        #     Sensor at x=20, y=14: closest beacon is at x=25, y=17
        #     Sensor at x=17, y=20: closest beacon is at x=21, y=22
        #     Sensor at x=16, y=7: closest beacon is at x=15, y=3
        #     Sensor at x=14, y=3: closest beacon is at x=15, y=3
        #     Sensor at x=20, y=1: closest beacon is at x=15, y=3
        # """

        def parse_positions(data: str) -> tuple[Vector, Vector]:
            match = re.findall('[xy]=([+-]?\\d+)', data.strip())
            sensor_x, sensor_y, beacon_x, beacon_y = list(map(int, match))
            return Vector(sensor_x, sensor_y), Vector(beacon_x, beacon_y)

        def create_devices(sensor_position: Vector, beacon_position: Vector) -> tuple[Device, Device]:
            beacon_distance = abs(beacon_position.x - sensor_position.x) + abs(beacon_position.y - sensor_position.y)
            sensor = Sensor(Vector(sensor_position.x, sensor_position.y), int(beacon_distance))
            beacon = Beacon(beacon_position)

            return sensor, beacon

        position_pairs = list(map(parse_positions, self.puzzle_input.strip().splitlines()))
        self.devices = set(flatten(starmap(create_devices, position_pairs)))

    def part1(self):
        row = 2000000
        combined_coverage = get_combined_coverage_at(row, devices=self.devices)

        devices_at_row = list(filter(lambda device: device.position.y == row, self.devices))
        covered_cells = sum(map(lambda interval: interval.length, combined_coverage))
        return covered_cells - len(devices_at_row)

    def part2(self):
        tuning_multiplier = 4000000
        search_interval = Interval(0, 4000001)

        beacon_finder = partial(find_distress_beacon_at, devices=self.devices, search_interval=search_interval)

        with ProcessPoolExecutor() as pool:
            for distress_beacon_position in pool.map(beacon_finder, search_interval, chunksize=10000):
                if not distress_beacon_position:
                    continue

                tuning_frequency = tuning_multiplier * distress_beacon_position.x + distress_beacon_position.y
                return tuning_frequency

        return "Not found"
