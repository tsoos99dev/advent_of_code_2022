import math
from abc import abstractmethod
from asyncio import Protocol
from collections import deque
from dataclasses import dataclass, field
from queue import PriorityQueue, Empty
from typing import Iterable, TypeVar, Callable

from itertoolsx import iter_except


Node = TypeVar("Node")


@dataclass
class PathNotFoundError(Exception):
    start: Node
    end: Node

    def __str__(self):
        return f"No path exists between {self.start} and {self.end}"


@dataclass(order=True)
class ScoredNode:
    f_score: float
    node: Node = field(compare=False)


def reconstruct_path(came_from: dict[Node, Node], current: Node) -> list[Node]:
    path = deque()

    while current in came_from:
        current = came_from[current]
        path.appendleft(current)

    return list(path)


def a_star(
        start: Node,
        goal: Node,
        neighbours: Callable[[Node], Iterable[Node]],
        heuristic: Callable[[Node], float],
        distance: Callable[[Node, Node], float]
) -> list[Node]:
    open_set: PriorityQueue[ScoredNode] = PriorityQueue()
    open_set.put_nowait(ScoredNode(heuristic(start), start))

    came_from: dict[Node, Node] = {}
    g_score = {start: 0}

    for current_scored_node in iter_except(open_set.get_nowait, Empty):
        current_node = current_scored_node.node
        if current_node is goal:
            return reconstruct_path(came_from, current_node)

        for neighbour in neighbours(current_node):
            tentative_g_score = g_score.get(current_node, math.inf) + distance(current_node, neighbour)
            if tentative_g_score >= g_score.get(neighbour, math.inf):
                continue

            came_from[neighbour] = current_node
            g_score[neighbour] = tentative_g_score
            f_score = tentative_g_score + heuristic(neighbour)
            scored_neighbour = ScoredNode(f_score, neighbour)

            if neighbour in map(lambda scored: scored.node, open_set.queue):
                continue

            open_set.put_nowait(scored_neighbour)

    raise PathNotFoundError(start, goal)