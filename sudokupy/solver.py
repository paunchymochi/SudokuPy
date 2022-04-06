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

class DeduceOperation:
    __slots__ = ['_cell', '_candidates_to_remove']
    def __init__(self, cell:Cell, remove_candidates:List[int]=None, set_candidates:List[int]=None):
        self._cell = cell
        self._candidates_to_remove = self._get_candidates_to_remove(remove_candidates, set_candidates)
    
    @property
    def cell(self):
        return self._cell
    
    @property
    def candidates_to_remove(self):
        return self._candidates_to_remove

    def _get_candidates_to_remove(self, remove_candidates:List[int]=None, set_candidates:List[int]=None):
        if remove_candidates is not None:
            if type(remove_candidates) is int:
                remove_candidates = [remove_candidates]
            candidates_to_remove = list(set(remove_candidates))
        elif set_candidates is not None:
            if type(set_candidates) is int:
                set_candidates = [set_candidates]
            candidates_to_remove = self._set_to_remove(set_candidates)
        
        candidates_to_remove.sort()
        return candidates_to_remove

    def _set_to_remove(self, set_candidates:List[int]):
        existing_candidates = self._cell.candidates
        remove_candidates = [candidate for candidate in existing_candidates if candidate not in set_candidates]
        return remove_candidates
    
    def __eq__(self, other):
        if self._cell == other._cell:
            if self._candidates_to_remove == other._candidates_to_remove:
                return True
        return False
    
class _BaseDeducer:
    def __init__(self):
        self._affected_cells:List[Cell] = []
        self._operations:List[DeduceOperation] = []
    
    def count_pending_operations(self):
        return len(self._operations)
    
    def list_pending_operations(self):
        return [operation.__repr__() for operation in self._operations]

    def eliminate(self):
        self._clear_affected_cells()
        for operation in self._operations:
            operation.cell.remove_candidates(operation.candidates_to_remove)
            self._add_affected_cell(operation.cell)
        self._clear_operations()

    def _add_operation(self, cell:Cell, remove_candidates:List[int]=None, set_candidates:List[int]=None):
        operation = DeduceOperation(cell, remove_candidates, set_candidates)
        self._operations.append(operation)

    def _clear_operations(self):
        self._operations = []

    def _add_affected_cell(self, cell:Cell):
        if cell not in self._affected_cells:
            self._affected_cells.append(cell)

    def _clear_affected_cells(self):
        self._affected_cells = []
    
class _Companion:
    def __init__(self, cell:Cells, other=None):
        self.cells:List[Cell] = []
        self.candidates = []
        self.companion = []
        self.skip = True
        self.valid = False
        self._init_other(other)
        if self._add(cell):
            self.skip = False
            self.valid = self._is_valid()
    
    def __repr__(self):
        return f'<_CandidateSet cells:{self.cells} companion:{self.companion}>'
    
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
    
    def _add(self, cell:Cells) -> bool:
        if cell in self.cells:
            return False
        
        candidates = cell.candidates

        if len(candidates) == 0:
            return False

        self.cells.append(cell)
        self.candidates.append(candidates)
        self.companion = list(set(self.companion+candidates))

        return True
    
class CompanionDeducer(_BaseDeducer):

    def __init__(self):
        super().__init__()
        self._sliced_cells:Cells=None

    def deduce(self, sliced_cells:Cells):
        self._sliced_cells = sliced_cells

        max_level = self._get_max_level(self._sliced_cells)
        companions = {}
        level = 1

        companions[0] = [None]

        while level <= max_level and len(self._operations) == 0:
            companions[level] = self._make_companions(self._sliced_cells, companions[level-1])
            level += 1
        
    def _make_companions(self, sliced_cells:Cells, companions:List[_Companion]=None) -> List[_Companion]:
        if companions is None:
            companions = [None]
        new_companions = []
        cell_list = self._get_cell_list(sliced_cells)
        for other_companion in companions:
            for cell in cell_list:
                companion = _Companion(cell, other_companion)
                if companion not in new_companions:
                    if not companion.skip:
                        new_companions.append(companion)
                    if companion.valid:
                        self._make_new_operations(companion, sliced_cells)
        return new_companions
    
    def _make_new_operations(self, companion:_Companion, sliced_cells:Cells):
        cell_list = self._get_cell_list(sliced_cells)
        for cell in cell_list:
            if cell not in companion.cells:
                if any([candidate in companion.companion for candidate in cell.candidates]):
                    self._add_operation(cell, remove_candidates=companion.companion)
    
    def _get_cell_list(self, cells:Cells) -> List[Cell]:
        cell_list = []
        for row in cells.data:
            for cell in row:
                cell_list.append(cell)
        return cell_list
    
    def _get_max_level(self, cells:Cells):
        values = cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return 8 - len(values)

