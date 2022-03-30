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
    return [[0]*9]*9

class TestGridData:
    def test_zero_grid(self, zero_grid):
        gd = GridData(zero_grid)
        rows = gd.rows
        cols = gd.columns
        boxes = gd.boxes

        assert rows[0] == tuple([0]*9)
        assert cols[0] == tuple([0]*9)
        assert boxes[0][0] == tuple([0]*9)
    
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
            GridData(input_grid[1:])
    
    def test_missing_columns(self, input_grid):
        with pytest.raises(ValueError):
            GridData([row[1:] for row in input_grid])
    
    def test_non_numbers(self, input_grid):
        with pytest.raises(ValueError):
            GridData([[str(item) for item in row] for row in input_grid])
    
    def test_conflicts(self, input_grid):
        input_grid[0][0] = 4
        with pytest.raises(ValueError):
            GridData(input_grid)
    
    def test_conflicts_row(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[0][8] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid)
    
    def test_conflicts_column(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[5][0] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid)
    
    def test_conflicts_box(self, zero_grid):
        zero_grid[0][0] = 1
        zero_grid[2][2] = 1
        with pytest.raises(ValueError):
            GridData(zero_grid)
    
    def test_set_item(self, zero_grid):
        gd = GridData(zero_grid)

        inputs = [
            [0,0,1],
            [1,1,2],
            [4,5,3],
            [8,8,4]
        ]
        for arg in inputs:
            gd.set_item(*arg)
        
        for arg in inputs:
            assert gd.data[arg[0], arg[1]] == arg[2]
    
    def test_set_row(self, zero_grid):
        gd = GridData(zero_grid)

        inputs = [
            [0, [1,2,3,4,5,6,7,8,9]],
            [1, [2,0,0,0,0,0,0,0,0]],
            [2, [3,4,5,0,0,0,9,0,0]]
        ]

        for arg in inputs:
            gd.set_row(*arg)
        
        for arg in inputs:
            assert gd.rows[arg[0]] == arg[1]
    
    def test_set_column(self, zero_grid):
        gd = GridData(zero_grid)

        inputs = [
            [0, [1,2,3,4,5,6,7,8,9]],
            [1, [2,0,0,0,0,0,0,0,0]],
            [2, [3,4,5,0,0,0,9,0,0]]
        ]

        for arg in inputs:
            gd.set_column(*arg)
        
        for arg in inputs:
            assert gd.columns[arg[0]] == arg[1]
    
    def test_set_box(self, zero_grid):
        gd = GridData(zero_grid)

        inputs = [
            [0, 0, [1,2,3,4,5,6,7,8,9]],
            [3, 3, [2,0,0,0,0,0,0,0,0]],
            [6, 0, [3,4,5,0,0,0,9,0,0]]
        ]

        for arg in inputs:
            gd.set_box(*arg)
        
        for arg in inputs:
            assert gd.boxes[arg[0], arg[1]] == arg[2]