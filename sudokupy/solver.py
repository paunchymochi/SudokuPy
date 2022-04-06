
import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from typing import List, Dict

def _validate_cells(cells:Cells):
    if len(cells) != 9:
        raise ValueError('cells must have 9 elements')
    if not isinstance(cells, Cells):
        print(f'type: {type(cells)}')
        raise TypeError('cells must be instance of Cells')
    
class _Companion:
    def __init__(self, cell:Cells, other=None):
        self.positions = []
        self.candidates = []
        self.companion = []
        self.skip = True
        self.valid = False
        self._init_other(other)
        if self._add(cell):
            self.skip = False
            self.valid = self._is_valid()
    
    def __repr__(self):
        return f'<_CandidateSet positions:{self.positions} companion:{self.companion}>'
    
    def __eq__(self, other):
        return len(self) == len(other) and all([pos in other.positions for pos in self.positions])
    
    def __len__(self):
        return len(self.positions)
    
    def _is_valid(self) -> bool:
        return len(self.positions) == len(self.companion)
    
    def _init_other(self, other):
        if other is None:
            return
        if not isinstance(other, type(self)):
            raise TypeError()
        self.positions = other.positions.copy()
        self.candidates = other.candidates.copy()
        self.companion = other.companion.copy()
    
    def _add(self, cell:Cells) -> bool:
        pos = self._get_position(cell)
        if pos in self.positions:
            return False
        
        if len(cell.candidates) == 0:
            return False
        
        candidates = self._get_candidates(cell)

        self.positions.append(pos)
        self.candidates.append(candidates)
        self.companion = list(set(self.companion+candidates))

        return True
    
    def _get_position(self, cell:Cell):
        return (cell.row, cell.column)
    
    def _get_candidates(self, cell:Cell):
        return cell.candidates

class CompanionDeducer:

    def __init__(self, cells:Cells):
        _validate_cells(cells)
        self.cells = cells
        self.affected_positions = []
        self._deduce()

    def _deduce(self):
        max_level = self._get_max_level(self.cells)
        self.companions = {}
        self.valid_companions = []
        self.level = 1

        self.companions[0] = [None]

        while self.level <= max_level and len(self.valid_companions) == 0:
            self.companions[self.level] = self._make_companions(self.cells, self.companions[self.level-1])
            self.level += 1
        
    def eliminate(self):
        affected_positions = []
        for valid_companion in self.valid_companions:
            result = self._eliminate_companion(valid_companion)
            affected_positions.extend(result)
        self.affected_positions = affected_positions
        return affected_positions
        
    def _eliminate_companion(self, valid_companion:_Companion):
        affected_positions = []
        for row in self.cells.data:
            for cell in row:
                position = (cell.row, cell.column)
                if position not in valid_companion.positions:
                    affected_positions.append((cell.row, cell.column))
                    cell.remove_candidates(valid_companion.companion)
        return affected_positions
        
    def _make_companions(self, cells:Cells, companions:List[_Companion]=None) -> List[_Companion]:
        if companions is None:
            companions = [None]
        new_companions = []
        cells_data = self._flatten_cells_data(cells.data)
        for other_companion in companions:
            for row in cells.data:
                for cell in row:
                    companion = _Companion(cell, other_companion)
                    if companion not in new_companions:
                        if not companion.skip:
                            new_companions.append(companion)
                        if companion.valid:
                            self.valid_companions.append(companion)
        return new_companions
    
    def _flatten_cells_data(self, cells_data):
        flattened = []
        for row in cells_data:
            for cell in row:
                flattened.append(cell)
        return flattened
    
    def _get_max_level(self, cells:Cells):
        values = cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return 8 - len(values)

class LineBoxDeducer:
    def __init__(self, cells:Cells, row=None, col=None):
        self.cells = cells
        if row is not None:
            self.line = cells[row]
        elif col is not None:
            self.line = cells[:, col]
        else:
            raise ValueError('must provide either row or col')
    
    def _get_boxes(self, row=None, col=None):
        rows = []
        cols = []
        toplefts = [0, 3, 6]
        if row is not None:
            rows = [(row//3)*3]
            cols = toplefts
        elif col is not None:
            cols = [(col//3)*3]
            rows = toplefts
        
        boxes = []
        for r in rows:
            for c in cols:
                boxes.append(self.cells[r:r+3, c:c+3])
        return boxes

class ValueDeducer:
    def __init__(self):
        pass

    def eliminate(self, cells:Cells):
        values = cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)

        for row in cells.data:
            for cell in row:
                cell.remove_candidates(values)
                if cell.value != 0:
                    cell.set_candidates([])

class Deducer:
    def __init__(self, cells: Cells):
        self.cells = cells

    def deduce_row(self, row:int):
        self._deduce_cells(self.cells[row])
    
    def deduce_column(self, col:int):
        self._deduce_cells(self.cells[:, col])
    
    def deduce_box(self, boxrow:int, boxcol:int):
        self._deduce_cells(self.cells[boxrow*3:boxrow*3+3,boxcol*3:boxcol*3+3])
    
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
        _validate_cells(cells)
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
        candidate_sets = _CandidateSets(cells)
        candidate_sets.eliminate()

    