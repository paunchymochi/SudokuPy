import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from typing import List, Dict
import random

class _Injection:
    def __init__(self, cell:Cell):
        self._cell = cell
        self._candidates = cell.candidates
        self._untried_candidates = cell.candidates.copy()
    
    def __repr__(self):
        return f'<InjectionCell value:{self._value} candidates:{self._candidates}>'
    
    @property
    def position(self):
        return (self._cell.row, self._cell.column)

    def guess(self) -> int:
        new_value = random.choice(self._untried_candidates)
        self._untried_candidates.remove(new_value)
        self._value = new_value
        self._cell.value = new_value
    
    def has_untried_candidates(self) -> bool:
        return len(self._untried_candidates) > 0


class Injector:

    def __init__(self, cells:Cells):
        self._cells = cells
        self._injection_cells: List[_Injection] = []
        self._guesses = 0
        self._popped = False
        self._backups = {}
    
    def inject(self):
        injection_cell = self._get_current_injection_cell()
        self._make_new_guess(injection_cell)
    
    def _get_current_injection_cell(self) -> _Injection:
        if self._guesses == 0:
            return self._make_new_injection_cell()
        
        injection_cell = self._get_next_unfilled_cell()

        if injection_cell is None:
            injection_cell = self._rollback_to_valid_injection_cell()

        return injection_cell
    
    def _rollback_to_valid_injection_cell(self) -> _Injection:
        while len(self._injection_cells) > 0:
            injection_cell = self._pop_injection_cell()
            if injection_cell.has_untried_candidates:
                return injection_cell
        raise ValueError('No Solution for board')
    
    def _make_new_injection_cell(self) -> _Injection:
        cell = self._get_next_unfilled_cell()
        injection_cell = _Injection(cell)
        self._save_backup(injection_cell)
        return injection_cell
    
    def _make_new_guess(self, injection_cell:_Injection):
        if self._popped:
            self._restore_backup(injection_cell)
            self._popped = False
        self._guesses += 1
        injection_cell.guess()
        self._push_injection_cell(injection_cell)
    
    def _push_injection_cell(self, injection_cell:_Injection):
        self._injection_cells.append(injection_cell)

    def _pop_injection_cell(self) -> _Injection:
        injection_cell = self._injection_cells.pop()
        self._popped = True
        return injection_cell

    def _save_backup(self, injection_cell:_Injection):
        position = injection_cell.position
        self._backups[position] = self._cells.get_candidates(True)
    
    def _retrieve_backup(self, injection_cell:_Injection):
        position = injection_cell.position
        return self._backups[position]
    
    def _restore_backup(self, injection_cell:_Injection):
        candidates = self._backups[injection_cell]
        self._cells.candidates = candidates
    
    def _get_next_unfilled_cell(self):
        # fill boxes clockwise starting from box[0, 0]
        boxes = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1) ]

        for (boxrow, boxcol) in boxes:
            cells = self._get_cells_in_box(boxrow, boxcol)
            for cell in cells:
                if cell.value == 0:
                    return cell
            return None
    
    def _get_cells_in_box(self, boxrow:int, boxcol:int) -> List[Cell]:
        box = self._cells[boxrow*3:boxrow*3+3, boxcol*3:boxcol*3+3]
        return box.flatten()
    
