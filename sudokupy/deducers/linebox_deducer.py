import sys
sys.path.append('../..')
from sudokupy.cell import Cell, Cells
from sudokupy.deducers.deducer_base import _BaseDeducer 
from typing import Dict, Optional, List

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
    