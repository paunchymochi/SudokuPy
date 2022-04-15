import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent.absolute())
from sudokupy.cell import Cell, Cells
from typing import Dict, Tuple, List, Union

class Transaction:
    __slots__ = ['_cell', '_candidates']
    def __init__(self, cell:Cell):
        self._cell = cell
        self._candidates = []
    
    def __repr__(self):
        return f'<Transaction cell:{self._cell.__repr__()} candidates:{self._candidates}>'
    
    @property
    def cell(self):
        return self._cell
    
    @property
    def candidates(self):
        return self._candidates
    
    def add(self, candidates: List[int]):
        if len(self._candidates) == 0:
            self._candidates = candidates.copy()
        else:
            self._candidates.extend(candidates)
            self._remove_duplicate_candidates()
        self._candidates.sort()
    
    def _remove_duplicate_candidates(self):
        candidates = list(set(self._candidates))
        self._candidates = candidates

    def __eq__(self, other):
        return self._cell == other._cell

class Transactions:
    __slots__ = '_transactions_dict'
    def __init__(self):
        self._transactions_dict:Dict[Tuple[int], List[Transaction]] = {}
        self.clear_transactions()
    
    def __str__(self):
        return f'# of transactions:{len(self._transactions_dict)}\n' + '\n'.join(transaction.__repr__() for transaction in self.transactions)

    def __repr__(self):
        return f'<Transactions\n{self.__str__()}\n>'
    
    def __len__(self):
        return len(self._transactions_dict)
    
    @property
    def transactions(self) -> List[Transaction]:
        return self.get_transactions()

    def add_transaction(self, cell:Cell, remove_candidates:Union[int, List[int]]):
        position = self._get_position(cell)
        if not self._cell_in_transactions(position):
            self._make_new_transactions_entry(cell)
        self._append_transaction(position, remove_candidates)
    
    def extend_transactions(self, other:'Transactions'):
        other_transactions = other.transactions
        for transaction in other_transactions:
            self.add_transaction(transaction.cell, transaction.candidates)

    def clear_transactions(self):
        self._transactions_dict = {}

    def get_transactions(self) -> List[Transaction]:
        return list(self._transactions_dict.values())

    def _append_transaction(self, position:Tuple[int], remove_candidates:Union[int, List[int]]):
        remove_candidates = self._validate_candidates(remove_candidates)
        self._transactions_dict[position].add(remove_candidates)
    
    def _validate_candidates(self, candidates:Union[int, List[int]]) -> List[int]:
        if type(candidates) is int:
            candidates = [candidates]
        return candidates
    
    def _make_new_transactions_entry(self, cell:Cell):
        position = self._get_position(cell)
        self._transactions_dict[position] = Transaction(cell)

    def _cell_in_transactions(self, position:Tuple[int]) -> bool:
        return position in self._transactions_dict.keys()
    
    def _get_position(self, cell:Cell) -> Tuple[int]:
        return (cell.row, cell.column)
    
class _BaseDeducer:
    def __init__(self):
        self._affected_cells:List[Cell] = []
        self._transactions = Transactions()
    
    @property
    def transactions(self):
        return self._transactions.get_transactions()
    
    @property
    def affected_cells(self):
        return self._affected_cells
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self._transactions.__str__()} \n>'
    
    def _validate_sliced_cells(self, sliced_cells:Cells):
        if not isinstance(sliced_cells, Cells):
            print(f'type: {type(sliced_cells)}')
            raise TypeError('cells must be instance of Cells')
        if len(sliced_cells) != 9:
            raise ValueError('cells must have 9 elements')

    def eliminate(self):
        self._clear_affected_cells()
        for transaction in self.transactions:
            transaction.cell.remove_candidates(transaction.candidates)
            self._add_affected_cell(transaction.cell)
        self.clear_transactions()

    def _add_transaction(self, cell:Cell, remove_candidates:List[int]=None):
        self._transactions.add_transaction(cell, remove_candidates)

    def clear_transactions(self):
        self._transactions.clear_transactions()

    def _add_affected_cell(self, cell:Cell):
        if cell not in self._affected_cells:
            self._affected_cells.append(cell)

    def _clear_affected_cells(self):
        self._affected_cells = []
    