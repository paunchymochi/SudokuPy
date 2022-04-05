
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
    
class _CandidateSet:
    def __init__(self, cell:Cells, other=None):
        self.positions = []
        self.candidates = []
        self.candidate_set = []
        self.skip = True
        self.valid = False
        self._init_other(other)
        if self._add(cell):
            self.skip = False
            self.valid = self._is_valid()
    
    def __repr__(self):
        return f'<_CandidateSet positions:{self.positions} candidate_set:{self.candidate_set}>'
    
    def __eq__(self, other):
        return len(self) == len(other) and all([pos in other.positions for pos in self.positions])
    
    def __len__(self):
        return len(self.positions)
    
    def _is_valid(self) -> bool:
        return len(self.positions) == len(self.candidate_set)
    
    def _init_other(self, other):
        if other is None:
            return
        if not isinstance(other, type(self)):
            raise TypeError()
        self.positions = other.positions.copy()
        self.candidates = other.candidates.copy()
        self.candidate_set = other.candidate_set.copy()
    
    def _add(self, cell:Cells) -> bool:
        pos = self._get_position(cell)
        if pos in self.positions:
            return False
        
        if len(cell.candidates) == 0:
            return False
        
        candidates = self._get_candidates(cell)

        self.positions.append(pos)
        self.candidates.append(candidates)
        self.candidate_set = list(set(self.candidate_set+candidates))

        return True
    
    def _get_position(self, cell:Cell):
        return (cell.row, cell.column)
    
    def _get_candidates(self, cell:Cell):
        return cell.candidates

class _CandidateSets:

    def __init__(self, cells:Cells):
        _validate_cells(cells)
        self.cells = cells
        self.affected_positions = []
        self._deduce()

    def _deduce(self):
        max_level = self._get_max_level(self.cells)
        self.sets = {}
        self.valid_sets = []
        self.level = 1

        self.sets[0] = [None]

        while self.level <= max_level and len(self.valid_sets) == 0:
            self.sets[self.level] = self._combine_candidate_sets(self.cells, self.sets[self.level-1])
            self.level += 1
        
    def eliminate(self):
        affected_positions = []
        for valid_set in self.valid_sets:
            result = self._eliminate_set(valid_set)
            affected_positions.extend(result)
        self.affected_positions = affected_positions
        return affected_positions
        
    def _eliminate_set(self, valid_set:_CandidateSet):
        affected_positions = []
        for row in self.cells.data:
            for cell in row:
                position = (cell.row, cell.column)
                if position not in valid_set.positions:
                    affected_positions.append((cell.row, cell.column))
                    cell.remove_candidates(valid_set.candidate_set)
        return affected_positions
        
    def _combine_candidate_sets(self, cells:Cells, sets:List[_CandidateSet]=None) -> List[_CandidateSet]:
        if sets is None:
            sets = [None]
        new_sets = []
        cells_data = self._flatten_cells_data(cells.data)
        for other_set in sets:
            for row in cells.data:
                for cell in row:
                    candidate_set = _CandidateSet(cell, other_set)
                    if candidate_set not in new_sets:
                        if not candidate_set.skip:
                            new_sets.append(candidate_set)
                        if candidate_set.valid:
                            self.valid_sets.append(candidate_set)
        return new_sets
    
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

    def _deduce_candidate_sets(self, cells:Cells):
        candidates = cells.get_candidates(flatten=True)
        candidate_sets = self._get_candidate_sets(candidates)

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

    