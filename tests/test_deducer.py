import pytest
import sys
sys.path.append('..')
from sudokupy.cell import Cells, Cell
from sudokupy.board import Board
from sudokupy.deducers.deducer import Deducer, Deducers
from sudokupy.deducers.deducer_base import  Transaction, Transactions
from sudokupy.deducers.companion_deducer import CompanionDeducer, _Companion
from sudokupy.deducers.linebox_deducer import LineBoxDeducer
from sudokupy.deducers.candidate_deducer import SingleCandidateDeducer
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
