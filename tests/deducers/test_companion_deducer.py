import pytest
import sys
sys.path.append('../..')
from sudokupy.cell import Cell
from sudokupy.board import Board
from sudokupy.deducers.companion_deducer import CompanionDeducer, _Companion

class TestCompanionDeducer:
    def test_repr(self):
        d = CompanionDeducer()
        repr = d.__repr__()
        assert 'CompanionDeducer' in repr

    def test_single_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 1].set_candidates(5)

        d.deduce(board.row[0])
        assert len(d.transactions) == 8

        board.cell[0, 2].remove_candidates(5)
        d.clear_transactions()
        d.deduce(board.row[0])
        assert len(d.transactions) == 7
        
        d.eliminate()
        assert len(d.affected_cells) == 7
    
    def test_double_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[3, 5].set_candidates([2, 4])
        board.cell[7, 5].set_candidates([2, 4])

        d.deduce(board.col[5])
        assert len(d.transactions) == 7
        for transaction in d.transactions:
            assert transaction.candidates == [2, 4]

        board.cell[0, 5].set_candidates([1, 3])
        board.cell[8, 5].set_candidates([1, 3])

        d.clear_transactions()
        d.deduce(board.col[5])
        assert len(d.transactions) == 5
        for transaction in d.transactions:
            assert transaction.candidates == [1, 2, 3, 4]
            assert transaction.cell.column == 5
    
    def test_triple_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 0].set_candidates([1,3])
        board.cell[0, 2].set_candidates([3, 5])
        board.cell[1, 1].set_candidates([1, 5])

        d.deduce(board.box[0, 0])
        assert len(d.transactions) == 6
        for transaction in d.transactions:
            assert transaction.candidates == [1, 3, 5]
    
    def test_quadruple_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 0].set_candidates([1,3])
        board.cell[0, 2].set_candidates([3, 5])
        board.cell[1, 1].set_candidates([1, 7])

        d.deduce(board.box[0, 0], 4)
        assert len(d.transactions) == 0

        board.cell[1, 0].set_candidates([5, 7])
        d.deduce(board.box[0, 0], 4)
        assert len(d.transactions) == 5
        for transaction in d.transactions:
            assert transaction.candidates == [1, 3, 5, 7]

class TestCompanion:
    def test_constructor(self):
        b = Board()
        c = _Companion(b.cell[0, 0].flatten()[0], max_level=3)
        assert len(c.candidates) == 0
        assert c.candidates == []
        assert c.companion == []
        assert c.skip == True
        assert c.valid == False

        c = _Companion(b.cell[0, 0].flatten()[0], max_level=9)
        assert len(c.candidates) == 1
        assert len(c.candidates[0]) == 9
        assert len(c.companion) == 9
        assert c.skip == False
        assert c.valid == False
    
    def test_constructor_other(self):
        b = Board()
        cell1 = b.cell[0, 0].flatten()[0]
        cell1.candidates = [1, 2, 3]
        c = _Companion(cell1)

        cell2 = b.cell[1, 1].flatten()[0]
        cell2.candidates = [2, 3, 4]
        c2 = _Companion(cell2, c)
        assert len(c2.candidates) == 2
        assert c2.candidates[0] == [1, 2, 3]
        assert c2.candidates[1] == [2, 3, 4]
        assert c2.companion == [1, 2, 3, 4]
    
    def test_repr(self):
        c = _Companion(Cell(0, 0, 0))
        repr = c.__repr__()
        assert 'Companion' in repr
    
    def test_eq(self):
        b = Board()
        b.box[0, 0].candidates = [2, 3, 4]
        c1 = _Companion(b.cell[1, 1].flatten()[0], max_level=3)
        c2 = _Companion(b.cell[1, 1].flatten()[0], max_level=3)
        assert c1 == c2
        c3 = _Companion(b.cell[0, 0].flatten()[0], max_level=3)
        assert c1 != c3
    
    def test_len(self):
        b = Board()
        b.cells.candidates = [2, 3, 4]
        c = _Companion(b.cell[0, 0].flatten()[0], max_level=3)
        assert len(c) == 1
        c = _Companion(b.cell[1, 1].flatten()[0], max_level=3)
        assert len(c) == 1

        c = _Companion(b.cell[8, 8].flatten()[0], c, max_level=3)
        assert len(c) == 2