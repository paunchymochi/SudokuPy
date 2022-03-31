from typing import Union, List

class Cell:
    __slots__ = ['_row', '_column', '_value']

    def __init__(self, row: int, column: int, value: int):
        self._validate_position(row, 'row')
        self._validate_position(column, 'column')
        self._row = row
        self._column = column

        self.set_value(value)
    
    def __repr__(self):
        return f'<Cell row:{self._row} column:{self._column} value:{self._value}>'

    @property
    def row(self) -> int:
        return self._row
    
    @property
    def column(self) -> int:
        return self._column
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value:int):
        self._validate_value(value)
        self._value = value
    
    @property
    def box(self) -> int:
        return self.boxrow * 3 + self.boxcol
    
    @property
    def boxrow(self) -> int:
        return self._row // 3
    
    @property
    def boxcol(self) -> int:
        return self._column // 3
    
    def set_value(self, value: int):
        self._validate_value(value)
        self._value = value
    
    def _validate_position(self, pos: int, pos_name: str):
        if pos not in range(0, 9):
            raise ValueError(f'{pos_name} must be an integer between 0 and 8')
    
    def _validate_value(self, value: int):
        if value not in range(0, 10):
            raise ValueError('cell value must be an integer between 0 and 9')


class Cells:
    def __init__(self, _cells:Union['Cells', List['Cells'], List[List['Cells']]]=None):
        self._row_count = 0
        self._col_count = 0
        if _cells is None:
            self._is_sliced = False
            self._make_default_cells()
        else:
            self._is_sliced = True
            if isinstance(_cells, Cell):
                self._data = [[_cells]]
                self._row_count = 1
                self._col_count = 1
            elif isinstance(_cells[0], Cell):
                self._data = [_cells]
                self._row_count = len(_cells)
                self._col_count = 1
            else:
                self._data = _cells
                self._row_count = len(_cells)
                self._col_count = len(_cells[0])
    
    def __str__(self):
        return '\n'.join([' '.join([str(item.value) for item in row]) for row in self._data])
    
    def __repr__(self):
        return '<Cells>\n' + '\n'.join([' '.join([str(item.value) for item in row]) for row in self._data])
    
    def __len__(self):
        return self._count_data()
    
    def __getitem__(self, key):
        if type(key) is tuple:
            cells = self._data[key[0]]
            if type(cells[0]) is list:
                return Cells([row[key[1]] for row in cells])
            else:
                return Cells(cells[key[1]])
        else:
            return Cells(self._data[key])
    
    @property
    def data(self):
        return self._data
    
    @property
    def is_sliced(self):
        return self._is_sliced

    def _make_default_cells(self):
        row_count = 9
        col_count = 9
        cells = []
        for r in range(row_count):
            row = []
            for c in range(col_count):
                row.append(Cell(r, c, 0))
            cells.append(row)
        self._data = cells
        self._row_count = row_count
        self._col_count = col_count
    
    def set_values(self, values: Union[int, List[int], List[List[int]]]):
        flat_values = self._flatten(values)
        flat_data = self._flatten(self._data)

        if len(flat_values) != len(flat_data):
            raise ValueError(f'values (len={len(flat_values)}) '\
                'must have to same number of elements ' \
                'as elements in Cells (len={self._count_data()})')
        
        for i, value in enumerate(flat_values):
            flat_data[i].set_value(value)
    

    def _flatten(self, matrix) -> List:

        if type(matrix) not in [list, tuple]:
            return [matrix]
        
        if type(matrix[0]) not in [list, tuple]:
            return matrix
        
        flattened = []
        for row in matrix:
            flattened.extend(row)
        return flattened
    
    def _count_data(self):
        return self._row_count * self._col_count

