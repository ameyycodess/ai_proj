import pygame
import copy

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

FONT = pygame.font.SysFont('Arial', 40)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

class Piece:
    PADDING = 10
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        pygame.draw.circle(win, GOLD, (self.x, self.y), radius + self.OUTLINE) if self.king else None

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

class Board:
    def __init__(self):
        self.board = []
        self.green_left = self.red_left = 12
        self.green_kings = self.red_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == GREEN:
                self.green_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, RED))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, GREEN))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece.color == RED:
                self.red_left -= 1
            else:
                self.green_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return 'Green'
        elif self.green_left <= 0:
            return 'Red'
        return None

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = GREEN
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.win)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self._get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.selected
        if (row, col) in self.valid_moves:
            self.board.move(piece, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True

    def _get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == GREEN or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board.get_piece(r, left)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board.get_piece(r, right)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == GREEN:
            self.turn = RED
        else:
            self.turn = GREEN

# Evaluation function for Minimax
def evaluate(board):
    return board.green_left - board.red_left + (board.green_kings * 0.5 - board.red_kings * 0.5)

# Get all valid moves for a color
def get_all_moves(board, color):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = game._get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            temp_board.move(temp_piece, move[0], move[1])
            if skip:
                temp_board.remove(skip)
            moves.append(temp_board)
    return moves

# Minimax algorithm with alpha-beta pruning
def minimax(position, depth, max_player, alpha, beta, game):
    if depth == 0 or position.winner() is not None:
        return evaluate(position), position

    if max_player:
        max_eval = float('-inf')
        best_move = None
        for move in get_all_moves(position, GREEN):
            evaluation = minimax(move, depth - 1, False, alpha, beta, game)[0]
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
            if max_eval == evaluation:
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_all_moves(position, RED):
            evaluation = minimax(move, depth - 1, True, alpha, beta, game)[0]
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
            if min_eval == evaluation:
                best_move = move
        return min_eval, best_move

# Main game loop
game = Game(WIN)

def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        if game.turn == RED:
            value, new_board = minimax(game.board, 3, False, float('-inf'), float('inf'), game)
            game.board = new_board
            game.change_turn()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                game.select(row, col)

        game.update()

        winner = game.board.winner()
        if winner:
            print(f'{winner} wins!')
            run = False

    pygame.quit()

main()
