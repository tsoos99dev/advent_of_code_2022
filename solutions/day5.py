from dataclasses import dataclass
from itertools import dropwhile, compress
from collections import deque

from calendar.calendar import Calendar
from itertoolsx import isplit, batched


@Calendar.register(day=5)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        stacks_raw, moves_raw = isplit(self.puzzle_input.splitlines(), '')

        stack_info = list(map(lambda stack: list(map(lambda crate: crate[1], batched(stack, 4))), stacks_raw))
        self.stack_ids, rows = stack_info[-1], stack_info[:-1]

        self.crate_stacks = list(map(lambda crate_stack: list(dropwhile(lambda crate: crate == ' ', crate_stack)), zip(*rows)))

        self.moves = list(map(lambda move_raw: list(map(int, compress(move_raw.split(' '), [0, 1, 0, 1, 0, 1]))), moves_raw))

    @property
    def stacks(self):
        return {
            int(stack_ids): deque(stack)
            for stack_ids, stack in zip(self.stack_ids, self.crate_stacks)
        }

    def part1(self):
        stacks = self.stacks

        def move_crates_9000(n, source, dest):
            for _ in range(n):
                crate = stacks[source].popleft()
                stacks[dest].appendleft(crate)

        for move in self.moves:
            move_crates_9000(*move)

        return "".join(map(lambda stack: stack.popleft(), stacks.values()))

    def part2(self):
        stacks = self.stacks

        def move_crates_9001(n, source, dest):
            temp = deque()
            for _ in range(n):
                crate = stacks[source].popleft()
                temp.append(crate)

            for _ in range(n):
                crate = temp.pop()
                stacks[dest].appendleft(crate)

        for move in self.moves:
            move_crates_9001(*move)

        return "".join(map(lambda stack: stack.popleft(), stacks.values()))


