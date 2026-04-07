"""
puzzle_canvas.py — Member 4
Draws the 8-puzzle board on a tkinter Canvas with a modern dark theme.
"""

import tkinter as tk

# ── Visual constants ─────────────────────────────────────────────────────────
CELL = 110      # tile size in pixels
GAP  =   4      # gap between adjacent tiles
PAD  =  20      # padding around the whole grid

# Colour palette
BG        = "#0d0d1a"
TILE_BG   = "#1a2744"
TILE_FG   = "#e8eaf6"
BLANK_BG  = "#080f1e"
BORDER    = "#263a66"
ACCENT2   = "#00e5ff"
SUCCESS   = "#00e676"
GOLD      = "#ffd54f"
SHADOW    = "#050c1a"
TILE_TOP  = "#1f2f52"
GOAL_TILE = "#1e3a5f"
GOAL_TOP  = "#243d66"

# Goal positions for "is-this-tile-in-place?" highlighting
_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_POS = {tile: (i // 3, i % 3) for i, tile in enumerate(_GOAL)}


def make_canvas(parent: tk.Widget) -> tk.Canvas:
    """
    Create and return a tkinter Canvas sized to hold the 3×3 grid.
    The canvas uses the dark background colour with no border highlight.
    """
    size = 3 * CELL + 2 * GAP + 2 * PAD
    canvas = tk.Canvas(
        parent,
        width=size, height=size,
        bg=BG,
        highlightthickness=0,
    )
    return canvas


def draw_board(canvas: tk.Canvas, state: tuple,
               highlight_blank: bool = False,
               done: bool = False):
    """
    Render the 8-puzzle board onto ``canvas``.

    Args:
        canvas:          The tkinter Canvas to draw on.
        state:           9-tuple of tile values (0 = blank).
        highlight_blank: If True, tint the blank cell lightly (used during
                         animation to show movement).
        done:            If True, render a ★ in the blank cell and tint
                         correctly-placed tiles with SUCCESS green.
    """
    canvas.delete("all")

    for index, tile in enumerate(state):
        row, col = divmod(index, 3)

        x0 = PAD + col * (CELL + GAP)
        y0 = PAD + row * (CELL + GAP)
        x1 = x0 + CELL
        y1 = y0 + CELL
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        if tile == 0:
            _draw_blank(canvas, x0, y0, x1, y1, cx, cy,
                        highlight_blank, done)
        else:
            _draw_tile(canvas, x0, y0, x1, y1, cx, cy,
                       tile, index, done)


# ── Private helpers ───────────────────────────────────────────────────────────

def _draw_blank(canvas, x0, y0, x1, y1, cx, cy,
                highlight_blank: bool, done: bool):
    fill = "#0d2137" if (highlight_blank or done) else BLANK_BG
    canvas.create_rectangle(x0, y0, x1, y1,
                            fill=fill, outline=BORDER, width=2)
    if done:
        canvas.create_text(cx, cy, text="★",
                           fill=SUCCESS, font=("Helvetica", 36, "bold"))


def _draw_tile(canvas, x0, y0, x1, y1, cx, cy,
               tile: int, index: int, done: bool):
    """Draw a numbered tile with shadow + top-edge highlight."""
    is_in_place = (GOAL_POS[tile] == divmod(index, 3))
    base_color = GOAL_TILE if is_in_place else TILE_BG
    top_color  = GOAL_TOP  if is_in_place else TILE_TOP
    outline    = ACCENT2   if (is_in_place and done) else BORDER

    # Drop shadow
    canvas.create_rectangle(x0 + 3, y0 + 3, x1 + 3, y1 + 3,
                            fill=SHADOW, outline="")
    # Main tile body
    canvas.create_rectangle(x0, y0, x1, y1,
                            fill=base_color, outline=outline, width=2)
    # Top-edge shine (gradient simulation)
    canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y0 + 18,
                            fill=top_color, outline="")
    # Number label
    text_color = SUCCESS if (is_in_place and done) else TILE_FG
    canvas.create_text(cx, cy, text=str(tile),
                       fill=text_color,
                       font=("Helvetica", 34, "bold"))
