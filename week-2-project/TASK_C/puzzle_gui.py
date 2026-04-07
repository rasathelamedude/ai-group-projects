"""
puzzle_gui.py — Member 5
Main application window: side panel, controls, animation loop.
Imports from all other modules and wires everything together.
"""

import tkinter as tk
import threading

from puzzle_board     import random_solvable_state
from puzzle_algorithm import best_first_search
from puzzle_writer    import write_solution_to_file
from puzzle_canvas    import make_canvas, draw_board, BG, PAD, CELL, GAP

# ── Colours used only in the control panel ────────────────────────────────────
PANEL_BG = "#0a1628"
BORDER   = "#263a66"
ACCENT   = "#4fc3f7"
ACCENT2  = "#00e5ff"
SUCCESS  = "#00e676"
WARN     = "#ff7043"
MUTED    = "#546e7a"
WHITE    = "#eceff1"
GOLD     = "#ffd54f"


class EightPuzzleApp:
    """
    Main application class.
    Builds the GUI, starts the solver in a background thread,
    and plays back the solution step by step.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("8-Puzzle  ·  Best-First Search")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # State
        self._aid    = None   # after() id for animation cancellation
        self._state  = None   # currently displayed puzzle state
        self._start  = None   # initial board for this round
        self._path   = None   # solution path: [(move, state), ...]
        self._cost   = None   # total cost (= number of moves)
        self._step   = 0      # current animation step index

        self._build_ui()
        self._new_game()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(hdr, text="8-PUZZLE",
                 font=("Helvetica", 22, "bold"),
                 bg=BG, fg=ACCENT2).pack(side="left")
        tk.Label(hdr, text="  Best-First Search",
                 font=("Helvetica", 13),
                 bg=BG, fg=MUTED).pack(side="left", pady=4)

        # Thin divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=24)

        # Main body: canvas + side panel side by side
        body = tk.Frame(self.root, bg=BG)
        body.pack(padx=24, pady=16)

        # Board canvas (created by puzzle_canvas)
        self.canvas = make_canvas(body)
        self.canvas.grid(row=0, column=0, padx=(0, 20))

        # Side panel
        panel = tk.Frame(body, bg=PANEL_BG, padx=18, pady=18)
        panel.grid(row=0, column=1, sticky="ns")
        panel.grid_propagate(False)
        panel.config(width=220)
        self._build_panel(panel)

        # Status bar at the very bottom
        self._bar = tk.Label(
            self.root, text="",
            font=("Helvetica", 9), bg="#050510", fg=MUTED,
            anchor="w", padx=12, pady=5)
        self._bar.pack(fill="x", side="bottom")

    def _build_panel(self, panel: tk.Frame):
        """Populate the side info panel with labels, slider, and buttons."""
        tk.Label(panel, text="INFO",
                 font=("Helvetica", 11, "bold"),
                 bg=PANEL_BG, fg=ACCENT).pack(anchor="w")
        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x", pady=(4, 10))

        # Info rows
        self._lbl = {}
        for key, init in [("Status", "Generating…"),
                           ("Step",   "—"),
                           ("Move",   "—"),
                           ("Cost",   "—"),
                           ("Total",  "—")]:
            self._lbl[key] = self._info_row(panel, key, init)

        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x", pady=12)

        # Heuristic note
        tk.Label(panel, text="Heuristic:",
                 font=("Helvetica", 9), bg=PANEL_BG, fg=MUTED).pack(anchor="w")
        tk.Label(panel, text="Manhattan Distance",
                 font=("Helvetica", 9, "bold"),
                 bg=PANEL_BG, fg=WHITE).pack(anchor="w")
        tk.Label(panel, text="Move cost: 1",
                 font=("Helvetica", 9),
                 bg=PANEL_BG, fg=MUTED).pack(anchor="w", pady=(2, 14))

        # Speed slider
        tk.Label(panel, text="Speed  (ms/step)",
                 font=("Helvetica", 9),
                 bg=PANEL_BG, fg=MUTED).pack(anchor="w")
        self._speed = tk.IntVar(value=500)
        tk.Scale(panel, variable=self._speed, from_=80, to=1500,
                 orient="horizontal", bg=PANEL_BG, fg=WHITE,
                 troughcolor="#1a2744", highlightthickness=0,
                 sliderrelief="flat", length=184).pack(anchor="w")

        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x", pady=10)

        # Buttons
        self._btn_play = tk.Button(
            panel, text="▶  PLAY",
            font=("Helvetica", 11, "bold"),
            bg="#1565c0", fg=WHITE,
            activebackground="#1976d2", activeforeground=WHITE,
            relief="flat", pady=8, state="disabled",
            cursor="hand2", command=self._play)
        self._btn_play.pack(fill="x", pady=(0, 6))

        tk.Button(
            panel, text="↺  NEW PUZZLE",
            font=("Helvetica", 10, "bold"),
            bg="#1b5e20", fg=WHITE,
            activebackground="#2e7d32", activeforeground=WHITE,
            relief="flat", pady=8,
            cursor="hand2", command=self._new_game
        ).pack(fill="x")

    def _info_row(self, parent: tk.Frame, label: str, value: str) -> tk.Label:
        """Create one key/value row in the info panel."""
        row = tk.Frame(parent, bg=PANEL_BG)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{label:<8}",
                 font=("Helvetica", 9), bg=PANEL_BG, fg=MUTED,
                 width=8, anchor="w").pack(side="left")
        lbl = tk.Label(row, text=value,
                       font=("Helvetica", 10, "bold"),
                       bg=PANEL_BG, fg=WHITE, anchor="w")
        lbl.pack(side="left")
        return lbl

    # ── Game flow ─────────────────────────────────────────────────────────────

    def _new_game(self):
        """Reset state, generate a new puzzle, and start BFS in background."""
        if self._aid:
            self.root.after_cancel(self._aid)
            self._aid = None

        self._path  = None
        self._cost  = None
        self._step  = 0
        self._start = random_solvable_state()
        self._state = self._start

        self._set("Status", "Solving…",  ACCENT)
        self._set("Step",   "—",          WHITE)
        self._set("Move",   "—",          WHITE)
        self._set("Cost",   "—",          WHITE)
        self._set("Total",  "—",          WHITE)
        self._btn_play.config(state="disabled")
        self._bar.config(text="Best-First Search running in background…", fg=MUTED)

        draw_board(self.canvas, self._state)
        threading.Thread(target=self._solve, daemon=True).start()

    def _solve(self):
        """Run BFS + write solution.txt (background thread)."""
        path, cost = best_first_search(self._start)
        write_solution_to_file(self._start, path, cost)
        self._path = path
        self._cost = cost
        self.root.after(0, self._on_solved)   # hand back to main thread

    def _on_solved(self):
        """Called from main thread once BFS is done."""
        if self._path is None:
            self._set("Status", "NO SOLUTION", WARN)
            self._bar.config(text="No solution found.  solution.txt updated.", fg=WARN)
        else:
            self._set("Status", "READY ✓",   SUCCESS)
            self._set("Total",  str(self._cost), GOLD)
            self._btn_play.config(state="normal")
            self._bar.config(
                text=(f"Solved in {len(self._path)} moves (cost={self._cost}). "
                      f"solution.txt written.  Press ▶ PLAY."),
                fg=SUCCESS)

    # ── Animation ─────────────────────────────────────────────────────────────

    def _play(self):
        """Start (or restart) the step-by-step animation from the beginning."""
        self._step  = 0
        self._state = self._start
        self._btn_play.config(state="disabled")
        self._set("Status", "Playing…", ACCENT)
        draw_board(self.canvas, self._state, highlight_blank=True)
        self._tick()

    def _tick(self):
        """Advance one step in the animation, then schedule the next."""
        if self._step >= len(self._path):
            # Finished — show goal state
            self._set("Status", "GOAL  ★",                     SUCCESS)
            self._set("Step",   f"{len(self._path)}/{len(self._path)}", GOLD)
            self._bar.config(
                text=f"Goal reached!  Moves: {len(self._path)}  Cost: {self._cost}",
                fg=SUCCESS)
            draw_board(self.canvas, self._state, done=True)
            self._btn_play.config(state="normal")
            return

        move_name, new_state = self._path[self._step]
        self._step  += 1
        self._state  = new_state

        self._set("Step", f"{self._step}/{len(self._path)}", WHITE)
        self._set("Move", move_name,                          ACCENT2)
        self._set("Cost", str(self._step),                    WHITE)
        self._bar.config(
            text=f"Step {self._step}: moved blank {move_name}  |  cost so far: {self._step}",
            fg=MUTED)

        draw_board(self.canvas, self._state, highlight_blank=True)
        self._aid = self.root.after(self._speed.get(), self._tick)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set(self, key: str, text: str, color: str = WHITE):
        self._lbl[key].config(text=text, fg=color)
