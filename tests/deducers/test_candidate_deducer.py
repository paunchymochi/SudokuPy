import pytest
import sys
sys.path.append('../..')
from sudokupy.board import Board
from sudokupy.deducers.candidate_deducer import SingleCandidateDeducer

class TestSingleCandidateDeducer:
    def test_repr(self):
        d = SingleCandidateDeducer(Board.cells)
        repr = d.__repr__()
        assert 'SingleCandidateDeducer' in repr

    def test_deduce(self):
        board = Board()
        d = SingleCandidateDeducer(board.cells)
        board.cell[0, 0].candidates = [1]
        d.deduce(board.box[0, 0])
        assert len(d.transactions) == (9-1) + 6 + 6  # box, row, col
        
        for transaction in d.transactions:
            assert transaction.candidates == [1]
    
    def test_deduce_two_single_candidates(self):
        board = Board()
        d = SingleCandidateDeducer(board.cells)
        board.cell[3, 3].candidates = [1]
        board.cell[3, 8].candidates = [3]
        d.deduce(board.row[3])
        assert len(d.transactions) == (8 + 8) + 3 + (6 + 6) # box, row, col

        assert sum([[1, 3] == transaction.candidates for transaction in d.transactions]) == 7
        assert sum([[1] == transaction.candidates for transaction in d.transactions]) == 6 + 6
        assert sum([[3] == transaction.candidates for transaction in d.transactions]) == 6 + 6
    