from dataclasses import dataclass
from functools import reduce, partial
from itertools import cycle, accumulate, pairwise, starmap
from typing import Iterable, Protocol

import mathx
from calendar.calendar import Calendar
from itertoolsx import take
from mathx import Vector


class Action(Protocol):
    def apply(self, position: Vector) -> Vector:
        ...


class FallDownAction:
    def apply(self, position: Vector) -> Vector:
        return position + Vector(0, -1)


@dataclass
class JetPushAction:
    push: Vector

    def apply(self, position: Vector) -> Vector:
        return position + self.push


@Calendar.register(day=17)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>"

        self.shapes = (
            [
                0b11110000
            ],
            [
                0b01000000,
                0b11100000,
                0b01000000
            ],
            [
                0b11100000,
                0b00100000,
                0b00100000
            ],
            [
                0b10000000,
                0b10000000,
                0b10000000,
                0b10000000
            ],
            [
                0b11000000,
                0b11000000
            ]
        )

    def jet_shape_to_vector(self, shape: str) -> Vector:
        match shape:
            case '>':
                return Vector(1, 0)
            case '<':
                return Vector(-1, 0)

        raise ValueError("Incorrect jet shape")

    def check_collision(self, position: Vector, shape: list[int], world_state: list[int]):
        if position.x < 0 or position.y < 0:
            return True

        for row_ind, row in enumerate(shape):
            wold_row = row >> int(position.x)
            if wold_row & 1:
                return True

            if wold_row & world_state[int(position.y) + row_ind]:
                return True

        return False

    def apply_action(self, position: Vector, action: Action, *_, shape: list[int], world_state: list[int]) -> Vector:
        new_position = action.apply(position)
        if self.check_collision(new_position, shape, world_state):
            return position

        return new_position

    def simulate_round(self, position: Vector, actions: Iterable[Action], *_, shape: list[int], world_state: list[int]) -> tuple[Vector, Vector]:
        prev_position = None
        current_position = position

        for action in actions:
            prev_position = current_position
            current_position = self.apply_action(current_position, action, shape=shape, world_state=world_state)

        return prev_position, current_position

    def simulate_sequence(self, top_line: int, shape: list[int], *_, actions: Iterable[Iterable[Action]], world_state: list[int]) -> int:
        current_position = Vector(2, top_line + 4)

        if len(world_state) < top_line + 100:
            world_state.extend([0b00000000]*100)

        for round_actions in actions:
            prev_position, new_position = self.simulate_round(current_position, round_actions, shape=shape, world_state=world_state)
            current_position = new_position

            if prev_position == new_position:
                break

        for row_ind, row in enumerate(shape):
            world_state[int(current_position.y) + row_ind] |= row >> int(current_position.x)

        # for row in reversed(world_state):
        #     print(f"{row:08b}")
        #
        # print()

        potential_top_line = int(current_position.y) + len(shape) - 1
        new_top_line = max(top_line, potential_top_line)

        return new_top_line

    def simulate(self, rounds: int):
        jet_pattern = map(self.jet_shape_to_vector, cycle(self.puzzle_input.strip()))
        shape_pattern = cycle(self.shapes)

        world_state: list[int] = [0b11111111]
        actions = map(
            lambda push: [
                JetPushAction(push),
                FallDownAction()
            ],
            jet_pattern
        )

        return accumulate(
            take(rounds, shape_pattern),
            partial(self.simulate_sequence, actions=actions, world_state=world_state),
            initial=0
        )

    def find_cycle(self, it: list[int]):
        cycle_length = 0

        for i in range(1, len(it) // 2):
            if it[-i:] != it[-2 * i:-i]:
                continue

            cycle_length = i
            break

        for i in range(len(it) - cycle_length):
            if it[i: i + cycle_length] != it[i + cycle_length:i + 2 * cycle_length]:
                continue

            return i, cycle_length

        return None

    def part1(self):
        top_lines = list(self.simulate(2022))
        return top_lines[-1]

    def part2(self):
        rounds = 1000000000000
        top_lines = list(self.simulate(5000))
        differences = list(starmap(lambda l1, l2: l2 - l1, pairwise(top_lines)))
        start_ind, cycle_length = self.find_cycle(differences)

        whole_cycles, remaining_rounds = divmod(rounds - start_ind, cycle_length)

        transition_increment = top_lines[start_ind]
        cycle_top_line_increment = whole_cycles * (top_lines[start_ind + cycle_length] - top_lines[start_ind])
        remaining_increment = sum(differences[start_ind: start_ind + remaining_rounds])

        return transition_increment + cycle_top_line_increment + remaining_increment


