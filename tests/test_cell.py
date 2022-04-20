import sys
sys.path.append('..')
from sudokupy.cell import Cell, Cells, Candidate
import pytest

class TestCandidate:
    def test_repr(self):
        c = Candidate()
        repr = c.__repr__()
        for i in range(1, 10):
            assert repr.count(str(i)) == 1
        assert repr.count('<') == 1
        assert repr.count('>') == 1
    
    def test_str(self):
        c = Candidate()
        s = c.__str__()
        for i in range(1, 10):
            assert s.count(str(i)) == 1
    
    def test_print_grid(self):
        c = Candidate()
        c.set([1])
        s = c.print_grid()
        assert s.count('1') == 1
        assert s.count('.') == 8

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
        
    def test_set_candidates(self):
        c = Cell(0, 0, 0)
        assert c.candidates == list(range(1, 10))

        c.set_candidates(1)
        assert c.candidates == [1]

        c.set_candidates([2])
        assert c.candidates == [2]

        c.set_candidates([1,2,3])
        assert c.candidates == [1,2,3]

        with pytest.raises(ValueError):
            c.set_candidates(0)

    def test_remove_candidates(self):
        c = Cell(0, 0, 0)
        assert len(c.candidates) == 9

        c.remove_candidates(1)
        assert len(c.candidates) == 8
        assert 1 not in c.candidates

        c.remove_candidates([2])
        assert len(c.candidates) == 7
        assert c.candidates == [3,4,5,6,7,8,9]

        c.remove_candidates([1,2,3])
        assert len(c.candidates) == 6
        assert c.candidates == [4,5,6,7,8,9]

        c.remove_candidates([1,2,3])
        assert len(c.candidates) == 6
        
        with pytest.raises(ValueError):
            c.remove_candidates('2')
    
    def test_reset_candidates(self):
        c = Cell(0, 0, 0)
        assert len(c.candidates) == 9

        c.set_candidates([1])
        assert len(c.candidates) == 1
        c.reset_candidates()
        assert len(c.candidates) == 9

    def test_candidates(self):
        c = Cell(0, 0, 0)
        x = [1,3,5,7,9]
        c.candidates = x
        assert c.candidates == x

        c.candidates = 1
        assert c.candidates == [1]

        with pytest.raises(ValueError):
            c.candidates = 0
    
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
    
    def test_print_value(self):
        cell = Cell(0, 0, 0)
        assert cell.print_value == '.'

        for val in range(1, 10):
            assert Cell(1, 1, val).print_value == str(val)
    
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
        assert c.__repr__() == '<Cell (1,2)=3>'
    
    def test_set_permanence(self):
        c = Cell(1, 2, 3)
        assert c.is_permanent == False
        c.set_permanence(True)
        assert c.is_permanent == True
    
    def test_set_value(self):
        c = Cell(1, 2, 3)
        c.set_value(7)
        assert c.value == 7
        c.set_permanence(True)
        with pytest.raises(ValueError):
            c.set_value(5)
    
    def test_copy(self):
        c1 = Cell(1, 2, 3)
        c1.candidates = [4, 5, 6]
        c1.set_permanence(True)

        c2 = c1.copy()
        assert c1 == c2
        assert c1 is not c2
        assert c2.candidates == c1.candidates
        assert c2.is_permanent == c1.is_permanent

        c1.value = 9
        c1.candidates = []

        assert c2.value == 3
        assert c2.candidates == [4, 5, 6]
    
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

        assert str.count('\n') == 8 + 2 + 3 # 8 between grid, 2 for headers, 3 for box
        assert 'rows:9' in repr
        assert 'cols:9' in repr

        cells2 = cells[:5, :4]
        str = cells2.__str__()
        repr = cells2.__repr__()

        assert str.count('\n') == 4 + 2 # 4 between grid, 2 for headers, no box
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
    
    def test_reset_candidates(self):
        c = Cells()
        for row in c.data:
            for cell in row:
                cell.set_candidates(1)
                assert len(cell.candidates) == 1
        c.reset_candidates()
        for row in c.data:
            for cell in row:
                assert len(cell.candidates) == 9
    
    def test_remove_candidates(self):
        c = Cells()
        c.remove_candidates([1, 2])
        for row in c.data:
            for cell in row:
                assert len(cell.candidates) == 7
        
        c2 = c[0]
        c2.remove_candidates([3])
        for cell in c.data[0]:
            assert len(cell.candidates) == 6
        for cell in c.data[1]:
            assert len(cell.candidates) == 7
    
    def test_set_candidates(self):
        c = Cells()
        c[0, 0].set_candidates([1,2,3])
        assert c.data[0][0].candidates == [1, 2, 3]

        c[1].set_candidates(2)
        for cell in c.data[1]:
            assert cell.candidates == [2]
    
    def test_get_values(self):
        cells = Cells()

        values = cells.get_values(flatten=False)

        assert len(values) == 9
        for row in values:
            assert len(row) == 9
            for cell in row:
                assert cell == 0
        
        values = cells.get_values(flatten=True)

        assert len(values) == 81
        for cell in values:
            assert cell == 0

    def test_get_candidates(self):
        cells = Cells()

        candidates = cells.get_candidates(flatten=False)

        assert len(candidates) == 9
        for row in candidates:
            assert len(row) == 9
            for cell in row:
                assert cell == list(range(1, 10))
        
        candidates = cells.get_candidates(flatten=True)

        assert len(candidates) == 81
        for cell in candidates:
            assert cell == list(range(1, 10))
    
    def test_candidate(self):
        cells = Cells()
        c = cells.candidates
        assert len(c) == 9
        for row in c:
            assert len(row) == 9
            for cell in c:
                assert len(cell) == 9
        
        cells2 = cells[3]
        c = cells2.candidates
        assert len(c) == 1
        assert len(c[0]) == 9
        for cell in c[0]:
            assert len(cell) == 9
        
        cells.set_candidates([1, 2, 3])
        cells3 = cells[3:6, 0:3]
        c = cells3.candidates
        assert len(c) == 3
        for row in c:
            assert len(row) == 3
            for cell in c:
                assert len(cell) == 3
    
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

        with pytest.raises(ValueError):
            c[0].contains(10)
        with pytest.raises(ValueError):
            c[:, 1].contains([['0']])

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
    
    def test_print_candidates(self):
        c = Cells()
        s = c.print_candidates()
        substrings = ['123', '456', '789']
        for substring in substrings:
            assert s.count(substring) == 81
        
        s = c[1].print_candidates()
        for substring in substrings:
            assert s.count(substring) == 9
        
        s = c[0,0].print_candidates()
        for substring in substrings:
            assert s.count(substring) == 1
        
        c.data[0][0].remove_candidates([1, 3])
        s = c.print_candidates()
        assert s.count('.2.') == 1
    
    def test_as_cell(self):
        cells = Cells()
        cell = cells[0, 1].as_cell()
        assert isinstance(cell, Cell)
        assert cell.row == 0
        assert cell.column == 1

        with pytest.raises(ValueError):
            cells[0, 0:3].as_cell()
    
    def test_copy(self):
        cells1 = Cells()
        cells1[3, 5].values = 5
        cells1[2:4].candidates = [2, 3, 4]
        cells2 = cells1.copy()
        assert cells1 == cells2
        assert cells1 is not cells2
        cell_list = cells2.flatten()
        for i, cell in enumerate(cells1.flatten()):
            assert cell_list[i] == cell
        
        cells1[0, 0].values = 9
        cells1[0, 0].candidates = []
        
        assert cells2[0, 0].as_cell().value == 0
        assert cells2[0, 0].as_cell().candidates == list(range(1, 10))
        


    
