from typing import Union, List

class Candidate:
    __slots__ = ['_values']

    def __init__(self):
        self._values = self._get_default_values()
    
    def __repr__(self):
        return f'<Candidate\n{self.print_grid()}\n>'
    
    def __str__(self):
        return self.print_grid()
    
    @property
    def values(self) -> List[int]:
        return self._values
    
    def _get_default_values(self) -> List[int]:
        return list(range(1, 10))
    
    def remove(self, values: Union[int, List[int]]):
        if type(values) is int:
            values = [values]
        self._validate_values(values)
        self._values = [v for v in self._values if v not in values]
    
    def set(self, values: Union[int, List[int]]):
        if type(values) is int:
            values = [values]
        self._validate_values(values)
        self._values = values
    
    def _get_removed(self) -> List[int]:
        return [num for num in range(1, 10) if num not in self._values]
    
    def count(self):
        return len(self._values)

    def _validate_values(self, values: List[int]):
        for value in values:
            if value not in range(1, 10):
                raise ValueError('cell value must be an integer between 1 and 9')
    
    def print_grid(self):
        numbers = [[1,2,3],[4,5,6],[7,8,9]]
        grid = '\n'.join([''.join([str(num) for num in row]) for row in numbers])
        removed_vals = self._get_removed()
        for removed_val in removed_vals:
            grid = grid.replace(str(removed_val), '.')
        return grid
    
    def print_list(self):
        numbers = '123456789'
        removed_vals = self._get_removed()
        for removed_val in removed_vals:
            numbers = numbers.replace(str(removed_val), '.')
        num_list = []
        num_list.append(numbers[0:3])
        num_list.append(numbers[3:6])
        num_list.append(numbers[6:9])
        return num_list

class Cell:
    __slots__ = ['_row', '_column', '_value', '_candidates']

    def __init__(self, row: int, column: int, value: int):
        self._validate_position(row, 'row')
        self._validate_position(column, 'column')
        self._row = row
        self._column = column
        self._candidates = Candidate()

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
    def candidates(self) -> Candidate:
        return self._candidates.values
    
    @candidates.setter
    def candidates(self, values=Union[int, List[int]]):
        self.set_candidates(values)
    
    @property
    def print_value(self) -> str:
        return str(self._value).replace('0', '.')
    
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
    
    def print_candidates(self):
        return self._candidates.print_list()
    
    def set_value(self, value: int):
        self._validate_value(value)
        self._value = value
    
    def reset_candidates(self):
        self._candidates = Candidate()
    
    def set_candidates(self, values=Union[int, List[int]]):
        self._candidates.set(values)
    
    def remove_candidates(self, values=Union[int, List[int]]):
        self._candidates.remove(values)
    
    def _validate_position(self, pos: int, pos_name: str):
        if pos not in range(0, 9):
            raise ValueError(f'{pos_name} must be an integer between 0 and 8')
    
    def _validate_value(self, value: int):
        if value not in range(0, 10):
            raise ValueError('cell value must be an integer between 0 and 9')

