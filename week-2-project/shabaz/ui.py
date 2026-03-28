import os
import threading
import time
import tkinter as tk
from tkinter import font as tkfont

from solver import bfs, random_puzzle
from solution_writer import write_solution_file

BG = "#0D0D14"
CARD = "#16161F"
TILE_CLR = "#1E1E2E"
TILE_HI = "#2A2A3E"
BLANK_CLR = "#0D0D14"
ACCENT = "#7C6AF7"  # purple
ACCENT2 = "#F76A8C"  # pink
TEXT_MAIN = "#E8E6FF"
TEXT_DIM = "#5A5870"
GREEN = "#4ADE80"
BORDER = "#2A2840"

TILE_SIZE = 110
GAP = 8
BOARD_PAD = 24
ANIM_MS = 340  # animation duration per step


class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle · BFS Solver")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.solution_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution.txt")

        self._init_fonts()

        self._build_ui()
        self._new_game()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(28, 0))

        tk.Label(hdr, text="8-PUZZLE", font=self.f_title, bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text=" · BFS SOLVER", font=self.f_title, bg=BG, fg=ACCENT2).pack(side="left")

        tk.Label(
            self,
            text="breadth-first search  ·  optimal solution",
            font=self.f_small,
            bg=BG,
            fg=TEXT_DIM,
        ).pack(anchor="w", padx=24)

        tk.Frame(self, height=1, bg=BORDER).pack(fill="x", padx=24, pady=12)

        board_px = TILE_SIZE * 3 + GAP * 2 + BOARD_PAD * 2
        self.canvas = tk.Canvas(
            self,
            width=board_px,
            height=board_px,
            bg=CARD,
            highlightthickness=2,
            highlightbackground=BORDER,
        )
        self.canvas.pack(padx=24)

        self.var_status = tk.StringVar(value="Generating puzzle…")
        self.var_cost = tk.StringVar(value="")

        status_f = tk.Frame(self, bg=BG)
        status_f.pack(fill="x", padx=24, pady=(14, 0))

        tk.Label(
            status_f,
            textvariable=self.var_status,
            font=self.f_status,
            bg=BG,
            fg=TEXT_MAIN,
            anchor="w",
        ).pack(side="left")
        tk.Label(
            status_f,
            textvariable=self.var_cost,
            font=self.f_status,
            bg=BG,
            fg=GREEN,
            anchor="e",
        ).pack(side="right")

        prog_bg = tk.Frame(self, bg=BORDER, height=4)
        prog_bg.pack(fill="x", padx=24, pady=8)
        prog_bg.pack_propagate(False)
        self.prog_fill = tk.Frame(prog_bg, bg=ACCENT, height=4)
        self.prog_fill.place(x=0, y=0, relheight=1, relwidth=0)

        self.var_step = tk.StringVar(value="")
        tk.Label(self, textvariable=self.var_step, font=self.f_small, bg=BG, fg=TEXT_DIM).pack()

        btn_f = tk.Frame(self, bg=BG)
        btn_f.pack(pady=(10, 28))

        self.btn_play = self._btn(btn_f, "▶  PLAY", ACCENT, self._play)
        self.btn_play.pack(side="left", padx=6)

        self._btn(btn_f, "⟳  NEW", TEXT_DIM, self._new_game).pack(side="left", padx=6)
        self._btn(btn_f, "📄  OPEN FILE", TEXT_DIM, self._open_file).pack(side="left", padx=6)

    def _init_fonts(self):
        specs = {
            "f_title": {"size": 22, "weight": "bold"},
            "f_tile": {"size": 32, "weight": "bold"},
            "f_small": {"size": 11},
            "f_btn": {"size": 12, "weight": "bold"},
            "f_status": {"size": 13},
        }
        for name, opts in specs.items():
            try:
                font = tkfont.Font(family="Courier New", **opts)
            except Exception:
                font = tkfont.Font(**opts)
            setattr(self, name, font)

    def _btn(self, parent, text, color, cmd):
        return tk.Button(
            parent,
            text=text,
            font=self.f_btn,
            bg=TILE_CLR,
            fg=color,
            activebackground=TILE_HI,
            activeforeground=TEXT_MAIN,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=cmd,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
        )

    def _cell_xy(self, idx):
        r, c = divmod(idx, 3)
        x = BOARD_PAD + c * (TILE_SIZE + GAP)
        y = BOARD_PAD + r * (TILE_SIZE + GAP)
        return x, y

    def _draw_board(self, state):
        self.canvas.delete("all")
        for i, val in enumerate(state):
            x, y = self._cell_xy(i)
            if val == 0:
                self.canvas.create_rectangle(
                    x, y, x + TILE_SIZE, y + TILE_SIZE, fill=BLANK_CLR, outline=BORDER, width=2
                )
            else:
                self.canvas.create_rectangle(
                    x + 4, y + 4, x + TILE_SIZE + 4, y + TILE_SIZE + 4, fill="#08080F", outline=""
                )
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + TILE_SIZE,
                    y + TILE_SIZE,
                    fill=TILE_CLR,
                    outline=BORDER,
                    width=2,
                )
                self.canvas.create_text(
                    x + TILE_SIZE // 2,
                    y + TILE_SIZE // 2,
                    text=str(val),
                    font=self.f_tile,
                    fill=TEXT_MAIN,
                )

    def _new_game(self):
        self._stop_anim()
        self.steps = []
        self.cur_step = 0
        self.animating = False

        puzzle = random_puzzle()
        self._draw_board(puzzle)
        self.var_status.set("Solving with BFS…")
        self.var_cost.set("")
        self.var_step.set("")
        self._set_progress(0)
        self.btn_play.config(state="disabled", fg=TEXT_DIM)

        threading.Thread(target=self._solve, args=(puzzle,), daemon=True).start()

    def _solve(self, puzzle):
        t0 = time.time()
        steps = bfs(puzzle)
        dt = time.time() - t0

        if steps is None:
            self.after(0, lambda: self.var_status.set("No solution found!"))
            return

        cost = len(steps) - 1
        write_solution_file(self.solution_path, steps)
        self.steps = steps
        self.after(0, lambda: self._on_solved(cost, dt))

    def _on_solved(self, cost, dt):
        self.var_status.set(f"Solved in {dt:.2f}s  ·  ready to play")
        self.var_cost.set(f"Cost: {cost} moves")
        self.var_step.set(f"Step 0 / {cost}   ·   solution.txt saved ✓")
        self._draw_board(self.steps[0])
        self.btn_play.config(state="normal", fg=ACCENT)

    def _play(self):
        if self.animating or not self.steps:
            return
        if self.cur_step >= len(self.steps) - 1:
            self.cur_step = 0
        self.animating = True
        self.btn_play.config(state="disabled", fg=TEXT_DIM)
        self._anim_step()

    def _anim_step(self):
        if not self.animating:
            return
        if self.cur_step >= len(self.steps) - 1:
            self._finish_anim()
            return

        state = self.steps[self.cur_step]
        next_state = self.steps[self.cur_step + 1]
        blank_idx = next_state.index(0)
        moved_idx = state.index(0)
        moved_val = next_state[moved_idx]

        total = len(self.steps) - 1
        self._set_progress(self.cur_step / total)
        self.var_step.set(f"Step {self.cur_step + 1} / {total}   ·   moved tile {moved_val}")
        self._animate_tile(state, next_state, moved_idx, blank_idx)

    def _animate_tile(self, old_state, new_state, from_idx, to_idx):
        fx, fy = self._cell_xy(from_idx)
        tx, ty = self._cell_xy(to_idx)
        val = old_state[from_idx]

        frames = 16
        dx = (tx - fx) / frames
        dy = (ty - fy) / frames
        frame_ms = ANIM_MS // frames

        def draw_frame(f):
            if not self.animating:
                return
            self._draw_board(old_state)
            self.canvas.create_rectangle(
                tx, ty, tx + TILE_SIZE, ty + TILE_SIZE, fill=BLANK_CLR, outline=BORDER, width=2
            )
            cx = fx + dx * f
            cy = fy + dy * f
            self.canvas.create_rectangle(
                cx + 4, cy + 4, cx + TILE_SIZE + 4, cy + TILE_SIZE + 4, fill="#08080F", outline=""
            )
            self.canvas.create_rectangle(
                cx, cy, cx + TILE_SIZE, cy + TILE_SIZE, fill=ACCENT2, outline=ACCENT, width=2
            )
            self.canvas.create_text(
                cx + TILE_SIZE // 2, cy + TILE_SIZE // 2, text=str(val), font=self.f_tile, fill=TEXT_MAIN
            )

            if f < frames:
                self._anim_id = self.after(frame_ms, lambda: draw_frame(f + 1))
            else:
                self._draw_board(new_state)
                self.cur_step += 1
                self._anim_id = self.after(120, self._anim_step)

        draw_frame(0)

    def _finish_anim(self):
        self.animating = False
        self._set_progress(1)
        self._draw_board(self.steps[-1])
        total = len(self.steps) - 1
        self.var_status.set("✓  Puzzle solved!")
        self.var_step.set(f"Completed in {total} moves")
        self.btn_play.config(state="normal", fg=ACCENT, text="▶  REPLAY")

    def _stop_anim(self):
        self.animating = False
        if hasattr(self, "_anim_id"):
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass

    def _set_progress(self, pct):
        self.prog_fill.place(x=0, y=0, relheight=1, relwidth=min(pct, 1.0))

    def _open_file(self):
        if os.path.exists(self.solution_path):
            if os.name == "nt":
                os.startfile(self.solution_path)
            else:
                os.system(f'open "{self.solution_path}" 2>/dev/null || xdg-open "{self.solution_path}"')
        else:
            self.var_status.set("No solution file yet — solve first!")
