# N-Bishop Genetic Algorithm Visualizer

## Project Purpose

This project is mainly an Artificial Intelligence / Genetic Algorithm project, not a chess game. The chessboard is only used to visualize the result.

The goal is to build a Python application that uses a Genetic Algorithm to find the best arrangement of bishops on an `N x N` chessboard so that bishops do not attack each other, while saving and displaying the best solution from every generation.

## What The Application Does

The program follows the same GA workflow described in the lecture:

1. Create many random chessboard solutions
2. Treat each solution as a chromosome
3. Calculate fitness for every chromosome
4. Select the better chromosomes
5. Apply crossover and mutation
6. Create new generations
7. Save the best solution from each generation
8. Show the selected generation on a chessboard

## Why This Version Matches The Real Requirement

The original requirement says:

`Use a genetic algorithm to place as many bishops as possible on a chessboard without any bishop threatening another.`

Because of that, this project does not use the simplified "one bishop per row with exactly one bishop" representation. Instead, it uses a full `2D` chromosome where each inner array belongs to one row and stores the column numbers that contain bishops. This allows the algorithm to place more or fewer bishops and therefore search for the maximum number of safe bishops.

## Chromosome Representation

This project stores each solution as a `2D` array of row data.

Meaning:

- the outer array represents the board rows
- each inner array contains the column numbers that have bishops in that row
- an empty inner array means that row has no bishops

Example for a `4 x 4` board:

```python
[
    [1, 3],
    [2],
    [],
    [0],
]
```

This means:

- row `0` has bishops in columns `1` and `3`
- row `1` has a bishop in column `2`
- row `2` has no bishops
- row `3` has a bishop in column `0`

For an `8 x 8` board, the chromosome has `8` inner arrays, one for each row.

This is still a full candidate board arrangement, but it is easier to read and explain than a flattened `1D` list.

## Fitness Function

The fitness function measures how good a candidate board is.

It rewards:

- more bishops on the board

It penalizes:

- diagonal conflicts between bishops

Formula:

`fitness = (bishop_count * 100) - (conflict_count * conflict_penalty)`

Two bishops attack each other when:

`abs(row1 - row2) == abs(col1 - col2)`

The conflict penalty is intentionally large so that conflict-free solutions are ranked above boards that place a few extra bishops but still contain attacks.

## GA Components Implemented

The code clearly includes the GA topics required by the lecture:

- Population generation
- Chromosome / candidate representation
- Fitness evaluation
- Parent selection using tournament selection
- Crossover using row-based single-point crossover
- Mutation using add, remove, or move changes inside rows
- Generation-by-generation evolution
- Best solution selection
- Solution test

The solution test checks whether:

- there are no conflicts
- the known maximum number of bishops has been reached

For an `N x N` board with `N > 1`, the maximum number of non-attacking bishops is:

`2N - 2`

## Saved Generation History

The application saves the best chromosome from every generation in `generations.json`.

Each saved record includes:

- generation number
- best chromosome genes
- fitness value
- bishop count
- conflict count

The user can load this history, pick any saved generation from the list, and display that exact board on the chessboard.

## Project Files

- `main.py`: application entry point and GA generation loop
- `ga_core.py`: chromosome creation, fitness calculation, solution test, evaluation
- `ga_operators.py`: parent selection, crossover, mutation, next generation creation
- `storage.py`: save and load generation history
- `board_widget.py`: chessboard visualization
- `history_ui.py`: saved-generation list and selection panel
- `models.py`: shared data classes
- `config.py`: application settings and default parameters

## How To Run

```bash
python main.py
```
