from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BOARD_ROW_COLUMN_REPRESENTATION = "row_column_lists_2d"


@dataclass
class Chromosome:
    genes: list[list[int]] = field(default_factory=list)
    fitness: int = 0
    bishops: int = 0
    conflicts: int = 0

    def clone(self) -> "Chromosome":
        return Chromosome(
            genes=[row[:] for row in self.genes],
            fitness=self.fitness,
            bishops=self.bishops,
            conflicts=self.conflicts,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "genes": self.genes,
            "fitness": self.fitness,
            "bishops": self.bishops,
            "conflicts": self.conflicts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chromosome":
        return cls(
            genes=[list(row) for row in data.get("genes", [])],
            fitness=int(data.get("fitness", 0)),
            bishops=int(data.get("bishops", 0)),
            conflicts=int(data.get("conflicts", 0)),
        )


@dataclass
class GenerationRecord:
    generation_number: int
    best_chromosome: Chromosome

    def label(self) -> str:
        return (
            f"Gen {self.generation_number:03d} | "
            f"fitness {self.best_chromosome.fitness:>5} | "
            f"bishops {self.best_chromosome.bishops:>2} | "
            f"conflicts {self.best_chromosome.conflicts}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "generation_number": self.generation_number,
            "best_chromosome": self.best_chromosome.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationRecord":
        return cls(
            generation_number=int(data.get("generation_number", 0)),
            best_chromosome=Chromosome.from_dict(data.get("best_chromosome", {})),
        )


@dataclass
class RunHistory:
    board_size: int
    population_size: int
    generations_requested: int
    mutation_rate: float
    representation: str = BOARD_ROW_COLUMN_REPRESENTATION
    records: list[GenerationRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "board_size": self.board_size,
            "population_size": self.population_size,
            "generations_requested": self.generations_requested,
            "mutation_rate": self.mutation_rate,
            "representation": self.representation,
            "records": [record.to_dict() for record in self.records],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunHistory":
        return cls(
            board_size=int(data.get("board_size", 8)),
            population_size=int(data.get("population_size", 0)),
            generations_requested=int(data.get("generations_requested", 0)),
            mutation_rate=float(data.get("mutation_rate", 0.0)),
            representation=str(data.get("representation", "")),
            records=[
                GenerationRecord.from_dict(item)
                for item in data.get("records", [])
            ],
        )
