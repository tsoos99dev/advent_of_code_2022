import queue
import re
from dataclasses import dataclass, field
from functools import reduce
from itertools import starmap, count
from queue import Queue, PriorityQueue

from calendar.calendar import Calendar
from itertoolsx import iter_except
from search import a_star


@dataclass(order=True)
class ScoredValvePermutation:
    open_valves: list[tuple[str, int]] = field(compare=False)
    score: int


@Calendar.register(day=16)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
        #     Valve BB has flow rate=13; tunnels lead to valves CC, AA
        #     Valve CC has flow rate=2; tunnels lead to valves DD, BB
        #     Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
        #     Valve EE has flow rate=3; tunnels lead to valves FF, DD
        #     Valve FF has flow rate=0; tunnels lead to valves EE, GG
        #     Valve GG has flow rate=0; tunnels lead to valves FF, HH
        #     Valve HH has flow rate=22; tunnel leads to valve GG
        #     Valve II has flow rate=0; tunnels lead to valves AA, JJ
        #     Valve JJ has flow rate=21; tunnel leads to valve II
        # """

        self.layout: dict[str, list[str]] = {}
        self.valves: dict[str, int] = {}

        def parse_valve(data: str):
            match = re.findall('Valve(.*)has.*rate=(.*);.*valves?(.*)', data)
            if not match:
                raise ValueError("Invalid valve input string")

            valve_id, flow_rate, neighbours = match[0]
            valve_id = valve_id.strip()
            flow_rate = int(flow_rate)
            neighbours = list(map(lambda neighbour: neighbour.strip(), neighbours.split(',')))

            self.valves[valve_id] = flow_rate
            self.layout[valve_id] = neighbours

        lines = self.puzzle_input.strip().splitlines()
        for line in lines:
            parse_valve(line)

    def calculate_released_pressure(self, after: int, open_valves: list[tuple[str, int]]):
        return sum(starmap(
            lambda valve_id, released_at: self.valves[valve_id] * max(0, after - released_at),
            open_valves)
        )

    def find_shortest_distance(self, start: str, end: str) -> int:
        result = a_star(
            start, end,
            lambda valve_id: self.layout[valve_id],
            lambda valve_id: 0,
            lambda valve1, valve2: 1
        )
        return int(result.length)

    def find_best_permutation_before(self, end: int, first_valve: str, workers: int):
        pressurized_valves = list(
            map(
                lambda valve_data: valve_data[0],
                sorted(
                    filter(lambda valve_data: valve_data[1] != 0, self.valves.items()),
                    key=lambda valve_data: valve_data[1],
                    reverse=True
                )
            )
        )

        distances: dict[tuple[str, str], int] = {}

        expand_queue: PriorityQueue[ScoredValvePermutation] = PriorityQueue()
        prune_queue: PriorityQueue[ScoredValvePermutation] = PriorityQueue()

        expand_queue.put_nowait(ScoredValvePermutation([(first_valve, 0)], 0))
        best_permutation = []
        best_score = 0

        while not expand_queue.empty():
            for permutation in iter_except(expand_queue.get_nowait, queue.Empty):
                last_valve, total_time = permutation.open_valves[-1]

                open_valve_ids = list(starmap(lambda valve_id, _: valve_id, permutation.open_valves))
                remaining_valves = list(filter(
                    lambda valve_data: valve_data not in open_valve_ids,
                    pressurized_valves
                ))

                for valve_id in remaining_valves:
                    distance = distances.get((last_valve, valve_id), None)
                    if distance is None:
                        distance = self.find_shortest_distance(last_valve, valve_id)
                        distances[last_valve, valve_id] = distance
                        distances[valve_id, last_valve] = distance

                    new_total_time = total_time + distance + 1

                    if new_total_time >= 30:
                        continue

                    new_open_valves = permutation.open_valves + [(valve_id, new_total_time)]
                    released = self.calculate_released_pressure(after=end, open_valves=new_open_valves)

                    if released > best_score:
                        best_score = released
                        best_permutation = new_open_valves

                    prune_queue.put_nowait(
                        ScoredValvePermutation(open_valves=new_open_valves, score=-released)
                    )

            max_ideal_pressure_released = 0
            for permutation in iter_except(prune_queue.get_nowait, queue.Empty):
                last_valve, total_time = permutation.open_valves[-1]
                current_pressure_released = -permutation.score

                open_valve_ids = list(starmap(lambda valve_id, _: valve_id, permutation.open_valves))
                remaining_valves = list(filter(
                    lambda valve_data: valve_data not in open_valve_ids,
                    pressurized_valves
                ))

                ideal_pressure_released = self.calculate_released_pressure(
                    after=end,
                    open_valves=list(zip(remaining_valves, count(total_time + 2, 2)))
                )

                if ideal_pressure_released + current_pressure_released < max_ideal_pressure_released:
                    break

                expand_queue.put_nowait(permutation)
                print(permutation, remaining_valves, ideal_pressure_released + current_pressure_released)

        return best_permutation, best_score

    def part1(self):
        best_permutation, score = self.find_best_permutation_before(end=30, first_valve='AA', workers=1)
        print(best_permutation, score, {valve_id: self.valves[valve_id] for valve_id, t in best_permutation})

    def part2(self):
        # best_permutation, score = self.find_best_permutation_before(end=26, first_valve='AA', workers=2)
        # print(best_permutation, score, {valve_id: self.valves[valve_id] for valve_id, t in best_permutation})
        ...
