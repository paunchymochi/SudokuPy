import pytest
import sys
sys.path.append('..')
from sudokupy.deducers.vertex_deducer import VertexCoupleDeducer, VertexCouple, VertexCouples, VertexDict, VertexPair
from sudokupy.cell import Cell, Cells

class TestVertexPair:
    def test_is_row_pair(self):
        p = VertexPair(1, Cell(1, 2, 0), Cell(1, 5, 0))
        assert p.is_row_pair() == True
        p = VertexPair(1, Cell(0, 5), Cell(8, 5))
        assert p.is_row_pair() == False
    
    def test_eq(self):
        p = VertexPair(1, Cell(5, 0, 0), Cell(8, 0, 0))
        p2 = VertexPair(2, Cell(5, 0, 0), Cell(8, 0, 0))
        p3 = VertexPair(1, Cell(1, 0, 0), Cell(2, 0, 0))
        assert p != p2
        assert p == p3
    
    def test_candidate(self):
        for i in range(1, 10):
            p = VertexPair(i, Cell(4, 0, 0), Cell(5, 0, 0))
            assert p.candidate == i
    
    def test_cells(self):
        c1 = Cell(3, 0, 0)
        c2 = Cell(5, 0, 0)
        p = VertexPair(2, c1, c2)
        assert p.cells == (c1, c2)
    
    # def test_topleft_cell(self):
    #     for i in range(9):
    #         p = VertexPair(1, Cell(3, i, 0), Cell(7, i, 0))
    #         assert p.topleft_cell == c

    def test_row_col(self):
        cases = [
            [[3, 0], [6, 0]],
            [[0, 4], [0, 8]]
        ]
        for case in cases:
            p = VertexPair(1, Cell(case[0][0], case[0][1]), Cell(case[1][0], case[1][1]))
            assert p.rows == [case[0][0], case[1][0]]
            assert p.cols == [case[0][1], case[1][1]]
    
    def test_vertex_rowcol(self):
        p = VertexPair(1, Cell(0, 5, 0), Cell(0, 8, 0))
        assert p.vertex_row == 0
        assert p.vertex_cols == [5, 8]

        p = VertexPair(1, Cell(1, 0, 0), Cell(4, 0, 0))
        assert p.vertex_row == 0
        assert p.vertex_cols == [1, 4]
    
    def test_is_row_pair(self):
        p = VertexPair(1, Cell(0, 5, 0), Cell(0, 8, 0))
        assert p.is_row_pair == True
        p = VertexPair(1, Cell(1, 0, 0), Cell(4, 0, 0))
        assert p.is_row_pair == False

    def test_invalid_inputs(self):
        with pytest.raises(ValueError):
            p = VertexPair(1, Cell(1, 1, 0), Cell(0, 5, 0))
        
class TestVertexCouple:
    def test_valid_couple(self):
        p1 = VertexPair(1, Cell(0, 4, 0), Cell(0, 7, 0))
        p2 = VertexPair(1, Cell(5, 4, 0), Cell(5, 7, 0))
        c1 = VertexCouple([p1])
        assert c1.pairs == [p1]
        assert c1.discard == False
        assert c1.valid == False

        c2 = VertexCouple([p2], c1)
        assert c2.pairs == [p1, p2]
        assert c2.discard == False
        assert c2.valid == True

        c3 = VertexCouple([p1, p2])
        assert c3.pairs == [p1, p2]
        assert c2.discard == False
        assert c2.valid == True
    
    def test_invalid_parameter(self):
        p = VertexPair(1, Cell(0, 4, 0), Cell(0, 7, 0))
        with pytest.raises(TypeError):
            c = VertexCouple(p)
        
        with pytest.raises(TypeError):
            c = VertexCouple([0])

    def test_eq(self):
        p1 = VertexPair(1, Cell(0, 4), Cell(0, 7))
        p2 = VertexPair(1, Cell(3, 4), Cell(3, 7))
        p3 = VertexPair(2, Cell(0, 4), Cell(0, 7))
        p4 = VertexPair(2, Cell(3, 4), Cell(3, 7))
        c1 = VertexCouple([p1, p2])
        c2 = VertexCouple([p3, p4])
        c3 = VertexCouple([p2, p1])

        assert c1 != c2
        assert c1 == c1
        assert c1 == c3

class TestVertexDict:
    def test_len(self):
        d = VertexDict()
        assert len(d) == 0

        for i in range(1, 10):
            p1 = VertexPair(i, Cell(0, 4), Cell(0, 7))
            p2 = VertexPair(i, Cell(3, 4), Cell(3, 7))
            c = VertexCouple([p1, p2])

            d.add_couple(c)
            assert len(d) == i

        for i in range(1, 10):
            p3 = VertexPair(i, Cell(1, 5), Cell(7, 5))
            p4 = VertexPair(i, Cell(1, 8), Cell(7, 8))
            c = VertexCouple([p3, p4])
            d.add_couple(c)
            assert len(d) == 10 + i