import random
from collections import deque

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)  # 0 = blank tile

MOVES = {
    0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
    3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
    6: [3, 7], 7: [4, 6, 8], 8: [5, 7],
}


def bfs(start):
    """Return list of states from start to goal, or None if unsolvable."""
    start = tuple(start)
    if start == GOAL:
        return [start]

    visited = {start: None}
    queue = deque([start])

    while queue:
        state = queue.popleft()
        blank = state.index(0)
        for neighbor in MOVES[blank]:
            new = list(state)
            new[blank], new[neighbor] = new[neighbor], new[blank]
            ns = tuple(new)
            if ns not in visited:
                visited[ns] = state
                if ns == GOAL:
                    path = []
                    cur = ns
                    while cur is not None:
                        path.append(cur)
                        cur = visited[cur]
                    return path[::-1]
                queue.append(ns)
    return None


def is_solvable(puzzle):
    """Count inversions to check solvability."""
    flat = [x for x in puzzle if x != 0]
    inv = sum(
        1
        for i in range(len(flat))
        for j in range(i + 1, len(flat))
        if flat[i] > flat[j]
    )
    return inv % 2 == 0


def random_puzzle():
    while True:
        tiles = list(range(9))
        random.shuffle(tiles)
        if is_solvable(tiles):
            return tiles
