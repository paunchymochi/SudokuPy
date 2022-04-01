from ..sudokupy.board import Board
import pytest

class TestBoard:
    def test_row(self):
        b = Board()
        row = b.row[1]
        assert len(row) == 9
        assert row.topleft_row == 1
        assert row.topleft_column == 0
    
    def test_col(self):
        b = Board()
        col = b.col[1]
        assert len(col) == 9
        assert col.topleft_column == 1
        assert col.topleft_row == 0

    def test_box(self):
        b = Board()
        box = b.box[1, 2]
        assert len(box) == 9
        assert box.topleft_row == 3
        assert box.topleft_column == 6