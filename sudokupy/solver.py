
import sys
sys.path.append('..')
from sudokupy.cell import Cells

class CandidateSet:
    def __init__(self):
        raise NotImplementedError

class Deducer:
    def __init__(self, cells: Cells):
        self.cells = cells

    def deduce_row(self, row:int):
        self._deduce_cells(self.row[row])
    
    def deduce_column(self, col:int):
        self._deduce_cells(self.col[col])
    
    def deduce_box(self, boxrow:int, boxcol:int):
        self._deduce_cells(self.box[boxrow, boxcol])
    
    def deduce_adjacent(self, row:int, col:int):
        self.deduce_row(row)
        self.deduce_column(col)
        self.deduce_box(row//3, col//3)
    
    def deduce(self):
        for i in range(9):
            self.deduce_row(i)
            self.deduce_column(i)
        for i in range(3):
            for j in range(3):
                self.deduce_box(i, j)

    def _deduce_cells(self, cells:Cells):
        self._validate_deduce_input(cells)
        self._eliminate_values(cells)
        self._eliminate_sets(cells)
    
    def _eliminate_values(self, cells:Cells):
        values = cells.get_values(flatten=True)
        values = list(set(values))

        for row in cells.data:
            for cell in row:
                cell.remove_candidates(values)
                if cell.value != 0:
                    cell.set_candidates([])
    
    def _eliminate_sets(self, cells:Cells):
        raise NotImplementedError
