import sys
sys.path.append('../..')
from sudokupy.cell import Cells, Cell
from sudokupy.deducers.deducer_base import _BaseDeducer

from typing import List, Dict, Optional, Union, Tuple

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

class VertexPair:
    def __init__(self, candidate:int, topleft_cell: Cell, cell1: Cell, cell2: Cell):
        self.candidate = candidate
        self.cells = (cell1, cell2)
        self.topleft_cell = topleft_cell
        self.rows = [cell.row for cell in self.cells]
        self.cols = [cell.column for cell in self.cells]
        self.vertex_row:int = 0
        self.vertex_cols:List[int] = []
        self._make_vertex_rowcol()
    
    def __repr__(self):
        return f'<VertexPair candidate:{self.candidate} cells:{self.cells}>'
    
    def __eq__(self, other:'VertexPair'):
        if self.candidate == other.candidate:
            if self.topleft_cell == other.topleft_cell:
                return True
        return False
    
    def is_row_pair(self):
        if self.rows[0] == self.rows[1]:
            return True
        else:
            return False
    
    def _make_vertex_rowcol(self):
        if self.is_row_pair():
            self.vertex_row = self.rows[0]
            self.vertex_cols = self.cols
        else:
            self.vertex_row = self.cols[0]
            self.vertex_cols = self.rows

class VertexCouple:
    def __init__(self, vertex_pairs:List[VertexPair], other:'VertexCouple'=None):
        if type(vertex_pairs) is not list:
            vertex_pairs = [vertex_pairs]
        self.pairs:List[VertexPair] = []
        self.discard = False
        self.valid = False
        self.completed = False

        if not self._validate_input(vertex_pairs, other):
            self.discard = True
            return 

        self._init_other(other)
        self._append_pair(vertex_pairs)
        self._validate_pairs()

    def __repr__(self):
        return f'<VertexCouple pairs:{self.pairs} discard:{self.discard} valid:{self.valid}>'
    
    def __eq__(self, other:'VertexCouple'):
        if len(other) != len(self):
            return False
        for pair in self.pairs:
            if pair not in other.pairs:
                return False
        return True
    
    @property
    def candidate(self):
        return self.pairs[0].candidate
    
    def get_pairs(self):
        return self.pairs
    
    def __len__(self):
        return len(self.pairs)

    def _init_other(self, other:'VertexCouple'):
        if other is not None:
            self.pairs = other.pairs.copy()
    
    def _append_pair(self,vertex_pairs:List[VertexPair]):
        self.pairs.extend(vertex_pairs)
    
    def _validate_input(self, vertex_pairs:List[VertexPair], other:Optional['VertexCouple']) -> bool:
        if other is None:
            return True

        for vertex_pair in vertex_pairs:
            if vertex_pair.candidate != other.candidate:
                return False
            
            if vertex_pair in other.pairs:
                return False

        return True
    
    def _validate_pairs(self):
        vertex_cols = self.get_vertex_cols()
        if len(vertex_cols) == len(self.pairs):
            self.valid = True

    def set_completed(self):
        self.completed = True
    
    def get_cell_list(self) -> List[Cell]:
        cell_list = []
        for pair in self.pairs:
            cell_list.extend(pair.cells)
        return cell_list
    
    def get_vertex_cols(self):
        cols = []
        for pair in self.pairs:
            cols.extend(pair.vertex_cols)
        
        return list(set(cols))
    
    def is_row_couple(self):
        return self.pairs[0].is_row_pair()

