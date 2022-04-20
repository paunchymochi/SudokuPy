import sys
sys.path.append('../..')
from sudokupy.cell import Cells
from sudokupy.deducers.deducer_base import _BaseDeducer 

class ValueDeducer(_BaseDeducer):
    def __init__(self):
        super().__init__('ValueDeducer')
        self._cells_with_assigned_candidates = []
        self._cells_with_values = []
    
    def deduce(self, sliced_cells:Cells):
        self._validate_sliced_cells(sliced_cells)
        self._sliced_cells = sliced_cells

        values = self._get_values(sliced_cells)

        for cell in sliced_cells.flatten():
            candidates = cell.candidates
            if len(candidates) > 0:
                if cell.value != 0:
                    self._add_transaction(cell, remove_candidates=candidates)
                else:
                    candidates = [candidate for candidate in candidates if candidate in values]
                    if len(candidates) > 0:
                        self._add_transaction(cell, remove_candidates=candidates)
    
    def _get_values(self, sliced_cells:Cells):
        values = sliced_cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return values
