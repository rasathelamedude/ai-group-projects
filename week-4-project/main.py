from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from board_widget import BoardWidget
from config import (
    APP_TITLE,
    DEFAULT_BOARD_SIZE,
    DEFAULT_DELAY_MS,
    DEFAULT_GENERATIONS,
    DEFAULT_MUTATION_RATE,
    DEFAULT_POPULATION_SIZE,
)
from ga_core import (
    create_population,
    evaluate_population,
    max_non_attacking_bishops,
    solution_test,
)
from ga_operators import build_next_population
from history_ui import HistoryPanel
from models import GenerationRecord, RunHistory
from storage import clear_history, load_history, reset_history, save_generation


class NBishopApp(ttk.Frame):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, padding=12)
        self.parent = parent
        self.pack(fill="both", expand=True)

        self.worker_thread: threading.Thread | None = None
        self.message_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.is_running = False

        self.board_size_var = tk.IntVar(value=DEFAULT_BOARD_SIZE)
        self.population_var = tk.IntVar(value=DEFAULT_POPULATION_SIZE)
        self.generations_var = tk.IntVar(value=DEFAULT_GENERATIONS)
        self.mutation_var = tk.DoubleVar(value=DEFAULT_MUTATION_RATE)
        self.delay_var = tk.IntVar(value=DEFAULT_DELAY_MS)

        self.status_var = tk.StringVar(value="Ready.")
        self.live_var = tk.StringVar(
            value="Run the genetic algorithm to evolve bishop arrangements and review the best chromosome from each generation."
        )

        self._build_layout()
        self.after(100, self._poll_queue)
        self._load_existing_history()

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.board = BoardWidget(self, board_size=self.board_size_var.get())
        self.board.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        sidebar = ttk.Frame(self)
        sidebar.grid(row=0, column=1, sticky="ns")

        controls = ttk.LabelFrame(sidebar, text="Genetic Algorithm Controls", padding=12)
        controls.pack(fill="x")

        ttk.Label(controls, text="Board size").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(controls, from_=4, to=12, textvariable=self.board_size_var, width=10).grid(
            row=0, column=1, sticky="ew", pady=2
        )

        ttk.Label(controls, text="Population").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(controls, from_=20, to=300, increment=10, textvariable=self.population_var, width=10).grid(
            row=1, column=1, sticky="ew", pady=2
        )

        ttk.Label(controls, text="Generations").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(controls, from_=20, to=500, increment=10, textvariable=self.generations_var, width=10).grid(
            row=2, column=1, sticky="ew", pady=2
        )

        ttk.Label(controls, text="Mutation rate").grid(row=3, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.mutation_var, width=12).grid(
            row=3, column=1, sticky="ew", pady=2
        )

        ttk.Label(controls, text="Delay (ms)").grid(row=4, column=0, sticky="w")
        ttk.Spinbox(controls, from_=0, to=1000, increment=20, textvariable=self.delay_var, width=10).grid(
            row=4, column=1, sticky="ew", pady=2
        )

        controls.columnconfigure(1, weight=1)

        button_row = ttk.Frame(controls)
        button_row.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        button_row.columnconfigure(0, weight=1)

        self.run_button = ttk.Button(button_row, text="Run Genetic Algorithm", command=self.run_algorithm)
        self.run_button.grid(row=0, column=0, sticky="ew")

        self.load_button = ttk.Button(button_row, text="Load Saved History", command=self._load_existing_history)
        self.load_button.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        self.clear_button = ttk.Button(button_row, text="Clear Saved History", command=self._clear_saved_history)
        self.clear_button.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        ttk.Label(sidebar, textvariable=self.live_var, wraplength=340, justify="left").pack(
            fill="x", pady=(12, 0)
        )
        ttk.Label(sidebar, textvariable=self.status_var, wraplength=340, justify="left").pack(
            fill="x", pady=(8, 12)
        )

        self.history_panel = HistoryPanel(sidebar, board=self.board)
        self.history_panel.pack(fill="both", expand=True)

    def run_algorithm(self) -> None:
        if self.is_running:
            return

        try:
            board_size = int(self.board_size_var.get())
            population_size = int(self.population_var.get())
            generations = int(self.generations_var.get())
            mutation_rate = float(self.mutation_var.get())
            delay_ms = int(self.delay_var.get())
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
            return

        if mutation_rate < 0 or mutation_rate > 1:
            messagebox.showerror("Invalid Input", "Mutation rate must be between 0 and 1.")
            return

        self.is_running = True
        self.run_button.config(state="disabled")
        self.load_button.config(state="disabled")
        self.clear_button.config(state="disabled")
        self.status_var.set("Running genetic algorithm...")
        self.live_var.set("Starting population...")

        history = reset_history(board_size, population_size, generations, mutation_rate)
        self.history_panel.set_history(history)

        self.worker_thread = threading.Thread(
            target=self._run_worker,
            args=(board_size, population_size, generations, mutation_rate, delay_ms),
            daemon=True,
        )
        self.worker_thread.start()

    def _run_worker(
        self,
        board_size: int,
        population_size: int,
        generations: int,
        mutation_rate: float,
        delay_ms: int,
    ) -> None:
        population = create_population(population_size, board_size)
        target_bishops = max_non_attacking_bishops(board_size)
        best_record: GenerationRecord | None = None

        for generation in range(generations):
            population = evaluate_population(population, board_size)
            best_chromosome = population[0].clone()
            best_record = GenerationRecord(generation_number=generation + 1, best_chromosome=best_chromosome)

            history = save_generation(
                record=best_record,
                board_size=board_size,
                population_size=population_size,
                generations_requested=generations,
                mutation_rate=mutation_rate,
            )
            self.message_queue.put(("generation", history))

            if solution_test(best_chromosome, board_size):
                self.message_queue.put(
                    (
                        "done",
                        (
                            f"Reached the optimum of {target_bishops} bishops with no conflicts "
                            f"at generation {generation + 1}."
                        ),
                    )
                )
                return

            if generation < generations - 1:
                population = build_next_population(
                    population=population,
                    population_size=population_size,
                    board_size=board_size,
                    mutation_rate=mutation_rate,
                )

            if delay_ms > 0:
                time.sleep(delay_ms / 1000)

        if best_record is None:
            self.message_queue.put(("done", "No generations were produced."))
            return

        self.message_queue.put(
            (
                "done",
                (
                    f"Finished {generations} generations. Best result: "
                    f"fitness {best_record.best_chromosome.fitness}, "
                    f"bishops {best_record.best_chromosome.bishops}/{target_bishops}, "
                    f"conflicts {best_record.best_chromosome.conflicts}."
                ),
            )
        )

    def _poll_queue(self) -> None:
        while not self.message_queue.empty():
            message_type, payload = self.message_queue.get()

            if message_type == "generation":
                history = payload
                if isinstance(history, RunHistory):
                    self.history_panel.append_record(history)
                    if history.records:
                        latest = history.records[-1].best_chromosome
                        target_bishops = max_non_attacking_bishops(history.board_size)
                        self.live_var.set(
                            f"Generation {history.records[-1].generation_number}: "
                            f"fitness {latest.fitness}, "
                            f"bishops {latest.bishops}/{target_bishops}, "
                            f"conflicts {latest.conflicts}"
                        )

            if message_type == "done":
                self.is_running = False
                self.run_button.config(state="normal")
                self.load_button.config(state="normal")
                self.clear_button.config(state="normal")
                self.status_var.set(str(payload))

        self.after(100, self._poll_queue)

    def _load_existing_history(self) -> None:
        history = load_history()
        if history is None:
            self.status_var.set("No compatible saved generations found yet.")
            return

        self.history_panel.set_history(history)
        self.status_var.set(f"Loaded {len(history.records)} saved generations from disk.")
        if history.records:
            latest = history.records[-1].best_chromosome
            target_bishops = max_non_attacking_bishops(history.board_size)
            self.live_var.set(
                f"Latest saved result: fitness {latest.fitness}, "
                f"bishops {latest.bishops}/{target_bishops}, "
                f"conflicts {latest.conflicts}"
            )

    def _clear_saved_history(self) -> None:
        if self.is_running:
            return

        clear_history()
        empty_history = RunHistory(
            board_size=self.board_size_var.get(),
            population_size=0,
            generations_requested=0,
            mutation_rate=0.0,
            records=[],
        )
        self.history_panel.set_history(empty_history)
        self.status_var.set("Saved history cleared.")
        self.live_var.set(
            "Run the genetic algorithm to evolve bishop arrangements and review the best chromosome from each generation."
        )


def main() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)
    root.minsize(980, 680)
    NBishopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
