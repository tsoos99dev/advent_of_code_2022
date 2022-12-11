from typing import Protocol, Any, Callable


class Solution(Protocol):
    def part1(self) -> Any:
        ...

    def part2(self) -> Any:
        ...


SolutionTemplate = Callable[[str], Solution]


class Calendar:
    solutions: dict[int, SolutionTemplate] = {}

    @classmethod
    def get(cls, day: int):
        solution = cls.solutions.get(day, None)

        if solution is None:
            raise KeyError(f"There isn't a solution for day {day}")

        with open(f"inputs/input{day}.txt", encoding='utf-8') as file:
            puzzle_input = file.read()

        return solution(puzzle_input)

    @classmethod
    def register(cls, day: int):
        def wrapper(template: SolutionTemplate):
            cls.solutions[day] = template

        return  wrapper


