from models import Chromosome
from typing import List, Tuple


def select_parents(population: List[Chromosome]) -> Tuple[Chromosome, Chromosome]:
    # TODO: selection strategy (tournament, roulette, etc.)
    pass


def crossover(
    parent1: Chromosome, parent2: Chromosome
) -> Tuple[Chromosome, Chromosome]:
    # TODO: produce two children from two parents
    pass


def mutate(chromosome: Chromosome, mutation_rate: float = 0.1) -> Chromosome:
    # TODO: randomly alter genes
    pass
