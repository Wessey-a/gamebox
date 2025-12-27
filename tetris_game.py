import pygame
import random
import sys


class Button:
    """Button class for creating clickable buttons"""

    def __init__(self, x, y, width, height, text, color=(70, 130, 180), hover_color=(100, 160, 210),
                 text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 32)
        self.hovered = False

    def draw(self, surface):
        """Draw the button on the given surface"""
        # Draw button with hover effect
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)

        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """Check if mouse is hovering over button"""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.CELL_SIZE = 30
        self.GRID_WIDTH = 10
        self.GRID_HEIGHT = 20
        # Increase screen width to accommodate button
        self.SCREEN_WIDTH = self.CELL_SIZE * (self.GRID_WIDTH + 10)
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.GRID_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris - Arrow Keys: Move, Up: Rotate | ESC to Exit")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.FALL_SPEED = 0.5  # Block fall speed (seconds per cell)
        self.fall_timer = 0

        # Color definitions
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (50, 50, 50)
        self.COLORS = [
            (0, 240, 240),  # I - Cyan
            (0, 0, 240),  # J - Blue
            (240, 160, 0),  # L - Orange
            (240, 240, 0),  # O - Yellow
            (0, 240, 0),  # S - Green
            (160, 0, 240),  # T - Purple
            (240, 0, 0)  # Z - Red
        ]

        # Shape definitions (7 basic shapes)
        self.SHAPES = [
            [[1, 1, 1, 1]],  # I
            [[1, 0, 0], [1, 1, 1]],  # J
            [[0, 0, 1], [1, 1, 1]],  # L
            [[1, 1], [1, 1]],  # O
            [[0, 1, 1], [1, 1, 0]],  # S
            [[0, 1, 0], [1, 1, 1]],  # T
            [[1, 1, 0], [0, 1, 1]]  # Z
        ]

        # Initialize restart button (initially hidden)
        self.restart_button = None

        self.reset_game()

    def reset_game(self):
        """Reset game state"""
        self.grid = [[0 for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.new_piece()
        self.font = pygame.font.SysFont(None, 24)
        self.font_large = pygame.font.SysFont(None, 36)

        # Hide restart button when game starts
        self.restart_button = None

    def new_piece(self):
        """Create new piece"""
        self.current_shape_idx = random.randint(0, len(self.SHAPES) - 1)
        self.current_shape = [row[:] for row in self.SHAPES[self.current_shape_idx]]
        self.current_color = self.COLORS[self.current_shape_idx]
        self.current_x = self.GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        # Check if game is over (new piece cannot be placed)
        if self.check_collision(self.current_x, self.current_y, self.current_shape):
            self.game_over = True
            # Create restart button when game over
            self.create_restart_button()

    def create_restart_button(self):
        """Create the restart button"""
        button_width = 6 * self.CELL_SIZE  # Width: 6 cells
        button_height = 2 * self.CELL_SIZE  # Height: 2 cells
        button_x = (self.SCREEN_WIDTH - button_width) // 2  # X coordinate: horizontally centered
        button_y = self.SCREEN_HEIGHT - button_height - 40  # Y coordinate: 40 pixels above bottom

        self.restart_button = Button(
            button_x,
            button_y,
            button_width,
            button_height,
            "RESTART"
        )

    def check_collision(self, x, y, shape):
        """Check if piece collides with grid or other pieces"""
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    # Calculate actual position in grid
                    grid_x = x + col_idx
                    grid_y = y + row_idx

                    # Check boundaries
                    if (grid_x < 0 or grid_x >= self.GRID_WIDTH or
                            grid_y >= self.GRID_HEIGHT):
                        return True

                    # Check if overlaps with existing block
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return True
        return False

    def rotate_shape(self, shape):
        """Rotate piece (clockwise 90 degrees)"""
        # Transpose matrix then reverse each row
        return [[shape[y][x] for y in range(len(shape) - 1, -1, -1)]
                for x in range(len(shape[0]))]

    def merge_piece(self):
        """Merge current piece into grid"""
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_x = self.current_x + col_idx
                    grid_y = self.current_y + row_idx
                    if 0 <= grid_y < self.GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.current_color

    def clear_lines(self):
        """Clear filled lines and calculate score"""
        lines_to_clear = []
        for row_idx in range(self.GRID_HEIGHT):
            if all(self.grid[row_idx]):
                lines_to_clear.append(row_idx)

        if not lines_to_clear:
            return 0

        # Score calculation (Tetris standard scoring)
        line_count = len(lines_to_clear)
        self.lines_cleared += line_count
        self.score += [100, 300, 500, 800][min(line_count - 1, 3)] * self.level

        # Update level (level up every 10 lines cleared)
        self.level = self.lines_cleared // 10 + 1
        self.FALL_SPEED = max(0.05, 0.5 - (self.level - 1) * 0.05)

        # Clear lines and make above lines fall
        for row_idx in lines_to_clear:
            del self.grid[row_idx]
            self.grid.insert(0, [0 for _ in range(self.GRID_WIDTH)])

        return line_count

    def draw_grid(self):
        """Draw game grid and pieces"""
        # Draw background grid
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                rect = pygame.Rect(
                    x * self.CELL_SIZE,
                    y * self.CELL_SIZE,
                    self.CELL_SIZE - 1,
                    self.CELL_SIZE - 1
                )
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)
                else:
                    pygame.draw.rect(self.screen, self.GRAY, rect, 1)

        # Draw current falling piece
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (self.current_x + col_idx) * self.CELL_SIZE,
                        (self.current_y + row_idx) * self.CELL_SIZE,
                        self.CELL_SIZE - 1,
                        self.CELL_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, self.current_color, rect)

        # Draw next piece preview
        preview_x = self.GRID_WIDTH + 2
        preview_y = 3
        next_shape = self.SHAPES[(self.current_shape_idx + 1) % len(self.SHAPES)]
        next_color = self.COLORS[(self.current_shape_idx + 1) % len(self.COLORS)]

        # Draw preview title
        preview_text = self.font.render("Next:", True, self.WHITE)
        self.screen.blit(preview_text,
                         (preview_x * self.CELL_SIZE, (preview_y - 2) * self.CELL_SIZE))

        # Draw preview piece
        for row_idx, row in enumerate(next_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (preview_x + col_idx) * self.CELL_SIZE,
                        (preview_y + row_idx) * self.CELL_SIZE,
                        self.CELL_SIZE - 1,
                        self.CELL_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, next_color, rect)

        # Draw score and level info
        info_x = self.GRID_WIDTH + 2
        info_y = 8

        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, self.WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, self.WHITE)

        self.screen.blit(score_text, (info_x * self.CELL_SIZE, info_y * self.CELL_SIZE))
        self.screen.blit(level_text, (info_x * self.CELL_SIZE, (info_y + 1.5) * self.CELL_SIZE))
        self.screen.blit(lines_text, (info_x * self.CELL_SIZE, (info_y + 3) * self.CELL_SIZE))

        # Draw control hints
        controls_y = info_y + 6
        controls = [
            "Controls:",
            "left/right:Move",
            "up:Rotate",
            "down:Soft Drop",
            "Space : Hard Drop",
            "ESC : Exit"
        ]

        for i, text in enumerate(controls):
            control_text = self.font.render(text, True, self.WHITE)
            self.screen.blit(control_text,
                             (info_x * self.CELL_SIZE, (controls_y + i * 1.2) * self.CELL_SIZE))

    def draw_game_over(self):
        """Draw game over screen with restart button"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(overlay, (0, 0))

        # Draw game over text
        game_over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        hint_text = self.font.render("Click RESTART button to play again", True, (200, 200, 100))

        self.screen.blit(game_over_text,
                         (self.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(score_text,
                         (self.SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(hint_text,
                         (self.SCREEN_WIDTH // 2 - hint_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2))

        # Draw restart button if it exists
        if self.restart_button:
            # Update button hover state
            mouse_pos = pygame.mouse.get_pos()
            self.restart_button.check_hover(mouse_pos)
            self.restart_button.draw(self.screen)

    def draw(self):
        """Draw entire game screen"""
        self.screen.fill(self.BLACK)
        self.draw_grid()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """Run main game loop"""
        running = True
        last_time = pygame.time.get_ticks()
        soft_drop = False

        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        # Keep R key as alternative way to restart
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if not self.check_collision(self.current_x - 1, self.current_y, self.current_shape):
                                self.current_x -= 1
                        elif event.key == pygame.K_RIGHT:
                            if not self.check_collision(self.current_x + 1, self.current_y, self.current_shape):
                                self.current_x += 1
                        elif event.key == pygame.K_UP:
                            # Rotate piece
                            rotated = self.rotate_shape(self.current_shape)
                            if not self.check_collision(self.current_x, self.current_y, rotated):
                                self.current_shape = rotated
                        elif event.key == pygame.K_DOWN:
                            soft_drop = True
                        elif event.key == pygame.K_SPACE:
                            # Hard drop (drop to bottom)
                            while not self.check_collision(self.current_x, self.current_y + 1, self.current_shape):
                                self.current_y += 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        soft_drop = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if restart button was clicked
                    if self.game_over and self.restart_button and self.restart_button.is_clicked(event):
                        self.reset_game()

            if not running:
                break

            # Update game state
            if not self.game_over:
                # Update fall timer
                speed = self.FALL_SPEED / 10 if soft_drop else self.FALL_SPEED
                self.fall_timer += delta_time

                if self.fall_timer >= speed:
                    self.fall_timer = 0
                    # Try to move down
                    if not self.check_collision(self.current_x, self.current_y + 1, self.current_shape):
                        self.current_y += 1
                    else:
                        # Can't move down, merge piece and create new one
                        self.merge_piece()
                        self.clear_lines()
                        self.new_piece()

            # Draw
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        return


if __name__ == "__main__":
    game = TetrisGame()
    game.run()