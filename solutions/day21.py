import asyncio
import operator
from asyncio import Future
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import permutations
from typing import Callable, Optional, Protocol

from calendar.calendar import Calendar
from itertoolsx import first


class Expression(Protocol):
    def evaluate(self) -> Fraction:
        ...

    def solve_for(self, unknown: 'Expression', given: Optional['Expression'] = None) -> Optional[Fraction]:
        ...


@dataclass
class NumericExpression:
    number: Fraction

    def evaluate(self) -> Fraction:
        return self.number

    def solve_for(self, unknown: Expression, given: Optional[Expression] = None) -> Optional[Fraction]:
        if self is not unknown:
            return None

        if given is None:
            return None

        return given.evaluate()


class Operation(Protocol):
    def __call__(self, *args: Expression) -> Expression:
        ...


UnaryOperator = Callable[[Fraction], Fraction]


@dataclass
class UnaryOperatorExpression:
    operator: UnaryOperator
    operand: Expression = field(repr=False)

    def evaluate(self) -> Fraction:
        return self.operator(self.operand.evaluate())

    def solve_for(self, unknown: Expression, given: Optional[Expression] = None) -> Optional[Fraction]:
        if given is None:
            return None

        if self is not unknown:
            return self.operand.solve_for(unknown, UnaryOperatorExpression(self.operator, given))

        return given.evaluate()


BinaryOperator = Callable[[Fraction, Fraction], Fraction]


@dataclass
class BinaryOperatorExpression:
    operator: BinaryOperator
    operands: tuple[Expression, Expression] = field(repr=False)
    inverse: Operation

    def evaluate(self) -> Fraction:
        return self.operator(*map(lambda operand: operand.evaluate(), self.operands))

    def solve_for(self, unknown: Expression, given: Optional[Expression] = None) -> Optional[Fraction]:
        if self is not unknown:
            return first(
                map(lambda operands: operands[0].solve_for(
                    unknown,
                    given=BinaryOperatorExpression(
                        self.operator,
                        (given, self.inverse(operands[1])),
                        self.inverse
                    ) if given is not None else operands[1]),
                    permutations(self.operands)
                ),
                default=None,
                pred=lambda solution: solution is not None
            )

        if given is None:
            return None

        return given.evaluate()


@Calendar.register(day=21)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     root: pppw + sjmn
        #     dbpl: 5
        #     cczh: sllz + lgvd
        #     zczc: 2
        #     ptdq: humn - dvpt
        #     dvpt: 3
        #     lfqf: 4
        #     humn: 5
        #     ljgn: 2
        #     sjmn: drzm * dbpl
        #     sllz: 4
        #     pppw: cczh / lfqf
        #     lgvd: ljgn * ptdq
        #     drzm: hmdt - zczc
        #     hmdt: 32
        # """

        def additive_inverse(operand: Expression) -> Expression:
            return UnaryOperatorExpression(operator.neg, operand)

        def multiplicative_inverse(operand: Expression) -> Expression:
            return UnaryOperatorExpression(lambda a: 1 / a, operand)

        def addition(left: Expression, right: Expression) -> Expression:
            return BinaryOperatorExpression(operator.add, (left, right), additive_inverse)

        def multiplication(left: Expression, right: Expression) -> Expression:
            return BinaryOperatorExpression(operator.mul, (left, right), multiplicative_inverse)

        operators = {
            '+': addition,
            '-': lambda left, right: addition(left, additive_inverse(right)),
            '*': multiplication,
            '/': lambda left, right: multiplication(left, multiplicative_inverse(right)),
        }

        expressions: dict[str, Future[Expression]] = {}

        async def parse_expression(data: str) -> None:
            match data.strip().split(' '):
                case [raw_id, raw_number]:
                    expression_id = raw_id.strip(':')
                    number = int(raw_number)
                    future = expressions.setdefault(expression_id, Future())
                    future.set_result(NumericExpression(Fraction(number)))
                case [raw_id, left_operand, operator_symbol, right_operand]:
                    expression_id = raw_id.strip(':')
                    operator_builder = operators[operator_symbol]
                    left_expression = await expressions.setdefault(left_operand, Future())
                    right_expression = await expressions.setdefault(right_operand, Future())
                    future = expressions.setdefault(expression_id, Future())
                    future.set_result(operator_builder(left_expression, right_expression))

        content = self.puzzle_input.strip().splitlines()
        asyncio.run(asyncio.wait(map(parse_expression, content)))
        self.expressions: dict[str, Expression] = {
            expression_id: future.result()
            for expression_id, future in expressions.items()
        }

    def part1(self):
        root = self.expressions['root']
        result = root.evaluate()
        return result

    def part2(self):
        human = self.expressions['humn']
        root = self.expressions['root']
        result = root.solve_for(human)

        # Check result

        human.number = result
        root.operator = operator.sub

        assert root.evaluate() == 0

        return result





