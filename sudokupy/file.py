import sys
sys.path.append('..')
from pathlib import Path
from typing import List
from sudokupy.cell import Cells
import tkinter
from tkinter import filedialog

class _FileDialog:
    def __init__(self):
        self._init_root_tk()

    def _init_root_tk(self):
        root = tkinter.Tk()
        root.withdraw()
        root.lift()
        root.attributes('-topmost', True)
        self._root_tk = root
    
    @classmethod
    def askopenfilename(self):
        result = filedialog.askopenfilename(title='Open CSV File', filetypes=[('CSV File', '*.csv')], initialdir='../boards')
        return result
    
    @classmethod
    def askdirectory(self):
        result = filedialog.askdirectory(title='Choose Folder')
        return result

class File:
    def __init__(self, folder:str=None):
        self.set_folder(folder)
    
    def read_csv(self, filename:str=None):
        if filename is None:
            filename = _FileDialog.askopenfilename()
        path = self.get_path(filename)
        self._validate_path(path)
        csv_data = self._get_csv_data(path)
        board = self._make_cells(csv_data)
        return board
    
    def to_csv(self, cells:Cells, filename:str) -> List[str]:
        path = self.get_path(filename)
        csv_lines = self._make_csv_lines(cells)

        with open(path, 'w') as f:
            for line in csv_lines:
                f.write(line + '\n')
        
        return csv_lines

    def _make_csv_lines(self, cells:Cells) -> List[str]:
        lines = []
        for row in cells.data:
            line = [str(cell.value) for cell in row]
            line_str = ','.join(line)
            lines.append(line_str)
        return lines
    
    def _validate_path(self, path:Path):
        if not path.exists():
            raise FileExistsError(f'path {path} does not exist')
    
    def _get_csv_data(self, path:Path) -> List[List[int]]:

        lines = []
        with open(path, 'r') as f:
            lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        lines = [line.split(',') for line in lines]
        lines = [[int(s) for s in line] for line in lines]
        return lines
    
    def _make_cells(self, csv_data:List[List[int]]):
        cells = Cells()
        cells.values = csv_data
        return cells
    
    def choose_folder(self):
        folder = _FileDialog.askdirectory()
        self.set_folder(folder)

    def set_folder(self, folder:str):
        if folder == '':
            folder = None
        self._folder = folder

    def get_folder(self) -> Path:
        folder = self._folder
        if folder is None:
            folder = 'boards'
        folder = Path(folder)
        if folder.is_absolute():
            return folder
        else:
            board_folder = Path(__file__).parent.parent / folder
        return board_folder

    def get_path(self, filename:str) -> Path:
        folder = self.get_folder()
        return folder/filename
