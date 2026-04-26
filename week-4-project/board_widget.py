import tkinter as tk
from models import Chromosome

BOARD_SIZE = 8


class BoardWidget(tk.Frame):
    # Constructor
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # TODO: build canvas, draw grid
        pass

    def render(self, chromosome: Chromosome) -> None:
        # TODO: clear board and place bishop icons at gene positions
        pass
