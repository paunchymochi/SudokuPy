import pytest
import sys
sys.path.append('..')
from sudokupy.file import File

class TestFile:
    def test_get_folder(self):
        file = File()
        folder = file.get_folder()
        assert folder.exists() == True
    
    def test_get_path(self):
        file = File()
        path = file.get_path('easy01.csv')
        assert path.exists() == True
    
    def test_read_csv(self):
        file = File()
        cells = file.read_csv('easy01.csv')
        assert cells[0].get_values(flatten=True) == [7, 0, 4, 9, 0, 0, 5, 6, 8]

    def test_read_csv_non_existent(self):
        file = File()
        with pytest.raises(FileExistsError):
            board = file.read_csv('zzzzz.csv')
