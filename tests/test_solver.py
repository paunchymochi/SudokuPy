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

    def test_row_linebox(self):
        board = Board()
        d = LineBoxDeducer(board.cells)
        for cell in board.row[0].flatten():
            cell.set_candidates([])
        
        board.cell[0, 0].set_candidates([1, 8, 9])
        board.cell[0, 1].set_candidates([1, 3, 6, 8])
        board.cell[0, 3].set_candidates([1, 4, 5, 6])
        board.cell[0, 4].set_candidates([5, 6, 7, 9])
        board.cell[0, 7].set_candidates([1, 2, 3, 5])
        board.cell[0, 8].set_candidates([2, 4, 6, 7, 9])

        d.deduce(row=0)
        assert len(d.operations) == 12
        for operation in d.operations:
            assert operation.candidates_to_remove in [[2], [8]]
        
    def test_col_linebox(self):
        board = Board()
        d = LineBoxDeducer(board.cells)
        for cell in board.col[4].flatten():
            cell.set_candidates([])
        
        board.cell[0, 4].set_candidates([1, 3, 7, 8])
        board.cell[1, 4].set_candidates([1, 4, 7, 9])
        board.cell[2, 4].set_candidates([2, 4, 7, 9])
        board.cell[3, 4].set_candidates([2, 3, 4, 7])
        board.cell[4, 4].set_candidates([3, 5, 6, 8])
        board.cell[7, 4].set_candidates([2, 5, 7, 8])
        board.cell[8, 4].set_candidates([4, 5, 6])

        d.deduce(col=4)
        assert len(d.operations) == 12
        for operation in d.operations:
            assert operation.candidates_to_remove in [[1],[9]]

class TestValueDeducer:
    def test_filled_cell_with_candidates(self):
        board = Board()
        d = ValueDeducer()
        for cell in board.box[0, 0].flatten():
            cell.set_candidates([])
        cell = board.cell[0, 0]
        cell.set_values(5)
        cell.set_candidates(list(range(1, 10)))

        d.deduce(board.box[0, 0])
        assert len(d.operations) == 1
        assert d.operations[0].candidates_to_remove == list(range(1, 10))

        cell = board.cell[2, 2]
        cell.set_values(6)
        cell.set_candidates(list(range(1, 10)))

        d.clear_operations()
        d.deduce(board.box[0, 0])
        assert len(d.operations) == 2
        for operation in d.operations:
            assert operation.candidates_to_remove == list(range(1, 10))
    
    def test_one_value(self):
        board = Board()
        d = ValueDeducer()
        board.cell[0, 0].values = 5

        d.deduce(board.row[0])
        assert len(d.operations) == 9
        for operation in d.operations:
            assert operation.candidates_to_remove in [[5], list(range(1, 10))]
        
        assert sum([[5] == operation.candidates_to_remove for operation in d.operations]) == 8
        assert sum([list(range(1, 10)) == operation.candidates_to_remove for operation in d.operations]) == 1

    def test_two_values(self):
        board = Board()
        d = ValueDeducer()
        board.cell[3, 3].values = 2
        board.cell[4, 5].values = 7

        d.deduce(board.box[1, 1])
        assert len(d.operations) == 9

        assert sum([[2, 7] == operation.candidates_to_remove for operation in d.operations]) == 7
        assert sum([list(range(1, 10)) == operation.candidates_to_remove for operation in d.operations]) == 2
    
class TestDeducer:
    pass