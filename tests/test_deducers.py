import pytest
import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from sudokupy.board import Board
from sudokupy.deducers.deducer_base import  Transaction, Transactions
from sudokupy.deducers.linebox_deducer import LineBoxDeducer
from sudokupy.deducers.value_deducer import ValueDeducer
from sudokupy.deducers.vertex_deducer import VertexCoupleDeducer

class TestTransaction:
    def test_cell(self):
        cell = Cell(0, 0, 0)
        t = Transaction(cell)
        assert t.cell == cell

    def test_add(self):
        cell = Cell(0, 0, 0)
        t = Transaction(cell)
        assert t.candidates == []

        t.add([3, 1, 2])
        assert t.candidates == [1, 2, 3]

        t.add([4])
        assert t.candidates == [1, 2, 3, 4]

        t.add([1])
        assert t.candidates == [1, 2, 3, 4]

    def test_eq(self):
        cell = Cell(0, 0, 0)
        cell2 = Cell(0, 0, 8)
        t1 = Transaction(cell)
        t2 = Transaction(cell2)

        assert t1 == t2

        cell3 = Cell(1, 1, 0)
        cell4 = Cell(1, 1, 7)
        t3 = Transaction(cell3)
        t4 = Transaction(cell4)

        assert t3 != t1
        assert t3 == t4

    def test_repr(self):
        cell = Cell(0, 0, 0)
        t = Transaction(cell)
        repr = t.__repr__()
        assert 'Transaction' in repr

class TestTransactions:
    def test_repr(self):
        t = Transactions()
        assert t.__str__().count('Transaction') == 0
        assert t.__repr__().count('Transaction') == 1

        t.add_transaction(Cell(0, 0, 0), [1])
        assert t.__str__().count('Transaction') == 1
        assert t.__repr__().count('Transaction') == 2
    
    def test_transactions(self):
        t = Transactions()
        assert t.transactions == []

        t.add_transaction(Cell(0, 0, 0), [2, 3])
        assert len(t.transactions) == 1
        assert isinstance(t.transactions[0], Transaction)
    
    def test_len(self):
        t = Transactions()
        assert len(t) == 0

        t.add_transaction(Cell(0, 0, 0), [1])
        assert len(t) == 1
        t.add_transaction(Cell(0, 0, 4), [3, 4, 5])
        assert len(t) == 1

        t.add_transaction(Cell(1, 1, 0), [7, 8, 9])
        assert len(t) == 2

    def test_extend_transactions(self):
        t1 = Transactions()
        t2 = Transactions()
        t3 = Transactions()

        assert len(t1.transactions) == 0
        t2.add_transaction(Cell(0, 0, 0), [1, 2])
        t1.extend_transactions(t2)
        assert len(t1.transactions) == 1
        assert isinstance(t1.transactions[0], Transaction)
        assert t1.transactions[0].candidates == [1, 2]
        t3.add_transaction(Cell(0, 0, 0), [3, 4])
        t1.extend_transactions(t3)
        assert len(t1.transactions) == 1
        assert t1.transactions[0].candidates == [1, 2, 3, 4]

        t2.add_transaction(Cell(8, 8, 0), [7, 8, 9])
        t1.extend_transactions(t2)
        assert len(t1.transactions) == 2
        assert t1.transactions[-1].candidates == [7, 8, 9]

    def test_clear_transactions(self):
        t = Transactions()
        t.add_transaction(Cell(0, 0, 0), [1, 2])
        assert len(t.transactions) == 1

        t.clear_transactions()
        assert len(t.transactions) == 0

    def test_get_transactions(self):
        t = Transactions()
        result = t.get_transactions()
        assert type(result) is list
        assert len(result) == 0

        t.add_transaction(Cell(0, 0, 0), [1, 2])
        result = t.get_transactions()
        assert type(result) is list
        assert len(result) == 1

class TestLineBoxDeducer:
    def test_repr(self):
        d = LineBoxDeducer(Board.cells)
        assert 'LineBoxDeducer' in d.__repr__()

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
        assert len(d.transactions) == 12
        for transaction in d.transactions:
            assert transaction.candidates in [[2], [8]]
        
    def test_col_linebox(self):
        board = Board()
        d = LineBoxDeducer(board.cells)
        for cell in board.col[4].flatten():
            cell.set_candidates([])
        
        # remove 1 & 9 in box[0, 1]
        board.cell[0, 4].set_candidates([1, 3, 7, 8])
        board.cell[1, 4].set_candidates([1, 4, 7, 9])
        board.cell[2, 4].set_candidates([2, 4, 7, 9])
        board.cell[3, 4].set_candidates([2, 3, 4, 7])
        board.cell[4, 4].set_candidates([3, 5, 6, 8])
        board.cell[7, 4].set_candidates([2, 5, 7, 8])
        board.cell[8, 4].set_candidates([4, 5, 6])

        d.deduce(col=4)
        assert len(d.transactions) == 6
        for transaction in d.transactions:
            assert transaction.candidates == [1, 9]

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
