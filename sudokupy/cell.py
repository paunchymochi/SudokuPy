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
    def __init__(self, cells:Union['Cells', List['Cells'], List[List['Cells']]]=None, _sliced=False):
        self._sliced = _sliced
        if cells is None:
            self._make_default_cells()
        else:
            if isinstance(cells, Cell):
                self._cells = [[cells]]
            elif isinstance(cells[0], Cell):
                self._cells = [cells]
            else:
                self._cells = cells
    
    def __str__(self):
        return '\n'.join([' '.join([str(item.value) for item in row]) for row in self._cells])
    
    def __repr__(self):
        return '<Cells>\n' + '\n'.join([' '.join([str(item.value) for item in row]) for row in self._cells])

    def __getitem__(self, key):
        if type(key) is tuple:
            cells = self._cells[key[0]]
            if type(cells[0]) is list:
                return Cells([row[key[1]] for row in cells], _sliced=True)
            else:
                return Cells(cells[key[1]], _sliced=True)
        else:
            return Cells(self._cells[key], _sliced=True)

    def _make_default_cells(self):
        cells = []
        for r in range(9):
            row = []
            for c in range(9):
                row.append(Cell(r, c, 0))
            cells.append(row)
        self._cells = cells