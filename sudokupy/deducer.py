import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from typing import List, Dict, Optional, Union, Tuple
import random

class Transaction:
    __slots__ = ['_cell', '_candidates']
    def __init__(self, cell:Cell):
        self._cell = cell
        self._candidates = []
    
    def __repr__(self):
        return f'<Transaction cell:{self._cell.__repr__()} candidates:{self._candidates}>'
    
    @property
    def cell(self):
        return self._cell
    
    @property
    def candidates(self):
        return self._candidates
    
    def add(self, candidates: List[int]):
        if len(self._candidates) == 0:
            self._candidates = candidates.copy()
        else:
            self._candidates.extend(candidates)
            self._remove_duplicate_candidates()
        self._candidates.sort()
    
    def _remove_duplicate_candidates(self):
        candidates = list(set(self._candidates))
        self._candidates = candidates

    def __eq__(self, other):
        return self._cell == other._cell

class Transactions:
    __slots__ = '_transactions_dict'
    def __init__(self):
        self._transactions_dict:Dict[Tuple[int], List[Transaction]] = {}
        self.clear_transactions()
    
    def __str__(self):
        return f'# of transactions:{len(self._transactions_dict)}\n' + '\n'.join(transaction.__repr__() for transaction in self.transactions)

    def __repr__(self):
        return f'<Transactions\n{self.__str__()}\n>'
    
    def __len__(self):
        return len(self._transactions_dict)
    
    @property
    def transactions(self) -> List[Transaction]:
        return self.get_transactions()

    def add_transaction(self, cell:Cell, remove_candidates:Union[int, List[int]]):
        position = self._get_position(cell)
        if not self._cell_in_transactions(position):
            self._make_new_transactions_entry(cell)
        self._append_transaction(position, remove_candidates)
    
    def extend_transactions(self, other:'Transactions'):
        other_transactions = other.transactions
        for transaction in other_transactions:
            self.add_transaction(transaction.cell, transaction.candidates)

    def clear_transactions(self):
        self._transactions_dict = {}

    def get_transactions(self) -> List[Transaction]:
        return list(self._transactions_dict.values())

    def _append_transaction(self, position:Tuple[int], remove_candidates:Union[int, List[int]]):
        remove_candidates = self._validate_candidates(remove_candidates)
        self._transactions_dict[position].add(remove_candidates)
    
    def _validate_candidates(self, candidates:Union[int, List[int]]) -> List[int]:
        if type(candidates) is int:
            candidates = [candidates]
        return candidates
    
    def _make_new_transactions_entry(self, cell:Cell):
        position = self._get_position(cell)
        self._transactions_dict[position] = Transaction(cell)

    def _cell_in_transactions(self, position:Tuple[int]) -> bool:
        return position in self._transactions_dict.keys()
    
    def _get_position(self, cell:Cell) -> Tuple[int]:
        return (cell.row, cell.column)
    
class _BaseDeducer:
    def __init__(self):
        self._affected_cells:List[Cell] = []
        self._transactions = Transactions()
    
    @property
    def transactions(self):
        return self._transactions.get_transactions()
    
    @property
    def affected_cells(self):
        return self._affected_cells
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self._transactions.__str__()} \n>'
    
    def _validate_sliced_cells(self, sliced_cells:Cells):
        if not isinstance(sliced_cells, Cells):
            print(f'type: {type(sliced_cells)}')
            raise TypeError('cells must be instance of Cells')
        if len(sliced_cells) != 9:
            raise ValueError('cells must have 9 elements')

    def eliminate(self):
        self._clear_affected_cells()
        for transaction in self.transactions:
            transaction.cell.remove_candidates(transaction.candidates)
            self._add_affected_cell(transaction.cell)
        self.clear_transactions()

    def _add_transaction(self, cell:Cell, remove_candidates:List[int]=None):
        self._transactions.add_transaction(cell, remove_candidates)

    def clear_transactions(self):
        self._transactions.clear_transactions()

    def _add_affected_cell(self, cell:Cell):
        if cell not in self._affected_cells:
            self._affected_cells.append(cell)

    def _clear_affected_cells(self):
        self._affected_cells = []
    
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

