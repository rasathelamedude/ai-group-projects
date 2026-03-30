"""
puzzle_algorithm.py — Member 1
Best-First Search algorithm with Manhattan Distance heuristic.
"""

import heapq
from puzzle_board import GOAL, GOAL_POS, neighbors


def manhattan_distance(state: tuple) -> int:
    """
    Compute the Manhattan Distance heuristic for a given puzzle state.

    For each non-blank tile, sum the horizontal + vertical distances
    between its current position and its goal position.

    This is an admissible heuristic (never overestimates), making
    Best-First Search complete for solvable puzzles.
    """
    total = 0
    for index, tile in enumerate(state):
        if tile != 0:  # skip the blank
            current_row, current_col = divmod(index, 3)
            goal_row, goal_col = GOAL_POS[tile]
            total += abs(current_row - goal_row) + abs(current_col - goal_col)
    return total


def best_first_search(start: tuple):
    """
    Solve the 8-puzzle from ``start`` using Best-First Search.

    The priority queue is ordered by h(n) = Manhattan Distance only
    (greedy best-first — not A*).  Each move costs 1.

    Returns:
        (path, cost)  where path = [(move_name, state), ...]
                      and   cost  = len(path)  (total number of moves).
        (None, None)  if no solution exists (should not happen for
                      solvable inputs).
    """
    h_start = manhattan_distance(start)
    # heap entries: (heuristic, tie_breaker, state, path_so_far)
    heap = [(h_start, 0, start, [])]
    visited = {start}
    counter = 1  # unique tie-breaker so tuples never need deep comparison

    while heap:
        h, _, state, path = heapq.heappop(heap)

        if state == GOAL:
            return path, len(path)

        for move_name, next_state in neighbors(state):
            if next_state not in visited:
                visited.add(next_state)
                h_next = manhattan_distance(next_state)
                new_path = path + [(move_name, next_state)]
                heapq.heappush(heap, (h_next, counter, next_state, new_path))
                counter += 1

    return None, None  # no solution found

