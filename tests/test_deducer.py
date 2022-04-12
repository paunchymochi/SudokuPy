import pytest
import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from sudokupy.board import Board
from sudokupy.deducer import CompanionDeducer, LineBoxDeducer, ValueDeducer, SingleCandidateDeducer, Deducer, Transaction, Transactions

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

        t.add_transaction(Cell(0, 0, 0), [1])
        assert t.__str__().count('Transaction') == 1
    
    def test_transactions(self):
        t = Transactions()
        assert t.transactions == []

        t.add_transaction(Cell(0, 0, 0), [2, 3])
        assert len(t.transactions) == 1
        assert isinstance(t.transactions[0], Transaction)

    def test_extend_transactions(self):
        raise NotImplementedError

    def test_clear_transactions(self):
        raise NotImplementedError

    def test_get_transactions(self):
        raise NotImplementedError


class TestCompanionDeducer:
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

class TestSingleCandidateDeducer:
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
    
class TestDeducer:
    def test_is_solvable(self):
        board = Board()
        d = Deducer(board.cells)
        board.row[0].candidates = []
        board.row[0].values = [1, 2, 3, 4, 5, 6, 0, 0, 0]
        board.cell[0, 6].candidates = [7, 9]
        board.cell[0, 7].candidates = [7, 8]

        assert d.is_solvable() == False

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

