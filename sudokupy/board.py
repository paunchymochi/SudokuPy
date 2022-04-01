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
            if key is not int or key not in list(range(max_value)):
                raise ValueError(f'index must be an int between 0 and {max_value}')
            return True
        
        def _validate_tuple(self, key:tuple, num_elements:int) -> bool:
            if len(key) != num_elements:
                raise ValueError(f'index must have a dimension of {num_elements}')
            return True

    class Row(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)
        
        def __getitem__(self, key):
            key = self._cast_tuple(key)
            self._validate_tuple(key, 1)
            self._validate_slicer(key[0], 8)
            return self.cells[key]

    class Col(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key):
            key = self._cast_tuple(key)
            self._validate_tuple(key, 1)
            self._validate_slicer(key[0], 8)
            return self.cells[:, key]

    class Box(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 2)
            self._validate_slicer(key[0], 2)
            self._validate_slicer(key[1], 2)
            return self.cells[key[0]*3, key[1]*3]
    
    class Cell(_Slice):
        def __init__(self, cells:Cells):
            super().__init__(cells)

        def __getitem__(self, key) -> Cells:
            key = self._cast_tuple(key)
            self._validate_tuple(key, 2)
            self._validate_slicer(key[0], 8)
            self._validate_slicer(key[1], 8)
            return self.cells[key[0], key[1]]

    def __init__(self):
        self.cells = Cells()
        self.row = self.Row(self.cells)
        self.col = self.Col(self.cells)
        self.box = self.Box(self.cells)
        self.cell = self.Cell(self.cells)
    