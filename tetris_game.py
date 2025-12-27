import pygame
import random
import sys

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.CELL_SIZE = 30
        self.GRID_WIDTH = 10
        self.GRID_HEIGHT = 20
        self.SCREEN_WIDTH = self.CELL_SIZE * (self.GRID_WIDTH + 6)
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.GRID_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris - Arrow Keys: Move, Up: Rotate | ESC to Exit")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.FALL_SPEED = 0.5  # 方块下落速度 (秒/格)
        self.fall_timer = 0

        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (50, 50, 50)
        self.COLORS = [
            (0, 240, 240),   # I - Cyan
            (0, 0, 240),     # J - Blue
            (240, 160, 0),   # L - Orange
            (240, 240, 0),   # O - Yellow
            (0, 240, 0),     # S - Green
            (160, 0, 240),   # T - Purple
            (240, 0, 0)      # Z - Red
        ]

        # 方块形状定义 (7种基本形状)
        self.SHAPES = [
            [[1, 1, 1, 1]],  # I
            [[1, 0, 0], [1, 1, 1]],  # J
            [[0, 0, 1], [1, 1, 1]],  # L
            [[1, 1], [1, 1]],        # O
            [[0, 1, 1], [1, 1, 0]],  # S
            [[0, 1, 0], [1, 1, 1]],  # T
            [[1, 1, 0], [0, 1, 1]]   # Z
        ]

        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        self.grid = [[0 for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.new_piece()
        self.font = pygame.font.SysFont(None, 24)
        self.font_large = pygame.font.SysFont(None, 36)

    def new_piece(self):
        """创建新的方块"""
        self.current_shape_idx = random.randint(0, len(self.SHAPES) - 1)
        self.current_shape = [row[:] for row in self.SHAPES[self.current_shape_idx]]
        self.current_color = self.COLORS[self.current_shape_idx]
        self.current_x = self.GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        # 检查游戏是否结束 (新方块无法放置)
        if self.check_collision(self.current_x, self.current_y, self.current_shape):
            self.game_over = True

    def check_collision(self, x, y, shape):
        """检查方块是否与网格或其他方块碰撞"""
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    # 计算在网格中的实际位置
                    grid_x = x + col_idx
                    grid_y = y + row_idx

                    # 检查边界
                    if (grid_x < 0 or grid_x >= self.GRID_WIDTH or
                            grid_y >= self.GRID_HEIGHT):
                        return True

                    # 检查是否与已有方块重叠
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return True
        return False

    def rotate_shape(self, shape):
        """旋转方块 (顺时针90度)"""
        # 转置矩阵然后反转每一行
        return [[shape[y][x] for y in range(len(shape)-1, -1, -1)]
                for x in range(len(shape[0]))]

    def merge_piece(self):
        """将当前方块合并到网格中"""
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_x = self.current_x + col_idx
                    grid_y = self.current_y + row_idx
                    if 0 <= grid_y < self.GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.current_color

    def clear_lines(self):
        """清除已填满的行并计分"""
        lines_to_clear = []
        for row_idx in range(self.GRID_HEIGHT):
            if all(self.grid[row_idx]):
                lines_to_clear.append(row_idx)

        if not lines_to_clear:
            return 0

        # 计分 (俄罗斯方块标准计分)
        line_count = len(lines_to_clear)
        self.lines_cleared += line_count
        self.score += [100, 300, 500, 800][min(line_count-1, 3)] * self.level

        # 更新等级 (每清除10行升一级)
        self.level = self.lines_cleared // 10 + 1
        self.FALL_SPEED = max(0.05, 0.5 - (self.level - 1) * 0.05)

        # 清除行并让上面的行下落
        for row_idx in lines_to_clear:
            del self.grid[row_idx]
            self.grid.insert(0, [0 for _ in range(self.GRID_WIDTH)])

        return line_count

    def draw_grid(self):
        """绘制游戏网格和方块"""
        # 绘制背景网格
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

        # 绘制当前下落的方块
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

        # 绘制下一个方块预览
        preview_x = self.GRID_WIDTH + 2
        preview_y = 3
        next_shape = self.SHAPES[(self.current_shape_idx + 1) % len(self.SHAPES)]
        next_color = self.COLORS[(self.current_shape_idx + 1) % len(self.COLORS)]

        # 绘制预览标题
        preview_text = self.font.render("Next:", True, self.WHITE)
        self.screen.blit(preview_text,
                        (preview_x * self.CELL_SIZE, (preview_y - 2) * self.CELL_SIZE))

        # 绘制预览方块
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

        # 绘制分数和等级信息
        info_x = self.GRID_WIDTH + 2
        info_y = 8

        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, self.WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, self.WHITE)

        self.screen.blit(score_text, (info_x * self.CELL_SIZE, info_y * self.CELL_SIZE))
        self.screen.blit(level_text, (info_x * self.CELL_SIZE, (info_y + 1.5) * self.CELL_SIZE))
        self.screen.blit(lines_text, (info_x * self.CELL_SIZE, (info_y + 3) * self.CELL_SIZE))

        # 绘制控制提示
        controls_y = info_y + 6
        controls = [
            "Controls:",
            "←→ : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "R : Restart",
            "ESC : Exit"
        ]

        for i, text in enumerate(controls):
            control_text = self.font.render(text, True, self.WHITE)
            self.screen.blit(control_text,
                           (info_x * self.CELL_SIZE, (controls_y + i * 1.2) * self.CELL_SIZE))

    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        restart_text = self.font.render("Press R to Restart | ESC to Exit", True, (200, 200, 100))

        self.screen.blit(game_over_text,
                        (self.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                         self.SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(score_text,
                        (self.SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                         self.SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text,
                        (self.SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                         self.SCREEN_HEIGHT // 2 + 40))

    def draw(self):
        """绘制整个游戏画面"""
        self.screen.fill(self.BLACK)
        self.draw_grid()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        running = True
        last_time = pygame.time.get_ticks()
        soft_drop = False

        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # 转换为秒
            last_time = current_time

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if not self.check_collision(self.current_x - 1, self.current_y, self.current_shape):
                                self.current_x -= 1
                        elif event.key == pygame.K_RIGHT:
                            if not self.check_collision(self.current_x + 1, self.current_y, self.current_shape):
                                self.current_x += 1
                        elif event.key == pygame.K_UP:
                            # 旋转方块
                            rotated = self.rotate_shape(self.current_shape)
                            if not self.check_collision(self.current_x, self.current_y, rotated):
                                self.current_shape = rotated
                        elif event.key == pygame.K_DOWN:
                            soft_drop = True
                        elif event.key == pygame.K_SPACE:
                            # 硬降 (直接落到底部)
                            while not self.check_collision(self.current_x, self.current_y + 1, self.current_shape):
                                self.current_y += 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        soft_drop = False

            if not running:
                break

            # 更新游戏状态
            if not self.game_over:
                # 更新下落计时器
                speed = self.FALL_SPEED / 10 if soft_drop else self.FALL_SPEED
                self.fall_timer += delta_time

                if self.fall_timer >= speed:
                    self.fall_timer = 0
                    # 尝试下落
                    if not self.check_collision(self.current_x, self.current_y + 1, self.current_shape):
                        self.current_y += 1
                    else:
                        # 无法下落，合并方块并创建新方块
                        self.merge_piece()
                        self.clear_lines()
                        self.new_piece()

            # 绘制
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        return


if __name__ == "__main__":
    game = TetrisGame()
    game.run()