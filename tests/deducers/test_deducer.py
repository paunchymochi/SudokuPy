import pytest
import sys
sys.path.append('../..')
from sudokupy.cell import Cell
from sudokupy.board import Board
from sudokupy.deducers.deducer import Deducer, Deducers

class TestDeducer:
    def test_repr(self):
        d = Deducer(Board.cells)
        repr = d.__repr__()
        assert 'Deducer' in repr

    def test_is_solvable(self):
        board = Board()
        d = Deducer(board.cells)
        assert d.is_solvable() == True
        board.row[0].candidates = []
        board.row[0].values = [1, 2, 3, 4, 5, 6, 0, 0, 0]
        board.cell[0, 6].candidates = [7, 9]
        board.cell[0, 7].candidates = [7, 8]

        assert d.is_solvable() == False
    
    def test_states(self):
        b = Board()
        d = Deducer(b.cells)

        for strategy in Deducers:
            assert d._states[strategy][0] == True
        
        d.disable_companion_deducer()
        d.disable_linebox_deducer()
        d.disable_single_candidate_deducer()
        d.disable_value_deducer()
        d.disable_vertex_deducer()

        for strategy in Deducers:
            assert d._states[strategy][0] == False
        
        d.enable_companion_deducer(4)
        d.enable_linebox_deducer()
        d.enable_single_candidate_deducer()
        d.enable_value_deducer()
        d.enable_vertex_deducer(2)

        for strategy in Deducers:
            assert d._states[strategy][0] == True
        
        assert d._states[Deducers.COMPANION_DEDUCER][1] == 4
        assert d._states[Deducers.VERTEX_DEDUCER][1] == 2
    
    def test_deduce_adjacent__values(self):
        b =  Board()
        d = Deducer(b.cells)
        b.cell[0, 0].values = 5
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 9 + 6 + 6 # box, row, col
        for transaction in d.transactions:
            if transaction.cell == Cell(0, 0):
                assert transaction.candidates == list(range(1, 10))
            else:
                assert transaction.candidates == [5]
        
        d = Deducer(b.cells)
        d.disable_value_deducer()
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 0
    
    def test_deduce_adjacent__single_candidates(self):
        b = Board()
        d = Deducer(b.cells)
        b.cell[0, 0].candidates = [5]
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 8 + 6 + 6 # box, row, col
        for transaction in d.transactions:
            assert transaction.candidates == [5]
        
        d = Deducer(b.cells)
        d.disable_single_candidate_deducer()
        d.disable_companion_deducer()
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 0
    
    def test_deduce_adjacent__lineboxes(self):
        b = Board()
        d = Deducer(b.cells)
        b.row[0].remove_candidates(5)
        b.col[0].remove_candidates(7)
        b.cell[0, 0].candidates = [5, 6, 7]
        b.cell[2, 0].candidates = [5, 6, 7]
        b.cell[0, 2].candidates = [5, 6, 7]
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 8
        for transaction in d.transactions:
            if transaction.cell.row == 0:
                assert transaction.candidates == [7]
            elif transaction.cell.column == 0:
                assert transaction.candidates == [5]
            else:
                assert transaction.candidates == [5, 7]

        d = Deducer(b.cells)
        d.disable_linebox_deducer()
        d.disable_companion_deducer()
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 0
    
    def test_deduce_adjacent__companions(self):
        b = Board()
        d = Deducer(b.cells)

        b.cell[0, 0].candidates = [5, 7]
        b.cell[0, 5].candidates = [5, 9]
        b.cell[0, 7].candidates = [7, 9]
        b.cell[5, 0].candidates = [5, 8]
        b.cell[7, 0].candidates = [7, 8]
        b.cell[2, 1].candidates = [5, 6]
        b.cell[2, 2].candidates = [6, 7]
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 6 + 4 + 4 # box, row, col
        for transaction in d.transactions:
            if transaction.cell.row == 0 and transaction.cell.column > 2:
                assert transaction.candidates == [5, 7, 9]
            elif transaction.cell.column == 0 and transaction.cell.row > 2:
                assert transaction.candidates == [5, 7, 8]
            elif transaction.cell.row > 1 and transaction.cell.column > 1:
                assert transaction.candidates == [5, 6, 7]
            elif transaction.cell.row == 0:
                assert transaction.candidates == [5, 6, 7, 9]
            elif transaction.cell.column == 0:
                assert transaction.candidates == [5, 6, 7, 8]

        d = Deducer(b.cells)
        d.disable_companion_deducer()
        d.deduce_adjacent(0, 0)
        assert len(d.transactions) == 0

    def test_deduce_value(self):
        board = Board()
        d = Deducer(board.cells)
        board.cell[0, 0].values = 5
        d.deduce_value(board.box[0, 0])
        assert len(d.transactions) == 9
    
    def test_deduce_companion(self):
        board = Board()
        d = Deducer(board.cells)
        board.cell[0, 0].candidates = [1, 3]
        board.cell[1, 1].candidates = [3, 5]
        board.cell[2, 2].candidates = [1, 5]
        d.deduce_companion(board.box[0, 0])
        assert len(d.transactions) == 6
    
    def test_deduce_linebox(self):
        board = Board()
        d = Deducer(board.cells)
        for cell in board.col[2].flatten():
            cell.candidates = []
        board.cell[0, 2].candidates = [1, 4, 6]
        board.cell[1, 2].candidates = [1, 2, 3, 8]
        board.cell[4, 2].candidates = [2, 3, 4, 8]
        board.cell[6, 2].candidates = [2, 3, 4]
        board.cell[7, 2].candidates = [2, 3, 6, 8]

        d.deduce_linebox(board.col[2])
        assert len(d.transactions) == 6
        for transaction in d.transactions:
            assert transaction.candidates == [1]
    
    def test_deduce__one_value(self):
        board = Board()
        d = Deducer(board.cells)
        board.cell[0, 0].values = 5
        board.cell[0, 0].candidates = []
        d.deduce()
        assert len(d.transactions) == 8 + 6 + 6 # box, row, col
        for transaction in d.transactions:
            assert transaction.candidates == [5]
    
    def test_deduce__two_values(self):
        board = Board()
        d = Deducer(board.cells)
        board.cell[1, 1].values = 5
        board.cell[2, 2].values = 6
        d.deduce()
        assert len(d.transactions) == 9 + 12 + 12 # box, row, col

        assert sum([list(range(1, 10)) == x.candidates for x in d.transactions]) == 2
        assert sum([5, 6] == x.candidates for x in d.transactions) == 9 - 2
        assert sum([5] == x.candidates for x in d.transactions) == 6 + 6
        assert sum([6] == x.candidates for x in d.transactions) == 6 + 6
    
    def test_deduce__linebox(self):
        board = Board()
        d = Deducer(board.cells)
        board.row[0].candidates = []

        # remove 9 from box 1, 8 from box 3
        candidates = [
            [1, 2, 9], [2, 3, 4], [2, 3, 9],
            [2, 3, 4, 5], [1, 2, 3, 4, 5], [3, 4, 5],
            [3, 4, 5, 8], [1, 2, 5], [2, 3, 4, 5]
        ]
        for i, candidate in enumerate(candidates):
            board.cell[0, i].candidates = candidate
        d.deduce()
        assert len(d.transactions) == 12
        assert sum([9] == x.candidates for x in d.transactions) == 6
        assert sum([8] == x.candidates for x in d.transactions) == 6
    
    def test_deduce__companion(self):
        board = Board()
        d = Deducer(board.cells)
        
        # [1,3,5] in box[0][0], [3,5,8] in col[1]
        candidates_dict = {
            (0, 0): [1, 3],
            (1, 1): [3, 5],
            (2, 2): [1, 5],
            (6, 1): [3, 8],
            (7, 1): [5, 8]
        }
        for (x, y), candidates in candidates_dict.items():
            board.cell[x, y].candidates = candidates
        d.deduce()
        assert len(d.transactions) == 6 + (6-2)
        assert sum([1, 3, 5] == x.candidates for x in d.transactions) == 4
        assert sum([3, 5, 8] == x.candidates for x in d.transactions) == 4
        assert sum([1, 3, 5, 8] == x.candidates for x in d.transactions) == 2
