import sys
sys.path.append('../..')
from sudokupy.cell import Cells, Cell
from sudokupy.deducers.deducer_base import _BaseDeducer

from typing import List, Dict, Optional, Union, Tuple

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