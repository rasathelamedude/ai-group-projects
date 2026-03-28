import time


def write_solution_file(path, steps):
    lines = []
    lines.append("=" * 50)
    lines.append("        8-PUZZLE  ·  BFS SOLUTION")
    lines.append("=" * 50)
    lines.append(f"  Total moves (cost) : {len(steps) - 1}")
    lines.append(f"  Generated at       : {time.strftime('%Y-%m-%d  %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")

    def fmt_board(state):
        rows = []
        rows.append("  ┌───┬───┬───┐")
        for r in range(3):
            row = state[r * 3 : (r + 1) * 3]
            cells = " │ ".join(str(v) if v != 0 else " " for v in row)
            rows.append(f"  │ {cells} │")
            if r < 2:
                rows.append("  ├───┼───┼───┤")
        rows.append("  └───┴───┴───┘")
        return "\n".join(rows)

    for i, state in enumerate(steps):
        if i == 0:
            lines.append("  INITIAL BOARD")
        else:
            lines.append(f"  STEP {i}  (move tile {steps[i - 1][steps[i].index(0)]})")
        lines.append(fmt_board(state))
        lines.append("")

    lines.append("=" * 50)
    lines.append("  PUZZLE SOLVED ✓")
    lines.append("=" * 50)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
