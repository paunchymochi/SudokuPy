from .cell import Cell, Cells

class Board:
    class _Slice:
        def __init__(self, cells:Cells):
            self._cells = cells

        def __getitem__(self, key):
            raise NotImplementedError
        
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
        raise NotImplementedError
    
    def deduce_row(self, row:int):
        raise NotImplementedError
    
    def deduce_column(self, col:int):
        raise NotImplementedError
    
    def deduce_box(self, boxrow:int, boxcol:int):
        raise NotImplementedError
    
    def deduce_cell(self, row:int, col:int):
        raise NotImplementedError
    
    def resolve_cell(self, row:int, col:int):
        raise NotImplementedError


    