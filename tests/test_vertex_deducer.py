import pytest
import sys
sys.path.append('..')
from sudokupy.deducers.vertex_deducer import VertexCoupleDeducer, VertexCouple, VertexCouples, VertexDict, VertexPair
from sudokupy.cell import Cell, Cells

class TestVertexPair:
    def test_is_row_pair(self):
        p = VertexPair(1, Cell(1, 0, 0), Cell(1, 2, 0), Cell(1, 5, 0))
        assert p.is_row_pair() == True
        p = VertexPair(1, Cell(0, 5), Cell(0, 5), Cell(8, 5))
        assert p.is_row_pair() == False
    
    def test_eq(self):
        p = VertexPair(1, Cell(0, 0, 0), Cell(5, 0, 0), Cell(8, 0, 0))
        p2 = VertexPair(2, Cell(0, 0, 0), Cell(5, 0, 0), Cell(8, 0, 0))
        p3 = VertexPair(1, Cell(0, 0, 0), Cell(1, 0, 0), Cell(2, 0, 0))
        assert p != p2
        assert p == p3
    
    def test_candidate(self):
        for i in range(1, 10):
            p = VertexPair(i, Cell(0, 0, 0), Cell(4, 0, 0), Cell(5, 0, 0))
            assert p.candidate == i
    
    def test_cells(self):
        c1 = Cell(3, 0, 0)
        c2 = Cell(5, 0, 0)
        p = VertexPair(2, Cell(0, 0, 0), c1, c2)
        assert p.cells == (c1, c2)
    
    def test_topleft_cell(self):
        for i in range(9):
            c = Cell(0, i, 0)
            
            p = VertexPair(1, c, Cell(3, i, 0), Cell(7, i, 0))
            assert p.topleft_cell == c

    def test_row_col(self):
        cases = [
            [[3, 0], [6, 0]],
            [[0, 4], [0, 8]]
        ]
        for case in cases:
            p = VertexPair(1, Cell(0, 0, 0), Cell(case[0][0], case[0][1]), Cell(case[1][0], case[1][1]))
            assert p.rows == [case[0][0], case[1][0]]
            assert p.cols == [case[0][1], case[1][1]]

