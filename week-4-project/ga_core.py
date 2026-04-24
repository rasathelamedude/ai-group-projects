from models import Chromosome, GenerationRecord
from typing import List
import random

BOARD_SIZE = 8

"""
The way bishop placement (a.k.a. chromosome) is represented is as follows:
- A chromosome is a list of 8 integers, where each integer index represents a rown on the board, and the value at that index represents the column where a bishop is placed in that row.

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


def create_chromosome() -> Chromosome:
    # Generate a random chromosome (bishop placement)
    return [random.randint(0, BOARD_SIZE - 1) for _ in range(BOARD_SIZE)]


def create_population(size: int) -> List[Chromosome]:
    # Generate initial population
    population: List[Chromosome] = []

    for _ in range(size):
        chromosome: Chromosome = create_chromosome()
        population.append(chromosome)

    return population


"""
The fitness of a chromosome is the number of non-attacking bishop pairs.
The more non-attacking pairs, the higher the fitness. 
"""


def calculate_fitness(chromosome: Chromosome) -> int:
    # Count non-attacking bishop pairs
    non_attacking_pairs = 0

    for i in range(BOARD_SIZE):
        for j in range(i + 1, BOARD_SIZE):
            # Check if bishops at row i and row j are attacking each other
            if not _is_attacking(chromosome, i, j):
                non_attacking_pairs += 1

    return non_attacking_pairs


"""
Two bishops are attacking each other if the difference in their column positions equals the difference in their row positions.
"""


def _is_attacking(chromosome: Chromosome, row1: int, row2: int) -> bool:
    # Check if bishops at row1 and row2 are attacking each other
    return abs(chromosome[row1] - chromosome[row2]) == abs(row1 - row2)


def evaluate_population(population: List[Chromosome]) -> List[Chromosome]:
    # Sort population by fitness (descending)
    return sorted(population, key=calculate_fitness, reverse=True)
