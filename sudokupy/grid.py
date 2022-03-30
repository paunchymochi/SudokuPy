from typing import List, Tuple

class GridData:
    def __init__(self, grid_data: List[List[int]]=None, raises_error=False):
        self._raises_error = raises_error
        self._valid = True

        if grid_data is None:
            grid_data = self._get_zero_grid()
        else:
            self._validate(grid_data, raises_error=raises_error)

        self._data = grid_data
        self._rows = self._get_rows(grid_data)
        self._columns = self._get_columns(grid_data)
        self._boxes = self._get_boxes(grid_data)
    
    @property
    def data(self) -> List[List[int]]:
        return self._data
    
    @property
    def rows(self) -> Tuple[Tuple[int]]:
        return self._rows
    
    @property
    def columns(self) -> Tuple[Tuple[int]]:
        return self._columns
    
    @property
    def boxes(self) -> Tuple[Tuple[Tuple[int]]]:
        return self._boxes
    
    @property
    def valid(self) -> bool:
        return self._valid
    
    def set_item(self, row: int, col: int, value: int):

        new_data = self._data.copy()
        new_data[row][col] = value

        if self._validate(new_data, raises_error=True):
            self._data = new_data
    
    def set_row(self, row: int, values: List[int]):

        if len(values) != 9:
            raise ValueError('values must have 9 elemtns')

        new_data = self._data.copy()
        for i in range(9):
            new_data[row][i] = values[i]
        
        if self._validate(new_data, raises_error=True):
            self._data = new_data
    
    def set_column(self, column: int, values: List[int]):

        if len(values) != 9:
            raise ValueError('values must have 9 elemtns')

        new_data = self._data.copy()
        for i in range(9):
            new_data[i][column] = values[i]
        
        if self._validate(new_data, raises_error=True):
            self._data = new_data
    
    def set_box(self, topleft_row: int, topleft_col: int, values: List[int]):

        if len(values) != 9:
            raise ValueError('values must have 9 elemtns')

        new_data = self._data.copy()
        for row_offset in range(3):
            for col_offset in range(3):
                new_data[topleft_row + row_offset][topleft_col + col_offset] = values[row_offset * 3 + col_offset]
        
        if self._validate(new_data, raises_error=True):
            self._data = new_data
    
    def _get_zero_grid(self) -> List[List[int]]:
        return [[0]*9]*9
    
    def _get_rows(self, grid_data: List[List[int]]) -> Tuple[Tuple[int]]:
        rows = [tuple(row) for row in grid_data]
        return tuple(rows)

    def _get_columns(self, grid_data: List[List[int]]) -> Tuple[Tuple[int]]:
        return tuple(zip(*grid_data))

    def _get_boxes(self, grid_data: List[List[int]]) -> Tuple[Tuple[Tuple[int]]]:
        def _get_box(topleft_row: int, topleft_col: int) -> Tuple[int]:
            box = []
            for i in range(topleft_row, topleft_row + 3):
                for j in range(topleft_col, topleft_col + 3):
                    box.append(grid_data[i][j])
            return tuple(box)
        
        def _get_boxrow(topleft_row: int) -> Tuple[Tuple[int]]:
            boxrow = []
            for topleft_col in range(0, 9, 3):
                boxrow.append(_get_box(topleft_row, topleft_col))
            return tuple(boxrow)
        
        boxes = []
        for topleft_row in range(0, 9, 3):
            boxes.append(_get_boxrow(topleft_row))
        
        return tuple(boxes)
    
    def _flatten_boxes(self, boxes: Tuple[Tuple[Tuple[int]]]) -> Tuple[Tuple[int]]:
        flattened_boxes = []

        for boxrow in boxes:
            for box in boxrow:
                flattened_boxes.append(box)
        
        return tuple(flattened_boxes)
    
    def _validate(self, grid_data: List[List[int]], raises_error: bool) -> bool:
        if not self._validate_structure(grid_data, raises_error=raises_error): return False
        if not self._validate_numbers(grid_data, raises_error=raises_error): return False
        if not self._validate_conflicts(grid_data, raises_error=raises_error): return False

        return True
    
    def _validate_structure(self, grid_data: List[List[int]], raises_error: bool):
        if len(grid_data) != 9:
            if raises_error:
                raise ValueError('grid_data must have 9 rows')
            else:
                self._valid = False
                return False
        
        for row in grid_data:
            if len(row) != 9:
                if raises_error:
                    raise ValueError('each grid_data row must have 9 elements (columns)')
                else:
                    self._valid = False
                    return False
        return True
    
    def _validate_numbers(self, grid_data: List[List[int]], raises_error: bool):
        allowed_numbers = list(range(10))

        result = all([all([item in allowed_numbers for item in row]) for row in grid_data])

        if not result:
            if raises_error:
                raise ValueError('each item must be an int between 0 and 9')
            else:
                self._valid = False
                return False
        return True
    
    def _validate_conflicts(self, grid_data: List[List[int]], raises_error: bool):
        groups = {}
        groups['rows'] = self._get_rows(grid_data)
        groups['columns'] = self._get_columns(grid_data)
        groups['boxes'] = self._flatten_boxes(self._get_boxes(grid_data))

        for key, item in groups.items():
            if self._groups_have_duplicate_nonzero_number(item):
                if raises_error:
                    raise ValueError(f'duplicated number found in {key}')
                else:
                    self._valid = False
                    return False
        return True

    def _groups_have_duplicate_nonzero_number(self, groups: List[List[int]]) -> bool:
        return any([self._group_has_duplicate_nonzero_number(group) for group in groups])

    def _group_has_duplicate_nonzero_number(self, group: List[int]) -> bool:
        sorted_group = list(group).copy()
        sorted_group.sort()

        for i in range(1, len(sorted_group)):
            if sorted_group[i] > 0 and sorted_group[i] == sorted_group[i-1]:
                return True
        
        return False

class Grid:
    def __init__(self):
        raise NotImplementedError