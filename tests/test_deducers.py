import pytest
import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from sudokupy.board import Board
from sudokupy.deducers.deducer_base import  Transaction, Transactions
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
