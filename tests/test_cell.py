import pytest
from ..sudokupy.cell import Cell

class TestCell:
    def test_constructor(self):
        c = Cell(0, 1, 2)
        assert c.row == 0
        assert c.column == 1
        assert c.value == 2
