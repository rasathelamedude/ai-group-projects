from __future__ import annotations

from models import Chromosome
from typing import List
import random
from config import DEFAULT_BOARD_SIZE, DEFAULT_INITIAL_DENSITY

BOARD_SIZE = DEFAULT_BOARD_SIZE

"""
The way bishop placement (a.k.a. chromosome) is represented is as follows:
- A chromosome is a list of 8 integers, where each integer index represents a row on the board, and the value at that index represents the column where a bishop is placed in that row.

For example, the chromosome [0, 2, 4, 6, 1, 3, 5, 7] represents the following board configuration:
- Row 0: Bishop at column 0
- Row 1: Bishop at column 2
- Row 2: Bishop at column 4
- Row 3: Bishop at column 6
- Row 4: Bishop at column 1
- Row 5: Bishop at column 3
- Row 6: Bishop at column 5
- Row 7: Bishop at column 7
"""


def board_cell_count(board_size: int = BOARD_SIZE) -> int:
    # Total number of cells on the board
    return board_size * board_size


def _normalize_row(row: List[int], board_size: int) -> List[int]:
    # Only return columns that are integers and are between 0 and board_size - 1
    valid_columns = {
        col for col in row if isinstance(col, int) and 0 <= col < board_size
    }

    return sorted(valid_columns)


# Calculate the maximum number of bishops that can be placed on the board without attacking each other
def max_non_attacking_bishops(board_size: int = BOARD_SIZE) -> int:
    if board_size <= 0:
        return 0
    if board_size == 1:
        return 1

    return 2 * board_size - 2


"""
Two bishops are attacking each other if the difference in their column positions equals the difference in their row positions.
"""


def _is_attacking(chromosome: Chromosome, first_row: int, second_row: int) -> bool:
    # Check if bishops at row1 and row2 are attacking each other

    return abs(first_row - second_row) == abs(
        chromosome.genes[first_row][0] - chromosome.genes[second_row][0]
    )


# Convert a chromosome to a list of tuples (row, col) representing the positions of the bishops on the board
def chromosome_to_positions(
    chromosome: Chromosome,
    board_size: int = BOARD_SIZE,
) -> list[tuple[int, int]]:
    return [
        (row_index, col_index)
        for row_index, row in enumerate(chromosome.genes[:board_size])
        for col_index in row
    ]


def active_positions(chromosome: Chromosome) -> List[tuple[int, int]]:
    return chromosome_to_positions(chromosome)


def create_chromosome(
    board_size: int = DEFAULT_BOARD_SIZE,
    fill_probability: float = DEFAULT_INITIAL_DENSITY,
) -> Chromosome:
    # Generate a random chromosome (bishop placement)
    genes = [
        [col for col in range(board_size) if random.random() < fill_probability]
        for _ in range(board_size)
    ]

    genes = [_normalize_row(row, board_size) for row in genes]

    if not any(genes):
        random_row = random.randrange(board_size)
        random_col = random.randrange(board_size)
        genes[random_row] = [random_col]

    return Chromosome(genes=genes)


def create_population(
    size: int, board_size: int = DEFAULT_BOARD_SIZE
) -> List[Chromosome]:
    # Generate initial population
    population: List[Chromosome] = []

    for _ in range(size):
        chromosome: Chromosome = create_chromosome(board_size=board_size)
        population.append(chromosome)

    return population


"""
The fitness of a chromosome is the number of non-attacking bishop pairs.
The more non-attacking pairs, the higher the fitness. 
"""


def calculate_fitness(chromosome: Chromosome, board_size: int = BOARD_SIZE) -> int:
    # Count non-attacking bishop pairs
    bishop_count: int = sum(len(row) for row in chromosome.genes)
    conflict_count: int = 0
    positions: List[tuple[int, int]] = active_positions(chromosome)

    for position_index, first_position in enumerate(positions):
        first_row, first_col = first_position

        for second_position in positions[position_index + 1 :]:
            second_row, second_col = second_position

            if _is_attacking(chromosome, first_row, second_row):
                conflict_count += 1

    conflict_penalty = (board_cell_count(board_size) + 1) * 100
    chromosome.bishops = bishop_count
    chromosome.conflicts = conflict_count
    chromosome.fitness = (bishop_count * 100) - (conflict_count * conflict_penalty)

    return chromosome.fitness


def evaluate_population(
    population: List[Chromosome], board_size: int = BOARD_SIZE
) -> List[Chromosome]:
    # Sort population by fitness (descending)
    for chromosome in population:
        calculate_fitness(chromosome, board_size)

    return sorted(population, key=lambda chromosome: chromosome.fitness, reverse=True)


def get_conflicting_positions(
    chromosome: Chromosome,
    board_size: int = DEFAULT_BOARD_SIZE,
) -> set[tuple[int, int]]:
    conflicts: set[tuple[int, int]] = set()
    positions: List[tuple[int, int]] = active_positions(chromosome)

    for position_index, first_position in enumerate(positions):
        first_row, first_col = first_position
        for second_position in positions[position_index + 1 :]:
            second_row, second_col = second_position
            if _is_attacking(chromosome, first_row, second_row):
                conflicts.add(first_position)
                conflicts.add(second_position)

    return conflicts


def solution_test(
    chromosome: Chromosome,
    board_size: int = DEFAULT_BOARD_SIZE,
) -> bool:
    calculate_fitness(chromosome, board_size)

    return (
        chromosome.conflicts == 0
        and chromosome.bishops == max_non_attacking_bishops(board_size)
    )
