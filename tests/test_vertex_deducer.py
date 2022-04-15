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