class VertexDict:
    def __init__(self):
        self._dict:dict[int, List[VertexCouple]] = {}
    
    def __repr__(self):
        return f'<VertexDict {self._dict}>'
    
    def __len__(self):
        return len(self._dict)
    
    def get_candidates(self):
        return self._dict.keys()
    
    def get_couples(self, candidate:int) -> 'List[VertexCouple]':
        if candidate not in self._dict.keys():
            return [None]
        return self._dict[candidate]
    
    def get_valid_couples(self) -> List[VertexCouple]:
        valid_couples = []
        for couples in self._dict.values():
            for couple in couples:
                if couple.valid:
                    valid_couples.append(couple)
        return valid_couples
    
    def has_valid_couples(self) -> bool:
        for couples in self._dict.values():
            for couple in couples:
                if couple.valid:
                    return True
        return False
    
    def add_couple(self, couple:VertexCouple):
        if not self._validate_couple(couple):
            return

        candidate = couple.candidate
        if candidate not in self._dict.keys():
            self._new_candidate(candidate)
        if couple not in self._dict[candidate]:
            self._dict[candidate].append(couple)
    
    def remove_couple(self, couple:VertexCouple):
        candidate = couple.candidate
        if couple in self._dict[candidate]:
            self._dict[candidate].remove(couple)
    
    def has_couple(self, couple:VertexCouple) -> bool:
        candidate = couple.candidate
        if not candidate in self._dict.keys():
            return False
        if couple in self._dict[candidate]:
            return True
        return False
    
    def _validate_couple(self, couple:VertexCouple) -> bool:
        if couple.discard:
            return False
        return True
    
    def _new_candidate(self, candidate:int):
        self._dict[candidate] = []

class VertexCouples:
    def __init__(self):
        self._pairs_dict = VertexDict()
        self._uncoupled_pairs_dict = VertexDict()
        self._joined_pairs:dict[int, VertexDict] = {}

    def __repr__(self):
        return f'<VertexCouples\nuncoupled_pairs:{self._uncoupled_pairs_dict}\n'\
            f'joined_pairs:{self._joined_pairs}\n>'
    
    def get_valid_couples(self) -> List[VertexCouple]:
        pass

    def add_pair(self, vertex_pair:VertexPair):
        couple = VertexCouple(vertex_pair)
        if not self._pairs_dict.has_couple(couple):
            self._pairs_dict.add_couple(couple)
            self._uncoupled_pairs_dict.add_couple(couple)
    
    def find_couples(self, max_vertex_pairs=3):
        couples_dict:dict[int, VertexDict] = {0: VertexDict()}
        valid_couples_found = False

        level = 1
        while level <= max_vertex_pairs and not valid_couples_found:
            couples_dict[level] = self._join_uncoupled_pairs(couples_dict[level-1])
            self._joined_pairs[level] = couples_dict[level]
            valid_couples_found = couples_dict[level].has_valid_couples()
            level += 1
        
        return couples_dict[level-1].get_valid_couples()
    
    def _join_uncoupled_pairs(self, parent_couples_dict:VertexDict) -> VertexDict:
        joined_couples = VertexDict()

        for candidate in self._uncoupled_pairs_dict.get_candidates():
            uncoupled_pairs = self._uncoupled_pairs_dict.get_couples(candidate)
            if len(uncoupled_pairs) < 2:
                continue # Not enough pairs in candidate to form a vertex
            parent_couples = parent_couples_dict.get_couples(candidate)
            for parent_couple in parent_couples:
                couples = self._make_couples(uncoupled_pairs, parent_couple)
                for couple in couples:
                    joined_couples.add_couple(couple)
        return joined_couples
    
    def _make_couples(self, pairs:List[VertexCouple], parent_couple:VertexCouple=None) -> List[VertexCouple]:
        couples = []
        for pair in pairs:
            joined_couple = VertexCouple(pair.pairs, parent_couple)
            couples.append(joined_couple)
        return couples

class VertexCoupleDeducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__()
        self._cells:Cells = cells
        self._vertices = VertexCouples()
        
    def deduce(self, row:int=None, col:int=None, max_vertex_pairs=3):
        flattened_sliced_cells = self._get_flattened_sliced_cells(row, col)
        pairs = self._find_pairs(flattened_sliced_cells)
        self._add_pairs(pairs)
        valid_couples = self._find_couples(max_vertex_pairs)

        # if self._vertices.valid_couples_found:
        self._make_new_transactions(valid_couples)
        
        return pairs

    def _make_new_transactions(self, valid_couples:List[VertexCouple]):

        for valid_couple in valid_couples:
            if valid_couple.completed:
                continue

            candidate = valid_couple.candidate
            is_row = valid_couple.is_row_couple()
            vertex_cols = valid_couple.get_vertex_cols()
            valid_cell_list = valid_couple.get_cell_list()

            rows, cols = self._make_rowscols(is_row, vertex_cols)

            cells = []
            for row in rows:
                for col in cols:
                    cell = self._cells.data[row][col]
                    cells.append(cell)
            for valid_cell in valid_cell_list:
                cells.remove(valid_cell)
            
            for cell in cells:
                self._make_new_transaction(cell, candidate)
    
    def _make_rowscols(self, is_row:bool, vertex_cols:List[int]) -> 'tuple[List[int]]':
        if is_row:
            rows = list(range(9))
            cols = vertex_cols
        else:
            cols = list(range(9))
            rows = vertex_cols
        return (rows, cols)
    
    def _make_new_transaction(self, cell:Cell, candidate:int):
        self._add_transaction(cell, candidate)

    def _get_flattened_sliced_cells(self, row:int=None, col:int=None) -> List[Cell]:
        if row is not None:
            slice = self._cells[row].flatten()
        elif col is not None:
            slice = self._cells[col].flatten()
        else:
            raise ValueError('Must provide either row or col')
        
        return slice
    
    def _find_pairs(self, flattened_sliced_cells:List[Cell]) -> List[VertexPair]:
        pairs = []
        counts:dict[int, List[int]] = {}
        for i in range(1, 10):
            counts[i] = []
        
        for cell in flattened_sliced_cells:
            for candidate in cell.candidates:
                counts[candidate].append(cell)
        
        for candidate, cells in counts.items():
            if len(cells) == 2:
                topleft_cell = self._get_topleft_cell(flattened_sliced_cells)
                pair = VertexPair(candidate, topleft_cell, cells[0], cells[1])
                pairs.append(pair)
        return pairs
        
    def _get_topleft_cell(self, flattened_sliced_cells:List[Cell]) -> Cell:
        return flattened_sliced_cells[0]
    
    def _add_pairs(self, pairs:List[VertexPair]):
        for pair in pairs:
            self._vertices.add_pair(pair)
    
    def _find_couples(self, max_vertex_pairs=3):
        couples = self._vertices.find_couples(max_vertex_pairs)
        return couples

class Deducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__()
        self._cells = cells
        self.value_deducer = ValueDeducer()
        self.single_candidate_deducer = SingleCandidateDeducer(cells)
        self.companion_deducer = CompanionDeducer()
        self.linebox_deducer = LineBoxDeducer(cells)
        self.vertex_deducer = VertexCoupleDeducer(cells)
    
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
    
    def _deduce_adjacent_vertices(self, row:int, col:int):
        self.deduce_vertex(self._get_row(row))
        self.deduce_vertex(self._get_col(col))
    
    def deduce(self):
        self._deduce_all_values()
        if len(self.transactions) > 0: return
        self._deduce_all_single_candidates()
        if len(self.transactions) > 0: return
        self._deduce_all_lineboxes()
        if len(self.transactions) > 0: return
        # self._deduce_all_vertices()
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
        cells_list = self._get_all_sliced_cells(include_boxes=True)
        for cells in cells_list:
            self.deduce_value(cells)
    
    def _deduce_all_single_candidates(self):
        cells_list = self._get_all_rows()
        for cells in cells_list:
            self.deduce_single_candidate(cells)
    
    def _deduce_all_companions(self):
        cells_list = self._get_all_sliced_cells(include_boxes=True)
        for cells in cells_list:
            self.deduce_companion(cells)

    def _deduce_all_lineboxes(self):
        cells_list = self._get_all_sliced_cells(include_boxes=False)
        for cells in cells_list:
            self.deduce_linebox(cells)
    
    def _deduce_all_vertices(self):
        cells_list = self._get_all_sliced_cells(include_boxes=False)
        for cells in cells_list:
            self.deduce_vertex(cells)
    
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
        row, col = self._get_rowcol_from_sliced_cells(sliced_cells)

        self.linebox_deducer.deduce(row, col)
        self._transactions.extend_transactions(self.linebox_deducer._transactions)
    
    def deduce_vertex(self, sliced_cells:Cells):
        row, col = self._get_rowcol_from_sliced_cells(sliced_cells)

        self.vertex_deducer.deduce(row, col)
        self._transactions.extend_transactions(self.vertex_deducer._transactions)
    
    def _get_rowcol_from_sliced_cells(self, sliced_cells:Cells):
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
        
        return (row, col)

