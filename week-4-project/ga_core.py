from models import Chromosome, GenerationRecord
from typing import List
import random

BOARD_SIZE = 8


def create_chromosome() -> Chromosome:
    # TODO: random initial placement
    pass


def create_population(size: int) -> List[Chromosome]:
    # TODO: generate initial population
    pass


def calculate_fitness(chromosome: Chromosome) -> int:
    # TODO: count non-attacking bishop pairs
    pass


def evaluate_population(population: List[Chromosome]) -> List[Chromosome]:
    # TODO: apply calculate_fitness to each, return sorted
    pass
