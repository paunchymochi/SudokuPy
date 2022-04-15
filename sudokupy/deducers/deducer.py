import sys
sys.path.append('../..')
from sudokupy.deducers.deducer_base import _BaseDeducer
from sudokupy.deducers.companion_deducer import CompanionDeducer
from sudokupy.cell import Cells
from sudokupy.deducer import ValueDeducer, SingleCandidateDeducer, LineBoxDeducer, VertexCoupleDeducer
from typing import List

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
