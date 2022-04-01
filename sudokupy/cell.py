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
    def __init__(self, _cells:List[List['Cells']]=None):
        self._row_count = 0
        self._col_count = 0
        if _cells is None:
            self._is_sliced = False
            self._make_default_cells()
        else:
            self._is_sliced = True
            if type(_cells) is not list or type(_cells[0]) is not list or not isinstance(_cells[0][0], Cell):
                raise ValueError('_cells structure not valid')
            self._data = _cells
            self._row_count = len(_cells)
            self._col_count = len(_cells[0])
    
    def __str__(self):
        return self._print_grid()
    
    def __repr__(self):
        return f'<Cells \n{self._print_grid()}\nrows:{self._row_count} cols:{self._col_count}>'
    
    def _print_grid(self):
        def _print_row_grid(row: List[Cell]):
            return ' '.join([str(item.value) for item in row])
        
        def _print_row_index(row: List[Cell]):
            return f'{row[0].row} |'
        
        def _print_rows(data: List[List[Cell]]):
            return '\n'.join([_print_row_index(row)+_print_row_grid(row) for row in data])
        
        def _print_header(row: List[Cell]):
            nums = [cell.column + 1 for cell in row]
            nums = [str(num) for num in nums]
            nums = ' '.join(nums)
            sep = '   ' + '_'*(len(row)*2-1)
            return f'   {nums}\n{sep}\n'
        
        grid = _print_header(self._data[0]) + _print_rows(self._data)
        return grid
    
    def __len__(self):
        return self._count_data()
    
    def __getitem__(self, key):
        if type(key) is not tuple:
            key = (key,)

        sliced_rows = self._data[key[0]]
        if type(sliced_rows[0]) is not list: # single row selected
            sliced_rows = [sliced_rows]
        
        if len(key) > 1: # column slicer provided
            sliced_rows = [row[key[1]] for row in sliced_rows]
            if type(sliced_rows[0]) is not list: # single column selected
                sliced_rows = [[cell] for cell in sliced_rows]
        
        return Cells(sliced_rows)

    @property
    def data(self) -> List[List[Cell]]:
        return self._data
    
    @property
    def is_sliced(self) -> bool:
        return self._is_sliced
    
    @property
    def values(self) -> List[List[int]]:
        return self._get_values()

    @values.setter
    def values(self, values: Union[int, List[int], List[List[int]]]):
        self.set_values(values)

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
    
    def _get_values(self):
        values = [[cell.value for cell in row] for row in self._data]
        return values

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

