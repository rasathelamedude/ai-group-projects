"""
puzzle_writer.py — Rasyar
Writes the full solution log to a file (solution.txt).
"""

def draw_board_ascii(state: tuple) -> str:
    """
    The function renders a puzzle state as a readable 3-line ASCII board.
    
    Example output:
        1 | 2 | 3
        -----------
        4 | _ | 6
        -----------
        7 | 8 | 5
        
    Args:
        state: A tuple representing the current state of the puzzle, where 0 represents the blank tile.
    Returns:
        A string representing the ASCII art of the puzzle board.
    """
    
    rows = []
    for row in range(3):
        cells = []
        
        for col in range(3):
            tile = state[row * 3 + col]
            
            if tile == 0:
                cells.append("_")
            else:
                cells.append(str(tile))
        rows.append("  " + " | ".join(cells))
        
    separator = "  " + "-" * 11
    return (
      f"{rows[0]}\n"
      f"{separator}\n"
      f"{rows[1]}\n"
      f"{separator}\n"
      f"{rows[2]}"
    )
    