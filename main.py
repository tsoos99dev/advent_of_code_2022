from pprint import pprint

from calendar.calendar import Calendar


def main():
    solution = Calendar.get(day=9)

    pprint(solution.part1())
    pprint(solution.part2())


if __name__ == '__main__':
    main()