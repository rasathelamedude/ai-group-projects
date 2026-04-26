from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from board_widget import BoardWidget
from ga_core import chromosome_to_positions, max_non_attacking_bishops
from models import RunHistory
from storage import load_history


class HistoryPanel(ttk.Frame):
    def __init__(self, parent: tk.Misc, board: BoardWidget, **kwargs):
        super().__init__(parent, **kwargs)
        self.board = board
        self.history: Optional[RunHistory] = None

        title_label = ttk.Label(self, text="Saved Best Generations", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_frame, height=18, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.details_label = ttk.Label(
            self,
            text="Pick a generation to display it on the board.",
            wraplength=320,
            justify="left",
        )
        self.details_label.pack(anchor="w", pady=(8, 0))

    def set_history(self, history: RunHistory) -> None:
        self.history = history
        self.board.set_board_size(history.board_size)

        self.listbox.delete(0, tk.END)
        for record in history.records:
            self.listbox.insert(tk.END, record.label())

        if history.records:
            self.show_latest()
        else:
            self.details_label.config(
                text="The saved history is empty. Run the algorithm to create drafts."
            )
            self.board.render(None)

    def append_record(self, history: RunHistory) -> None:
        self.set_history(history)

    def load_saved_history(self) -> Optional[RunHistory]:
        history = load_history()
        if history is not None:
            self.set_history(history)
        return history

    def show_latest(self) -> None:
        if self.history is None or not self.history.records:
            return

        last_index = len(self.history.records) - 1
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(last_index)
        self.listbox.see(last_index)
        self._show_record(last_index)

    def on_select(self, _event: tk.Event) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return

        self._show_record(selection[0])

    def _show_record(self, index: int) -> None:
        if self.history is None:
            return

        record = self.history.records[index]
        chromosome = record.best_chromosome
        positions = chromosome_to_positions(chromosome, self.history.board_size)
        target_bishops = max_non_attacking_bishops(self.history.board_size)
        self.board.render(chromosome)
        self.details_label.config(
            text=(
                f"Generation {record.generation_number}\n"
                f"Fitness: {chromosome.fitness}\n"
                f"Bishops: {chromosome.bishops}/{target_bishops}\n"
                f"Conflicts: {chromosome.conflicts}\n"
                f"Rows: {chromosome.genes}\n"
                f"Positions: {positions}"
            )
        )
