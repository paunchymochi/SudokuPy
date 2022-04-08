import sys
sys.path.append('..')
from pathlib import Path
from sudokupy.board import Board
from sudokupy.cell import Cell

class File:
    def __init__(self, folder:str=None):
        self.set_folder(folder)
    
    def read_csv(self, filename:str):
        pass

    def set_folder(self, folder:str):
        self._folder = folder

    def get_folder(self) -> Path:
        folder = self._folder
        if folder is None:
            folder = 'boards'
        return Path(folder)

    def get_path(self, filename:str) -> Path:
        folder = self.get_folder()
        return folder/filename
