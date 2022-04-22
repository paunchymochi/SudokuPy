import sys
sys.path.append('..')
from sudokupy.board import Board
from sudokupy.deducers.deducer import Deducer
from sudokupy.injector import Injector
from sudokupy.cell import Cell, Cells
from sudokupy.deducers.deducer_base import Transaction
from sudokupy.injector import _Injection
from typing import List
from pathlib import Path

class Solver:
    def __init__(self, board:Board=None):
        self._unsolved_board:Board = None
        self._solved_board:Board = None
        self._deducer:Deducer = None
        self._injector:Injector = None
        self.set_board(board)

    @property
    def solved_board(self) -> Board:
        return self._solved_board
    @property
    def unsolved_board(self) -> Board:
        return self._unsolved_board
    
    @property
    def transactions(self) -> List[Transaction]:
        return self._deducer.transactions
    
    @property
    def injections(self) -> List[_Injection]:
        return self._injector.injections
    
    def __repr__(self):
        return f'<Solver\nOriginal Board:\n{self._unsolved_board.cells.__str__()}\n\nSolved Board:\n{self._solved_board.cells.__str__()}\n>'

    def set_board(self, board:Board):
        if board is None:
            return
        if not isinstance(board, Board):
            raise TypeError('board must be an instance of Board')
        self._unsolved_board = board.copy()
        self._solved_board = board.copy()
        self._deducer = Deducer(self._solved_board.cells)
        self._injector = Injector(self._solved_board.cells)
    
    def solve(self, board:Board=None) -> Board:
        self.set_board(board)
        while not self._is_board_solved():
            self._deduce()
            self._inject()
        return self._solved_board
    
    def to_csv(self, filename:str) -> Path:
        if self._solved_board is None:
            return
        self._solved_board.to_csv(filename)
    
    def _is_board_solved(self) -> bool:
        cells = self._solved_board.cells.get_values(flatten=True)
        if 0 in cells:
            return False
        else:
            return True
    
    def _deduce(self):
        self._deducer.deduce()
        while len(self._deducer.transactions) > 0:
            self._deducer.eliminate()
            self._deducer.deduce()
    
    def _inject(self):
        self._injector.inject()
