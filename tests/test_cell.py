import pytest
from ..sudokupy.cell import Cell, Cells

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
    
    def test_value_setter(self):
        for val in range(10):
            c = Cell(0, 0, 0)
            c.value = val
            assert c.value == val
        
        with pytest.raises(ValueError):
            c = Cell(0, 0, 0)
            c.value = 11
        
        with pytest.raises(ValueError):
            c = Cell(0, 0, 0)
            c.value = '0'
    
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
        cells = Cells()
        assert len(cells) == 81
        assert cells.is_sliced == False
        cells2 = cells[0]
        cells3 = Cells(cells2.data)
        assert len(cells2) == len(cells3) == 9
        assert cells2.is_sliced == cells3.is_sliced == True

        cells4 = cells[0,0]
        cells5 = Cells(cells4.data)
        assert len(cells4) == len(cells5) == 1
        assert cells4.is_sliced == cells5.is_sliced == True
    
    def test_repr(self):
        raise NotImplementedError
    
    def test_len(self):
        cells = Cells()
        assert len(cells) == 81
        assert len(cells[:]) == 81
        assert len(cells[1]) == 9
        assert len(cells[1,1]) == 1
    
    def test_setitem(self):
        raise NotImplementedError
    
    def test_set_values(self):
        c = Cells()

        c.set_values([1]*81)
        assert c.data[0][0].value == 1
        assert c.data[8][8].value == 1

        c[0,0].set_values(2)
        assert c.data[0][0].value == 2

        c[1].set_values(list(range(9)))
        for i in range(9):
            assert c.data[1][i].value == i
        
        c[0:3, 3:6].set_values([ [1,2,3], [4,5,6], [7,8,9] ])
        for i in range(3):
            for j in range(3):
                assert c.data[i][j+3].value == (i*3) + (j+1)
    
    def test_data(self):
        c1 = Cells()
        c2 = c1[0]
        c3 = c1[0,0]

        cells = [c1, c2, c3]

        for cell in cells:
            data = cell.data
            assert type(data) is list
            assert type(data[0]) is list
            assert isinstance(data[0][0], Cell)
