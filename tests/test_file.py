import pytest
import sys
sys.path.append('..')
from sudokupy.file import File
from sudokupy.cell import Cells

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
    
    def test_to_csv(self, tmpdir):
        file = File(tmpdir)
        cells = Cells()
        filename = 'empty.csv'

        result = file.to_csv(cells, filename)
        assert result == [','.join(['0']*9) for _ in range(9)]
        path = file.get_path(filename)
        assert path.exists()

        cells2 = file.read_csv(filename)
        assert cells == cells2


