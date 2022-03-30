import pytest
from ..sudokupy.grid import GridData, Grid

@pytest.fixture
def input_grid():
    return [
        [3,7,8,4,1,5,9,6,2],
        [4,2,9,7,6,3,1,8,5],
        [5,6,1,9,2,8,3,7,4],
        [8,3,2,1,5,7,4,9,6],
        [1,9,6,2,8,4,7,5,3],
        [7,4,5,3,9,6,2,1,8],
        [9,8,4,6,7,2,5,3,1],
        [2,5,7,8,3,1,6,4,9],
        [6,1,3,5,4,9,8,2,7]
    ]

@pytest.fixture
def zero_grid():
    return [[0 for _ in range(9)] for _ in range(9)]

class TestGridData:
    def test_zero_grid(self):
        gd = GridData()
        rows = gd.rows
        cols = gd.columns
        boxes = gd.boxes

        assert rows[0] == tuple([0]*9)
        assert cols[0] == tuple([0]*9)
        assert boxes[0][0] == tuple([0]*9)
    
    def test_constructor(self, zero_grid):
        gd = GridData(zero_grid)
        assert gd.valid == True

        grids = {}
        grids['invalid_number_grid'] = [[10 for _ in range(9)] for _ in range(9)]
        grids['invalid_type_grid'] = [['0' for _ in range(9)] for _ in range(9)]
        grids['invalid_row_structure_grid'] = [[0 for _ in range(9)] for _ in range(11)]
        grids['invalid_col_structure_grid'] = [[0 for _ in range(11)] for _ in range(9)]

        for key, val in grids.items():
            print(key, val)
            gd = GridData(val, raises_error=False)
            assert gd.valid == False
            with pytest.raises(ValueError):
                gd = GridData(val, raises_error=True)

    def test_rows(self, input_grid):
        gd = GridData(input_grid)
        rows = gd.rows
        assert rows[0] == tuple(input_grid[0])

    def test_columns(self, input_grid):
        gd = GridData(input_grid)
        cols = gd.columns
        assert len(cols) == 9
        assert cols[0] == (3,4,5,8,1,7,9,2,6)
        assert cols[-1] == (2,5,4,6,3,8,1,9,7)

    def test_boxes(self, input_grid):
        gd = GridData(input_grid)
        boxes = gd.boxes
        assert len(boxes) == 3
        for boxrow in boxes:
            assert len(boxrow) == 3
        assert boxes[0][0] == (3,7,8,4,2,9,5,6,1)
        assert boxes[1][1] == (1,5,7,2,8,4,3,9,6)
        assert boxes[2][2] == (5,3,1,6,4,9,8,2,7)
    
    def test_missing_rows(self, input_grid):
        with pytest.raises(ValueError):
            GridData(input_grid[1:], raises_error=True)
    
    def test_missing_columns(self, input_grid):
        with pytest.raises(ValueError):
            GridData([row[1:] for row in input_grid], raises_error=True)
    
    def test_non_numbers(self, input_grid):
        with pytest.raises(ValueError):
            GridData([[str(item) for item in row] for row in input_grid], raises_error=True)
    
    def test_conflicts(self, input_grid):
        input_grid[0][0] = 4
        with pytest.raises(ValueError):
            GridData(input_grid, raises_error=True)
    
    def test_conflicts_row(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[0][8] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid, raises_error=True)
    
    def test_conflicts_column(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[5][0] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid, raises_error=True)
    
    def test_conflicts_box(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[2][2] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid, raises_error=True)
    
    def test_set_item(self):
        gd = GridData()

        inputs = [
            [0,0,1],
            [1,1,2],
            [4,5,3],
            [8,8,4]
        ]
        for arg in inputs:
            gd.set_item(*arg)
        
        for arg in inputs:
            assert gd.data[arg[0]][arg[1]] == arg[2]
    
    def test_set_row(self, zero_grid):
        gd = GridData(zero_grid)

        inputs = [
            [0, [1,2,3,4,5,6,7,8,9]],
            [1, [6,0,0,0,0,0,0,0,0]],
            [2, [7,8,9,0,0,0,1,0,0]]
        ]

        for arg in inputs:
            gd.set_row(*arg)
        
        for arg in inputs:
            assert gd.rows[arg[0]] == tuple(arg[1])
    
    def test_set_column(self):
        gd = GridData()

        inputs = [
            [0, [1,2,3,4,5,6,7,8,9]],
            [1, [6,0,0,0,0,0,0,0,0]],
            [2, [7,8,9,0,0,0,1,0,0]]
        ]

        for arg in inputs:
            gd.set_column(*arg)
        
        for arg in inputs:
            assert gd.columns[arg[0]] == tuple(arg[1])
    
    def test_set_box(self):
        gd = GridData()

        inputs = [
            [0, 0, [1,2,3,4,5,6,7,8,9]],
            [1, 1, [2,0,0,0,0,0,0,0,0]],
            [2, 1, [3,4,5,0,0,0,9,0,0]]
        ]

        for arg in inputs:
            gd.set_box(*arg)
        
        for arg in inputs:
            assert gd.boxes[arg[0]][arg[1]] == tuple(arg[2])
    
    def test_set_item_error(self):
        gd = GridData(raises_error=True)

        with pytest.raises(ValueError):
            gd.set_item(0,0,10)
        
        gd.set_item(0,0,1)

        with pytest.raises(ValueError):
            gd.set_item(0,1,1)
        
        with pytest.raises(ValueError):
            gd.set_item(8, 0, 1)

    def test_set_row_error(self):
        gd = GridData(raises_error=True)

        with pytest.raises(ValueError):
            gd.set_row(10, [0]*9)
        
        with pytest.raises(ValueError):
            gd.set_row(0, [10]*9)
        
        with pytest.raises(ValueError):
            gd.set_row(0, [0]*2)
        
        with pytest.raises(ValueError):
            gd.set_row(0, [1,2,3,4,5,6,7,8,1])
        
        gd.set_row(0, [1,2,3,4,5,6,7,8,9])
        with pytest.raises(ValueError):
            gd.set_row(1, [1,0,0,0,0,0,0,0,0])

    def test_set_column_error(self):
        gd = GridData(raises_error=True)

        with pytest.raises(ValueError):
            gd.set_column(10, [0]*9)
        
        with pytest.raises(ValueError):
            gd.set_column(0, [10]*9)
        
        with pytest.raises(ValueError):
            gd.set_column(0, [0]*2)
        
        with pytest.raises(ValueError):
            gd.set_column(0, [1,2,3,4,5,6,7,8,1])
        
        gd.set_column(0, [1,2,3,4,5,6,7,8,9])
        with pytest.raises(ValueError):
            gd.set_column(1, [1,0,0,0,0,0,0,0,0])


    def test_set_box_error(self):
        gd = GridData(raises_error=True)

        with pytest.raises(ValueError):
            gd.set_box(10, 10, [0]*9)
        
        with pytest.raises(ValueError):
            gd.set_box(3, 3, [0]*9)

        with pytest.raises(ValueError):
            gd.set_box(0, 0, [10]*9)
        
        with pytest.raises(ValueError):
            gd.set_box(0, 0, [0]*2)
        
        with pytest.raises(ValueError):
            gd.set_box(0, 0, [1,2,3,4,5,6,7,8,1])
        
        gd.set_box(0, 0, [1,2,3,4,5,6,7,8,9])
        with pytest.raises(ValueError):
            gd.set_box(0, 2, [1,0,0,0,0,0,0,0,0])

    def test_valid(self):
        gd = GridData(raises_error=False)

        gd.set_item(0, 0, 1)
        assert gd.valid == True
        gd.set_item(1, 1, 1, False)
        assert gd.valid == False
    
    def test_counts(self):
        gd = GridData()
        counts = gd.counts()
        assert counts[0] == 81
        for i in range(1, 10):
            assert counts[i] == 0
        
        gd.set_row(0, list(range(1, 10)))
        counts = gd.counts()
        assert counts[0] == 72
        for i in range(1, 10):
            assert counts[i] == 1
    
    def test_count(self):
        gd = GridData()
        assert gd.count() == 0

        gd.set_row(0 ,list(range(1, 10)))
        assert gd.count() == 9
        assert gd.count(1) == 1
        assert gd.count([1, 2, 3]) == 3
        assert gd.count([1, 1, 2, 3, 4]) == 4

    def test_repr(self):
        gd = GridData()
        str_string = gd.__str__()
        repr_string = gd.__repr__()

        assert str_string.count('\n') == 8
        assert repr_string.count('#') == 10



