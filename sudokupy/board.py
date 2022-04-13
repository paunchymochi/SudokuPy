import sys
sys.path.append('..')
from sudokupy.cell import Cells

from typing import List, Tuple

class Board:
    class _Slice:
        def __init__(self, cells:Cells):
            self._cells = cells

        def _cast_tuple(self, key):
            if type(key) is not tuple:
                key = (key, )
            return key
        
        def _validate_slicer(self, key, max_value:int) -> bool:
            if type(key) is not int or key not in list(range(max_value+1)):
                raise ValueError(f'index must be an int between 0 and {max_value}')
            return True
        
        def _validate_tuple(self, key:tuple, num_elements:int) -> bool:
            if len(key) != num_elements:
                raise ValueError(f'index must have a dimension of {num_elements}')
            return True

    class Row(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)
        
        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 1)
            self._validate_slicer(key[0], 8)
            return self._cells[key[0]]

    class Col(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 1)
            self._validate_slicer(key[0], 8)
            return self._cells[:, key[0]]

    class Box(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 2)
            self._validate_slicer(key[0], 2)
            self._validate_slicer(key[1], 2)
            topleft_row = key[0]*3
            topleft_col = key[1]*3
            return self._cells[topleft_row:topleft_row+3, topleft_col:topleft_col+3]
    
    class Cell(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 2)
            self._validate_slicer(key[0], 8)
            self._validate_slicer(key[1], 8)
            return self._cells[key[0], key[1]]

    def __init__(self):
        self._cells = Cells()
        self.row = self.Row(self.cells)
        self.col = self.Col(self.cells)
        self.box = self.Box(self.cells)
        self.cell = self.Cell(self.cells)
    
    def __repr__(self):
        return f'<Board\n{self.cells.__str__()}\n\n{self.cells.print_candidates()}\n>'
    
    @property
    def cells(self) -> Cells:
        return self._cells
    
    def get_row(self, row:int) -> Cells:
        return self.cells[row]

    def get_col(self, col:int) -> Cells:
        return self.cells[:, col]

    def get_box(self, row:int, col:int) -> Cells:
        row = (row // 3) * 3
        col = (col // 3) * 3
        return self.cells[row:row+3, col:col+3]

    def get_cell(self, row:int, col:int) -> Cells:
        return self.cells[row, col]
    
    def reset_candidates(self):
        self.cells.reset_candidates()
    
    def resolve(self) -> Tuple[int, int]:
        candidates = self.cells.get_candidates()
        resolved_cells = self._resolve_selection(candidates)
        return resolved_cells
    
    def resolve_adjacent(self, row:int, col:int) -> List[Tuple[int, int]]:
        box_cells = self.box[row//3, col//3]
        row_cells = self.row[row]
        col_cells = self.col[col]

        resolved_cells = []

        for cells in [box_cells, row_cells, col_cells]:
            candidates = cells.get_candidates()
            resolved_cells.extend(self._resolve_selection(candidates))
        return resolved_cells

    def _resolve_selection(self, candidates:List[List[List[int]]]) -> List[Tuple[int, int]]:
        resolved_cells = []
        for i, row in enumerate(candidates):
            for j, cell in enumerate(row):
                if len(cell) == 1:
                    self.cell[i, j].set_values(cell[0])
                    self.cell[i, j].set_candidates([])
                    resolved_cells.append((i, j))
        return resolved_cells
    