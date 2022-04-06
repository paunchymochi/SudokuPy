import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from typing import List, Dict, Optional, Union

def _validate_cells(cells:Cells):
    if len(cells) != 9:
        raise ValueError('cells must have 9 elements')
    if not isinstance(cells, Cells):
        print(f'type: {type(cells)}')
        raise TypeError('cells must be instance of Cells')

def _get_pending_operations_message(operations:dict):
    return {'Number of operations': sum([len(x) for x in operations.values()]), 'Operations': operations}

class _DeduceOperation:
    __slots__ = ['_cell', '_candidates_to_remove']
    def __init__(self, cell:Cell, remove_candidates:List[int]=None, set_candidates:List[int]=None):
        self._cell = cell
        self._candidates_to_remove = self._get_candidates_to_remove(remove_candidates, set_candidates)
    
    def __repr__(self):
        return f'DeduceOperation cell:{self._cell.__repr__()} candidates_to_remove:{self._candidates_to_remove}>'
    
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
        self._operations:List[_DeduceOperation] = []
    
    @property
    def operations(self):
        return self._operations
    
    def __repr__(self):
        return f'<{__name__}\n' + '\n'.join(self.list_pending_operations()) + '>'
    
    def count_pending_operations(self):
        return len(self._operations)
    
    def list_pending_operations(self):
        return [operation.__repr__() for operation in self._operations]

    def eliminate(self):
        self._clear_affected_cells()
        for operation in self._operations:
            operation.cell.remove_candidates(operation.candidates_to_remove)
            self._add_affected_cell(operation.cell)
        self.clear_operations()

    def _add_operation(self, cell:Cell, remove_candidates:List[int]=None, set_candidates:List[int]=None):
        operation = _DeduceOperation(cell, remove_candidates, set_candidates)
        self._operations.append(operation)

    def clear_operations(self):
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
        for other_companion in companions:
            for cell in sliced_cells.flatten():
                companion = _Companion(cell, other_companion)
                if companion not in new_companions:
                    if not companion.skip:
                        new_companions.append(companion)
                    if companion.valid:
                        self._make_new_operations(companion, sliced_cells)
        return new_companions
    
    def _make_new_operations(self, companion:_Companion, sliced_cells:Cells):
        for cell in sliced_cells.flatten():
            if cell not in companion.cells:
                if any([candidate in companion.companion for candidate in cell.candidates]):
                    self._add_operation(cell, remove_candidates=companion.companion)
    
    def _get_max_level(self, cells:Cells):
        values = cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return min(8 - len(values), 5)

class LineBoxDeducer(_BaseDeducer):
    class _SegmentExclusiveCandidates:
        def __init__(self, cells:Cells, row:Optional[int], col:Optional[int]):
            line = self._get_line(cells, row, col)
            self.exclusive_candidates = self._get_segment_exclusive_candidates(line)

        def _get_line(self, cells:Cells, row:Optional[int], col:Optional[int]) -> Cells:
            if row is not None:
                line = self._cells[row]
            elif col is not None:
                line = self._cells[:, col]
            else:
                raise ValueError('must provide either row or col')
            return line

        def _get_segment_exclusive_candidates(self, line:Cells):
            exclusive_candidates = []
            counts = self._get_candidate_counts_by_segment(line)

            for candidate, data in counts.items():
                if data['count'] == 1:
                    exclusive_candidates.append([candidate, data['segment_index']])
            return exclusive_candidates
        
        def _get_candidate_counts_by_segment(self, line:Cells) -> Dict:
            line_candidates = self._get_line_candidates(line)
            segment_candidates = self._get_segmented_line_candidates(line)

            counts = {}
            for candidate in line_candidates:
                counts[candidate] = {'count':0, 'segment_index':[]}
                for segment_index, segment_candidate in enumerate(segment_candidates):
                    if candidate in segment_candidate:
                        counts[candidate]['count'] += 1
                        counts[candidate]['segment_index'].append(segment_index)
            return counts

        def _get_line_candidates(self, line:Cells) -> List[int]:
            candidate_set = []
            candidates = line.get_candidates(flatten=True)
            for candidate in candidates:
                candidate_set.extend(candidate)
            candidate_set = list(set(candidate_set))
            return candidate_set
        
        def _get_segmented_line_candidates(self, line:Cells) -> List[List[int]]:
            candidates = []
            segmented_line = self._get_segmented_line(line)
            for segment in segmented_line:
                segment_candidates = []
                for cell in segment:
                    segment_candidates.extend(cell.candidates)
                candidates.append(list(set(segment_candidates)))
            return candidates
        
        def _get_segmented_line(self, line:Cells) -> List[List[Cell]]:
            cells = line.flatten()
            segmented_line = []
            for i in [0, 3, 6]:
                segmented_line.append(cells[i:i+3])
            return segmented_line

    def __init__(self, cells:Cells):
        super().__init__()
        self._cells = cells
    
    def deduce(self, row:int=None, col:int=None):
        self._row = row
        self._col = col

        segment_exclusive_candidates = self._SegmentExclusiveCandidates(self._cells, row, col).exclusive_candidates
        boxes = self._get_boxes()

        for candidate, segment_index in segment_exclusive_candidates:
            box = boxes[segment_index]
            for cell in box.flatten():
                self._deduce_cell(cell, candidate)
                
    def _deduce_cell(self, cell:Cell, remove_candidate:int):
        if cell.row == self._row or cell.column == self._col:
            return
        if remove_candidate in cell.candidates:
            self._add_operation(cell, remove_candidates=[remove_candidate])
    
    def _get_boxes(self) -> List[Cells]:
        row = self._row
        col = self._col
        toplefts = [0, 3, 6]
        if row is not None:
            rows = [(row//3)*3]
            cols = toplefts
        elif col is not None:
            rows = toplefts
            cols = [(col//3)*3]
        
        boxes = []
        for r in rows:
            for c in cols:
                boxes.append(self._cells[r:r+3, c:c+3])
        return boxes
    
class ValueDeducer(_BaseDeducer):
    def __init__(self):
        super().__init__()
        self._cells_with_assigned_candidates = []
        self._cells_with_values = []
    
    def deduce(self, sliced_cells:Cells):
        _validate_cells(sliced_cells)
        self._sliced_cells = sliced_cells

        values = self._get_values(sliced_cells)

        for cell in sliced_cells.flatten():
            candidates = cell.candidates
            if len(candidates) > 0:
                if cell.value != 0:
                    self._add_operation(cell, remove_candidates=candidates)
                else:
                    candidates_to_remove = [candidate for candidate in candidates if candidate in values]
                    if len(candidates_to_remove) > 0:
                        self._add_operation(cell, remove_candidates=candidates_to_remove)
    
    def _get_values(self, sliced_cells:Cells):
        values = sliced_cells.get_values(flatten=True)
        values = list(set(values))
        if 0 in values:
            values.remove(0)
        return values

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