class LineBoxDeducer(_BaseDeducer):
    def __init__(self, cells:Cells):
        super().__init__()
        self._cells = cells
    
    def deduce(self, row:int=None, col:int=None):
        self._row = row
        self._col = col
        self._deduce_box()

    def _deduce_box(self):
        candidate_segment_counts = self._get_candidate_segment_counts()
        boxes = self._get_boxes()
        for candidate, value in candidate_segment_counts.items():
            if value['count'] == 1:
                box = boxes[value['segment_index']]
                for cell in box.flatten():
                    self._deduce_cell(cell, candidate)
                
    def _deduce_cell(self, cell:Cell, remove_candidate:int):
        if cell.row == self._row or cell.column == self._col:
            return
        if remove_candidate in cell.candidates:
            self._add_operation(cell, remove_candidates=[remove_candidate])

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
    
    
class ValueDeducer:
    def __init__(self):
        self.sliced_cells:Cells = None
        self.affected_positions = []
        self._cells_with_assigned_candidates = []
        self._cells_with_values = []
    
    @property
    def pending_operations(self) -> int:
        return len(self._cells_with_assigned_candidates) + len(self._cells_with_values)
    
    def clear_pending_operations(self):
        self._cells_with_assigned_candidates = {}
        self._cells_with_values = []
    
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
        self._values = self._get_values(sliced_cells)

        for row in self.sliced_cells.data:
            for cell in row:
                candidates = cell.candidates
                if any([value in candidates for value in self._values]):
                    self._add_cell_with_assigned_candidates(cell, candidates)
                if cell.value != 0:
                    self._cells_with_values.append(cell)
    
    def _add_cell_with_assigned_candidates(self, cell:Cell, candidates:List[int]):
        for candidate in candidates:
            if candidate not in self._cells_with_assigned_candidates.keys():
                self._cells_with_assigned_candidates[candidate] = []
            if cell not in self._cells_with_assigned_candidates[candidate]:
                self._cells_with_assigned_candidates[candidate].append(cell)

    def _add_cell_with_values(self, cell:Cell):
        if cell not in self._cells_with_values:
            self._cells_with_values.append(cell)

    def eliminate(self):
        for cell in self._cells_with_assigned_candidates:
            cell.remove_candidates(self._values)
            self.affected_positions.append((cell.row, cell.column))
        for cell in self._cells_with_values:
            cell.set_candidates([])
            self.affected_positions.append((cell.row, cell.column))
        self.clear_pending_operations()
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
    
    @property
    def pending_operations(self):
        return self.value_deducer.pending_operations + self.linebox_deducer.pending_operations + self.companion_deducer.pending_operations

    def deduce_row(self, row:int, deduce_value=True, deduce_linebox=True, deduce_companion=True):
        cells = self.cells[row]
        self._deduce_cells(cells, deduce_value, deduce_linebox, deduce_companion)
    
    def deduce_column(self, col:int, deduce_value=True, deduce_linebox=True, deduce_companion=True):
        cells = self.cells[:, col]
        self._deduce_cells(cells, deduce_value, deduce_linebox, deduce_companion)
    
    def deduce_box(self, boxrow:int, boxcol:int, deduce_value=True, deduce_companion=True):
        cells = self.cells[boxrow*3:boxrow*3+3,boxcol*3:boxcol*3+3]
        self._deduce_cells(cells, deduce_value=deduce_value, deduce_linebox=False, deduce_companion=deduce_companion)
    
    def deduce_adjacent(self, row:int, col:int):
        self.deduce_row(row)
        self.deduce_column(col)
        self.deduce_box(row//3, col//3)
    
    def deduce(self):
        for flag in [[True, False, False], [False, True, False], [False, False, True]]:
            for i in range(9):
                self.deduce_row(i, flag[0], flag[1], flag[2])
                self.deduce_column(i, flag[0], flag[1], flag[2])
            for i in range(3):
                for j in range(3):
                    self.deduce_box(i, j, flag[0], flag[2])
            if self.pending_operations > 0:
                return
    
    def eliminate(self):
        self.value_deducer.eliminate()
        self.linebox_deducer.eliminate()
        self.companion_deducer.eliminate()

    def _deduce_cells(self, sliced_cells:Cells, deduce_value=False, deduce_linebox=False, deduce_companion=False):
        _validate_cells(sliced_cells)
        if deduce_value:
            self._deduce_values(sliced_cells)
        if deduce_linebox:
            self._deduce_lineboxes(sliced_cells)
        if deduce_companion:
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