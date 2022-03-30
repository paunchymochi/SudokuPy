import pytest

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

def test_rows(input_grid):
    raise NotImplementedError

def test_columns(input_grid):
    raise NotImplementedError

def test_boxes(input_grid):
    raise NotImplementedError