class LineBoxDeducer(_BaseDeducer):
    class _SegmentExclusiveCandidates:
        def __init__(self, cells:Cells, row:Optional[int], col:Optional[int]):
            line = self._get_line(cells, row, col)
            self.exclusive_candidates = self._get_segment_exclusive_candidates(line)

        def _get_line(self, cells:Cells, row:Optional[int], col:Optional[int]) -> Cells:
            if row is not None:
                line = cells[row]
            elif col is not None:
                line = cells[:, col]
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
            box = boxes[segment_index[0]]
            for cell in box.flatten():
                self._deduce_cell(cell, candidate)
                
    def _deduce_cell(self, cell:Cell, remove_candidate:int):
        if cell.row == self._row or cell.column == self._col:
            return
        if remove_candidate in cell.candidates:
            self._add_transaction(cell, remove_candidates=[remove_candidate])
    
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

class SingleCandidateDeducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__()
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

class PairedCandidate:
    def __init__(self, candidate:int, topleft_cell: Cell, cell1: Cell, cell2: Cell):
        self.candidate = candidate
        self.cells = (cell1, cell2)
        self.topleft_cell = topleft_cell
        self.rows = [cell.row for cell in self.cells]
        self.cols = [cell.column for cell in self.cells]
    
    def __eq__(self, other:'PairedCandidate'):
        if self.candidate == other.candidate:
            if self.topleft_cell == other.topleft_cell:
                return True
        return False
    
    def match_vertices(self, others:Union['PairedCandidate', List['PairedCandidate']]):
        if type(others) is not list:
            others = [others]
    
    def is_row_pair(self):
        if self.rows[0] == self.rows[1]:
            return True
        else:
            return False

class PairedVertices:
    def __init__(self):
        pass

class PairedVerticesDeducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__()
        self._cells = cells
        self._pairs = []
        self._vertices = []
        
    def deduce(self, row:int=None, col:int=None):
        pass
    
    def _find_pairs(self, flattened_sliced_cells:List[Cell], is_row:bool):
        pairs = []
        counts:dict[int, List[int]] = {}
        for i in range(1, 10):
            counts[i] = []
        
        for cell in flattened_sliced_cells:
            for candidate in cell.candidates:
                counts[candidate].append(cell)
        
        for candidate, cells in counts.items():
            if len(cells) == 2:
                topleft_cell = self._get_topleft_cell()
                pair = PairedCandidate(candidate, topleft_cell, cells[0], cells[1])
                pairs.append(pair)

        return pairs
    
    def _get_topleft_cell(flattened_sliced_cells:List[Cell]) -> Cell:
        return flattened_sliced_cells[0]


class Deducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__()
        self._cells = cells
        self.value_deducer = ValueDeducer()
        self.single_candidate_deducer = SingleCandidateDeducer(cells)
        self.companion_deducer = CompanionDeducer()
        self.linebox_deducer = LineBoxDeducer(cells)
    
    def is_solvable(self) -> bool:
        for cell in self._cells.flatten():
            if cell.value == 0 and cell.candidates == []:
                return False
        return True
    
    def deduce_adjacent(self, row:int, col:int):
        self._deduce_adjacent_values(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_single_candidates(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_lineboxes(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_companions(row, col)
    
    def _deduce_adjacent_values(self, row:int, col:int):
        self.deduce_value(self._get_row(row))
        self.deduce_value(self._get_col(col))
        self.deduce_value(self._get_box(row//3, col//3))
    
    def _deduce_adjacent_single_candidates(self, row:int, col:int):
        self.deduce_single_candidate(self._get_row(row))
        self.deduce_single_candidate(self._get_col(col))
        self.deduce_single_candidate(self._get_box(row//3, col//3))
    
    def _deduce_adjacent_lineboxes(self, row:int, col:int):
        self.deduce_linebox(self._get_row(row))
        self.deduce_linebox(self._get_col(col))
    
    def _deduce_adjacent_companions(self, row:int, col:int):
        self.deduce_companion(self._get_row(row))
        self.deduce_companion(self._get_col(col))
        self.deduce_companion(self._get_box(row//3, col//3))
    
    def deduce(self):
        self._deduce_all_values()
        if len(self.transactions) > 0: return
        self._deduce_all_single_candidates()
        if len(self.transactions) > 0: return
        self._deduce_all_lineboxes()
        if len(self.transactions) > 0: return
        self._deduce_all_companions()
    
    def eliminate(self):
        self._clear_affected_cells()
        self.value_deducer.eliminate()
        self.single_candidate_deducer.eliminate()
        self.linebox_deducer.eliminate()
        self.companion_deducer.eliminate()
        self._affected_cells.extend(self.value_deducer.affected_cells)
        self._affected_cells.extend(self.single_candidate_deducer.affected_cells)
        self._affected_cells.extend(self.linebox_deducer.affected_cells)
        self._affected_cells.extend(self.companion_deducer.affected_cells)
        self.clear_transactions()

    def _get_all_rows(self) -> List[Cells]:
        return [self._get_row(i) for i in range(9)]
    
    def _get_all_cols(self) -> List[Cells]:
        return [self._get_col(i) for i in range(9)]
    
    def _get_all_boxes(self) -> List[Cells]:
        return [self._get_box(i, j) for i in range(3) for j in range(3)]
    
    def _get_all_sliced_cells(self, include_boxes=True) -> List[Cells]:
        cells_list = []
        cells_list.extend(self._get_all_rows())
        cells_list.extend(self._get_all_cols())
        if include_boxes:
            cells_list.extend(self._get_all_boxes())
        return cells_list
    
    def _get_row(self, row:int) -> Cells:
        return self._cells[row]
    
    def _get_col(self, col:int) -> Cells:
        return self._cells[:, col]
    
    def _get_box(self, boxrow:int, boxcol:int) -> Cells:
        return self._cells[boxrow*3:boxrow*3+3,boxcol*3:boxcol*3+3]
    
    def _deduce_all_values(self):
        cells_list = self._get_all_sliced_cells(True)
        for cells in cells_list:
            self.deduce_value(cells)
    
    def _deduce_all_single_candidates(self):
        cells_list = self._get_all_rows()
        for cells in cells_list:
            self.deduce_single_candidate(cells)
    
    def _deduce_all_companions(self):
        cells_list = self._get_all_sliced_cells(True)
        for cells in cells_list:
            self.deduce_companion(cells)

    def _deduce_all_lineboxes(self):
        cells_list = self._get_all_sliced_cells(False)
        for cells in cells_list:
            self.deduce_linebox(cells)
    
    def deduce_value(self, sliced_cells:Cells):
        self.value_deducer.deduce(sliced_cells)
        self._transactions.extend_transactions(self.value_deducer._transactions)
    
    def deduce_single_candidate(self, sliced_cells:Cells):
        self.single_candidate_deducer.deduce(sliced_cells)
        self._transactions.extend_transactions(self.single_candidate_deducer._transactions)
    
    def deduce_companion(self, sliced_cells:Cells):
        self.companion_deducer.deduce(sliced_cells)
        self._transactions.extend_transactions(self.companion_deducer._transactions)
    
    def deduce_linebox(self, sliced_cells:Cells):
        row_count = sliced_cells.row_count
        col_count = sliced_cells.col_count

        if col_count == 9:
            row = sliced_cells.topleft_row
        else:
            row = None
        if row_count == 9:
            col = sliced_cells.topleft_column
        else:
            col = None
        
        if row is None and col is None:
            return

        self.linebox_deducer.deduce(row, col)
        self._transactions.extend_transactions(self.linebox_deducer._transactions)
    