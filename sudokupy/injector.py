import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from typing import List, Dict
import random

class _Injection:
    def __init__(self, cell:Cell, board_candidates:List[List[int]]):
        self._cell = cell
        self._available_candidates = cell.candidates
        self._untried_candidates = cell.candidates.copy()
        self._board_candidates = board_candidates
    
    @property
    def cell(self) -> Cell:
        return self._cell
    
    @property
    def untried_candidates(self) -> List[List[int]]:
        return self._untried_candidates
    
    @property
    def available_candidates(self) -> List[List[int]]:
        return self._available_candidates
    
    def __repr__(self):
        return f'<InjectionCell value:{self._cell.value} available_candidates:{self._available_candidates} untried_candidates:{self._untried_candidates}>'
    
    def guess(self) -> int:
        if not self.has_untried_candidates():
            raise ValueError('No guesses left')
        new_value = random.choice(self._untried_candidates)
        self._untried_candidates.remove(new_value)
        self._value = new_value
        self._cell.value = new_value
    
    def has_untried_candidates(self) -> bool:
        return len(self._untried_candidates) > 0

class Injector:
    def __init__(self, cells:Cells):
        self._cells = cells
        self._injections: List[_Injection] = []
        self._popped = False
        self._history = []
    
    @property
    def injections(self):
        return self._injections
    
    def get_history(self):
        return self._history
    
    def get_injections(self):
        return self._injections
    
    def inject(self):
        injection = self._get_injection()
        injection.guess()
    
    def _get_injection(self) -> _Injection:
        self._popped = False
        injection = self._new_injection()
        while injection is None:
            if len(self._injections) == 0:
                raise ValueError('No Solution')
            injection = self._pop_injection()
        self._rollback_candidates(injection)
        return injection
    
    def _rollback_candidates(self, injection:_Injection):
        if self._popped:
            self._cells.candidates = injection._board_candidates
            self._append_injection(injection)
    
    def _pop_injection(self) -> _Injection:
        self._popped = True
        injection = self._injections.pop()
        self._history.append({'action': 'pop', 'injection': injection})
        injection.cell.value = 0
        if injection.has_untried_candidates():
            return injection
        else:
            return None
    
    def _new_injection(self) -> _Injection:
        cell = self._get_next_unfilled_cell()
        if cell is None:
            return None

        board_candidates = self._get_board_candidates()
        injection = _Injection(cell, board_candidates)
        self._append_injection(injection)
        return injection
    
    def _append_injection(self, injection:_Injection):
        self._history.append({'action': 'new', 'injection': injection})
        self._injections.append(injection)
    
    def _get_board_candidates(self) -> List[List[int]]:
        return self._cells.get_candidates(flatten=True)

    def _get_next_unfilled_cell(self) -> Cell:
        # fill boxes clockwise starting from box[0, 0]
        boxes = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1)]

        for (boxrow, boxcol) in boxes:
            cells = self._get_cells_in_box(boxrow, boxcol)
            for cell in cells:
                if cell.value == 0:
                    if len(cell.candidates) > 0:
                        return cell
        return None
    
    def _get_cells_in_box(self, boxrow:int, boxcol:int) -> List[Cell]:
        box = self._cells[boxrow*3:boxrow*3+3, boxcol*3:boxcol*3+3]
        return box.flatten()