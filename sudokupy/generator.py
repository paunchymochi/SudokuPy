import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.solver import Deducer
import random
from typing import List, Tuple

class Generator:
    def __init__(self, seed:int=None):
        self.board = Board()
        self.deducer = Deducer(self.board.cells)
        # self.generate(seed)
    
    def __repr__(self):
        return f'<Board\n{self.board.cells}\n\n{self.board.cells.print_candidates()}\n>'
    
    def __str__(self):
        return f'{self.board.cells.print_candidates()}'

    def _set_seed(self, seed:int=None):
        if seed is not None:
            random.seed(seed)
    
    def generate(self, seed:int=None):
        self._set_seed(seed)
        self._generate_diagonal_boxes()
        while not self._is_board_complete():
            self._deduce_resolve()
            self._set_cell_value()

    def _is_board_complete(self) -> bool:
        cells = self.board.cells.get_values(flatten=True)
        if 0 in cells:
            return False
        else:
            return True
    
    def _generate_diagonal_boxes(self):
        for i in range(3):
            self.board.box[i, i].set_values(self._generate_box_sequence())
    
    def _generate_box_sequence(self) -> List[int]:
        numbers = list(range(1, 10))
        random_numbers = []
        for _ in range(9):
            num = random.choice(numbers)
            numbers.remove(num)
            random_numbers.append(num)
        return random_numbers
    
    def _deduce_resolve(self):
        while True:
            self.deducer.deduce()
            while len(self.deducer.operations) > 0:
                self.deducer.eliminate()
                self.deducer.deduce()
            results = self.board.resolve()
            if len(results) == 0:
                break
        # while len(results) > 0:
        #     for pos in results:
        #         results.remove(pos)
        #         results2 = self.board.resolve_adjacent(pos[0], pos[1])
        #         results.extend(results2)
    
    def _set_cell_value(self):
        # x, y = self._get_random_unfilled_cell()
        x, y = self._get_next_unfilled_cell()
        candidates = self.board.cell[x, y].get_candidates(flatten=True)[0]
        value = random.choice(candidates)
        self.board.cell[x, y].set_values(value)
    
    def _get_next_unfilled_cell(self) -> Tuple[int, int]:
        # fill boxes clockwise starting from box[0, 1]
        boxes = [(0, 1), (0, 2), (1, 2), (2, 1), (2, 0)]

        for (boxrow, boxcol) in boxes:
            box = self.board.box[boxrow, boxcol]
            for row in range(3):
                for col in range(3):
                    cell = box.data[row][col]
                    if cell.value == 0:
                        return (cell.row, cell.column)

    def _get_random_unfilled_cell(self) -> Tuple[int, int]:
        while True:
            x = random.randrange(9)
            y = random.randrange(9)
            if self.board.cell[x, y].get_values(flatten=True) == [0]:
                return (x, y)
