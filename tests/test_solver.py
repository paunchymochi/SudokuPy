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

class TestLineBoxDeducer:
    pass

class TestValueDeducer:
    pass

class TestDeducer:
    pass