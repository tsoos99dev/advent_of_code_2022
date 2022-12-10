from enum import Enum
from itertools import product, cycle
from collections import deque
from pprint import pprint
from typing import Iterable


class Outcomes(Enum):
    DRAW = 3
    WIN = 6
    LOSE = 0


def rotate(iter: Iterable, n: int = 1):
    d = deque(iter)
    while True:
        for item in d:
            yield item

        d.rotate(n)


def main():
    with open('input.txt', encoding='utf-8') as file:
        strategy_guide = file.read().splitlines()

        # Part 1
        scores = {
            f"{strategy[0]} {strategy[1]}": ord(strategy[1]) - ord('X') + 1 + outcome.value
            for strategy, outcome in zip(
                product("ABC", "XYZ"),
                rotate([Outcomes.DRAW, Outcomes.WIN, Outcomes.LOSE])
            )
        }

        print(sum(scores[round] for round in strategy_guide))

        # Part 2
        scores = {
            f"{strategy[0]} {strategy[1]}": ord(my_shape) - ord('X') + 1 + outcome.value
            for strategy, my_shape, outcome in zip(
                product("ABC", "XYZ"),
                rotate("ZXY", n=-1),
                cycle([Outcomes.LOSE, Outcomes.DRAW, Outcomes.WIN])
            )
        }

        print(sum(scores[round] for round in strategy_guide))


if __name__ == '__main__':
    main()