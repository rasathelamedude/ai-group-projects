"""
Task E — Vacuum World: Breadth-First Search (BFS)
Costs: UP=2  DOWN=0  LEFT=1  RIGHT=1
"""
import tkinter as tk, random, threading
from collections import deque

# ── Constants ──────────────────────────────────────────────────
ROWS, COLS = 6, 6
EMPTY, OBSTACLE, DIRT, VACUUM = 0, 1, 2, 3
MOVES = {"UP":((-1,0),2), "DOWN":((1,0),0), "LEFT":((0,-1),1), "RIGHT":((0,1),1)}

# ── Step 1: Generate random board ──────────────────────────────
def generate_board():
    board = [[EMPTY]*COLS for _ in range(ROWS)]
    cells = [(r,c) for r in range(ROWS) for c in range(COLS)]
    random.shuffle(cells)
    vp = cells.pop(); board[vp[0]][vp[1]] = VACUUM
    dp = cells.pop(); board[dp[0]][dp[1]] = DIRT
    for _ in range(random.randint(5,10)):
        if cells: r,c = cells.pop(); board[r][c] = OBSTACLE
    return board, vp, dp

# ── Step 2: BFS algorithm ──────────────────────────────────────
def bfs_solve(board, start, goal):
    queue   = deque([start])
    visited = {start: (None, None, 0)}  # pos -> (parent, move, cost)
    while queue:
        pos = queue.popleft()
        if pos == goal:                 # goal reached — rebuild path
            path, cur = [], pos
            while visited[cur][1]:
                parent, move, _ = visited[cur]
                path.append((move, cur)); cur = parent
            return list(reversed(path)), visited[goal][2]
        r, c = pos
        for move, ((dr,dc), mc) in MOVES.items():
            npos = (r+dr, c+dc)
            if (0<=npos[0]<ROWS and 0<=npos[1]<COLS
                    and board[npos[0]][npos[1]] != OBSTACLE
                    and npos not in visited):
                visited[npos] = (pos, move, visited[pos][2]+mc)
                queue.append(npos)
    return None, None                   # no solution

# ── Step 3: Write solution.txt ─────────────────────────────────
def write_file(board, start, goal, path, cost):
    SYM = {EMPTY:".", OBSTACLE:"#", DIRT:"D", VACUUM:"V"}
    def draw(vp):
        return "\n".join(" ".join("V" if (r,c)==vp else SYM[board[r][c]]
                                  for c in range(COLS)) for r in range(ROWS))
    with open("solution.txt","w",encoding="utf-8") as f:
        f.write(f"VACUUM WORLD — BFS\nGrid:{ROWS}x{COLS}  Vacuum:{start}  Dirt:{goal}\n")
        f.write("Costs: UP=2 DOWN=0 LEFT=1 RIGHT=1\nLegend: V=Vacuum D=Dirt #=Obstacle .=Empty\n\n")
        f.write("INITIAL BOARD:\n" + draw(start) + "\n\n")
        if path is None:
            f.write("NO SOLUTION — there is no solution because of obstacles.\n")
            f.write("The dirt cannot be reached. Board at time of failure:\n\n")
            f.write(draw(start) + "\n"); return
        total = 0
        for i,(move,npos) in enumerate(path,1):
            total += MOVES[move][1]
            f.write(f"Step {i}: {move} -> {npos}  (+{MOVES[move][1]}, total={total})\n")
            f.write(draw(npos)+"\n\n")
        f.write(f"GOAL REACHED!  Steps:{len(path)}  Total Cost:{cost}\n")

