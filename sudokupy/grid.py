from typing import List

class GridData:
    def __init__(self, grid_data: List[List[int]]):
        self._validate(grid_data)
        self._data = grid_data
        self._rows = self._get_rows(grid_data)
        self._columns = self._get_columns(grid_data)
        self._boxes = self._get_boxes(grid_data)
    
    @property
    def data(self) -> List[List[int]]:
        return self._data
    
    @property
    def rows(self) -> List[List[int]]:
        return self._rows
    
    @property
    def columns(self) -> List[List[int]]:
        return self._columns
    
    @property
    def boxes(self) -> List[List[List[int]]]:
        return self._boxes
    
    def _get_rows(self, grid_data: List[List[int]]) -> List[List[int]]:
        return grid_data

    def _get_columns(self, grid_data: List[List[int]]) -> List[List[int]]:
        return list(zip(*grid_data))

    def _get_boxes(self, grid_data: List[List[int]]) -> List[List[List[int]]]:
        def _get_box(topleft_row: int, topleft_col: int) -> List[int]:
            box = []
            for i in range(topleft_row, topleft_row + 3):
                for j in range(topleft_col, topleft_col + 3):
                    box.append(grid_data[i][j])
            return box
        
        def _get_boxrow(topleft_row: int) -> List[List[int]]:
            boxrow = []
            for topleft_col in range(0, 9, 3):
                boxrow.append(_get_box(topleft_row, topleft_col))
            return boxrow
        
        boxes = []
        for topleft_row in range(0, 9, 3):
            boxes.append(_get_boxrow(topleft_row))
        
        return boxes
    
    def _flatten_boxes(self, boxes: List[List[List[int]]]) -> List[List[int]]:
        flattened_boxes = []

        for boxrow in boxes:
            for box in boxrow:
                flattened_boxes.append(box)
        
        return flattened_boxes
    
    def _validate(self, grid_data: List[List[int]]):
        self._validate_structure(grid_data)
        self._validate_numbers(grid_data)
        self._validate_conflicts(grid_data)
    
    def _validate_structure(self, grid_data: List[List[int]]):
        if len(grid_data) != 9:
            raise ValueError('grid_data must have 9 rows')
        
        for row in grid_data:
            if len(row) != 9:
                raise ValueError('each grid_data row must have 9 elements (columns)')
    
    def _validate_numbers(self, grid_data: List[List[int]]):
        allowed_numbers = list(range(10))

        result = all([all([item in allowed_numbers for item in row]) for row in grid_data])

        if not result:
            raise ValueError('each item must be an int between 0 and 9')
    
    def _validate_conflicts(self, grid_data: List[List[int]]):
        rows = self._get_rows(grid_data)
        cols = self._get_columns(grid_data)
        boxes = self._flatten_boxes(self._get_boxes(grid_data))

        if any([self._validate_has_duplicate_nonzero_number(row) for row in rows]):
            raise ValueError('duplicated number found in rows')
        
        if any([self._validate_has_duplicate_nonzero_number(col) for col in cols]):
            raise ValueError('duplicated number found in columns')
        
        if any([self._validate_has_duplicate_nonzero_number(box) for box in boxes]):
            raise ValueError('duplicated number found in boxes')

    def _validate_has_duplicate_nonzero_number(self, group: List) -> bool:
        sorted_group = group.copy()
        sorted_group.sort()

        for i in range(1, len(sorted_group)):
            if sorted_group[i] > 0 and sorted_group[i] == sorted_group[i-1]:
                return True
        
        return False

class Grid:
    def __init__(self):
        raise NotImplementedError