import builtins
import operator
from collections import deque
from dataclasses import dataclass
from functools import cmp_to_key, reduce
from itertools import chain, starmap
from typing import Iterable, Optional

from calendar.calendar import Calendar
from itertoolsx import isplit, iter_except, first, iter_index, flatten, prepend


@Calendar.register(day=13)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     [1,1,3,1,1]
        #     [1,1,5,1,1]
        #
        #     [[1],[2,3,4]]
        #     [[1],4]
        #
        #     [9]
        #     [[8,7,6]]
        #
        #     [[4,4],4,4]
        #     [[4,4],4,4,4]
        #
        #     [7,7,7,7]
        #     [7,7,7]
        #
        #     []
        #     [3]
        #
        #     [[[]]]
        #     [[]]
        #
        #     [1,[2,[3,[4,[5,6,7]]]],8,9]
        #     [1,[2,[3,[4,[5,6,0]]]],8,9]
        # """

        def process(packet: Iterable[str]) -> list:
            buffer = deque()

            def process_buffer():
                content = "".join(iter_except(buffer.popleft, IndexError)).strip()
                if not content:
                    return

                yield int(content)

            for character in packet:
                match character:
                    case '[':
                        yield list(process(packet))
                    case ',':
                        yield from process_buffer()
                    case ']':
                        yield from process_buffer()
                        break
                    case other:
                        buffer.append(other)

        pairs = isplit(map(lambda line: line.strip(), self.puzzle_input.strip().splitlines()), '')
        self.packets = list(map(lambda pair: list(process(chain.from_iterable(pair))), pairs))

    def compare_packets(self, left: list, right: list) -> int:
        def compare_values(_left, _right) -> int:
            match [type(_left), type(_right)]:
                case [builtins.int, builtins.int]:
                    if _left == _right:
                        return 0

                    return -1 if _left < _right else 1
                case [builtins.int, builtins.list]:
                    return self.compare_packets([_left], _right)
                case [builtins.list, builtins.int]:
                    return self.compare_packets(_left, [_right])
                case [builtins.list, builtins.list]:
                    return self.compare_packets(_left, _right)

        first_match = first(
            starmap(compare_values, zip(left, right)),
            default=None,
            pred=lambda result: result != 0
        )

        if first_match is not None:
            return first_match

        if len(left) == len(right):
            return 0

        return -1 if len(left) < len(right) else 1

    def part1(self):
        return sum(index + 1 for index in iter_index((starmap(self.compare_packets, self.packets)), -1))

    def part2(self):
        divider_packets = [[[2]], [[6]]]
        sorted_packets = sorted(flatten(prepend(divider_packets, self.packets)), key=cmp_to_key(self.compare_packets))
        return reduce(operator.mul, map(lambda divider: sorted_packets.index(divider) + 1, divider_packets))