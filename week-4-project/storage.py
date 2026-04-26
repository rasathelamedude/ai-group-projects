from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from config import HISTORY_FILE
from models import BOARD_ROW_COLUMN_REPRESENTATION, GenerationRecord, RunHistory


def reset_history(
    board_size: int,
    population_size: int,
    generations_requested: int,
    mutation_rate: float,
    path: Path = HISTORY_FILE,
) -> RunHistory:
    history = RunHistory(
        board_size=board_size,
        population_size=population_size,
        generations_requested=generations_requested,
        mutation_rate=mutation_rate,
        records=[],
    )
    _write_history(history, path)
    return history


def save_generation(
    record: GenerationRecord,
    board_size: int,
    population_size: int,
    generations_requested: int,
    mutation_rate: float,
    path: Path = HISTORY_FILE,
) -> RunHistory:
    history = load_history(path)

    if history is None:
        history = reset_history(
            board_size=board_size,
            population_size=population_size,
            generations_requested=generations_requested,
            mutation_rate=mutation_rate,
            path=path,
        )

    history.records.append(record)
    _write_history(history, path)
    return history


def load_history(path: Path = HISTORY_FILE) -> Optional[RunHistory]:
    if not path.exists():
        return None

    raw_data = json.loads(path.read_text(encoding="utf-8"))
    history = RunHistory.from_dict(raw_data)

    if history.representation != BOARD_ROW_COLUMN_REPRESENTATION:
        return None

    for record in history.records:
        genes = record.best_chromosome.genes
        if len(genes) != history.board_size:
            return None
        for row in genes:
            if any(not isinstance(column, int) for column in row):
                return None
            if any(column < 0 or column >= history.board_size for column in row):
                return None
            if len(row) != len(set(row)):
                return None

    return history


def clear_history(path: Path = HISTORY_FILE) -> None:
    if path.exists():
        path.unlink()


def _write_history(history: RunHistory, path: Path) -> None:
    path.write_text(json.dumps(history.to_dict(), indent=2), encoding="utf-8")
