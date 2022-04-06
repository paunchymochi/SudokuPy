
from os import remove
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

def _get_pending_operations_message(operations:dict):
    return {'Number of operations': sum([len(x) for x in operations.values()]), 'Operations': operations}
    
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

    def __init__(self):
        self.sliced_cells:Cells=None
        self.affected_positions = []
        self._valid_companions = []
    
    def print_pending_operations(self):
        operations = {}
        operations['companions'] = self._valid_companions
        return _get_pending_operations_message(operations)
    
    @property
    def pending_operations(self) -> int:
        return len(self._valid_companions)

    def deduce(self, sliced_cells:Cells):
        self.sliced_cells = sliced_cells
        self.affected_positions = []

        max_level = self._get_max_level(self.sliced_cells)
        self._companions = {}
        self._valid_companions = []
        level = 1

        self._companions[0] = [None]

        while level <= max_level and len(self._valid_companions) == 0:
            self._companions[level] = self._make_companions(self.sliced_cells, self._companions[level-1])
            level += 1
        
    def eliminate(self):
        affected_positions = []
        for valid_companion in self._valid_companions:
            result = self._eliminate_companion(valid_companion)
            affected_positions.extend(result)
        self.affected_positions = affected_positions
        return affected_positions
        
    def _eliminate_companion(self, valid_companion:_Companion):
        affected_positions = []
        for row in self.sliced_cells.data:
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
                            self._valid_companions.append(companion)
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
    def __init__(self, cells:Cells):
        self._cells = cells
        self._elimination_cells = []
    
    def print_pending_operations(self):
        operations = {}
        operations['cells with eliminations'] = self._elimination_cells
        return _get_pending_operations_message(operations)
    
    @property
    def pending_operations(self) -> int:
        return len(self._elimination_cells)

    def _get_boxes(self) -> List[Cells]:
        row = self.row
        col = self.col
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
                boxes.append(self._cells[r:r+3, c:c+3])
        return boxes
    
    def _get_line_candidates(self, line:Cells) -> List[int]:
        candidate_set = []
        candidates = line.get_candidates(flatten=True)
        for candidate in candidates:
            candidate_set.extend(candidate)
        candidate_set = list(set(candidate_set))
        return candidate_set
    
    def _get_line(self) -> Cells:
        row = self.row
        col = self.col

        if row is not None:
            line = self._cells[row]
        elif col is not None:
            line = self._cells[:, col]
        else:
            raise ValueError('must provide either row or col')
        return line
    
    def _get_segmented_line(self, line:Cells) -> List[List[Cell]]:
        cells = []
        for row in line.data:
            for cell in row:
                cells.append(cell)
        segmented_line = []
        for i in [0, 3, 6]:
            segmented_line.append(cells[i:i+3])
        return segmented_line
    
    def _get_candidate_segment_counts(self):
        
        line = self._get_line()
        line_candidates = self._get_line_candidates(line)
        segmented_line = self._get_segmented_line(line)

        counts = {}
        for candidate in line_candidates:
            counts[candidate] = {'count':0, 'segment_index':[]}
            for segment_index, segment in enumerate(segmented_line):
                if any([candidate in cell.candidates for cell in segment]):
                    counts[candidate]['count'] += 1
                    counts[candidate]['segment_index'].append(segment_index)
        return counts
    
    def _deduce_box(self):
        candidate_segment_counts = self._get_candidate_segment_counts()
        boxes = self._get_boxes()
        for candidate, value in candidate_segment_counts.items():
            if value['count'] == 1:
                box = boxes[value['segment_index']]
                for row in box.data:
                    for cell in row:
                        self._deduce_cell(cell, candidate)
                
    def _deduce_cell(self, cell:Cell, remove_candidate:int):
        if cell.row == self.row or cell.column == self.col:
            return
        
        if remove_candidate in cell.candidates:
            if remove_candidate not in self._elimination_cells:
                self._elimination_cells[remove_candidate] = []
            self._elimination_cells[remove_candidate].append(cell)

    def deduce(self, row:int=None, col:int=None):
        self.row = row
        self.col = col
        self._elimination_cells:dict[int, List[Cell]] = {}
        self._deduce_box()
    
    def eliminate(self):
        self.affected_positions = []
        for candidate, cells in self._elimination_cells.items():
            for cell in cells:
                cell.remove_candidates(candidate)
                self.affected_positions.append((cell.row, cell.column))
        return self.affected_positions

class ValueDeducer:
    def __init__(self):
        self.sliced_cells:Cells = None
        self.affected_positions = []
        self._cells_with_assigned_candidates = []
        self._cells_with_values = []
    
    @property
    def pending_operations(self) -> int:
        return len(self._cells_with_assigned_candidates) + len(self._cells_with_values)
    
    def print_pending_operations(self):
        operations = {}
        operations['cells with assigned candidates'] = self._cells_with_assigned_candidates
        operations['cells with values'] = self._cells_with_values
        return _get_pending_operations_message(operations)
    
    def _get_values(self, sliced_cells:Cells):
        values = sliced_cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return values

    def deduce(self, sliced_cells:Cells):
        _validate_cells(sliced_cells)
        self.sliced_cells = sliced_cells
        self.affected_positions = []
        self._cells_with_assigned_candidates:List[Cell] = []
        self._cells_with_values:List[Cell] = []
        self._values = self._get_values(sliced_cells)

        for row in self.sliced_cells.data:
            for cell in row:
                candidates = cell.candidates
                if any([value in candidates for value in self._values]):
                    self._cells_with_assigned_candidates.append(cell)
                if cell.value != 0:
                    self._cells_with_values.append(cell)

    def eliminate(self):
        for cell in self._cells_with_assigned_candidates:
            cell.remove_candidates(self._values)
            self.affected_positions.append((cell.row, cell.column))
        for cell in self._cells_with_values:
            cell.set_candidates([])
            self.affected_positions.append((cell.row, cell.column))
        return self.affected_positions

class Deducer:
    def __init__(self, cells: Cells):
        self.cells = cells
        self.value_deducer = ValueDeducer()
        self.companion_deducer = CompanionDeducer()
        self.linebox_deducer = LineBoxDeducer(cells)
    
    def print_pending_operations(self):
        operations = {}
        operations['value_deducer'] = self.value_deducer.print_pending_operations()
        operations['linebox_deducer'] = self.linebox_deducer.print_pending_operations()
        operations['companion_deducer'] = self.companion_deducer.print_pending_operations()

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
    
    def eliminate(self):
        self.value_deducer.eliminate()
        self.linebox_deducer.eliminate()
        self.companion_deducer.eliminate()

    def _deduce_cells(self, sliced_cells:Cells):
        _validate_cells(sliced_cells)
        self._deduce_values(sliced_cells)
        if self.value_deducer.pending_operations == 0:
            self._deduce_lineboxes(sliced_cells)
            if self.linebox_deducer.pending_operations == 0:
                self._deduce_companions(sliced_cells)
    
    def _deduce_values(self, sliced_cells:Cells):
        self.value_deducer.deduce(sliced_cells)
    
    def _deduce_companions(self, sliced_cells:Cells):
        self.companion_deducer.deduce(sliced_cells)
    
    def _deduce_lineboxes(self, sliced_cells:Cells):
        row_count = sliced_cells.row_count
        col_count = sliced_cells.col_count

        if row_count == 9:
            row = sliced_cells.topleft_row
        else:
            row = None
        if col_count == 9:
            col = sliced_cells.topleft_column
        else:
            col = None
        
        if row is None and col is None:
            return

        self.linebox_deducer.deduce(row, col)