# ── Step 4: GUI ────────────────────────────────────────────────
CELL = 90; PAD = 20
C = {"bg":"#0d0d1a","cell":"#16213e","obs":"#2a1a10",
     "vac":"#00E5FF","dirt":"#FFD700","goal":"#00FF88","panel":"#0a1628"}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Task E — Vacuum BFS")
        self.root.configure(bg=C["bg"])
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        tk.Label(self.root, text="VACUUM WORLD — BFS", font=("Courier New",16,"bold"),
                 bg=C["bg"], fg=C["vac"]).pack(pady=8)
        main = tk.Frame(self.root, bg=C["bg"]); main.pack(padx=16)
        self.canvas = tk.Canvas(main, width=COLS*CELL+PAD*2, height=ROWS*CELL+PAD*2,
                                bg=C["bg"], highlightthickness=1, highlightbackground=C["vac"])
        self.canvas.pack(side="left", padx=(0,16))
        p = tk.Frame(main, bg=C["panel"], width=220, padx=10, pady=10)
        p.pack(side="left", fill="y"); p.pack_propagate(False)
        tk.Label(p, text="BFS INFO", font=("Courier New",13,"bold"),
                 bg=C["panel"], fg=C["vac"]).pack(pady=(4,8))
        self.lbl = {k: self._row(p,k,"...") for k in ["Status","Step","Move","Cost","Total"]}
        tk.Label(p, text="\nMove Costs:\n^ UP=2  v DOWN=0\n< LEFT=1  > RIGHT=1",
                 font=("Courier New",9), bg=C["panel"], fg="#888").pack(anchor="w")
        self.btn = tk.Button(p, text="▶ PLAY", font=("Courier New",11,"bold"),
                             bg="#0077aa", fg="white", relief="flat", pady=6,
                             state="disabled", command=self._play)
        self.btn.pack(fill="x", pady=(12,3))
        tk.Button(p, text="↺ NEW", font=("Courier New",11,"bold"),
                  bg="#0a3a2a", fg="white", relief="flat", pady=6,
                  command=self._new_game).pack(fill="x")
        self.speed = tk.IntVar(value=600)
        tk.Scale(p, variable=self.speed, from_=100, to=2000, orient="horizontal",
                 bg=C["panel"], fg="white", highlightthickness=0, length=190,
                 label="ms/step").pack(pady=8)
        self.bar = tk.Label(self.root, text="", font=("Courier New",10),
                            bg="#050510", fg="#888", anchor="w", padx=10, pady=4)
        self.bar.pack(fill="x")

    def _row(self, parent, label, value):
        f = tk.Frame(parent, bg=C["panel"]); f.pack(fill="x", pady=1)
        tk.Label(f, text=f"{label:<8}:", font=("Courier New",10),
                 bg=C["panel"], fg="#888").pack(side="left")
        v = tk.Label(f, text=value, font=("Courier New",10,"bold"),
                     bg=C["panel"], fg="white"); v.pack(side="left")
        return v

    def _new_game(self):
        if hasattr(self,"_aid") and self._aid: self.root.after_cancel(self._aid)
        self.board, self.vpos, self.dpos = generate_board()
        self.path = self.cost = None; self.step = 0
        for k,v in [("Status","Computing..."),("Step","0"),("Move","-"),("Cost","0"),("Total","?")]:
            self.lbl[k].config(text=v)
        self.btn.config(state="disabled")
        self.bar.config(text="Running BFS...")
        self.draw(self.vpos)
        threading.Thread(target=self._solve, daemon=True).start()

    def _solve(self):
        self.path, self.cost = bfs_solve(self.board, self.vpos, self.dpos)
        write_file(self.board, self.vpos, self.dpos, self.path, self.cost)
        self.root.after(0, self._done)

    def _done(self):
        if self.path is None:
            self.lbl["Status"].config(text="NO SOLUTION", fg="red")
            self.bar.config(text="No solution — dirt blocked. See solution.txt")
        else:
            self.lbl["Status"].config(text="READY", fg=C["goal"])
            self.lbl["Total"].config(text=str(self.cost))
            self.bar.config(text=f"Done: {len(self.path)} steps, cost={self.cost}. Press PLAY.")
            self.btn.config(state="normal")

    def _play(self):
        self.step = 0; self.btn.config(state="disabled")
        self.draw(self.vpos); self._tick()

    def _tick(self):
        if self.step >= len(self.path):
            self.lbl["Status"].config(text="GOAL ★", fg=C["goal"])
            self.bar.config(text=f"Goal reached! Cost={self.cost}")
            self.draw(self.path[-1][1], done=True)
            self.btn.config(state="normal"); return
        move, npos = self.path[self.step]; self.step += 1
        rc = sum(MOVES[m][1] for m,_ in self.path[:self.step])
        self.lbl["Step"].config(text=f"{self.step}/{len(self.path)}")
        self.lbl["Move"].config(text=move)
        self.lbl["Cost"].config(text=str(rc))
        self.bar.config(text=f"Step {self.step}: {move} -> {npos}  cost so far: {rc}")
        self.draw(npos)
        self._aid = self.root.after(self.speed.get(), self._tick)

    def draw(self, vpos, done=False):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x, y   = PAD+c*CELL, PAD+r*CELL
                cx, cy = x+CELL//2, y+CELL//2
                tile   = self.board[r][c]
                self.canvas.create_rectangle(x+2,y+2,x+CELL-2,y+CELL-2,
                    fill=C["obs"] if tile==OBSTACLE else C["cell"], outline="#1a2a4a")
                if   (r,c)==vpos:      self.canvas.create_text(cx,cy,text="★" if done else "●",
                                           fill=C["goal"] if done else C["vac"],font=("Courier New",28,"bold"))
                elif tile==DIRT:       self.canvas.create_text(cx,cy,text="◆",fill=C["dirt"],font=("Courier New",26,"bold"))
                elif tile==OBSTACLE:   self.canvas.create_text(cx,cy,text="▓",fill="#5a3a2a",font=("Courier New",28,"bold"))

# ── Run ────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
