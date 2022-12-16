from calendar.calendar import Calendar


def main():
    solution = Calendar.get(day=15)

    print(solution.part1())
    print(solution.part2())


if __name__ == '__main__':
    main()