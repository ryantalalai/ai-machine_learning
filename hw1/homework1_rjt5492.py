############################################################
# CMPSC 442: Uninformed Search
############################################################

student_name = "Ryan Joseph Talalai"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import math
import random
import copy
from collections import deque


############################################################
# Section 1: N-Queens
############################################################

def num_placements_all(n):
    x = math.factorial(n * n)
    y = math.factorial(n * n - n)
    z = math.factorial(n)
    y = y * z

    return x // y

def num_placements_one_per_row(n):
   
    return n ** n

def n_queens_valid(board):
    size = len(board)
    
    for i in range(size):
        for j in range(i + 1, size):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                return False
                
    return True


def n_queens_helper(n, board):
    if len(board) == n:
        yield board
    else:
        for y in [j for j in range(n) if n_queens_valid(board + [j])]:
            for i in n_queens_helper(n, board + [y]):
                yield i


def n_queens_solutions(n):
    for i in n_queens_helper(n, []):
        yield i



############################################################
# Section 2: Lights Out
############################################################

class LightsOutPuzzle(object):

    def __init__(self, board):
        
        self.board = board
        self.m = len(self.board)
        self.n = len(self.board[0])

    def get_board(self):
        return self.board
    

    
    def toggle_cell(self, row, col):
        self.board[row][col] = not self.board[row][col]

    def perform_move(self, row, col):
        num_rows = len(self.board)
        num_cols = len(self.board[0]) if num_rows > 0 else 0

        self.toggle_cell(row, col)

        if row - 1 >= 0:
            self.toggle_cell(row - 1, col)
        if col - 1 >= 0:
            self.toggle_cell(row, col - 1)
        if col + 1 < num_cols:
            self.toggle_cell(row, col + 1)
        if row + 1 < num_rows:
            self.toggle_cell(row + 1, col)
   


    def scramble(self):
        for i in range(self.m):
            for j in range(self.n):
                if random.random() < 0.5:
                    self.perform_move(i, j)

    def is_solved(self):
        for i in range(self.m):
            for j in range(self.n):
                if self.board[i][j]:
                    return False
        return True

    def copy(self):
        return LightsOutPuzzle(copy.deepcopy(self.board))

    def successors(self):
        num_rows = len(self.board)
        num_cols = len(self.board[0]) if num_rows > 0 else 0

        for row in range(num_rows):
            for col in range(num_cols):
                succ = self.copy()
                succ.perform_move(row, col)
                yield (row, col), succ



def find_solution(self):
    pass



def create_puzzle(rows, cols):
    return LightsOutPuzzle([[False] * cols for _ in range(rows)])

############################################################
# Section 3: Linear Disk Movement
############################################################

def solve_identical_disks(length, n):
    initial_state = tuple(range(n))
    queue = deque([(initial_state, [])])
    visited_states = set([initial_state])

    while queue:
        current_state, current_moves = queue.popleft()
        if current_state == tuple(range(length - n, length)):
            return current_moves
        for i in range(n):
            for step in [-2, -1, 1, 2]:
                new_position = current_state[i] + step
                if 0 <= new_position < length and new_position not in current_state:
                    new_state = list(current_state)
                    new_state[i] = new_position
                    new_state = tuple(new_state)
                    if new_state not in visited_states:
                        queue.append((new_state, current_moves + [(current_state[i], new_position)]))
                        visited_states.add(new_state)
    return None

def solve_distinct_disks(length, n):
    initial_state = tuple(range(n))
    queue = deque([(initial_state, [])])
    visited_states = set([initial_state])

    while queue:
        current_state, current_moves = queue.popleft()
        if current_state == tuple(range(length - n, length))[::-1]:
            return current_moves
        for i in range(n):
            for step in [-2, -1, 1, 2]:
                new_position = current_state[i] + step
                if 0 <= new_position < length and new_position not in current_state:
                    new_state = list(current_state)
                    new_state[i] = new_position
                    new_state = tuple(new_state)
                    if new_state not in visited_states:
                        queue.append((new_state, current_moves + [(current_state[i], new_position)]))
                        visited_states.add(new_state)

    return None

