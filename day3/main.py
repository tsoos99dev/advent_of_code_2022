from enum import Enum
from functools import reduce
from itertools import product, cycle, tee, islice, groupby

from collections import deque
from pprint import pprint
from typing import Iterable


def get_priority(item: str):
    return ord(item) - ord('a') + 1 if item.islower() else ord(item) - ord('A') + 27


def chunks(i: Iterable, n: int = 1):
    yield from map(
        lambda key_group: map(lambda ind_item: ind_item[1], key_group[1]),
        groupby(
            enumerate(i),
            lambda ind_item: ind_item[0] - ind_item[0] % n)
    )


def main():
    with open('input.txt', encoding='utf-8') as file:
        rucksacks = file.read().splitlines()

        # Part 1
        misplaced_items = [
            reduce(lambda a, b: a.intersection(b), map(set, chunks(rucksack, len(rucksack) // 2))).pop()
            for rucksack in rucksacks
        ]

        print(sum(get_priority(item) for item in misplaced_items))

        # Part 2
        badges = [
            reduce(lambda a, b: a.intersection(b), map(set, group)).pop()
            for group in chunks(rucksacks, 3)
        ]

        print(sum(get_priority(badge) for badge in badges))


if __name__ == '__main__':
    main()