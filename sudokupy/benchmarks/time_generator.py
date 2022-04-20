import sys
sys.path.append('..')
import time
from sudokupy.generator import BoardGenerator

def time_board_generator(from_seed:int=0, to_seed:int=100):
    results = []
    g = BoardGenerator()
    for i in range(from_seed, to_seed):
        time1 = time.time()
        result = g.generate(i)
        time2 = time.time()
        d = {
            'seed': i,
            'time': round(time2-time1, 2), 
            'is_complete': g._is_board_complete(),
            'injections': len(g._injector.get_history())
        }
        results.append(d)
        print(d)
    return results
