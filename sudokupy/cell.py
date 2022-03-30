
class Cell:
    def __init__(self, row: int, column: int, value: int):
        self._row = row
        self._column = column
        self._value = value
    
    @property
    def row(self) -> int:
        return self._row
    
    @property
    def column(self) -> int:
        return self._column
    
    @property
    def value(self) -> int:
        return self._value