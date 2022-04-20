import sys
sys.path.append('../..')
from sudokupy.deducers.deducer_base import _BaseDeducer
from sudokupy.deducers.companion_deducer import CompanionDeducer
from sudokupy.deducers.linebox_deducer import LineBoxDeducer
from sudokupy.deducers.value_deducer import ValueDeducer
from sudokupy.deducers.candidate_deducer import SingleCandidateDeducer
from sudokupy.deducers.vertex_deducer import VertexCoupleDeducer
from sudokupy.cell import Cells
from typing import List, Union
from enum import Enum

class Deducers(Enum):
    VALUE_DEDUCER = 0
    SINGLE_CANDIDATE_DEDUCER = 1
    COMPANION_DEDUCER = 2
    LINEBOX_DEDUCER = 3
    VERTEX_DEDUCER = 4

class Deducer(_BaseDeducer):
    def __init__(self, cells: Cells):
        super().__init__('Deducer')
        self._cells = cells
        self.value_deducer = ValueDeducer()
        self.single_candidate_deducer = SingleCandidateDeducer(cells)
        self.companion_deducer = CompanionDeducer()
        self.linebox_deducer = LineBoxDeducer(cells)
        self.vertex_deducer = VertexCoupleDeducer(cells)
        self._states = self._reset_states()
    
    def is_solvable(self) -> bool:
        for cell in self._cells.flatten():
            if cell.value == 0 and cell.candidates == []:
                return False
        return True
    
    def enable_value_deducer(self):
        self._set_state(Deducers.VALUE_DEDUCER, True)
    def enable_single_candidate_deducer(self):
        self._set_state(Deducers.SINGLE_CANDIDATE_DEDUCER, True)
    def enable_companion_deducer(self, max_companion_length:int=3):
        self._set_state(Deducers.COMPANION_DEDUCER, True, max_companion_length)
    def enable_linebox_deducer(self):
        self._set_state(Deducers.LINEBOX_DEDUCER, True)
    def enable_vertex_deducer(self, max_vertex_count:int=3):
        self._set_state(Deducers.VERTEX_DEDUCER, True, max_vertex_count)

    def disable_value_deducer(self):
        self._set_state(Deducers.VALUE_DEDUCER, False)
    def disable_single_candidate_deducer(self):
        self._set_state(Deducers.SINGLE_CANDIDATE_DEDUCER, False)
    def disable_companion_deducer(self):
        self._set_state(Deducers.COMPANION_DEDUCER, False)
    def disable_linebox_deducer(self):
        self._set_state(Deducers.LINEBOX_DEDUCER, False)
    def disable_vertex_deducer(self):
        self._set_state(Deducers.VERTEX_DEDUCER, False)

    def _reset_states(self) -> 'dict[Deducers, List[Union[bool, int]]]':
        d = {}
        d[Deducers.VALUE_DEDUCER] = [True, None]
        d[Deducers.SINGLE_CANDIDATE_DEDUCER] = [True, None]
        d[Deducers.COMPANION_DEDUCER] = [True, 3]
        d[Deducers.LINEBOX_DEDUCER] = [True, None]
        d[Deducers.VERTEX_DEDUCER] = [True, 3]
        return d

    def _set_state(self, deducer:Deducers, enabled:bool, max_option=None):
        self._states[deducer] = [enabled, max_option]
    
    def _is_enabled(self, deducer:Deducers) -> bool:
        return self._states[deducer][0]
    
    def deduce_adjacent(self, row:int, col:int):
        self._deduce_adjacent_values(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_single_candidates(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_lineboxes(row, col)
        if len(self.transactions) > 0: return
        self._deduce_adjacent_companions(row, col)
    
    def _deduce_adjacent_values(self, row:int, col:int):
        if not self._is_enabled(Deducers.VALUE_DEDUCER):
            return
        self.deduce_value(self._get_row(row))
        self.deduce_value(self._get_col(col))
        self.deduce_value(self._get_box(row//3, col//3))
    
    def _deduce_adjacent_single_candidates(self, row:int, col:int):
        if not self._is_enabled(Deducers.SINGLE_CANDIDATE_DEDUCER):
            return
        self.deduce_single_candidate(self._get_row(row))
        self.deduce_single_candidate(self._get_col(col))
        self.deduce_single_candidate(self._get_box(row//3, col//3))
    
    def _deduce_adjacent_lineboxes(self, row:int, col:int):
        if not self._is_enabled(Deducers.LINEBOX_DEDUCER):
            return
        self.deduce_linebox(self._get_row(row))
        self.deduce_linebox(self._get_col(col))
    
    def _deduce_adjacent_companions(self, row:int, col:int):
        if not self._is_enabled(Deducers.COMPANION_DEDUCER):
            return
        self.deduce_companion(self._get_row(row))
        self.deduce_companion(self._get_col(col))
        self.deduce_companion(self._get_box(row//3, col//3))
    
    def _deduce_adjacent_vertices(self, row:int, col:int):
        if not self._is_enabled(Deducers.VERTEX_DEDUCER):
            return
        self.deduce_vertex(self._get_row(row))
        self.deduce_vertex(self._get_col(col))
    
    def deduce(self):
        self._deduce_all_values()
        if len(self.transactions) > 0: return
        self._deduce_all_single_candidates()
        if len(self.transactions) > 0: return
        self._deduce_all_lineboxes()
        if len(self.transactions) > 0: return
        self._deduce_all_vertices()
        if len(self.transactions) > 0: return
        self._deduce_all_companions()
    
    def eliminate(self):
        self._clear_affected_cells()
        self.value_deducer.eliminate()
        self.single_candidate_deducer.eliminate()
        self.linebox_deducer.eliminate()
        self.companion_deducer.eliminate()
        self.vertex_deducer.eliminate()
        self._affected_cells.extend(self.value_deducer.affected_cells)
        self._affected_cells.extend(self.single_candidate_deducer.affected_cells)
        self._affected_cells.extend(self.linebox_deducer.affected_cells)
        self._affected_cells.extend(self.companion_deducer.affected_cells)
        self._affected_cells.extend(self.vertex_deducer.affected_cells)
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
        if not self._is_enabled(Deducers.VALUE_DEDUCER):
            return
        cells_list = self._get_all_sliced_cells(include_boxes=True)
        for cells in cells_list:
            self.deduce_value(cells)
    
    def _deduce_all_single_candidates(self):
        if not self._is_enabled(Deducers.SINGLE_CANDIDATE_DEDUCER):
            return
        cells_list = self._get_all_rows()
        for cells in cells_list:
            self.deduce_single_candidate(cells)
    
    def _deduce_all_companions(self):
        if not self._is_enabled(Deducers.COMPANION_DEDUCER):
            return
        cells_list = self._get_all_sliced_cells(include_boxes=True)
        for cells in cells_list:
            self.deduce_companion(cells)

    def _deduce_all_lineboxes(self):
        if not self._is_enabled(Deducers.LINEBOX_DEDUCER):
            return
        cells_list = self._get_all_sliced_cells(include_boxes=False)
        for cells in cells_list:
            self.deduce_linebox(cells)
    
    def _deduce_all_vertices(self):
        if not self._is_enabled(Deducers.VERTEX_DEDUCER):
            return
        cells_list = self._get_all_sliced_cells(include_boxes=False)
        for cells in cells_list:
            self.deduce_vertex(cells)
    
    def deduce_value(self, sliced_cells:Cells):
        if not self._is_enabled(Deducers.VALUE_DEDUCER):
            return
        self.value_deducer.deduce(sliced_cells)
        self._transactions.extend_transactions(self.value_deducer._transactions)
    
    def deduce_single_candidate(self, sliced_cells:Cells):
        if not self._is_enabled(Deducers.SINGLE_CANDIDATE_DEDUCER):
            return
        self.single_candidate_deducer.deduce(sliced_cells)
        self._transactions.extend_transactions(self.single_candidate_deducer._transactions)
    
    def deduce_companion(self, sliced_cells:Cells):
        if not self._is_enabled(Deducers.COMPANION_DEDUCER):
            return
        max_companion_length = self._states[Deducers.COMPANION_DEDUCER][1]
        self.companion_deducer.deduce(sliced_cells, max_companion_length)
        self._transactions.extend_transactions(self.companion_deducer._transactions)
    
    def deduce_linebox(self, sliced_cells:Cells):
        if not self._is_enabled(Deducers.LINEBOX_DEDUCER):
            return
        row, col = self._get_rowcol_from_sliced_cells(sliced_cells)

        self.linebox_deducer.deduce(row, col)
        self._transactions.extend_transactions(self.linebox_deducer._transactions)
    
    def deduce_vertex(self, sliced_cells:Cells):
        if not self._is_enabled(Deducers.VERTEX_DEDUCER):
            return
        row, col = self._get_rowcol_from_sliced_cells(sliced_cells)

        max_vertex_pairs = self._states[Deducers.VERTEX_DEDUCER][1]
        self.vertex_deducer.deduce(row, col, max_vertex_pairs)
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
