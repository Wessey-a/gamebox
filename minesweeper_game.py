import pygame
import random
import sys
from enum import Enum


class GameState(Enum):
    PLAYING = 0
    WIN = 1
    LOSE = 2


class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2
    QUESTION = 3


class Minesweeper:
    def __init__(self):
        pygame.init()

        # 颜色定义
        self.BG_COLOR = (200, 200, 200)  # 背景色
        self.GRID_COLOR = (150, 150, 150)  # 网格线颜色
        self.CELL_HIDDEN = (180, 180, 180)  # 未揭开格子颜色
        self.CELL_REVEALED = (220, 220, 220)  # 已揭开格子颜色
        self.CELL_FLAGGED = (255, 100, 100)  # 标记格子颜色
        self.CELL_QUESTION = (255, 255, 100)  # 问号格子颜色
        self.CELL_HIGHLIGHT = (240, 240, 240)  # 高亮颜色
        self.MINE_COLOR = (0, 0, 0)  # 地雷颜色
        self.TEXT_COLORS = [
            (0, 0, 255),  # 1: 蓝色
            (0, 128, 0),  # 2: 绿色
            (255, 0, 0),  # 3: 红色
            (0, 0, 128),  # 4: 深蓝
            (128, 0, 0),  # 5: 深红
            (0, 128, 128),  # 6: 青色
            (0, 0, 0),  # 7: 黑色
            (128, 128, 128)  # 8: 灰色
        ]

        # 难度设置 (行数, 列数, 地雷数)
        self.difficulties = {
            'easy': (9, 9, 10),  # 初级: 9x9, 10个地雷
            'medium': (16, 16, 40),  # 中级: 16x16, 40个地雷
            'hard': (16, 30, 99)  # 高级: 16x30, 99个地雷
        }

        # 默认难度
        self.difficulty = 'medium'
        self.rows, self.cols, self.mine_count = self.difficulties[self.difficulty]

        # 计算窗口大小 (格子大小40x40像素)
        self.cell_size = 40
        self.grid_width = self.cols * self.cell_size
        self.grid_height = self.rows * self.cell_size

        # 顶部信息栏高度
        self.info_height = 80

        # 底部控制栏高度
        self.control_height = 60

        # 总窗口大小
        self.SCREEN_WIDTH = self.grid_width
        self.SCREEN_HEIGHT = self.grid_height + self.info_height + self.control_height

        # 创建窗口
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('Minesweeper - Left click to reveal, Right click to flag, ESC to exit')

        # 游戏状态
        self.game_state = GameState.PLAYING
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
        self.flags_placed = 0

        # 字体
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_large = pygame.font.SysFont(None, 48)

        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # 初始化游戏
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        # 初始化游戏板
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_states = [[CellState.HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_state = GameState.PLAYING
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
        self.flags_placed = 0

        # 地雷位置将在第一次点击后生成
        self.mines = []

    def place_mines(self, first_click_row, first_click_col):
        """放置地雷，避开第一次点击的位置及其周围"""
        # 计算第一次点击周围的安全区域
        safe_cells = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = first_click_row + dr, first_click_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe_cells.add((r, c))

        # 生成所有可能的位置
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]

        # 移除安全区域
        available_cells = [cell for cell in all_cells if cell not in safe_cells]

        # 随机选择地雷位置
        self.mines = random.sample(available_cells, self.mine_count)

        # 设置地雷
        for r, c in self.mines:
            self.board[r][c] = -1  # -1 表示地雷

        # 计算每个格子的数字
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:  # 如果不是地雷
                    mine_count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.board[nr][nc] == -1:
                                    mine_count += 1
                    self.board[r][c] = mine_count

    def reveal_cell(self, row, col):
        """揭开格子"""
        # 如果游戏已结束或格子已揭开或已标记，则不处理
        if (self.game_state != GameState.PLAYING or
                self.cell_states[row][col] == CellState.REVEALED or
                self.cell_states[row][col] == CellState.FLAGGED):
            return

        # 如果是第一次点击，生成地雷
        if self.first_click:
            self.first_click = False
            self.place_mines(row, col)
            self.start_time = pygame.time.get_ticks()

        # 揭开当前格子
        self.cell_states[row][col] = CellState.REVEALED

        # 如果揭开的是地雷，游戏结束
        if self.board[row][col] == -1:
            self.game_state = GameState.LOSE
            # 揭开所有地雷
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c] == -1:
                        self.cell_states[r][c] = CellState.REVEALED
            return

        # 如果揭开的是空白格子，自动揭开周围的空白格子
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if self.cell_states[nr][nc] == CellState.HIDDEN:
                            self.reveal_cell(nr, nc)

        # 检查是否胜利
        self.check_win()

    def toggle_flag(self, row, col):
        """切换标记状态 (无标记 -> 旗帜 -> 问号 -> 无标记)"""
        if self.game_state != GameState.PLAYING or self.cell_states[row][col] == CellState.REVEALED:
            return

        current_state = self.cell_states[row][col]

        if current_state == CellState.HIDDEN:
            self.cell_states[row][col] = CellState.FLAGGED
            self.flags_placed += 1
        elif current_state == CellState.FLAGGED:
            self.cell_states[row][col] = CellState.QUESTION
            self.flags_placed -= 1
        elif current_state == CellState.QUESTION:
            self.cell_states[row][col] = CellState.HIDDEN

        # 检查是否胜利
        self.check_win()

    def check_win(self):
        """检查是否胜利"""
        # 胜利条件：所有非地雷格子都已揭开
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1 and self.cell_states[r][c] != CellState.REVEALED:
                    return

        # 所有地雷都已标记（可选，但标准扫雷不要求）
        for r, c in self.mines:
            if self.cell_states[r][c] != CellState.FLAGGED:
                # 如果地雷没有被标记，自动标记
                self.cell_states[r][c] = CellState.FLAGGED

        self.game_state = GameState.WIN

    def change_difficulty(self, difficulty):
        """改变游戏难度"""
        if difficulty in self.difficulties:
            self.difficulty = difficulty
            self.rows, self.cols, self.mine_count = self.difficulties[difficulty]

            # 重新计算窗口大小
            self.grid_width = self.cols * self.cell_size
            self.grid_height = self.rows * self.cell_size
            self.SCREEN_WIDTH = self.grid_width
            self.SCREEN_HEIGHT = self.grid_height + self.info_height + self.control_height

            # 创建新窗口
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

            # 重置游戏
            self.reset_game()

    def draw_cell(self, row, col, mouse_pos):
        """绘制单个格子"""
        x = col * self.cell_size
        y = row * self.cell_size + self.info_height

        cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

        # 检查鼠标是否悬停在该格子上
        mouse_over = cell_rect.collidepoint(mouse_pos)

        # 根据格子状态选择颜色
        state = self.cell_states[row][col]
        cell_value = self.board[row][col]

        if state == CellState.HIDDEN:
            color = self.CELL_HIGHLIGHT if mouse_over else self.CELL_HIDDEN
            pygame.draw.rect(self.screen, color, cell_rect)
            pygame.draw.rect(self.screen, self.GRID_COLOR, cell_rect, 1)

        elif state == CellState.REVEALED:
            color = self.CELL_REVEALED
            pygame.draw.rect(self.screen, color, cell_rect)
            pygame.draw.rect(self.screen, self.GRID_COLOR, cell_rect, 1)

            # 如果是地雷
            if cell_value == -1:
                # 绘制地雷（如果游戏输了，用红色表示踩中的地雷）
                if self.game_state == GameState.LOSE and (row, col) in self.mines:
                    # 检查这个地雷是否是玩家踩中的
                    if (row, col) in self.mines:
                        # 用红色圆表示踩中的地雷
                        center_x = x + self.cell_size // 2
                        center_y = y + self.cell_size // 2
                        pygame.draw.circle(self.screen, (255, 0, 0),
                                           (center_x, center_y), self.cell_size // 3)
                else:
                    # 普通地雷
                    center_x = x + self.cell_size // 2
                    center_y = y + self.cell_size // 2
                    pygame.draw.circle(self.screen, self.MINE_COLOR,
                                       (center_x, center_y), self.cell_size // 4)

                    # 地雷的光晕效果
                    pygame.draw.circle(self.screen, (100, 100, 100),
                                       (center_x, center_y), self.cell_size // 4 + 2, 2)

            # 如果是数字
            elif cell_value > 0:
                text = str(cell_value)
                text_color = self.TEXT_COLORS[cell_value - 1]
                text_surface = self.font_medium.render(text, True, text_color)
                text_rect = text_surface.get_rect(center=(x + self.cell_size // 2,
                                                          y + self.cell_size // 2))
                self.screen.blit(text_surface, text_rect)

        elif state == CellState.FLAGGED:
            color = self.CELL_HIGHLIGHT if mouse_over else self.CELL_FLAGGED
            pygame.draw.rect(self.screen, color, cell_rect)
            pygame.draw.rect(self.screen, self.GRID_COLOR, cell_rect, 1)

            # 绘制旗帜
            # 旗帜杆
            pole_x = x + self.cell_size // 2
            pygame.draw.line(self.screen, (0, 0, 0),
                             (pole_x, y + 5),
                             (pole_x, y + self.cell_size - 5), 2)

            # 旗帜
            flag_points = [
                (pole_x, y + 10),
                (pole_x + self.cell_size // 3, y + 15),
                (pole_x, y + 20)
            ]
            pygame.draw.polygon(self.screen, (255, 0, 0), flag_points)

        elif state == CellState.QUESTION:
            color = self.CELL_HIGHLIGHT if mouse_over else self.CELL_QUESTION
            pygame.draw.rect(self.screen, color, cell_rect)
            pygame.draw.rect(self.screen, self.GRID_COLOR, cell_rect, 1)

            # 绘制问号
            text_surface = self.font_medium.render("?", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x + self.cell_size // 2,
                                                      y + self.cell_size // 2))
            self.screen.blit(text_surface, text_rect)

    def draw_info_bar(self):
        """绘制顶部信息栏"""
        # 信息栏背景
        info_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.info_height)
        pygame.draw.rect(self.screen, (100, 100, 150), info_rect)

        # 地雷计数器
        mines_left = self.mine_count - self.flags_placed
        mines_text = f"Mines: {mines_left}"
        mines_surface = self.font_large.render(mines_text, True, (255, 255, 255))
        self.screen.blit(mines_surface, (20, 20))

        # 游戏状态表情
        face_x = self.SCREEN_WIDTH // 2 - 25
        face_y = 20
        face_size = 40

        if self.game_state == GameState.PLAYING:
            # 微笑脸
            pygame.draw.circle(self.screen, (255, 255, 0),
                               (face_x + face_size // 2, face_y + face_size // 2),
                               face_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + face_size // 3, face_y + face_size // 3), 3)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + 2 * face_size // 3, face_y + face_size // 3), 3)
            # 微笑的嘴巴
            pygame.draw.arc(self.screen, (0, 0, 0),
                            (face_x + 10, face_y + 20, face_size - 20, 15),
                            0, 3.14, 3)

        elif self.game_state == GameState.WIN:
            # 胜利的笑脸
            pygame.draw.circle(self.screen, (255, 255, 0),
                               (face_x + face_size // 2, face_y + face_size // 2),
                               face_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + face_size // 3, face_y + face_size // 3), 3)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + 2 * face_size // 3, face_y + face_size // 3), 3)
            # 大笑的嘴巴
            pygame.draw.arc(self.screen, (0, 0, 0),
                            (face_x + 5, face_y + 10, face_size - 10, 25),
                            3.14, 6.28, 3)

        elif self.game_state == GameState.LOSE:
            # 哭丧脸
            pygame.draw.circle(self.screen, (255, 255, 0),
                               (face_x + face_size // 2, face_y + face_size // 2),
                               face_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + face_size // 3, face_y + face_size // 3), 3)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (face_x + 2 * face_size // 3, face_y + face_size // 3), 3)
            # 向下的嘴巴
            pygame.draw.arc(self.screen, (0, 0, 0),
                            (face_x + 10, face_y + 30, face_size - 20, 15),
                            3.14, 6.28, 3)

        # 计时器
        if self.game_state == GameState.PLAYING and not self.first_click:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000

        time_text = f"Time: {self.elapsed_time}"
        time_surface = self.font_large.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (self.SCREEN_WIDTH - 150, 20))

    def draw_control_bar(self):
        """绘制底部控制栏"""
        # 控制栏背景
        control_rect = pygame.Rect(0, self.SCREEN_HEIGHT - self.control_height,
                                   self.SCREEN_WIDTH, self.control_height)
        pygame.draw.rect(self.screen, (100, 100, 150), control_rect)

        # 难度按钮
        difficulties = ['easy', 'medium', 'hard']
        button_width = 100
        button_height = 40
        button_margin = 20

        for i, diff in enumerate(difficulties):
            button_x = i * (button_width + button_margin) + button_margin
            button_y = self.SCREEN_HEIGHT - self.control_height // 2 - button_height // 2

            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # 按钮颜色（当前难度高亮）
            if diff == self.difficulty:
                color = (255, 200, 50)
            else:
                color = (200, 200, 200)

            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2, border_radius=5)

            # 按钮文字
            diff_text = {'easy': 'Beginner', 'medium': 'Intermediate', 'hard': 'Expert'}[diff]
            text_surface = self.font_medium.render(diff_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

        # 重新开始按钮
        restart_x = self.SCREEN_WIDTH - 120
        restart_y = self.SCREEN_HEIGHT - self.control_height // 2 - button_height // 2
        restart_rect = pygame.Rect(restart_x, restart_y, button_width, button_height)

        pygame.draw.rect(self.screen, (100, 200, 100), restart_rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), restart_rect, 2, border_radius=5)

        restart_text = "Restart"
        text_surface = self.font_medium.render(restart_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=restart_rect.center)
        self.screen.blit(text_surface, text_rect)

        # 控制提示
        hint_text = "Left: Reveal | Right: Flag/Unflag | ESC: Exit"
        hint_surface = self.font_small.render(hint_text, True, (255, 255, 255))
        self.screen.blit(hint_surface, (self.SCREEN_WIDTH // 2 - hint_surface.get_width() // 2,
                                        self.SCREEN_HEIGHT - self.control_height + 5))

    def draw(self):
        """绘制整个游戏"""
        self.screen.fill(self.BG_COLOR)

        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()

        # 绘制所有格子
        for row in range(self.rows):
            for col in range(self.cols):
                self.draw_cell(row, col, mouse_pos)

        # 绘制信息栏和控制栏
        self.draw_info_bar()
        self.draw_control_bar()

        # 如果游戏结束，显示消息
        if self.game_state == GameState.WIN:
            win_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150,
                                   self.info_height + self.grid_height // 2 - 50,
                                   300, 100)
            pygame.draw.rect(self.screen, (100, 200, 100, 200), win_rect, border_radius=10)

            win_text = f"You Win! Time: {self.elapsed_time}s"
            text_surface = self.font_large.render(win_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=win_rect.center)
            self.screen.blit(text_surface, text_rect)

        elif self.game_state == GameState.LOSE:
            lose_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150,
                                    self.info_height + self.grid_height // 2 - 50,
                                    300, 100)
            pygame.draw.rect(self.screen, (200, 100, 100, 200), lose_rect, border_radius=10)

            lose_text = "Game Over!"
            text_surface = self.font_large.render(lose_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=lose_rect.center)
            self.screen.blit(text_surface, text_rect)

    def handle_click(self, pos, button):
        """处理鼠标点击"""
        x, y = pos

        # 检查是否点击了控制栏
        if y > self.SCREEN_HEIGHT - self.control_height:
            # 检查是否点击了难度按钮
            button_width = 100
            button_height = 40
            button_margin = 20

            for i, diff in enumerate(['easy', 'medium', 'hard']):
                button_x = i * (button_width + button_margin) + button_margin
                button_y = self.SCREEN_HEIGHT - self.control_height // 2 - button_height // 2

                if (button_x <= x <= button_x + button_width and
                        button_y <= y <= button_y + button_height):
                    self.change_difficulty(diff)
                    return

            # 检查是否点击了重新开始按钮
            restart_x = self.SCREEN_WIDTH - 120
            restart_y = self.SCREEN_HEIGHT - self.control_height // 2 - button_height // 2

            if (restart_x <= x <= restart_x + button_width and
                    restart_y <= y <= restart_y + button_height):
                self.reset_game()
                return

        # 检查是否点击了游戏区域
        elif y >= self.info_height and y < self.info_height + self.grid_height:
            # 计算点击的格子
            col = x // self.cell_size
            row = (y - self.info_height) // self.cell_size

            if 0 <= row < self.rows and 0 <= col < self.cols:
                if button == 1:  # 左键
                    self.reveal_cell(row, col)
                elif button == 3:  # 右键
                    self.toggle_flag(row, col)

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)

            if not running:
                break

            # 绘制游戏
            self.draw()

            # 更新屏幕
            pygame.display.flip()

            # 控制帧率
            self.clock.tick(self.FPS)

        # 退出游戏
        pygame.quit()
        return


# 单独测试用
if __name__ == "__main__":
    game = Minesweeper()
    game.run()