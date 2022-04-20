import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.deducers.deducer import Deducer
from sudokupy.injector import Injector
from sudokupy.cell import Cell, Cells
import random
from typing import List, Tuple
from enum import Enum

class Difficulty(Enum):
    Easy=1
    Medium=2
    Hard=3
    Expert=4
    Evil=5

class CellValuesRemover:
    def __init__(self, cells:Cells, difficulty:Difficulty=Difficulty.Medium, seed:int=None):
        self._cells = cells
        self.set_difficulty(difficulty)
        self._reset(seed)
    
    def set_difficulty(self, difficulty:Difficulty):
        self._difficulty = difficulty
    def set_difficulty_easy(self):
        self.set_difficulty(Difficulty.Easy)
    def set_difficulty_medium(self):
        self.set_difficulty(Difficulty.Medium)
    def set_difficulty_hard(self):
        self.set_difficulty(Difficulty.Hard)
    def set_difficulty_expert(self):
        self.set_difficulty(Difficulty.Expert)
    def set_difficulty_evil(self):
        self.set_difficulty(Difficulty.Evil)
    
    def remove(self, seed:int=None) -> Cells:
        self._set_seed(seed)
        cells = self._cells.copy()
        cells.candidates = list(range(1, 10))
        filled_cells = self._get_filled_cells(cells)
        removal_count = self._get_removal_count(self._difficulty)

        for _ in range(removal_count):
            self._remove_cell(filled_cells)

        return cells

    def _get_filled_cells(self, cells:Cells):
        filled_cells = []
        cell_list = cells.flatten()
        for cell in cell_list:
            if cell.value != 0:
                filled_cells.append(cell)
        return filled_cells

    def _remove_cell(self, filled_cells:List[Cell]):
        cell = self._get_removal_cell(filled_cells)
        cell.value = 0
    
    def _get_removal_cell(self, filled_cells:List[Cell]) -> Cell:
        cell = random.choice(filled_cells)
        filled_cells.remove(cell)
        return cell

    def _get_removal_count(self, difficulty:Difficulty) -> int:
        if difficulty == Difficulty.Easy:
            return random.choice(range(42, 46))
        elif difficulty == Difficulty.Medium:
            return random.choice(range(48, 53))
        elif difficulty == Difficulty.Hard:
            return random.choice(range(53, 57))
        elif difficulty == Difficulty.Expert:
            return random.choice(range(57, 60))
        elif difficulty == Difficulty.Evil:
            return random.choice(range(60, 64))

    def _reset(self, seed:int=None):
        self._set_seed(seed)

    def _set_seed(self, seed:int=None):
        if seed is not None:
            random.seed(seed)

class BoardGenerator:
    def __init__(self, seed:int=None):
        self._reset(seed)
    
    def __repr__(self):
        return f'<Board\n{self._board.cells}\n\n{self._board.cells.print_candidates()}\n>'
    
    def __str__(self):
        return f'{self._board.cells.print_candidates()}'

    def _set_seed(self, seed:int=None):
        if seed is not None:
            random.seed(seed)
    
    def _reset(self, seed:int=None):
        self._board = Board()
        self._deducer = Deducer(self._board.cells)
        self._injector = Injector(self._board.cells)
        self._set_seed(seed)
    
    def generate(self, seed:int=None):
        self._reset(seed)
        self._generate_diagonal_boxes()
        while not self._is_board_complete():
            self._deduce()
            self._inject()
        return self._is_board_complete()

    def _is_board_complete(self) -> bool:
        cells = self._board.cells.get_values(flatten=True)
        if 0 in cells:
            return False
        else:
            return True
    
    def _generate_diagonal_boxes(self):
        for i in range(3):
            self._board.box[i, i].set_values(self._generate_box_sequence())
    
    def _generate_box_sequence(self) -> List[int]:
        numbers = list(range(1, 10))
        random_numbers = []
        for _ in range(9):
            num = random.choice(numbers)
            numbers.remove(num)
            random_numbers.append(num)
        return random_numbers
    
    def _deduce(self):
        self._deducer.deduce()
        while len(self._deducer.transactions) > 0:
            self._deducer.eliminate()
            self._deducer.deduce()
    
    def _inject(self):
        self._injector.inject()
    
    def _get_next_unfilled_cell(self) -> Cell:
        # fill boxes clockwise starting from box[0, 1]
        boxes = [(0, 1), (0, 2), (1, 2), (2, 1), (2, 0)]

        for (boxrow, boxcol) in boxes:
            box = self._board.box[boxrow, boxcol]
            for row in range(3):
                for col in range(3):
                    cell = box.data[row][col]
                    if cell.value == 0:
                        return cell

    def _get_random_unfilled_cell(self) -> Tuple[int, int]:
        while True:
            x = random.randrange(9)
            y = random.randrange(9)
            if self._board.cell[x, y].get_values(flatten=True) == [0]:
                return (x, y)
