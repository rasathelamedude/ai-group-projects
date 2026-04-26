from __future__ import annotations

import random

from config import (
    DEFAULT_BOARD_SIZE,
    DEFAULT_MUTATION_RATE,
    ELITE_RATIO,
    TOURNAMENT_SIZE,
)
from ga_core import get_conflicting_positions
from models import Chromosome


def select_parents(
    population: list[Chromosome],
    tournament_size: int = TOURNAMENT_SIZE,
) -> tuple[Chromosome, Chromosome]:
    return _tournament_pick(population, tournament_size), _tournament_pick(
        population, tournament_size
    )


def _tournament_pick(population: list[Chromosome], tournament_size: int) -> Chromosome:
    sample_size = min(tournament_size, len(population))
    contestants = random.sample(population, sample_size)
    return max(contestants, key=lambda chromosome: chromosome.fitness)


def crossover(
    parent1: Chromosome,
    parent2: Chromosome,
) -> tuple[Chromosome, Chromosome]:
    board_size = len(parent1.genes)
    if board_size < 2:
        return parent1.clone(), parent2.clone()

    split_point = random.randint(1, board_size - 1)

    child1 = Chromosome(
        genes=[row[:] for row in (parent1.genes[:split_point] + parent2.genes[split_point:])]
    )
    child2 = Chromosome(
        genes=[row[:] for row in (parent2.genes[:split_point] + parent1.genes[split_point:])]
    )
    return child1, child2


def mutate(
    chromosome: Chromosome,
    board_size: int = DEFAULT_BOARD_SIZE,
    mutation_rate: float = DEFAULT_MUTATION_RATE,
) -> Chromosome:
    genes = [row[:] for row in chromosome.genes]
    row_mutation_probability = min(1.0, mutation_rate * board_size)

    for row in range(board_size):
        if random.random() < row_mutation_probability:
            genes[row] = _mutate_row(genes[row], board_size)

    mutated = Chromosome(genes=genes)

    conflicting_positions = list(get_conflicting_positions(mutated, board_size))
    if conflicting_positions and random.random() < 0.70:
        conflict_row, conflict_col = random.choice(conflicting_positions)
        if conflict_col in mutated.genes[conflict_row]:
            mutated.genes[conflict_row].remove(conflict_col)

    if random.random() < 0.85:
        safe_positions = [
            (row, col)
            for row in range(board_size)
            for col in range(board_size)
            if col not in mutated.genes[row]
            and _is_safe_square(mutated.genes, row, col, board_size)
        ]
        if safe_positions:
            candidate_row, candidate_col = random.choice(safe_positions)
            mutated.genes[candidate_row].append(candidate_col)
            mutated.genes[candidate_row].sort()

    for row in range(board_size):
        mutated.genes[row] = sorted(set(mutated.genes[row]))

    if not any(mutated.genes):
        random_row = random.randrange(board_size)
        random_col = random.randrange(board_size)
        mutated.genes[random_row] = [random_col]

    return mutated


def build_next_population(
    population: list[Chromosome],
    population_size: int,
    board_size: int = DEFAULT_BOARD_SIZE,
    mutation_rate: float = DEFAULT_MUTATION_RATE,
    elite_ratio: float = ELITE_RATIO,
) -> list[Chromosome]:
    elite_count = max(2, int(population_size * elite_ratio))
    next_population = [chromosome.clone() for chromosome in population[:elite_count]]

    while len(next_population) < population_size:
        parent1, parent2 = select_parents(population)
        child1, child2 = crossover(parent1, parent2)
        next_population.append(mutate(child1, board_size, mutation_rate))

        if len(next_population) < population_size:
            next_population.append(mutate(child2, board_size, mutation_rate))

    return next_population


def _is_safe_square(
    genes: list[list[int]],
    candidate_row: int,
    candidate_col: int,
    board_size: int,
) -> bool:
    for row in range(board_size):
        for col in genes[row]:
            if abs(candidate_row - row) == abs(candidate_col - col):
                return False

    return True


def _mutate_row(row_values: list[int], board_size: int) -> list[int]:
    row = row_values[:]
    action = random.choice(["add", "remove", "move"])

    if action == "add":
        available_columns = [col for col in range(board_size) if col not in row]
        if available_columns:
            row.append(random.choice(available_columns))
    elif action == "remove":
        if row:
            row.remove(random.choice(row))
    else:
        if row:
            old_col = random.choice(row)
            row.remove(old_col)
            available_columns = [col for col in range(board_size) if col not in row]
            if available_columns:
                row.append(random.choice(available_columns))
            else:
                row.append(old_col)
        else:
            row.append(random.randrange(board_size))

    return sorted(set(row))
