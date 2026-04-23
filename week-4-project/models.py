from dataclasses import dataclass, field
from typing import List


@dataclass
class Chromosome:
    # A list of column positions, one per row
    # e.g. [2, 5, 0, 6] means bishop at (row0,col2), (row1,col5), etc.
    pass


@dataclass
class GenerationRecord:
    pass
