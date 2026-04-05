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
    
    
def write_solution_to_file(start: tuple, path, cost, filename: str = "solution.txt"):
    """
    The function writes a human-readable solution log to a specified file.
    
    The log includes:
      - Algorithm header and heuristic details
      - Initial board diagram
      - Every step (move name + board diagram + running cost)
      - Final summary line with total steps and total cost
    
    Args:
        start: The initial state of the puzzle as a tuple.
        path: A list of tuples representing the solution path, where each tuple represents a move and the resulting state.
        cost: The total cost of the solution path.
        filename: The name of the file to write the solution log to. Default is "solution.txt".
    Returns:
        None
    """
    
    lines = []
    
    # --- Header ---
    lines.append("=" * 50)
    lines.append("  8-PUZZLE SOLVER — BEST-FIRST SEARCH")
    lines.append("  Heuristic : Manhattan Distance")
    lines.append("  Cost/move : 1")
    lines.append("=" * 50)
    lines.append("")
    
    # --- Initial board ---
    lines.append("INITIAL BOARD:")
    lines.append(draw_board_ascii(start))
    lines.append("")
    
    # --- No solution case ---
    if path is None:
        lines.append("NO SOLUTION FOUND.")
        _flush(lines, filename)
        return
      
    # --- Solution summary ---
    lines.append(f"TOTAL STEPS : {len(path)}")
    lines.append(f"TOTAL COST  : {cost}  (each move = 1)")
    lines.append("")
    lines.append("-" * 50)
    lines.append("SOLUTION STEPS:")
    lines.append("-" * 50)
    lines.append("")
    
    
    # --- Solution Steps (board state at each step) ---
    for step_num, (move_name, state) in enumerate(path, start=1):
        lines.append(
          f"Step {step_num:>3}  |  Move: {move_name:<5}  |  Cost so far: {step_num}"
        )
        lines.append(draw_board_ascii(state))
        lines.append("")
        
    # --- Footer ---
    lines.append("=" * 50)
    lines.append(f"  GOAL REACHED!  Steps: {len(path)}  Total Cost: {cost}")
    lines.append("=" * 50)
    
    _flush(lines, filename)

def _flush(lines, filename):
    """
    Helper function to write the accumulated lines to the specified file.
    
    Args:
        lines: A list of strings representing the lines to write to the file.
        filename: The name of the file to write to.
    Returns:
        None
    """
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
    