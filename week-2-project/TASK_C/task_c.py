"""
task_c.py — Entry Point
8-Puzzle solver using Best-First Search.

Run this file to launch the application:
    python task_c.py

Module structure (one file per group member):
    puzzle_board.py     — Member 2: board state, move logic, puzzle generation
    puzzle_algorithm.py — Member 1: Best-First Search + Manhattan Distance
    puzzle_writer.py    — Member 3: solution.txt writer
    puzzle_canvas.py    — Member 4: tkinter canvas board drawing
    puzzle_gui.py       — Member 5: GUI window, controls, animation
"""

import tkinter as tk
from puzzle_gui import EightPuzzleApp

if __name__ == "__main__":
    root = tk.Tk()
    EightPuzzleApp(root)
    root.mainloop()
