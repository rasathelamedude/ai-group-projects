import os, threading, time, tkinter as tk
from tkinter import font as tkfont
from solver import bfs, random_puzzle
from solution_writer import write_solution_file

# ── colours ───────────────────────────────────────────────────────────────
BG, CARD, TILE_CLR, TILE_HI = "#0D0D14", "#16161F", "#1E1E2E", "#2A2A3E"
BLANK_CLR, ACCENT, ACCENT2  = "#0D0D14", "#7C6AF7", "#F76A8C"
TEXT_MAIN, TEXT_DIM, GREEN  = "#E8E6FF", "#5A5870", "#4ADE80"
BORDER = "#2A2840"

TILE_SIZE, GAP, BOARD_PAD, ANIM_MS = 110, 8, 24, 340


class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle · BFS Solver")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.solution_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution.txt")
        self.steps, self.cur_step, self.animating = [], 0, False

        # fonts
        for name, size, bold in [("f_title",22,1),("f_tile",32,1),("f_small",11,0),("f_btn",12,1),("f_status",13,0)]:
            setattr(self, name, tkfont.Font(family="Courier New", size=size, weight="bold" if bold else "normal"))

        self._build_ui()
        self._new_game()

    # ── button helper ──────────────────────────────────────────────────────
    def _btn(self, parent, text, cmd, primary=False):
        bg = ACCENT if primary else TILE_CLR
        fg = "#FFF"  if primary else TEXT_DIM
        b = tk.Button(parent, text=text, font=self.f_btn, bg=bg, fg=fg,
                      activebackground=TILE_HI, activeforeground=TEXT_MAIN,
                      relief="flat", padx=20, pady=9, cursor="hand2", command=cmd,
                      bd=0, highlightthickness=1, highlightbackground=BORDER)
        b.bind("<Enter>", lambda e: b.config(bg="#9D8FFF" if primary else TILE_HI,
                                             highlightbackground=ACCENT, fg=TEXT_MAIN))
        b.bind("<Leave>", lambda e: b.config(bg=bg, highlightbackground=BORDER, fg=fg))
        return b

    # ── UI build ───────────────────────────────────────────────────────────
    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(28,0))
        tk.Label(hdr, text="8-PUZZLE",      font=self.f_title, bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text=" · BFS SOLVER", font=self.f_title, bg=BG, fg=ACCENT2).pack(side="left")
        tk.Label(self, text="breadth-first search  ·  optimal solution",
                 font=self.f_small, bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=24)
        tk.Frame(self, height=1, bg=BORDER).pack(fill="x", padx=24, pady=12)

        board_px = TILE_SIZE*3 + GAP*2 + BOARD_PAD*2
        self.canvas = tk.Canvas(self, width=board_px, height=board_px, bg=CARD,
                                highlightthickness=2, highlightbackground=BORDER)
        self.canvas.pack(padx=24)

        self.var_status = tk.StringVar(value="Generating puzzle…")
        self.var_cost   = tk.StringVar(value="")
        self.var_step   = tk.StringVar(value="")

        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=24, pady=(14,0))
        tk.Label(sf, textvariable=self.var_status, font=self.f_status, bg=BG, fg=TEXT_MAIN, anchor="w").pack(side="left")
        tk.Label(sf, textvariable=self.var_cost,   font=self.f_status, bg=BG, fg=GREEN,     anchor="e").pack(side="right")

        pb = tk.Frame(self, bg=BORDER, height=4)
        pb.pack(fill="x", padx=24, pady=8)
        pb.pack_propagate(False)
        self.prog_fill = tk.Frame(pb, bg=ACCENT, height=4)
        self.prog_fill.place(x=0, y=0, relheight=1, relwidth=0)

        tk.Label(self, textvariable=self.var_step, font=self.f_small, bg=BG, fg=TEXT_DIM).pack()

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=(14,30))
        self.btn_play = self._btn(bf, "▶  PLAY", self._play, primary=True)
        self.btn_play.pack(side="left", padx=8)
        self._btn(bf, "⟳  NEW",       self._new_game).pack(side="left", padx=6)
        self._btn(bf, "📄  OPEN FILE", self._open_file).pack(side="left", padx=6)

    # ── board ──────────────────────────────────────────────────────────────
    def _cell_xy(self, idx):
        r, c = divmod(idx, 3)
        return BOARD_PAD + c*(TILE_SIZE+GAP), BOARD_PAD + r*(TILE_SIZE+GAP)

    def _draw_board(self, state):
        self.canvas.delete("all")
        for i, val in enumerate(state):
            x, y = self._cell_xy(i)
            if val == 0:
                self.canvas.create_rectangle(x,y,x+TILE_SIZE,y+TILE_SIZE, fill=BLANK_CLR, outline=BORDER, width=2)
            else:
                self.canvas.create_rectangle(x+4,y+4,x+TILE_SIZE+4,y+TILE_SIZE+4, fill="#08080F", outline="")
                self.canvas.create_rectangle(x,y,x+TILE_SIZE,y+TILE_SIZE, fill=TILE_CLR, outline=BORDER, width=2)
                self.canvas.create_text(x+TILE_SIZE//2, y+TILE_SIZE//2, text=str(val), font=self.f_tile, fill=TEXT_MAIN)

    # ── game logic ─────────────────────────────────────────────────────────
    def _new_game(self):
        self._stop_anim()
        self.steps, self.cur_step, self.animating = [], 0, False
        puzzle = random_puzzle()
        self._draw_board(puzzle)
        self.var_status.set("Solving with BFS…")
        self.var_cost.set(""); self.var_step.set("")
        self._set_progress(0)
        self.btn_play.config(state="disabled", fg=TEXT_DIM)
        threading.Thread(target=self._solve, args=(puzzle,), daemon=True).start()

    def _solve(self, puzzle):
        t0 = time.time()
        steps = bfs(puzzle)
        dt = time.time() - t0
        if steps is None:
            self.after(0, lambda: self.var_status.set("No solution found!")); return
        write_solution_file(self.solution_path, steps)
        self.steps = steps
        cost = len(steps) - 1
        self.after(0, lambda: (
            self.var_status.set(f"Solved in {dt:.2f}s  ·  ready to play"),
            self.var_cost.set(f"Cost: {cost} moves"),
            self.var_step.set(f"Step 0 / {cost}   ·   solution.txt saved ✓"),
            self._draw_board(steps[0]),
            self.btn_play.config(state="normal", fg="#FFF"),
        ))

    def _play(self):
        if self.animating or not self.steps: return
        if self.cur_step >= len(self.steps)-1: self.cur_step = 0
        self.animating = True
        self.btn_play.config(state="disabled", fg=TEXT_DIM)
        self._anim_step()

    def _anim_step(self):
        if not self.animating: return
        if self.cur_step >= len(self.steps)-1:
            self._finish_anim(); return
        s, ns = self.steps[self.cur_step], self.steps[self.cur_step+1]
        total = len(self.steps)-1
        self._set_progress(self.cur_step / total)
        self.var_step.set(f"Step {self.cur_step+1} / {total}   ·   moved tile {ns[s.index(0)]}")
        self._animate_tile(s, ns, s.index(0), ns.index(0))

    def _animate_tile(self, old, new, fi, ti):
        fx, fy = self._cell_xy(fi)
        tx, ty = self._cell_xy(ti)
        val, frames = old[fi], 16
        dx, dy = (tx-fx)/frames, (ty-fy)/frames

        def draw_frame(f):
            if not self.animating: return
            self._draw_board(old)
            self.canvas.create_rectangle(tx,ty,tx+TILE_SIZE,ty+TILE_SIZE, fill=BLANK_CLR, outline=BORDER, width=2)
            cx, cy = fx+dx*f, fy+dy*f
            self.canvas.create_rectangle(cx+4,cy+4,cx+TILE_SIZE+4,cy+TILE_SIZE+4, fill="#08080F", outline="")
            self.canvas.create_rectangle(cx,cy,cx+TILE_SIZE,cy+TILE_SIZE, fill=ACCENT2, outline=ACCENT, width=2)
            self.canvas.create_text(cx+TILE_SIZE//2, cy+TILE_SIZE//2, text=str(val), font=self.f_tile, fill=TEXT_MAIN)
            if f < frames:
                self._anim_id = self.after(ANIM_MS//frames, lambda: draw_frame(f+1))
            else:
                self._draw_board(new); self.cur_step += 1
                self._anim_id = self.after(120, self._anim_step)

        draw_frame(0)

    def _finish_anim(self):
        self.animating = False
        self._set_progress(1)
        self._draw_board(self.steps[-1])
        self.var_status.set("✓  Puzzle solved!")
        self.var_step.set(f"Completed in {len(self.steps)-1} moves")
        self.btn_play.config(state="normal", fg="#FFF", text="▶  REPLAY")

    def _stop_anim(self):
        self.animating = False
        if hasattr(self, "_anim_id"):
            try: self.after_cancel(self._anim_id)
            except: pass

    def _set_progress(self, pct):
        self.prog_fill.place(x=0, y=0, relheight=1, relwidth=min(pct, 1.0))

    def _open_file(self):
        if os.path.exists(self.solution_path):
            os.startfile(self.solution_path) if os.name=="nt" else \
            os.system(f'open "{self.solution_path}" 2>/dev/null || xdg-open "{self.solution_path}"')
        else:
            self.var_status.set("No solution file yet — solve first!")