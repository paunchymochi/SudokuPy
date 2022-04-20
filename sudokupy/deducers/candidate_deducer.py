import sys
sys.path.append('../..')
from sudokupy.cell import Cell, Cells
from sudokupy.deducers.deducer_base import _BaseDeducer 
from typing import List

class SingleCandidateDeducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__('SingleCandidateDeducer')
        self._cells = cells
        self._checked_cells:List[Cell]=[]
    
    def deduce(self, sliced_cells:Cells):
        for cell in sliced_cells.flatten():
            if cell not in self._checked_cells:
                if len(cell.candidates) == 1:
                    self._deduce_adjacent(cell)
                    self._checked_cells.append(cell)
    
    def _deduce_adjacent(self, cell:Cell):
        row = cell.row
        col = cell.column

        rows = self._cells[row].flatten()
        cols = self._cells[:, col].flatten()
        topleft_row = (row//3) * 3
        topleft_col = (col//3) * 3
        boxes = self._cells[topleft_row:topleft_row+3, topleft_col:topleft_col+3].flatten()

        rows.remove(cell)
        cols.remove(cell)
        boxes.remove(cell)

        adjacent_cells = rows + cols + boxes

        candidate = cell.candidates[0]
        for adjacent_cell in adjacent_cells:
            if candidate in adjacent_cell.candidates:
                self._add_transaction(adjacent_cell, candidate)
