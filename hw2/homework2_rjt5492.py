############################################################
# CMPSC 442: Informed Search
############################################################

student_name = "Ryan Joseph Talalai"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import random
import copy
import math
import queue



############################################################
# Section 1: Tile Puzzle
############################################################

def create_tile_puzzle(rows, cols):
    puzzle = [[c + (r * cols) + 1 for c in range(cols)] for r in range(rows)]
    puzzle[-1][-1] = 0
    return TilePuzzle(puzzle)

class TilePuzzle(object):
    
    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        self.empty=[]
        flag = False
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 0:
                    self.empty.append(i)
                    self.empty.append(j)
                    flag = True
                    break
            if flag:
                break

    def get_board(self):
        return self.board

    def perform_move(self, direction):
        new_row, new_col = self.empty
        if direction == "up":
            new_row-=1
        elif direction == "down":
            new_row+=1
        elif direction == "left":
            new_col-=1
        elif direction == "right":
            new_col+=1

        if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
            self.board[self.empty[0]][self.empty[1]], self.board[new_row][new_col] = \
            self.board[new_row][new_col], self.board[self.empty[0]][self.empty[1]]
            self.empty = [new_row, new_col]
            return True
        
        return False


    def scramble(self, num_moves):
        directions = ["up", "down", "left", "right"]
        for _ in range(num_moves):
            self.perform_move(random.choice(directions))

    def is_solved(self):
        if self.board == create_tile_puzzle(len(self.board[0]),len(self.board)).get_board():
            return True
        return False


    def copy(self):
        return TilePuzzle(copy.deepcopy(self.board))

    def successors(self):
        for i in ["up", "down", "left", "right"]:
            new_board = TilePuzzle(self.copy().get_board())
            new_board.perform_move(i)
            yield (i, new_board)


    # Required

    def find_solutions_iddfs(self):
        limit = 0
        while True:
            solution_found = False
            for moves in self.iddfs_helper(limit, []):
                solution_found = True
                yield moves
                break
            if solution_found:
                break
            limit+=1

    def iddfs_helper(self, limit, path):
        if self.is_solved():
            yield path
            return
        if limit <= 0:
            return
        for move, new_puzzle in self.successors():
            yield from new_puzzle.iddfs_helper(limit - 1, path + [move])

    # Required
    def man_dist(self, solved_board):
        tile_positions = {tile: (i, j) for i, row in enumerate(self.board) for j, tile in enumerate(row)}
        return sum(abs(i - tile_positions[val][0]) + abs(j - tile_positions[val][1])
                   for i, row in enumerate(solved_board) for j, val in enumerate(row) if val != 0)

    def tuple_up(self):
        return tuple(tuple(row) for row in self.board)

    def find_solution_a_star(self):
        solved_board = create_tile_puzzle(self.rows, self.cols).get_board()
        frontier = queue.PriorityQueue()
        came_from, cost_so_far = {self.tuple_up(): None}, {self.tuple_up(): 0}
        frontier.put((0, 0, self))
        move_counter = 0

        while not frontier.empty():
            i, j, current_puzzle = frontier.get()
            current_tuple = current_puzzle.tuple_up()

            if current_puzzle.is_solved():
                return self.recon(came_from, current_tuple)

            for move, next_puzzle in current_puzzle.successors():
                next_tuple = next_puzzle.tuple_up()
                new_cost = cost_so_far[current_tuple] + 1
                if next_tuple not in cost_so_far or new_cost < cost_so_far[next_tuple]:
                    cost_so_far[next_tuple] = new_cost
                    priority = new_cost + next_puzzle.man_dist(solved_board)
                    move_counter+=1
                    frontier.put((priority, move_counter, next_puzzle))
                    came_from[next_tuple] = (current_tuple, move)

    def recon(self, came_from, end_tuple):
        path = []
        while end_tuple in came_from and came_from[end_tuple] is not None:
            end_tuple, move = came_from[end_tuple]
            path.append(move)
        path.reverse()

        return path

############################################################
# Section 2: Grid Navigation
############################################################

def successors_grid(position, scene):
    directions = [
        ("up", (-1, 0)),
        ("down", (1, 0)),
        ("left", (0, -1)),
        ("right", (0, 1)),
        ("down-right", (1, 1)),
        ("up-right", (-1, 1)),
        ("down-left", (1, -1)),
        ("up-left", (-1, -1))
    ]
    r, c = len(scene), len(scene[0])
    for direction, (dr, dc) in directions:
        nr, nc = position[0] + dr, position[1] + dc
        if 0 <= nr < r and 0 <= nc < c and not scene[nr][nc]:
            yield (direction, (nr, nc))

def heuristic_grid(current, goal):
    return math.sqrt((current[0] - goal[0])**2 + (current[1] - goal[1])**2)

