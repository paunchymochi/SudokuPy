import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.injector import Injector, _Injection
import pytest

class TestInjection:
    def test_repr(self):
        b = Board()
        injection = _Injection(b.cells.data[0][0], b.cells.get_candidates(True))
        repr = injection.__repr__()
        sum = 0
        for i in range(0, 10):
            sum += repr.count(str(i))
        assert sum == 1 + 9 + 9 # value, available_candidates, untried_candidates

    def test_has_untried_candidates(self):
        b = Board()
        injection = _Injection(b.cells.data[0][0], b.cells.get_candidates(True))
        assert injection.has_untried_candidates() == True

        for i in range(8):
            injection.guess()
            assert injection.has_untried_candidates() == True
        
        injection.guess()
        assert injection.has_untried_candidates() == False
    
    def test_untried_candidates(self):
        b = Board()
        injection = _Injection(b.cells.data[0][0], b.cells.get_candidates(True))
        assert len(injection.untried_candidates) == 9
        injection.guess()
        assert len(injection.untried_candidates) == 8
    
    def test_available_candidates(self):
        b = Board()
        injection = _Injection(b.cells.data[0][0], b.cells.get_candidates(True))
        assert len(injection.available_candidates) == 9

        b.cell[1, 1].candidates = [3, 5, 7]
        injection = _Injection(b.cells.data[1][1], b.cells.get_candidates(True))
        assert len(injection.available_candidates) == 3
    
    def test_cell(self):
        b = Board()
        cell = b.cells.data[0][0]
        injection = _Injection(cell, b.cells.get_candidates(True))
        assert injection.cell == cell
    
    def test_guess(self):
        b = Board()
        cell = b.cells.data[0][0]
        injection = _Injection(cell, b.cells.get_candidates(True))

        for i in range(9):
            print(i)
            injection.guess()
            cell_value = cell.value
            assert len(injection.untried_candidates) == 8 - i
            assert cell_value not in injection.untried_candidates
        
        with pytest.raises(ValueError):
            injection.guess()



class TestInjector:
    def test_injections(self):
        b = Board()
        j = Injector(b.cells)

        assert j.injections == []

        j.inject()
        assert len(j.injections) == 1
        assert j.injections[0].cell == b.cells.data[0][0]
    
    def test_get_history(self):
        b = Board()
        j = Injector(b.cells)
        history = j.get_history()
        assert history == []

        j.inject()
        history = j.get_history()
        assert len(history) == 1
    
    def test_get_injections(self):
        b = Board()
        j = Injector(b.cells)
        injections = j.get_injections()
        assert injections == []

        for i in range(9):
            j.inject()
            injections = j.get_injections()
            assert len(injections) == 1 + i


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
    
    def test_inject_no_solution_3(self):
        b = Board()
        j = Injector(b.cells)
        b.cells.candidates = []
        b.cell[0, 0].candidates = [5, 6]

        j.inject()
        assert len(j.injections) == 1

        j.inject()
        assert len(j.injections) == 1

        with pytest.raises(ValueError):\
            j.inject()

