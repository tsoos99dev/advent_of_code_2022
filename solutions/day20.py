from dataclasses import dataclass, field
from itertools import cycle, dropwhile
from typing import Optional

from calendar.calendar import Calendar
from itertoolsx import triplewise, take, nth


@dataclass
class MixerNode:
    number: int
    next_node: Optional['MixerNode'] = field(default=None, repr=False, compare=False)
    prev_node: Optional['MixerNode'] = field(default=None, repr=False, compare=False)


class MixerList:
    def __init__(self, numbers: list[int]):
        self.nodes = list(map(MixerNode, numbers))

        self.head = self.nodes[0]
        self.count = len(numbers)

        for prev_node, current_node, next_node in triplewise(take(self.count + 2, cycle(self.nodes))):
            current_node.prev_node = prev_node
            current_node.next_node = next_node

    def __iter__(self):
        current_node = self.head

        while True:
            yield current_node
            current_node = current_node.next_node

    def insert_before(self, node: MixerNode, new_node: MixerNode):
        temp = node.prev_node
        node.prev_node = new_node
        new_node.prev_node = temp

        new_node.next_node = node
        temp.next_node = new_node

    def insert_after(self, node: MixerNode, new_node: MixerNode):
        temp = node.next_node
        node.next_node = new_node
        new_node.next_node = temp

        new_node.prev_node = node
        temp.prev_node = new_node

    def remove(self, node: MixerNode):
        if self.head is node:
            self.head = node.next_node

        prev_node = node.prev_node
        next_node = node.next_node

        prev_node.next_node = next_node
        next_node.prev_node = prev_node

    def mix(self):
        for node in self.nodes:
            steps = abs(node.number) % (self.count - 1)
            if steps == 0:
                # print(list(take(self.count, map(lambda node: node.number, self))))
                continue

            self.remove(node)

            destination = node
            for _ in range(steps):
                destination = destination.next_node if node.number > 0 else destination.prev_node

            if node.number > 0:
                self.insert_after(destination, node)
            else:
                self.insert_before(destination, node)

            # print(list(take(self.count, map(lambda node: node.number, self))))


@Calendar.register(day=20)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        # self.puzzle_input = """
        #     1
        #     2
        #     -3
        #     3
        #     -2
        #     0
        #     4
        # """

        self.content = list(map(int, self.puzzle_input.strip().splitlines()))

    def part1(self):
        nodes = MixerList(self.content)
        print(list(take(len(self.content), map(lambda node: node.number, nodes))))
        nodes.mix()
        print(list(take(len(self.content), map(lambda node: node.number, nodes))))

        node1 = nth(dropwhile(lambda node: node.number != 0, nodes), 1000)
        node2 = nth(dropwhile(lambda node: node.number != 0, nodes), 2000)
        node3 = nth(dropwhile(lambda node: node.number != 0, nodes), 3000)

        return node1.number + node2.number + node3.number

    def part2(self):
        decryption_key = 811589153
        decrypted_content = list(map(lambda number: decryption_key * number, self.content))

        nodes = MixerList(decrypted_content)
        print(list(take(len(self.content), map(lambda node: node.number, nodes))))

        for _ in range(10):
            nodes.mix()
            print(list(take(len(self.content), map(lambda node: node.number, nodes))))

        node1 = nth(dropwhile(lambda node: node.number != 0, nodes), 1000)
        node2 = nth(dropwhile(lambda node: node.number != 0, nodes), 2000)
        node3 = nth(dropwhile(lambda node: node.number != 0, nodes), 3000)

        return node1.number + node2.number + node3.number