class Cells:
    def __init__(self, _cells:List[List['Cell']]=None):
        self._data : List[List['Cell']] = [[]]
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
        def _print_row_grid(row: List[Cell], print_box:bool):
            rows_str = [item.print_value for item in row]
            if print_box:
                for i in [6, 3]:
                    rows_str.insert(i, '|')
                rows_str += '|'
            return ' '.join(rows_str)
        
        def _print_row_index(row: List[Cell]):
            return f'{row[0].row + 1} |'
        
        def _print_rows(data: List[List[Cell]], print_box:bool):
            rows = [_print_row_index(row)+_print_row_grid(row, print_box) for row in data]
            if print_box:
                for i in [6, 3]:
                    rows.insert(i, _print_line_break(9, True))
                rows.append(_print_line_break(9, True))

            return '\n'.join(rows)
        
        def _print_line_break(col_num: int, print_box:bool):
            sep = '   '
            if print_box:
                sep = '__|'
                sep += '| '.join(['_'*6 for _ in range(3)])
                sep += '|'
            else:
                sep += '_'*(col_num*2-1)
            return sep
        
        def _print_header(row: List[Cell], print_box:bool):
            nums = [cell.column + 1 for cell in row]
            nums = [str(num) for num in nums]
            nums = '   ' + ' '.join(nums)
            if print_box:
                nums = nums.replace(' 1', '|1')
                nums = nums.replace('4', '| 4')
                nums = nums.replace('7', '| 7')
                nums += ' |'
            sep = _print_line_break(len(row), print_box)
            return f'{nums}\n{sep}\n'
        
        if self._col_count == 9 and self._row_count == 9:
            print_box = True
        else:
            print_box = False
        grid = _print_header(self._data[0], print_box) + _print_rows(self._data, print_box)
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
    def topleft_row(self):
        return self._data[0][0].row
    
    @property
    def topleft_column(self):
        return self._data[0][0].column

    @property
    def values(self) -> List[List[int]]:
        return self._get_values()
    
    @values.setter
    def values(self, values: Union[int, List[int], List[List[int]]]):
        self.set_values(values)

    def print_candidates(self):
        def get_candidates():
            candidates = [[cell.print_candidates() for cell in row] for row in self.data]
            return candidates
        
        def get_row_index():
            return [row[0].row for row in self.data]
        
        def get_col_index():
            return [cell.column for cell in self.data[0]]
        
        def print_header():
            cols = get_col_index()
            s = '   '
            s += ' '.join(f' {col} ' for col in cols) 
            s += ' '
            return s

        def print_line_break(top_newline=False, bottom_newline=False):
            cols = len(get_col_index())
            s = ''
            if top_newline:
                s += '\n'
            s += '  ' + '-'*(cols*3 + cols + 1)
            if bottom_newline:
                s += '\n'
            return s
        
        def print_subrow(candidates, row, subrow, row_index):
            s = ''
            candidate_row = candidates[row]
            candidate_subrow = [cell[subrow] for cell in candidate_row]
            if subrow == 1:
                s += f'{row_index} '
            else:
                s += '  '
            s += '|'
            s += '|'.join(candidate_subrow)
            s += '|'
            return s
        
        def print_row(row, row_index):
            s = ''
            candidates = get_candidates()
            subrows = [print_subrow(candidates, row, subrow, row_index) for subrow in range(3)]
            return '\n'.join(subrows)

        s = ''
        s += print_header()
        s += print_line_break(True, True)
        rows = [print_row(row, row_index) for row, row_index in enumerate(get_row_index())]
        s += print_line_break(True, True).join(rows)
        s += print_line_break(top_newline=True)
        return s
    
    @property
    def candidates(self) -> List[List[List[int]]]:
        return self._get_candidates()
    
    def contains(self, values: Union[int, List[int]]) -> bool:
        if type(values) is int:
            values = [values]
        
        for value in values:
            if value not in range(9):
                raise ValueError(f'value must be an int between 0 and 9. Received [{value}]')
        
        cell_values = self._flatten(self.values)
        return all([value in cell_values for value in values])
    
    def reset_candidates(self):
        for row in self._data:
            for cell in row:
                cell.reset_candidates()

    def remove_candidates(self, values:Union[int, List[int]]):
        for row in self._data:
            for cell in row:
                cell.remove_candidates(values)

    def set_candidates(self, values:Union[int, List[int]]):
        for row in self._data:
            for cell in row:
                cell.set_candidates(values)

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
    
    def _get_values(self) -> List[List[int]]:
        values = [[cell.value for cell in row] for row in self._data]
        return values
    
    def _get_candidates(self) -> List[List[List[int]]]:
        candidates = [[cell.candidates for cell in row] for row in self._data]
        return candidates

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

