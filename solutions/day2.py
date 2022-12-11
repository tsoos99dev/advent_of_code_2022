from dataclasses import dataclass

from calendar.calendar import Calendar
from itertoolsx import triplewise

from enum import Enum
from itertools import product, cycle, chain, islice


class Outcomes(Enum):
    LOSE = 0
    DRAW = 3
    WIN = 6


class OpponentShapes(Enum):
    A = 1
    B = 2
    C = 3


class MyShapes(Enum):
    X = 1
    Y = 2
    Z = 3


@Calendar.register(day=2)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.strategy_guide = self.puzzle_input.splitlines()

    def part1(self):
        guessed_outcomes = map(
            lambda strategy, outcome: chain(strategy, [outcome]),
            product(OpponentShapes, MyShapes),
            chain.from_iterable(map(reversed, triplewise(islice(cycle(reversed(Outcomes)), 2, None))))
        )

        guessed_scores = {
            f"{opponent_shape.name} {my_shape.name}": my_shape.value + outcome.value
            for opponent_shape, my_shape, outcome in guessed_outcomes
        }

        return sum(guessed_scores[round] for round in self.strategy_guide)

    def part2(self):
        actual_outcomes = map(
            lambda strategy, my_shape, outcome: chain(strategy, [my_shape, outcome]),
            product(OpponentShapes, MyShapes),
            chain.from_iterable(triplewise(islice(cycle(MyShapes), 2, None))),
            cycle(Outcomes)
        )

        actual_scores = {
            f"{opponent_shape.name} {encrypted_outcome.name}": my_shape.value + outcome.value
            for opponent_shape, encrypted_outcome, my_shape, outcome in actual_outcomes
        }

        return sum(actual_scores[round] for round in self.strategy_guide)

