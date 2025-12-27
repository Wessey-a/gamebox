import pygame
import sys


class TicTacToe:
    def __init__(self):
        # 初始化pygame[citation:1]
        pygame.init()

        # Game constants
        self.WIDTH, self.HEIGHT = 500, 600
        self.BOARD_SIZE = 3
        self.CELL_SIZE = self.WIDTH // self.BOARD_SIZE

        # Color definitions
        self.BG_COLOR = (28, 40, 56)  # Dark blue background
        self.BOARD_COLOR = (44, 62, 80)  # Board color
        self.LINE_COLOR = (52, 73, 94)  # Line color
        self.X_COLOR = (231, 76, 60)  # X color - Red
        self.O_COLOR = (46, 204, 113)  # O color - Green
        self.TEXT_COLOR = (236, 240, 241)  # Text color
        self.HIGHLIGHT_COLOR = (41, 128, 185)  # Highlight color

        # Create game window[citation:1]
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe | Click to Play | ESC to Exit")

        # Game clock[citation:1]
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Game state
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        # Board: 0=empty, 1=X, 2=O
        self.board = [[0 for _ in range(self.BOARD_SIZE)]
                      for _ in range(self.BOARD_SIZE)]
        self.current_player = 1  # X goes first
        self.game_over = False
        self.winner = 0  # 0=none, 1=X wins, 2=O wins, 3=draw
        self.winning_line = None  # Winning line position

    def handle_events(self):
        """处理游戏事件[citation:1][citation:9]"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Exit game
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_n and not self.game_over:
                    self.reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                x, y = pygame.mouse.get_pos()
                if y < self.WIDTH:  # Only clicks on board area are valid
                    row = y // self.CELL_SIZE
                    col = x // self.CELL_SIZE
                    self.make_move(row, col)

        return True  # Continue game

    def make_move(self, row, col):
        """Make a move at specified position"""
        if self.board[row][col] == 0:  # Ensure position is empty
            self.board[row][col] = self.current_player

            # Check if game is over
            self.check_game_over()

            # Switch player
            if not self.game_over:
                self.current_player = 3 - self.current_player  # 1<->2

    def check_game_over(self):
        """检查游戏是否结束（获胜或平局）"""
        # Check rows
        for row in range(self.BOARD_SIZE):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != 0:
                self.winner = self.board[row][0]
                self.winning_line = ('row', row)
                self.game_over = True
                return

        # Check columns
        for col in range(self.BOARD_SIZE):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != 0:
                self.winner = self.board[0][col]
                self.winning_line = ('col', col)
                self.game_over = True
                return

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            self.winner = self.board[0][0]
            self.winning_line = ('diag', 0)  # Main diagonal
            self.game_over = True
            return

        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            self.winner = self.board[0][2]
            self.winning_line = ('diag', 1)  # Anti-diagonal
            self.game_over = True
            return

        # Check for draw
        if all(self.board[row][col] != 0
               for row in range(self.BOARD_SIZE)
               for col in range(self.BOARD_SIZE)):
            self.winner = 3  # Draw
            self.game_over = True

    def draw_board(self):
        """绘制棋盘"""
        # Draw board background
        board_rect = pygame.Rect(0, 0, self.WIDTH, self.WIDTH)
        pygame.draw.rect(self.screen, self.BOARD_COLOR, board_rect)

        # Draw grid lines
        for i in range(1, self.BOARD_SIZE):
            # Vertical lines
            pygame.draw.line(self.screen, self.LINE_COLOR,
                             (i * self.CELL_SIZE, 0),
                             (i * self.CELL_SIZE, self.WIDTH), 4)
            # Horizontal lines
            pygame.draw.line(self.screen, self.LINE_COLOR,
                             (0, i * self.CELL_SIZE),
                             (self.WIDTH, i * self.CELL_SIZE), 4)

    def draw_pieces(self):
        """绘制棋子"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                center_x = col * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = row * self.CELL_SIZE + self.CELL_SIZE // 2
                radius = self.CELL_SIZE // 3

                if self.board[row][col] == 1:  # Draw X
                    # Draw red X
                    offset = radius
                    pygame.draw.line(self.screen, self.X_COLOR,
                                     (center_x - offset, center_y - offset),
                                     (center_x + offset, center_y + offset), 8)
                    pygame.draw.line(self.screen, self.X_COLOR,
                                     (center_x + offset, center_y - offset),
                                     (center_x - offset, center_y + offset), 8)

                elif self.board[row][col] == 2:  # Draw O
                    # Draw green O
                    pygame.draw.circle(self.screen, self.O_COLOR,
                                       (center_x, center_y), radius, 8)

    def draw_winning_line(self):
        """绘制获胜连线"""
        if not self.winning_line:
            return

        line_type, index = self.winning_line
        line_width = 10

        if line_type == 'row':
            y = index * self.CELL_SIZE + self.CELL_SIZE // 2
            start_pos = (self.CELL_SIZE // 4, y)
            end_pos = (self.WIDTH - self.CELL_SIZE // 4, y)
        elif line_type == 'col':
            x = index * self.CELL_SIZE + self.CELL_SIZE // 2
            start_pos = (x, self.CELL_SIZE // 4)
            end_pos = (x, self.WIDTH - self.CELL_SIZE // 4)
        elif line_type == 'diag' and index == 0:  # Main diagonal
            start_pos = (self.CELL_SIZE // 4, self.CELL_SIZE // 4)
            end_pos = (self.WIDTH - self.CELL_SIZE // 4,
                       self.WIDTH - self.CELL_SIZE // 4)
        else:  # Anti-diagonal
            start_pos = (self.WIDTH - self.CELL_SIZE // 4, self.CELL_SIZE // 4)
            end_pos = (self.CELL_SIZE // 4, self.WIDTH - self.CELL_SIZE // 4)

        # Draw highlighted winning line
        pygame.draw.line(self.screen, self.HIGHLIGHT_COLOR,
                         start_pos, end_pos, line_width)

    def draw_status(self):
        """绘制游戏状态信息"""
        # Status area background
        status_rect = pygame.Rect(0, self.WIDTH, self.WIDTH, self.HEIGHT - self.WIDTH)
        pygame.draw.rect(self.screen, (35, 50, 70), status_rect)

        font_large = pygame.font.SysFont(None, 48)
        font_medium = pygame.font.SysFont(None, 36)
        font_small = pygame.font.SysFont(None, 24)

        # Game status text
        if self.game_over:
            if self.winner == 1:
                status_text = "X Wins! 🎉"
                color = self.X_COLOR
            elif self.winner == 2:
                status_text = "O Wins! 🎉"
                color = self.O_COLOR
            else:
                status_text = "It's a Tie! 🤝"
                color = self.TEXT_COLOR
        else:
            player = "X" if self.current_player == 1 else "O"
            color = self.X_COLOR if self.current_player == 1 else self.O_COLOR
            status_text = f"Player {player}'s Turn"

        # Render status text
        status_surface = font_large.render(status_text, True, color)
        self.screen.blit(status_surface,
                         (self.WIDTH // 2 - status_surface.get_width() // 2,
                          self.WIDTH + 30))

        # Control hints
        if self.game_over:
            restart_text = font_medium.render("Press R to Restart", True, (200, 200, 100))
            self.screen.blit(restart_text,
                             (self.WIDTH // 2 - restart_text.get_width() // 2,
                              self.WIDTH + 100))
        else:
            new_game_text = font_small.render("Press N for New Game", True, (150, 150, 150))
            self.screen.blit(new_game_text,
                             (self.WIDTH // 2 - new_game_text.get_width() // 2,
                              self.WIDTH + 100))

        # Exit hint
        exit_text = font_small.render("ESC to Exit to Game Launcher", True, (150, 150, 150))
        self.screen.blit(exit_text,
                         (self.WIDTH // 2 - exit_text.get_width() // 2,
                          self.WIDTH + 140))

        # Draw current player indicator
        indicator_size = 30
        indicator_y = self.WIDTH + 80

        if not self.game_over:
            # X player indicator
            x_indicator_color = self.X_COLOR if self.current_player == 1 else (100, 100, 100)
            x_indicator_rect = pygame.Rect(self.WIDTH // 2 - 60, indicator_y,
                                           indicator_size, indicator_size)
            pygame.draw.line(self.screen, x_indicator_color,
                             (x_indicator_rect.left + 8, x_indicator_rect.top + 8),
                             (x_indicator_rect.right - 8, x_indicator_rect.bottom - 8), 4)
            pygame.draw.line(self.screen, x_indicator_color,
                             (x_indicator_rect.right - 8, x_indicator_rect.top + 8),
                             (x_indicator_rect.left + 8, x_indicator_rect.bottom - 8), 4)

            # O player indicator
            o_indicator_color = self.O_COLOR if self.current_player == 2 else (100, 100, 100)
            o_indicator_center = (self.WIDTH // 2 + 60, indicator_y + indicator_size // 2)
            pygame.draw.circle(self.screen, o_indicator_color,
                               o_indicator_center, indicator_size // 2 - 4, 4)

    def draw(self):
        """绘制游戏所有元素[citation:9]"""
        # Fill background color
        self.screen.fill(self.BG_COLOR)

        # Draw board
        self.draw_board()

        # Draw pieces
        self.draw_pieces()

        # If game over, draw winning line
        if self.game_over and self.winning_line:
            self.draw_winning_line()

        # Draw status information
        self.draw_status()

        # Update display[citation:1]
        pygame.display.flip()

    def run(self):
        """运行游戏主循环[citation:1][citation:9]"""
        running = True
        while running:
            # 1. 处理事件[citation:9]
            running = self.handle_events()

            # 2. 绘制游戏[citation:9]
            self.draw()

            # 3. 控制游戏帧率[citation:1]
            self.clock.tick(self.FPS)

        # Exit game
        pygame.quit()
        return


if __name__ == "__main__":
    game = TicTacToe()
    game.run()