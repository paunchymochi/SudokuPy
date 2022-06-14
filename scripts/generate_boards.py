import sys
sys.path.append('..')
from sudokupy.generator import Generator


def main():
    difficulty = input('Choose difficulty\n1: Easy\n2: Medium\n3: Hard\n4: Expert\n5: Evil\nInput: ')
    num_boards = input('How many boards to generate? ')

if __name__ == '__main__':
    main()