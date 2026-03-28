"""Vacuum World — DFS Solver | Costs: UP=2, DOWN=0, LEFT=1, RIGHT=1"""
import tkinter as tk, random, threading

ROWS, COLS = 6, 6
EMPTY, OBSTACLE, DIRT, VACUUM = 0, 1, 2, 3
MOVES = {"UP":((-1,0),2),"DOWN":((1,0),0),"LEFT":((0,-1),1),"RIGHT":((0,1),1)}
BG,PANEL,CELL,OBS  = "#0d1117","#161b22","#1f2937","#374151"
VAC,DIRT_C,GOAL,TXT = "#f97316","#facc15","#4ade80","#e2e8f0"
DIM,BTN,SZ = "#6b7280","#2563eb",88

def make_board():
    b = [[EMPTY]*COLS for _ in range(ROWS)]
    cells = [(r,c) for r in range(ROWS) for c in range(COLS)]
    random.shuffle(cells)
    vr,vc=cells.pop(); b[vr][vc]=VACUUM
    dr,dc=cells.pop(); b[dr][dc]=DIRT
    for _ in range(random.randint(5,10)):
        if cells: r,c=cells.pop(); b[r][c]=OBSTACLE
    return b,(vr,vc),(dr,dc)

def dfs(board,start,goal):
    stack=[(start,[],0,{start})]
    while stack:
        pos,path,cost,seen=stack.pop()
        if pos==goal: return path,cost
        r,c=pos
        for mv,((dr,dc),mc) in MOVES.items():
            np=(r+dr,c+dc)
            if 0<=np[0]<ROWS and 0<=np[1]<COLS and board[np[0]][np[1]]!=OBSTACLE and np not in seen:
                stack.append((np,path+[(mv,np)],cost+mc,seen|{np}))
    return None,None

def save(board,start,goal,path,cost):
    SYM={EMPTY:".",OBSTACLE:"#",DIRT:"D",VACUUM:"V"}
    AR={"UP":"↑","DOWN":"↓","LEFT":"←","RIGHT":"→"}
    def draw(v): return "\n".join("  "+"  ".join("V"if(r,c)==v else SYM[board[r][c]] for c in range(COLS)) for r in range(ROWS))
    with open("solution.txt","w",encoding="utf-8") as f:
        f.write("╔══════════════════════════════════╗\n║   VACUUM WORLD — DFS SOLUTION    ║\n╚══════════════════════════════════╝\n\n")
        f.write(f"  Start:{start}  Goal:{goal}\n  Costs: UP=2  DOWN=0  LEFT=1  RIGHT=1\n\nINITIAL BOARD:\n{draw(start)}\n\n")
        if path is None:
            f.write("❌ NO SOLUTION — dirt is unreachable because of obstacles.\n"); return
        f.write(f"SOLUTION ({len(path)} steps):\n\n"); total=0
        for i,(mv,npos) in enumerate(path,1):
            sc=MOVES[mv][1]; total+=sc
            f.write(f"  Step {i:>2}: {AR[mv]} {mv:<5} → {npos}  (+{sc}, total={total})\n{draw(npos)}\n\n")
        f.write(f"╔══════════════════════════════════╗\n║  ✅ GOAL REACHED!  Cost = {cost:<6} ║\n╚══════════════════════════════════╝\n")

