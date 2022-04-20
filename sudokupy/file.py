import sys
sys.path.append('..')
from pathlib import Path
from typing import List
from sudokupy.cell import Cell

class File:
    def __init__(self, folder:str=None):
        self.set_folder(folder)
    
    def read_csv(self, filename:str):
        path = self.get_path(filename)
        csv_data = self._get_csv_data(path)
        board = self._make_board(csv_data)
        return board
    
    def _get_csv_data(self, path:Path) -> List[List[int]]:

        lines = []
        with open(path, 'r') as f:
            lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        lines = [line.split(',') for line in lines]
        lines = [[int(s) for s in line] for line in lines]
        return lines
    
    def _make_board(self, csv_data:List[List[int]]):
        from sudokupy.board import Board
        board = Board()
        board.cells.values = csv_data
        return board

    def set_folder(self, folder:str):
        self._folder = folder

    def get_folder(self) -> Path:
        folder = self._folder
        if folder is None:
            folder = 'boards'
        board_folder = Path(__file__).parent.parent.joinpath(folder)
        return board_folder

    def get_path(self, filename:str) -> Path:
        folder = self.get_folder()
        return folder/filename
