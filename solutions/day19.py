import operator
import queue
import re
from dataclasses import dataclass
from functools import reduce
from itertools import starmap
from queue import Queue

from calendar.calendar import Calendar
from itertoolsx import iter_except, dotproduct

ResourceGroup = tuple[int, int, int, int]
Action = tuple[int, int]
Strategy = tuple[Action, ...]
Blueprint = tuple[ResourceGroup, ResourceGroup, ResourceGroup, ResourceGroup]


@Calendar.register(day=19)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        # Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian.
        # Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian.
        # """

        def parse_blueprint(data: str) -> tuple[int, Blueprint]:
            match = re.findall("(\\d+)", data.strip())
            blueprint_id, \
            ore_robot_ore_cost, \
            clay_robot_ore_cost, \
            obsidian_robot_ore_cost, \
            obsidian_robot_clay_cost, \
            geode_robot_ore_cost, \
            geode_robot_obsidian_cost = list(map(int, match))

            return (
                blueprint_id,
                (
                    (ore_robot_ore_cost, 0, 0, 0),
                    (clay_robot_ore_cost, 0, 0, 0),
                    (obsidian_robot_ore_cost, obsidian_robot_clay_cost, 0, 0),
                    (geode_robot_ore_cost, 0, geode_robot_obsidian_cost, 0)
                )
            )

        self.blueprints = dict(map(parse_blueprint, self.puzzle_input.strip().splitlines()))

    def simulate(self, strategy: Strategy, blueprint: Blueprint, minutes: int) -> ResourceGroup:
        resources = [minutes, 0, 0, 0]

        for robot_id, build_time in strategy:
            gain = minutes - build_time
            cost = blueprint[robot_id]

            resources[robot_id] += gain
            resources = list(map(operator.sub, resources, cost))

        return tuple(resources)

    def get_possible_actions(self, strategy: Strategy, blueprint: Blueprint, minutes: int) -> tuple[Action, ...]:
        last_build_time = strategy[-1][-1] if strategy else 0
        resources = self.simulate(strategy, blueprint, last_build_time)
        possible_actions: dict[int, int] = {}

        for current_minute in range(last_build_time + 1, minutes):
            for robot_id, costs in enumerate(blueprint):
                if robot_id in possible_actions:
                    continue

                if not all(cost <= resource for cost, resource in zip(costs, resources)):
                    continue

                possible_actions[robot_id] = current_minute

            resources = self.simulate(strategy, blueprint, current_minute)
            # print(resources)

        return tuple(map(lambda item: tuple(item), possible_actions.items()))

    def find_max_geodes(self, blueprint: Blueprint, minutes: int):
        points = (1, 10, 100, 1000)

        hot_strategies: Queue[Strategy] = Queue()
        hot_strategies.put_nowait(tuple())

        max_geodes = 0
        best_strategies: dict[tuple[Action, ...], int] = {}

        for strategy in iter_except(hot_strategies.get_nowait, queue.Empty):
            resources = self.simulate(strategy, blueprint, minutes)

            if resources[3] > max_geodes:
                max_geodes = resources[3]
                # print(f"Max geodes cracked: {max_geodes} with strategy: {strategy}")

            possible_actions = self.get_possible_actions(strategy, blueprint, minutes)

            strategy_score = dotproduct(resources, points)
            best_score = best_strategies.get(possible_actions, 0)

            if strategy_score <= best_score:
                continue

            best_strategies[possible_actions] = strategy_score

            # print(f"{strategy} | {resources} | {possible_actions}")

            for possible_action in possible_actions:
                new_strategy = tuple([*strategy, possible_action])
                hot_strategies.put_nowait(new_strategy)

        return max_geodes

    def part1(self):
        total_quality_level = 0

        for blueprint_id, blueprint in self.blueprints.items():
            print(f"Evaluating blueprint {blueprint_id}...")
            max_geodes = self.find_max_geodes(blueprint, 24)
            print(f"Max geodes cracked: {max_geodes}")

            quality_level = blueprint_id * max_geodes
            total_quality_level += quality_level

        return total_quality_level

    def part2(self):
        max_geodes = list(map(
            lambda blueprint: self.find_max_geodes(blueprint, 32),
            list(self.blueprints.values())[:3]
        ))
        print(max_geodes)
        return reduce(operator.mul, max_geodes)

