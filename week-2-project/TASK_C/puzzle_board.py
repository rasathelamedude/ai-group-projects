"""
puzzle_board.py — Member 2
Board state definitions, move logic, and random solvable puzzle generation.
"""

import random

# ── Goal state & tile positions ──────────────────────────────────────────────
# 0 represents the blank tile
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Pre-compute where each tile belongs in the goal for fast heuristic lookup
GOAL_POS = {tile: (i // 3, i % 3) for i, tile in enumerate(GOAL)}

# ── Valid moves (direction → row/col delta) ───────────────────────────────────
MOVES = {
    "UP":    (-1,  0),
    "DOWN":  ( 1,  0),
    "LEFT":  ( 0, -1),
    "RIGHT": ( 0,  1),
}


def is_solvable(state: tuple) -> bool:
    """
    Return True if the puzzle state is solvable.
    A state is solvable iff the number of inversions among non-blank
    tiles is even.
    """
    tiles = [t for t in state if t != 0]
    inversions = sum(
        1 for i in range(len(tiles))
          for j in range(i + 1, len(tiles))
          if tiles[i] > tiles[j]
    )
    return inversions % 2 == 0


def random_solvable_state() -> tuple:
    """
    Generate a random 8-puzzle state that is:
    - solvable (passes inversion parity check)
    - not already the goal
    """
    while True:
        tiles = list(range(9))
        random.shuffle(tiles)
        state = tuple(tiles)
        if is_solvable(state) and state != GOAL:
            return state


def neighbors(state: tuple):
    """
    Yield (move_name, new_state) for every legal move from the given state.
    A move slides the blank tile in the given direction.
    """
    blank_index = state.index(0)
    blank_row, blank_col = divmod(blank_index, 3)

    for move_name, (dr, dc) in MOVES.items():
        new_row, new_col = blank_row + dr, blank_col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            tiles = list(state)
            tiles[blank_index], tiles[new_index] = tiles[new_index], tiles[blank_index]
            yield move_name, tuple(tiles)
