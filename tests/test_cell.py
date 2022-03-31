import pytest
from ..sudokupy.cell import Cell

class TestCell:
    def test_constructor(self):
        c = Cell(0, 1, 2)
        assert c.row == 0
        assert c.column == 1
        assert c.value == 2

    def test_row(self):
        for row in range(9):
            assert Cell(row, 0, 1).row == row
        
        with pytest.raises(ValueError):
            Cell(10, 0, 0)
        
        with pytest.raises(ValueError):
            Cell('0', 0, 0)
    
    def test_column(self):
        for col in range(9):
            assert Cell(0, col, 1).column == col
    
        with pytest.raises(ValueError):
            Cell(0, 10, 0)
        
        with pytest.raises(ValueError):
            Cell(0, '0', 0)
    
    def test_value(self):
        for val in range(10):
            assert Cell(1, 1, val).value == val
    
        with pytest.raises(ValueError):
            Cell(0, 0, 11)
        
        with pytest.raises(ValueError):
            Cell(0, 0, '0')
    
    def test_box(self):
        for row in [0, 3, 6]:
            for col in [1,4,7]:
                assert Cell(row, col, 0).box == (row // 3) * 3 + col // 3

    def test_boxrow(self):
        for row in range(9):
            assert Cell(row, 0, 0).boxrow == row // 3

    def test_boxcol(self):
        for col in range(9):
            assert Cell(0, col, 0).boxcol == col // 3
    
    def test_repr(self):
        c = Cell(1, 2, 3)
        assert c.__repr__() == '<Cell row:1 column:2 value:3>'

class TestCells:
    def test_constructor(self):
        raise NotImplementedError
    
    def test_repr(self):
        raise NotImplementedError
    
    def test_len(self):
        raise NotImplementedError
    
    def test_getitem(self):
        raise NotImplementedError
    
    def test_setitem(self):
        raise NotImplementedError
    
    def test_set_values(self):
        raise NotImplementedError
    
    def test_data(self):
        raise NotImplementedError