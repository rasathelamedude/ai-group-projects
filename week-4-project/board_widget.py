from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from config import DEFAULT_BOARD_SIZE
from ga_core import get_conflicting_positions
from models import Chromosome


class BoardWidget(ttk.Frame):
    def __init__(self, parent: tk.Misc, board_size: int = DEFAULT_BOARD_SIZE, **kwargs):
        super().__init__(parent, **kwargs)
        self.board_size = board_size
        self.cell_size = max(40, 480 // max(1, board_size))

        self.title_label = ttk.Label(self, text="Chess Board", font=("Segoe UI", 14, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 8))

        self.canvas = tk.Canvas(
            self,
            width=self.board_size * self.cell_size,
            height=self.board_size * self.cell_size,
            highlightthickness=1,
            highlightbackground="#999999",
            bg="white",
        )
        self.canvas.pack()

        self.legend_label = ttk.Label(
            self,
            text="Blue bishops are safe, red bishops are still in conflict.",
        )
        self.legend_label.pack(anchor="w", pady=(8, 0))

        self.render(None)

    def set_board_size(self, board_size: int) -> None:
        self.board_size = board_size
        self.cell_size = max(40, 480 // max(1, board_size))
        self.canvas.config(
            width=self.board_size * self.cell_size,
            height=self.board_size * self.cell_size,
        )
        self.render(None)

    def render(self, chromosome: Chromosome | None) -> None:
        self.canvas.delete("all")
        self._draw_grid()

        if chromosome is None:
            return

        conflicts = get_conflicting_positions(chromosome, self.board_size)

        for row, row_values in enumerate(chromosome.genes):
            for col in row_values:
                x1 = col * self.cell_size + 8
                y1 = row * self.cell_size + 8
                x2 = x1 + self.cell_size - 16
                y2 = y1 + self.cell_size - 16

                fill_color = "#cf3f3f" if (row, col) in conflicts else "#1f6aa5"
                self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, outline="")
                self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text="B",
                    fill="white",
                    font=("Segoe UI", max(12, self.cell_size // 3), "bold"),
                )

    def _draw_grid(self) -> None:
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
