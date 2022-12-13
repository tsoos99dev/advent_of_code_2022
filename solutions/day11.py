import operator
from collections import deque
from dataclasses import dataclass, field
from functools import reduce
from itertools import repeat, count
from typing import Iterable, Callable, Protocol

from calendar.calendar import Calendar
from itertoolsx import isplit, iter_except


class WorryBehaviour(Protocol):
    def update_level_of_worry(self,worry_level: int) -> int:
        ...


class FadingWorryBehaviour:
    def update_level_of_worry(self,worry_level: int) -> int:
        return worry_level // 3


@dataclass
class ModularWorryBehaviour:
    modulus: int

    def update_level_of_worry(self, worry_level: int) -> int:
        return worry_level % self.modulus


class Inspectable(Protocol):
    def inspect(self, operation: Callable[[int], int]) -> int:
        ...


@dataclass(frozen=True)
class Item:
    index: int
    inspection_notifier: Callable[[Callable[[int], int], int], int]

    def inspect(self, operation: Callable[[int], int]) -> int:
        return self.inspection_notifier(operation, self.index)


@dataclass
class Person:
    worry_levels: dict[int, int] = field(default_factory=dict)
    worry_behavior: WorryBehaviour = field(default_factory=FadingWorryBehaviour)

    def __post_init__(self):
        self.item_index_generator = count()

    def create_item(self, worry_level: int) -> Item:
        item_ind = next(self.item_index_generator)
        self.worry_levels[item_ind] = worry_level
        return Item(item_ind, self.witness_inspection)

    def witness_inspection(self, operation: Callable[[int], int], item_ind: int):
        current_worry_level = self.worry_levels[item_ind]
        worry_level_after_operation = operation(current_worry_level)
        worry_level_after_inspection = self.worry_behavior.update_level_of_worry(worry_level_after_operation)
        self.worry_levels[item_ind] = worry_level_after_inspection
        return worry_level_after_inspection


@dataclass
class Monkey:
    items: deque[Item]
    operation: Callable[[int], int]
    modulus: int
    test_passed_throw_handler: Callable[[Item], None]
    test_failed_throw_handler: Callable[[Item], None]

    def inspect_items(self) -> int:
        number_of_inspected_items = 0
        for item in iter_except(self.items.popleft, IndexError):
            worry_level_after_inspection = item.inspect(self.operation)

            throw_handler = self.test_passed_throw_handler if worry_level_after_inspection % self.modulus == 0 else self.test_failed_throw_handler
            throw_handler(item)

            number_of_inspected_items += 1

        return number_of_inspected_items

    def receive(self, item: Item):
        self.items.append(item)


@Calendar.register(day=11)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.monkey_data = list(isplit(self.puzzle_input.strip().splitlines(), ''))

    def parse_monkey(self, iam: Person, monkey_data: Iterable[str], monkey_getter: Callable[[int], Monkey]) -> tuple[int, Monkey]:
        monkey_data_iter = iter(monkey_data)

        # Parse index
        index_row = next(monkey_data_iter)
        ind = int(index_row.strip(': ').split(' ')[1])

        # Parse starting items
        items_row = next(monkey_data_iter)
        worry_levels = map(int, items_row.split(':')[1].split(','))
        items = deque(map(lambda worry_level: iam.create_item(worry_level), worry_levels))

        # Parse operation
        operators = {
            '+': operator.add,
            '*': operator.mul,
        }
        operation_row = next(monkey_data_iter)
        left_operand, operator_symbol, right_operand = operation_row.split('=')[1].strip().split(' ')
        operation = lambda worry_level: operators[operator_symbol](
            worry_level if left_operand == 'old' else int(left_operand),
            worry_level if right_operand == 'old' else int(right_operand)
        )

        # Parse test
        test_row = next(monkey_data_iter)
        modulus = int(test_row.split('by')[1])

        # Parse index of the monkey to throw the item to when the test passes
        test_passed_row = next(monkey_data_iter)
        test_passed_throw_ind = int(test_passed_row.split('monkey')[1])
        test_passed_throw_handler = lambda item: monkey_getter(test_passed_throw_ind).receive(item)

        # Parse index of the monkey to throw the item to when the test passes
        test_failed_row = next(monkey_data_iter)
        test_failed_throw_ind = int(test_failed_row.split('monkey')[1])
        test_failed_throw_handler = lambda item: monkey_getter(test_failed_throw_ind).receive(item)

        return ind, Monkey(items, operation, modulus, test_passed_throw_handler, test_failed_throw_handler)

    def create_monkeys(self, iam: Person):
        monkeys = {}
        for monkey_data in self.monkey_data:
            monkey_ind, monkey = self.parse_monkey(iam, monkey_data, lambda monkey_ind: monkeys[monkey_ind])
            monkeys[monkey_ind] = monkey

        return monkeys

    def get_monkey_business(self, monkeys: Iterable[Monkey], n: int):
        rounds = repeat(monkeys, n)
        inspection_counts = map(lambda round: list(map(lambda monkey: monkey.inspect_items(), round)), rounds)
        total_inspection_counts = sorted(map(sum, zip(*inspection_counts)), reverse=True)
        return reduce(operator.mul, total_inspection_counts[:2])

    def part1(self):
        iam = Person()
        iam.worry_behavior = FadingWorryBehaviour()
        monkeys = self.create_monkeys(iam)

        return self.get_monkey_business(monkeys.values(), 20)

    def part2(self):
        iam = Person()
        monkeys = self.create_monkeys(iam)
        combined_modulus = reduce(operator.mul, map(lambda monkey: monkey.modulus, monkeys.values()))
        iam.worry_behavior = ModularWorryBehaviour(combined_modulus)

        return self.get_monkey_business(monkeys.values(), 10000)
