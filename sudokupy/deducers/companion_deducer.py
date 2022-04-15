import sys
sys.path.append('../..')
from sudokupy.cell import Cell, Cells
from sudokupy.deducers.deducer_base import _BaseDeducer 
from typing import List

class _Companion:
    __slots__ = ['cells', 'candidates', 'companion', 'skip', 'valid']
    def __init__(self, cell:Cell, other=None, max_level:int=3):
        self.cells:List[Cell] = []
        self.candidates = []
        self.companion = []
        self.skip = True
        self.valid = False
        if not self._validate_cell(cell, max_level):
            return
        self._init_other(other)
        if self._add(cell):
            self.skip = False
            self.valid = self._is_valid()
    
    def __repr__(self):
        return f'<_Companion cells:{self.cells} companion:{self.companion}>'
    
    def __eq__(self, other):
        return len(self) == len(other) and all([cell in other.cells for cell in self.cells])
    
    def __len__(self):
        return len(self.cells)
    
    def _is_valid(self) -> bool:
        return len(self.cells) == len(self.companion)
    
    def _init_other(self, other):
        if other is None:
            return
        if not isinstance(other, type(self)):
            raise TypeError()
        self.cells = other.cells.copy()
        self.candidates = other.candidates.copy()
        self.companion = other.companion.copy()
    
    def _add(self, cell:Cell) -> bool:
        if cell in self.cells:
            return False
        
        candidates = cell.candidates

        self.cells.append(cell)
        self.candidates.append(candidates)
        self.companion = list(set(self.companion+candidates))

        return True
    
    def _validate_cell(self, cell:Cell, max_level:int) -> bool:
        if len(cell.candidates) == 0:
            return False
        if len(cell.candidates) > max_level:
            return False
        return True
    
    
class CompanionDeducer(_BaseDeducer):

    def __init__(self):
        super().__init__()

    def deduce(self, sliced_cells:Cells, max_companion_count:int=3):
        self._transactions_in_current_slice = False

        max_level = self._get_max_level(sliced_cells, max_companion_count)
        companions = {}
        level = 1

        companions[0] = [None]

        flattened_sliced_cells = sliced_cells.flatten()

        while level <= max_level and not self._transactions_in_current_slice:
            companions[level] = self._make_companions(flattened_sliced_cells, 
                    companions[level-1], max_level)
            level += 1
        
    def _make_companions(self, flattened_sliced_cells:List[Cell], 
            companions:List[_Companion]=None, 
            max_level:int=3) -> List[_Companion]:
        if companions is None:
            companions = [None]
        new_companions = []
        for other_companion in companions:
            for cell in flattened_sliced_cells:
                if len(cell.candidates) > max_level:
                    continue
                companion = _Companion(cell, other_companion, max_level)
                if companion.skip:
                    continue
                if companion not in new_companions:
                    new_companions.append(companion)
                if companion.valid:
                    self._make_new_transactions(companion, flattened_sliced_cells)
        return new_companions
    
    def _make_new_transactions(self, companion:_Companion, flattened_sliced_cells:List[Cell]):
        for cell in flattened_sliced_cells:
            if cell not in companion.cells:
                if any([candidate in companion.companion for candidate in cell.candidates]):
                    self._transactions_in_current_slice = True
                    self._add_transaction(cell, remove_candidates=companion.companion)
    
    def _get_max_level(self, cells:Cells, max_companion_count:int):
        values = cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return min(8 - len(values), max_companion_count)
