from typing import List

class GridData:
    def __init__(self, grid_data: List[List[str]]):
        self._validate(grid_data)
        self._data = grid_data
        self._rows = self._get_rows(grid_data)
        self._columns = self._get_columns(grid_data)
        self._boxes = self._get_boxes(grid_data)
    
    @property
    def data(self):
        return self._data
    
    @property
    def rows(self):
        return self._rows
    
    @property
    def columns(self):
        return self._columns
    
    @property
    def boxes(self):
        return self._boxes
    
    def _get_rows(self, grid_data: List[List[str]]):
        raise NotImplementedError

    def _get_columns(self, grid_data: List[List[str]]):
        raise NotImplementedError

    def _get_boxes(self, grid_data: List[List[str]]):
        raise NotImplementedError
    
    def _flatten_boxes(self, boxes: List[List[str]]):
        raise NotImplementedError
    
    def _validate(self, grid_data: List[List[str]]):
        self._validate_structure(grid_data)
        self._validate_numbers(grid_data)
        self._validate_duplicates(grid_data)
    
    def _validate_structure(self, grid_data: List[List[str]]):
        if len(grid_data) != 9:
            raise ValueError('grid_data must have 9 rows')
        
        for row in grid_data:
            if len(row) != 9:
                raise ValueError('each grid_data row must have 9 elements (columns)')
    
    def _validate_numbers(self, grid_data: List[List[str]]):
        raise NotImplementedError
    
    def _validate_duplicates(self, grid_data: List[List[str]]):
        raise NotImplementedError

        

class Grid:
    def __init__(self):
        raise NotImplementedError