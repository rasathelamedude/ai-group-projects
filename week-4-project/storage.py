from models import GenerationRecord
from typing import List
import json

SAVE_FILE_NAME = "generations.json"


def save_generation(record: GenerationRecord) -> None:
    # TODO: append record to JSON file
    pass


def load_all_generations() -> List[GenerationRecord]:
    # TODO: read and deserialize all records from file
    pass
