import pytest
import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.deducers.value_deducer import ValueDeducer

class TestValueDeducer:
    def test_repr(self):
        d = ValueDeducer()
        repr = d.__repr__()
        assert 'ValueDeducer' in repr

    def test_filled_cell_with_candidates(self):
        board = Board()
        d = ValueDeducer()
        for cell in board.box[0, 0].flatten():
            cell.set_candidates([])
        cell = board.cell[0, 0]
        cell.set_values(5)
        cell.set_candidates(list(range(1, 10)))

        d.deduce(board.box[0, 0])
        assert len(d.transactions) == 1
        assert d.transactions[0].candidates == list(range(1, 10))

        cell = board.cell[2, 2]
        cell.set_values(6)
        cell.set_candidates(list(range(1, 10)))

        d.clear_transactions()
        d.deduce(board.box[0, 0])
        assert len(d.transactions) == 2
        for transaction in d.transactions:
            assert transaction.candidates == list(range(1, 10))
    
    def test_one_value(self):
        board = Board()
        d = ValueDeducer()
        board.cell[0, 0].values = 5

        d.deduce(board.row[0])
        assert len(d.transactions) == 9
        for transaction in d.transactions:
            assert transaction.candidates in [[5], list(range(1, 10))]
        
        assert sum([[5] == transaction.candidates for transaction in d.transactions]) == 8
        assert sum([list(range(1, 10)) == transaction.candidates for transaction in d.transactions]) == 1

    def test_two_values(self):
        board = Board()
        d = ValueDeducer()
        board.cell[3, 3].values = 2
        board.cell[4, 5].values = 7

        d.deduce(board.box[1, 1])
        assert len(d.transactions) == 9

        assert sum([[2, 7] == transaction.candidates for transaction in d.transactions]) == 7
        assert sum([list(range(1, 10)) == transaction.candidates for transaction in d.transactions]) == 2
    
    def test_invalid_slice(self):
        b = Board()
        d = ValueDeducer()

        with pytest.raises(ValueError):
            d.deduce(b.cells[0, 0:4])
    
    def test_invalid_cell_type(self):
        d = ValueDeducer()

        with pytest.raises(TypeError):
            d.deduce('invalid type')