import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.injector import Injector
import pytest

class TestInjector:
    def test_inject_one_value(self):
        board = Board()
        j = Injector(board.cells)
        j.inject()
        assert board.cell[0, 0].flatten()[0].value in list(range(1, 10))
        assert len(j.injections) == 1
    
    def test_inject_no_solution(self):
        board = Board()
        j = Injector(board.cells)

        board.cell[0, 0].candidates = []

        with pytest.raises(ValueError):
            j.inject()
    
    def test_inject_no_solution_2(self):
        b = Board()
        j = Injector(b.cells)
        b.cell[0, 3].candidates = []

        for i in range(9):
            j.inject()
        
        with pytest.raises(ValueError):
            j.inject()

