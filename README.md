# SudokuPy
> Sudoku Generator and Solver

## About
SudokuPy solves a board as a human would: by eliminating candidates using a series of deduction techniques, guessing when all clues are exhausted, and repeating until the puzzle is complete.

SudokuPy generates a board by filling in cells, deducing, undoing filling-in of cells if board becomes unsolvable, until a solved board is generated. Then it removes cell values, the number of which is determined by the difficulty setting. 

## Using SudokuPy

### Generating a Board

```python
from generator import Generator
g = Generator()
board = g.generate(seed=123)
```

### Solving a Board

```python
from solver import Solver
s = Solver()
solved_board = s.solve(board)
```