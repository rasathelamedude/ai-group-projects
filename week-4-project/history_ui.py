import tkinter as tk
from models import GenerationRecord
from board_ui import BoardUi
from storage import load_all_generations
from typing import List


class HistoryPanel(tk.Frame):
    # Constructor
    def __init__(self, parent, board: BoardUi, **kwargs):
        super().__init__(parent, **kwargs)
        self.board = board
        # TODO: build listbox of past generations
        pass

    def load(self) -> None:
        # TODO: call load_all_generations(), populate listbox
        pass

    def on_select(self, event) -> None:
        # TODO: get selected GenerationRecord, call self.board.render()
        pass