def find_path(start, goal, scene):
    if scene[start[0]][start[1]] or scene[goal[0]][goal[1]]:
        return None

    pq = queue.PriorityQueue()
    pq.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not pq.empty():
        current_cost, current = pq.get()
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for _, next in successors_grid(current, scene):
            new_cost = cost_so_far[current] + heuristic_grid(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic_grid(next, goal)
                pq.put((priority, next))
                came_from[next] = current

    return None

############################################################
# Section 3: Linear Disk Movement, Revisited
############################################################

def generate_successors_disk(board, length):
    l = [-1]*length
    for position in board:
        l[position] = position
    for i, disk_position in enumerate(board):
        for move in [1, 2, -1, -2]:
            if 0 <= disk_position + move < length:
                if l[disk_position + move] == -1:
                    if move in [2, -2] and l[disk_position + int(move/2)] == -1:
                        continue
                    new_board = list(board)
                    new_board[i] += move
                    yield ((disk_position, disk_position + move), tuple(new_board))

def goal_state(board, length):
    return all(disk_position == (length-i-1) for i, disk_position in enumerate(board))

def heuristic_disks(board, length):
    return sum((abs(position - (length-i-1)) + 1) // 2 for i, position in enumerate(board))

def solve_distinct_disks(length, n):
    initial_board = tuple(range(n))
    frontier = queue.PriorityQueue()
    came_from = {initial_board: None}
    cost_so_far = {initial_board: 0}
    frontier.put((0, 0, initial_board))
    move_count = 0

    while not frontier.empty():
        _, _, current_board = frontier.get()
        if goal_state(current_board, length):
            return recon_disks(came_from, initial_board, current_board)
        for move, next_board in generate_successors_disk(current_board, length):
            new_cost = cost_so_far[current_board] + 1
            if next_board not in cost_so_far or new_cost < cost_so_far[next_board]:
                cost_so_far[next_board] = new_cost
                priority = new_cost + heuristic_disks(next_board, length)
                move_count += 1
                frontier.put((priority, move_count, next_board))
                came_from[next_board] = (current_board, move)

def recon_disks(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        current, move = came_from[current]
        path.append(move)
    path.reverse()
    return path

############################################################
# Section 4: Dominoes Game
############################################################

def create_dominoes_game(rows, cols):
    return DominoesGame([[False] * cols for _ in range(rows)])


class DominoesGame(object):

    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])

    def get_board(self):
        return self.board

    def reset(self):
        self.board = [[False] * self.cols for _ in range(self.rows)]

    def is_legal_move(self, row, col, vertical):
        if vertical:
            return row+1 < self.rows and not (self.board[row][col] or self.board[row + 1][col])
        else:
            return col+1 < self.cols and not (self.board[row][col] or self.board[row][col + 1])

    def legal_moves(self, vertical):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.is_legal_move(i,j,vertical):
                    yield (i,j)

    def perform_move(self, row, col, vertical):
        if not self.is_legal_move(row, col, vertical):
            return False
        self.board[row][col] = True
        if vertical:
            self.board[row + 1][col] = True
        else:
            self.board[row][col + 1] = True
        return True

    def game_over(self, vertical):
        if len(list(self.legal_moves(vertical))) == 0:
            return True
        return False

    def copy(self):
        return DominoesGame(copy.deepcopy(self.board))

    def successors(self, vertical):
        return (((i, j), self.successor_dom(i, j, vertical)) for i in range(self.rows) for j in range(self.cols) if self.is_legal_move(i, j, vertical))

    def successor_dom(self, row, col, vertical):
        successor = self.copy()
        successor.perform_move(row, col, vertical)
        return successor

    def get_random_move(self, vertical):
        moves = [move for move, _ in self.successors(vertical)]
        return random.choice(moves) if moves else None

    # Required
    def evaluate_state(self, vertical):
        return len(list(self.successors(vertical))) - len(list(self.successors(not vertical)))
    
    def min_max(self, depth, alpha, beta, vertical, is_maximizing_player, move=None):
        if depth == 0 or self.game_over(vertical):
            return move, self.evaluate_state(vertical) * (-1 if not is_maximizing_player else 1), 1

        if is_maximizing_player:
            max_eval, best_move, total = float('-inf'), move, 0
            for move, next_state in self.successors(vertical):
                _, eval, count = next_state.min_max(depth - 1, alpha, beta, not vertical, False, move)
                max_eval, best_move = (eval, move) if eval > max_eval else (max_eval, best_move)
                total += count
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return best_move, max_eval, total
        else:
            min_eval, best_move, total = float('inf'), move, 0
            for move, next_state in self.successors(vertical):
                _, eval, count = next_state.min_max(depth - 1, alpha, beta, not vertical, True, move)
                min_eval, best_move = (eval, move) if eval < min_eval else (min_eval, best_move)
                total += count
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return best_move, min_eval, total

    def get_best_move(self, vertical, limit):
        return self.min_max(limit, float('-inf'), float('inf'), vertical, True)
    

    #### 2093 ;) ####