class App:
    def __init__(self, root):
        self.root=root; self.root.title("Vacuum DFS"); self.root.configure(bg=BG)
        self.root.resizable(False,False); self._aid=None; self._build(); self._new()

    def _build(self):
        tk.Label(self.root,text="🤖  VACUUM WORLD — DFS",font=("Consolas",15,"bold"),bg=BG,fg=VAC).pack(pady=10)
        fr=tk.Frame(self.root,bg=BG); fr.pack(padx=16,pady=4)
        W=COLS*SZ+40; H=ROWS*SZ+40
        self.cv=tk.Canvas(fr,width=W,height=H,bg=BG,highlightthickness=2,highlightbackground=VAC)
        self.cv.pack(side="left",padx=(0,14))
        p=tk.Frame(fr,bg=PANEL,padx=14,pady=14); p.pack(side="left",fill="y")
        tk.Label(p,text="INFO",font=("Consolas",12,"bold"),bg=PANEL,fg=VAC).pack(pady=(0,8))
        self.lbl={}
        for k,v in [("Status","—"),("Step","—"),("Move","—"),("Cost","—"),("Total","—")]:
            rw=tk.Frame(p,bg=PANEL); rw.pack(fill="x",pady=2)
            tk.Label(rw,text=f"{k}:",width=7,anchor="w",font=("Consolas",10),bg=PANEL,fg=DIM).pack(side="left")
            lv=tk.Label(rw,text=v,font=("Consolas",10,"bold"),bg=PANEL,fg=TXT); lv.pack(side="left")
            self.lbl[k]=lv
        tk.Label(p,text="─"*22,bg=PANEL,fg="#2d3748").pack(pady=6)
        for ln in ["↑ UP=2","↓ DOWN=0","← LEFT=1","→ RIGHT=1"]:
            tk.Label(p,text=ln,font=("Consolas",10),bg=PANEL,fg=DIM).pack(anchor="w")
        tk.Label(p,text="─"*22,bg=PANEL,fg="#2d3748").pack(pady=6)
        self.btn=tk.Button(p,text="▶  PLAY",font=("Consolas",11,"bold"),bg=BTN,fg="white",
                           relief="flat",state="disabled",command=self._play,pady=6)
        self.btn.pack(fill="x",pady=3)
        tk.Button(p,text="↺  NEW BOARD",font=("Consolas",11,"bold"),bg="#166534",fg="white",
                  relief="flat",command=self._new,pady=6).pack(fill="x",pady=3)
        tk.Label(p,text="Speed (ms):",font=("Consolas",9),bg=PANEL,fg=DIM).pack(anchor="w",pady=(10,0))
        self.spd=tk.IntVar(value=600)
        tk.Scale(p,variable=self.spd,from_=100,to=2000,orient="horizontal",bg=PANEL,fg=TXT,
                 highlightthickness=0,length=180).pack()
        self.sb=tk.Label(self.root,text="",font=("Consolas",9),bg="#0a0a0a",fg=DIM,anchor="w",padx=10,pady=4)
        self.sb.pack(fill="x")

    def _new(self):
        if self._aid: self.root.after_cancel(self._aid)
        self.board,self.vp,self.dp=make_board()
        self.path=None; self.step=0; self.cur=self.vp
        for k,v in [("Status","Computing…"),("Step","—"),("Move","—"),("Cost","—"),("Total","—")]:
            self.lbl[k].config(text=v,fg=TXT)
        self.btn.config(state="disabled"); self.sb.config(text="Running DFS…")
        self._draw(self.vp); threading.Thread(target=self._solve,daemon=True).start()

    def _solve(self):
        p,c=dfs(self.board,self.vp,self.dp); save(self.board,self.vp,self.dp,p,c)
        self.path=p; self.total=c; self.root.after(0,self._done)

    def _done(self):
        if self.path is None:
            self.lbl["Status"].config(text="NO PATH",fg="red")
            self.sb.config(text="No solution — obstacles block the dirt. See solution.txt")
        else:
            self.lbl["Status"].config(text="READY ✓",fg=GOAL); self.lbl["Total"].config(text=str(self.total))
            self.sb.config(text=f"DFS done: {len(self.path)} steps, cost={self.total}. Press PLAY.")
            self.btn.config(state="normal")

    def _play(self):
        self.step=0; self.cur=self.vp; self.btn.config(state="disabled")
        self._draw(self.vp); self._tick()

    def _tick(self):
        if self.step>=len(self.path):
            self.lbl["Status"].config(text="GOAL ★",fg=GOAL); self._draw(self.cur,done=True)
            self.btn.config(state="normal"); return
        mv,npos=self.path[self.step]; self.step+=1; self.cur=npos
        rc=sum(MOVES[m][1] for m,_ in self.path[:self.step])
        self.lbl["Step"].config(text=f"{self.step}/{len(self.path)}")
        self.lbl["Move"].config(text=mv); self.lbl["Cost"].config(text=str(rc))
        self.sb.config(text=f"Step {self.step}: {mv} → {npos} | cost so far: {rc}")
        self._draw(npos); self._aid=self.root.after(self.spd.get(),self._tick)

    def _draw(self,vpos,done=False):
        self.cv.delete("all"); off=20
        for r in range(ROWS):
            for c in range(COLS):
                x,y=off+c*SZ,off+r*SZ; cx,cy=x+SZ//2,y+SZ//2
                t=self.board[r][c]; bg=OBS if t==OBSTACLE else CELL
                self.cv.create_rectangle(x+3,y+3,x+SZ-3,y+SZ-3,fill=bg,outline="#2d3748",width=1)
                if (r,c)==vpos:
                    self.cv.create_text(cx,cy,text="★"if done else"●",fill=GOAL if done else VAC,font=("Consolas",28,"bold"))
                elif t==DIRT:
                    self.cv.create_text(cx,cy,text="◆",fill=DIRT_C,font=("Consolas",26,"bold"))
                elif t==OBSTACLE:
                    self.cv.create_text(cx,cy,text="▓",fill="#9ca3af",font=("Consolas",26,"bold"))

if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()