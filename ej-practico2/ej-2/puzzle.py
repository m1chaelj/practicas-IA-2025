import copy
import random

class Puzzle:
    def __init__(self, board):
        self.board = board
        self.size = 4
        self.empty = self.find_empty()

    def find_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

def generar_tablero_aleatorio():
    numeros = list(range(16))
    random.shuffle(numeros)
    tablero = [numeros[i*4:(i+1)*4] for i in range(4)]
    return tablero



if __name__ == "__main__":
    tablero = generar_tablero_aleatorio()
    puzzle = Puzzle(tablero)
    print("Tablero aleatorio:")
    for fila in puzzle.board:
        print(fila)