import pytest
from ..sudokupy.cell import Cell, Cells, Candidate

class TestCandidate:
    def test_constructor(self):
        c = Candidate()
        assert c.count() == 9

    def test_remove(self):
        c = Candidate()
        assert c.count() == 9
        c.remove(1)
        assert c.count() == 8
        c.remove([2])
        assert c.count() == 7
        c.remove([2, 3])
        assert c.count() == 6
        c.remove([1,2,3])
        assert c.count() == 6

        with pytest.raises(ValueError):
            c.remove(0)
        with pytest.raises(ValueError):
            c.remove(['2'])

    def test_set(self):
        c = Candidate()
        assert c.count() == 9
        c.set(1)
        assert c.count() == 1
        c.set(2)
        assert c.count() == 1
        c.set([1,2,3])
        assert c.count() == 3

        with pytest.raises(ValueError):
            c.set(0)
        with pytest.raises(ValueError):
            c.set(['2'])

    def test_count(self):
        c = Candidate()
        assert c.count() == 9
        c.remove(1)
        assert c.count() == 8
        c.set([2,3])
        assert c.count() == 2

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
        cells = Cells()
        str = cells.__str__()
        repr = cells.__repr__()

        assert str.count('\n') == 8 + 2 # 8 between grid, 2 for headers
        assert 'rows:9' in repr
        assert 'cols:9' in repr

        cells2 = cells[:5, :4]
        str = cells2.__str__()
        repr = cells2.__repr__()

        assert str.count('\n') == 4 + 2
        assert 'rows:5' in repr
        assert 'cols:4' in repr
    
    def test_len(self):
        cells = Cells()
        assert len(cells) == 81
        assert len(cells[:]) == 81
        assert len(cells[1]) == 9
        assert len(cells[1,1]) == 1
    
    def test_values_getter(self):
        cells = Cells()
        values = cells.values
        assert len(values) == 9
        assert len(values[0]) == 9
        assert values[0][0] == 0

        cells2 = cells[1]
        values = cells2.values
        assert len(values) == 1
        assert len(values[0]) == 9

        cells3 = cells[:,1]
        values = cells3.values
        assert len(values) == 9
        assert len(values[0]) == 1

        cells3 = cells[1, 1]
        values = cells3.values
        assert len(values) == 1
        assert len(values[0]) == 1
        assert values[0][0] == 0

        cells4 = cells[3, 3:6]
        values = cells4.values
        assert len(values) == 1
        assert len(values[0]) == 3
    
    def test_values_setter(self):
        cells = Cells()
        cells[0,0].values = 1
        assert cells.data[0][0].value == 1

        cells[1].values = list(range(1, 10))
        for i in range(1, 10):
            assert cells.data[1][i-1].value == i
        
        cells[:, 2].values = list(range(1, 10))
        for i in range(1, 10):
            assert cells.data[i-1][2].value == i

        cells[3:6,3:6].values = [[1,2,3],[4,5,6],[7,8,9]]
        for i in range(3):
            for j in range(3):
                assert cells.data[i+3][j+3].value==(i*3)+(j+1)

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
    
    def test_invalid_set_values(self):
        c = Cells()
        for case in [ '', ['0']*81, [0]*80, ]:
            with pytest.raises(ValueError):
                c.set_values(case)
        
        c2 = c[0]
        for case in [ [1]*10, [1], ['1']*9]:
            with pytest.raises(ValueError):
                c2.set_values(case)
    
    def test_topleft(self):
        c = Cells()
        assert c.topleft_row == 0
        assert c.topleft_column == 0

        c1 = c[1, 2]
        assert c1.topleft_row == 1
        assert c1.topleft_column == 2

        c2 = c[3:5, 6:]
        assert c2.topleft_row == 3
        assert c2.topleft_column == 6
    
    def test_contains(self):
        c = Cells()
        assert c.contains(0) == True
        assert c.contains(1) == False

        c[0, 0].values = 1
        c[0, 1].values = 2
        c[0, 2].values = 3
        assert c[0].contains([0, 1]) == True
        assert c[0].contains([1, 2, 3]) == True
        assert c[:,1].contains([0, 2]) == True

    def test_data(self):
        c1 = Cells()
        c2 = c1[0]
        c3 = c1[:, 0]
        c4 = c1[0,0]

        cells = [c1, c2, c3, c4]
        rows = [9, 1, 9, 1]
        cols = [9, 9, 1, 1]

        for i, cell in enumerate(cells):
            data = cell.data
            assert type(data) is list
            assert type(data[0]) is list
            assert isinstance(data[0][0], Cell)
            assert len(data) == rows[i]
            assert len(data[0]) == cols[i]
    
    def test_invalid_constructor(self):
        c = Cells()
        data = c.data
        invalid_inputs = [
            '',
            [''],
            [['', ''], ['', '']],
            data[1],
            data[1][1],
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                Cells(invalid_input)
    
