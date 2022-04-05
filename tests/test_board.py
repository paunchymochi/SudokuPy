import sys
sys.path.append('..')
from sudokupy.board import Board
import pytest

class TestBoard:
    def test_row(self):
        b = Board()
        row = b.row[1]
        row.values = list(range(1, 10))
        assert len(row) == 9
        assert row.topleft_row == 1
        assert row.topleft_column == 0
        for i in range(9):
            assert row.values[0][i] == i + 1
    
    def test_col(self):
        b = Board()
        col = b.col[1]
        col.values = list(range(1, 10))
        assert len(col) == 9
        assert col.topleft_column == 1
        assert col.topleft_row == 0
        for i in range(9):
            assert col.values[i][0] == i + 1

    def test_box(self):
        b = Board()
        box = b.box[1, 2]
        box.values = list(range(1, 10))
        assert len(box) == 9
        assert box.topleft_row == 3
        assert box.topleft_column == 6
        for i in range(3):
            for j in range(3):
                assert box.values[i][j] == i*3 + j + 1
    
    def test_cell(self):
        b = Board()
        cell = b.cell[0,8]
        cell.values = 9
        assert len(cell) == 1
        assert cell.topleft_row == 0
        assert cell.topleft_column == 8
        assert cell.values[0][0] == 9

    def test_get_row(self):
        b = Board()
        row = b.get_row(8)
        assert row.topleft_row == 8
        assert row.topleft_column == 0

    def test_get_col(self):
        b = Board()
        col = b.get_col(8)
        assert col.topleft_column == 8
        assert col.topleft_row == 0

    def test_get_box(self):
        b = Board()
        box = b.get_box(4, 8)
        assert box.topleft_row == 3
        assert box.topleft_column == 6

    def test_get_cell(self):
        b = Board()
        cell = b.get_cell(4, 8)
        assert cell.topleft_row == 4
        assert cell.topleft_column == 8
    
    def test_get_error(self):
        b = Board()
        with pytest.raises(ValueError):
            b.row[10]
        with pytest.raises(ValueError):
            b.row[1, 2]
        with pytest.raises(ValueError):
            b.col[10]
        with pytest.raises(ValueError):
            b.col[1, 2]
        with pytest.raises(ValueError):
            b.box[0]
        with pytest.raises(ValueError):
            b.box[0,5]
        with pytest.raises(ValueError):
            b.cell[0]
        with pytest.raises(ValueError):
            b.cell[0, 10]
    
    def test_reset_candidates(self):
        b = Board()
        candidates = b.cells.candidates
        for row in candidates:
            for cell in row:
                assert cell == list(range(1, 10))
        
        b.cells.set_candidates([1, 2, 3])
        candidates = b.cells.candidates
        for row in candidates:
            for cell in row:
                assert cell == [1, 2, 3]
        
        b.reset_candidates()
        candidates = b.cells.candidates
        for row in candidates:
            for cell in row:
                assert cell == list(range(1, 10))
    
    def test_deduce_row(self):
        b = Board()
        b.cell[1, 1].values = 5
        b.deduce_row(1)
        candidates = b.row[1].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 8
            assert 5 not in candidate
        
        b.cell[1, 8].values = 6
        b.cell[1, 7].values = 9
        b.deduce_row(1)
        candidates = b.row[1].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 6
            assert 5 not in candidate
            assert 6 not in candidate
            assert 9 not in candidate
    
    def test_deduce_column(self):
        b = Board()
        b.cell[1, 1].values = 5
        b.deduce_column(1)
        candidates = b.col[1].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 8
            assert 5 not in candidate
        
        b.cell[2, 1].values = 6
        b.cell[3, 1].values = 7
        b.cell[1, 8].values = 9
        b.deduce_column(1)
        candidates = b.col[1].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 6
            assert 6 not in candidate
            assert 7 not in candidate
    
    def test_deduce_box(self):
        b = Board()
        b.cell[1, 1].values = 5
        b.deduce_box(0, 0)
        candidates = b.box[0, 0].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 8
            assert 5 not in candidate
        
        b.cell[0, 0].values = 1
        b.cell[2, 0].values = 9
        b.cell[3, 0].values = 8
        b.deduce_box(0, 0)
        candidates = b.box[0, 0].get_candidates(flatten=True)
        for candidate in candidates:
            assert len(candidate) == 6
            assert 1 not in candidate
            assert 9 not in candidate
    
    def test_deduce_adjacent(self):
        b = Board()
        b.cell[4, 4].values = 5

        b.cell[0, 4].values = 1
        b.cell[4, 0].values = 2
        b.cell[3, 3].values = 3
        b.deduce_adjacent(4, 4)
        box_candidates = b.box[1, 1].get_candidates(flatten=True)
        col_candidates = b.col[4].get_candidates(flatten=True)
        row_candidates = b.row[4].get_candidates(flatten=True)

        for candidate in box_candidates:
            assert 5 not in candidate
            assert 3 not in candidate
        
        for candidate in row_candidates:
            assert 5 not in candidate
            assert 2 not in candidate
        
        for candidate in col_candidates:
            assert 5 not in candidate
            assert 1 not in candidate
        
        for candidate in [box_candidates[4], row_candidates[4], col_candidates[4]]:
            assert 5 not in candidate
            assert 1 not in candidate
            assert 2 not in candidate
            assert 3 not in candidate
    
    def test_resolve(self):
        b = Board()
        b.cell[4, 4].set_candidates(8)
        b.cell[7, 7].set_candidates(9)
        result = b.resolve()
        assert b.cell[4, 4].get_values(flatten=True)[0] == 8
        assert b.cell[4, 4].get_candidates(flatten=True)[0] == []
        assert result == [(4, 4), (7, 7)]

        b.cell[0, 0].set_candidates([1,2])
        b.cell[0, 1].set_candidates(2)

        result = b.resolve()
        assert b.cell[0, 1].get_values(flatten=True)[0] == 2
        assert b.cell[0, 0].get_values(flatten=True)[0] == 0
        assert result == [(0, 1)]
        b.deduce_box(0, 0)
        result = b.resolve()
        assert b.cell[0, 1].get_values(flatten=True)[0] == 2
        assert b.cell[0, 0].get_values(flatten=True)[0] == 1
        assert result == [(0, 0)]
    
    def test_resolve_adjacent(self):
        b = Board()

        b.cell[0, 0].set_candidates(1)
        b.cell[0, 2].set_candidates(2)
        b.cell[2, 0].set_candidates(3)
        b.cell[1, 1].set_candidates(4)
        b.cell[3, 3].set_candidates(5)

        result = b.resolve_adjacent(0, 0)
        assert len(result) == 4
        assert (0, 0) in result
        assert (0, 2) in result
        assert (2, 0) in result
        assert (1, 1) in result
        assert (3, 3) not in result

        assert b.cell[0, 0].get_values(flatten=True)[0] == 1
        assert b.cell[0, 0].get_candidates(flatten=True)[0] == []
        assert b.cell[3, 3].get_values(flatten=True)[0] == 0
        assert b.cell[3, 3].get_candidates(flatten=True)[0] == [5]


