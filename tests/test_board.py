from ..sudokupy.board import Board
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
        raise NotImplementedError
    
    def test_deduce_row(self):
        raise NotImplementedError
    
    def test_deduce_column(self):
        raise NotImplementedError
    
    def test_deduce_box(self):
        raise NotImplementedError
    
    def test_deduce_cell(self):
        raise NotImplementedError
    
    def test_resolve_cell(self):
        raise NotImplementedError



        