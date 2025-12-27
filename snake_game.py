import pygame
import sys
import random
from typing import List, Tuple


class SnakeGame:
    def __init__(self):
        # 初始化pygame[citation:1]
        pygame.init()

        # 游戏常量
        self.WIDTH, self.HEIGHT = 600, 500
        self.GRID_SIZE = 20
        self.GRID_WIDTH = self.WIDTH // self.GRID_SIZE
        self.GRID_HEIGHT = self.HEIGHT // self.GRID_SIZE

        # 颜色定义[citation:9]
        self.BG_COLOR = (15, 56, 15)  # 深绿色背景
        self.GRID_COLOR = (30, 90, 30)  # 网格线颜色
        self.SNAKE_COLOR = (50, 205, 50)  # 蛇身颜色 - 亮绿色
        self.SNAKE_HEAD_COLOR = (0, 255, 0)  # 蛇头颜色 - 更亮的绿色
        self.FOOD_COLOR = (255, 50, 50)  # 食物颜色 - 红色
        self.TEXT_COLOR = (220, 220, 220)  # 文字颜色

        # 创建游戏窗口[citation:1]
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Snake Game - Use Arrow Keys | Press ESC to Exit")

        # 游戏时钟[citation:1]
        self.clock = pygame.time.Clock()
        self.FPS = 10

        # 游戏状态
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        # 蛇的初始位置和长度[citation:9]
        self.snake = [(self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # 初始向右移动
        self.next_direction = self.direction

        # 生成第一个食物
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self) -> Tuple[int, int]:
        """在随机位置生成食物，确保不在蛇身上"""
        while True:
            food_pos = (random.randint(0, self.GRID_WIDTH - 1),
                        random.randint(0, self.GRID_HEIGHT - 1))
            if food_pos not in self.snake:
                return food_pos

    def handle_events(self):
        """处理游戏事件[citation:1][citation:9]"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # 退出游戏

                # 方向控制（不能直接反向移动）
                if event.key == pygame.K_UP and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

        return True  # 继续游戏

    def update(self):
        """更新游戏状态[citation:9]"""
        if self.game_over:
            return

        # 更新方向
        self.direction = self.next_direction

        # 计算新的蛇头位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.GRID_WIDTH,
                    (head_y + dy) % self.GRID_HEIGHT)

        # 检查是否撞到自己
        if new_head in self.snake:
            self.game_over = True
            return

        # 添加新的蛇头
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            # 每得50分增加速度
            if self.score % 50 == 0 and self.FPS < 20:
                self.FPS += 1
        else:
            # 没吃到食物则移除蛇尾
            self.snake.pop()

    def draw_grid(self):
        """绘制游戏网格"""
        for x in range(0, self.WIDTH, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (x, 0), (x, self.HEIGHT), 1)
        for y in range(0, self.HEIGHT, self.GRID_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (0, y), (self.WIDTH, y), 1)

    def draw(self):
        """绘制游戏元素[citation:9]"""
        # 填充背景色
        self.screen.fill(self.BG_COLOR)

        # 绘制网格
        self.draw_grid()

        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            color = self.SNAKE_HEAD_COLOR if i == 0 else self.SNAKE_COLOR
            rect = pygame.Rect(x * self.GRID_SIZE, y * self.GRID_SIZE,
                               self.GRID_SIZE, self.GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (color[0] // 2, color[1] // 2, color[2] // 2),
                             rect, 2)  # 边框

            # 蛇头眼睛
            if i == 0:
                eye_size = self.GRID_SIZE // 5
                # 根据方向确定眼睛位置
                dx, dy = self.direction
                if dx != 0:  # 左右移动
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x * self.GRID_SIZE + self.GRID_SIZE // 3,
                                        y * self.GRID_SIZE + self.GRID_SIZE // 3),
                                       eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x * self.GRID_SIZE + 2 * self.GRID_SIZE // 3,
                                        y * self.GRID_SIZE + self.GRID_SIZE // 3),
                                       eye_size)
                else:  # 上下移动
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x * self.GRID_SIZE + self.GRID_SIZE // 3,
                                        y * self.GRID_SIZE + self.GRID_SIZE // 3),
                                       eye_size)
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x * self.GRID_SIZE + 2 * self.GRID_SIZE // 3,
                                        y * self.GRID_SIZE + self.GRID_SIZE // 3),
                                       eye_size)

        # 绘制食物（苹果形状）
        food_rect = pygame.Rect(self.food[0] * self.GRID_SIZE + 2,
                                self.food[1] * self.GRID_SIZE + 2,
                                self.GRID_SIZE - 4, self.GRID_SIZE - 4)
        pygame.draw.circle(self.screen, self.FOOD_COLOR,
                           food_rect.center, food_rect.width // 2)
        # 食物茎
        pygame.draw.rect(self.screen, (139, 69, 19),  # 棕色
                         (self.food[0] * self.GRID_SIZE + self.GRID_SIZE // 2 - 2,
                          self.food[1] * self.GRID_SIZE - 3, 4, 6))

        # 绘制分数
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

        # 绘制速度
        speed_text = font.render(f"Speed: {self.FPS}", True, self.TEXT_COLOR)
        self.screen.blit(speed_text, (self.WIDTH - 120, 10))

        # 游戏结束显示
        if self.game_over:
            # 半透明覆盖层
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # 黑色半透明
            self.screen.blit(overlay, (0, 0))

            # 游戏结束文字
            game_over_font = pygame.font.SysFont(None, 64)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(game_over_text,
                             (self.WIDTH // 2 - game_over_text.get_width() // 2,
                              self.HEIGHT // 2 - 50))

            # 最终分数
            final_score_font = pygame.font.SysFont(None, 48)
            final_score_text = final_score_font.render(f"Final Score: {self.score}",
                                                       True, self.TEXT_COLOR)
            self.screen.blit(final_score_text,
                             (self.WIDTH // 2 - final_score_text.get_width() // 2,
                              self.HEIGHT // 2 + 10))

            # 重新开始提示
            restart_font = pygame.font.SysFont(None, 32)
            restart_text = restart_font.render("Press R to Restart | ESC to Exit",
                                               True, (200, 200, 100))
            self.screen.blit(restart_text,
                             (self.WIDTH // 2 - restart_text.get_width() // 2,
                              self.HEIGHT // 2 + 80))

        # 绘制控制提示（游戏未结束时）
        if not self.game_over:
            control_font = pygame.font.SysFont(None, 24)
            control_text = control_font.render("Use Arrow Keys to Move | ESC to Exit",
                                               True, (150, 150, 150))
            self.screen.blit(control_text,
                             (self.WIDTH // 2 - control_text.get_width() // 2,
                              self.HEIGHT - 30))

        # 更新显示[citation:1]
        pygame.display.flip()

    def run(self):
        """运行游戏主循环[citation:1][citation:9]"""
        running = True
        while running:
            # 1. 处理事件[citation:9]
            running = self.handle_events()

            # 2. 更新游戏状态[citation:9]
            self.update()

            # 3. 绘制游戏[citation:9]
            self.draw()

            # 4. 控制游戏帧率[citation:1]
            self.clock.tick(self.FPS)

        # 退出游戏
        pygame.quit()
        return


if __name__ == "__main__":
    game = SnakeGame()
    game.run()