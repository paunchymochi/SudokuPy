import sys
sys.path.append('..')
from pathlib import Path
from sudokupy.board import Board
from sudokupy.cell import Cell

class File:
    def __init__(self):
        pass
    
    def read_csv(self, filename:str):
        pass

    def set_folder(self):
        pass

    def get_folder(self) -> Path:
        return Path('boards')

    def get_path(self, filename:str) -> Path:
        folder = self.get_folder()
        return folder/filename
