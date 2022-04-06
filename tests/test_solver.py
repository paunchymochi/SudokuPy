import pytest
import sys
sys.path.append('..')
from sudokupy.cell import Cells
from sudokupy.board import Board
from sudokupy.solver import CompanionDeducer, LineBoxDeducer, ValueDeducer, Deducer

@pytest.fixture
def blank_board():
    board = Board()
    for cell in board.cells.flatten():
        cell.set_candidates([])
    return board

class TestCompanionDeducer:
    def test_single_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 1].set_candidates(5)

        d.deduce(board.row[0])
        assert len(d.operations) == 8

        board.cell[0, 2].remove_candidates(5)
        d.clear_operations()
        d.deduce(board.row[0])
        assert len(d.operations) == 7
    
    def test_double_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[3, 5].set_candidates([2, 4])
        board.cell[7, 5].set_candidates([2, 4])

        d.deduce(board.col[5])
        assert len(d.operations) == 7
        for operation in d.operations:
            assert operation.candidates_to_remove == [2, 4]

        board.cell[0, 5].set_candidates([1, 3])
        board.cell[8, 5].set_candidates([1, 3])

        d.clear_operations()
        d.deduce(board.col[5])
        assert len(d.operations) == 5 + 5
        for operation in d.operations:
            assert operation.candidates_to_remove in [[2, 4], [1, 3]]
            assert operation.cell.column == 5

    def test_triple_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 0].set_candidates([1,3])
        board.cell[0, 2].set_candidates([3, 5])
        board.cell[1, 1].set_candidates([1, 5])

        d.deduce(board.box[0, 0])
        assert len(d.operations) == 6
        for operation in d.operations:
            assert operation.candidates_to_remove == [1, 3, 5]
    
    def test_quadruple_companion(self):
        d = CompanionDeducer()
        board = Board()
        board.cell[0, 0].set_candidates([1,3])
        board.cell[0, 2].set_candidates([3, 5])
        board.cell[1, 1].set_candidates([1, 7])

        d.deduce(board.box[0, 0])
        assert len(d.operations) == 0

        board.cell[1, 0].set_candidates([5, 7])
        d.deduce(board.box[0, 0])
        assert len(d.operations) == 5
        for operation in d.operations:
            assert operation.candidates_to_remove == [1, 3, 5, 7]

    
class TestLineBoxDeducer:
    pass

class TestValueDeducer:
    pass

class TestDeducer:
    pass