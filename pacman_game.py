import pygame
import sys

class PacManGame:
    def __init__(self):
        pygame.init()
        self.TILE_SIZE = 40
        self.FPS = 10
        self.SCREEN_WIDTH = 600
        self.SCREEN_HEIGHT = 480
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man - Use Arrow Keys | ESC to Exit")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.PINK = (255, 184, 255)
        self.GREEN = (0, 255, 0)

        # 游戏网格 (0=空地，1=墙，2=豆子，3=能量豆，4=幽灵，5=玩家)
        # 为适配窗口大小，使用了一个新的简化迷宫布局
        self.game_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 3, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 3, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1],
            [0, 0, 0, 1, 2, 1, 2, 2, 2, 1, 2, 1, 0, 0, 0],
            [1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 3, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 3, 1],
            [1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
        ]
        self.rows = len(self.game_map)
        self.cols = len(self.game_map[0])

        # 初始化游戏状态
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        self.player_pos = [self.rows - 1, 1]  # 玩家初始位置
        self.ghosts = [
            {'pos': [6, 7], 'color': self.RED, 'dir': 0},
            {'pos': [7, 7], 'color': self.PINK, 'dir': 1},
        ]
        self.score = 0
        self.game_over = False
        self.win = False
        # 将初始方向改为 3 (上) 或 2 (左)，因为上方/左方是空的
        self.player_dir = 3  # 改为：初始朝上，因为位置[13,1]是豆子(2)，可通行
        self.next_dir = 3  # 保持与 player_dir 一致

    def move_player(self):
        """移动玩家"""
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        dr, dc = dirs[self.player_dir]
        new_r = self.player_pos[0] + dr
        new_c = self.player_pos[1] + dc

        # 检查移动是否合法 (非墙且在边界内)
        if (0 <= new_r < self.rows and 0 <= new_c < self.cols and
                self.game_map[new_r][new_c] != 1):
            self.player_pos = [new_r, new_c]
            return True
        return False

    def move_ghosts(self):
        """移动幽灵 (简单随机移动)"""
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for ghost in self.ghosts:
            # 简单AI：尝试当前方向，如果撞墙则随机换方向
            dr, dc = dirs[ghost['dir']]
            new_r = ghost['pos'][0] + dr
            new_c = ghost['pos'][1] + dc

            if (0 <= new_r < self.rows and 0 <= new_c < self.cols and
                    self.game_map[new_r][new_c] != 1):
                ghost['pos'] = [new_r, new_c]
            else:
                # 随机选择一个新方向
                ghost['dir'] = (ghost['dir'] + 1) % 4

    def check_collisions(self):
        """检查碰撞和吃豆子"""
        r, c = self.player_pos
        cell = self.game_map[r][c]

        # 吃豆子
        if cell == 2:  # 普通豆子
            self.score += 10
            self.game_map[r][c] = 0
        elif cell == 3:  # 能量豆
            self.score += 50
            self.game_map[r][c] = 0

        # 检查是否吃完所有豆子
        beans_left = sum(row.count(2) + row.count(3) for row in self.game_map)
        if beans_left == 0:
            self.win = True
            self.game_over = True

        # 检查是否碰到幽灵
        for ghost in self.ghosts:
            if ghost['pos'] == self.player_pos:
                self.game_over = True
                self.win = False

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(self.BLACK)

        # 绘制地图
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.TILE_SIZE
                y = r * self.TILE_SIZE
                cell = self.game_map[r][c]

                if cell == 1:  # 墙
                    pygame.draw.rect(self.screen, self.BLUE,
                                   (x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif cell == 2:  # 豆子
                    center_x = x + self.TILE_SIZE // 2
                    center_y = y + self.TILE_SIZE // 2
                    pygame.draw.circle(self.screen, self.WHITE,
                                     (center_x, center_y), 4)
                elif cell == 3:  # 能量豆
                    center_x = x + self.TILE_SIZE // 2
                    center_y = y + self.TILE_SIZE // 2
                    pygame.draw.circle(self.screen, self.YELLOW,
                                     (center_x, center_y), 8)

        # 绘制玩家 (吃豆人)
        px = self.player_pos[1] * self.TILE_SIZE
        py = self.player_pos[0] * self.TILE_SIZE
        mouth_angle = 30  # 嘴巴张开的度数
        if self.player_dir == 0:  # 右
            start_angle = mouth_angle
            end_angle = 360 - mouth_angle
        elif self.player_dir == 2:  # 左
            start_angle = 180 + mouth_angle
            end_angle = 180 - mouth_angle
        elif self.player_dir == 1:  # 下
            start_angle = 90 + mouth_angle
            end_angle = 90 - mouth_angle
        else:  # 上
            start_angle = 270 + mouth_angle
            end_angle = 270 - mouth_angle

        pygame.draw.circle(self.screen, self.YELLOW,
                         (px + self.TILE_SIZE // 2, py + self.TILE_SIZE // 2),
                         self.TILE_SIZE // 2 - 2)
        # 绘制嘴巴（通过绘制一个重叠的黑色扇形实现）
        pygame.draw.arc(self.screen, self.BLACK,
                       (px + 2, py + 2, self.TILE_SIZE - 4, self.TILE_SIZE - 4),
                       start_angle, end_angle)

        # 绘制幽灵
        for ghost in self.ghosts:
            gx = ghost['pos'][1] * self.TILE_SIZE
            gy = ghost['pos'][0] * self.TILE_SIZE
            # 幽灵身体
            pygame.draw.circle(self.screen, ghost['color'],
                             (gx + self.TILE_SIZE // 2, gy + self.TILE_SIZE // 2 - 5),
                             self.TILE_SIZE // 2 - 2)
            # 幽灵底部（波浪效果）
            points = [(gx + 2, gy + self.TILE_SIZE // 2),
                     (gx + 8, gy + self.TILE_SIZE - 2),
                     (gx + 15, gy + self.TILE_SIZE // 2),
                     (gx + 22, gy + self.TILE_SIZE - 2),
                     (gx + 28, gy + self.TILE_SIZE // 2),
                     (gx + 35, gy + self.TILE_SIZE - 2),
                     (gx + self.TILE_SIZE - 2, gy + self.TILE_SIZE // 2)]
            pygame.draw.polygon(self.screen, ghost['color'], points)
            # 幽灵眼睛
            pygame.draw.circle(self.screen, self.WHITE,
                             (gx + self.TILE_SIZE // 2 - 5, gy + self.TILE_SIZE // 2 - 5), 4)
            pygame.draw.circle(self.screen, self.WHITE,
                             (gx + self.TILE_SIZE // 2 + 5, gy + self.TILE_SIZE // 2 - 5), 4)
            pygame.draw.circle(self.screen, self.BLUE,
                             (gx + self.TILE_SIZE // 2 - 5, gy + self.TILE_SIZE // 2 - 5), 2)
            pygame.draw.circle(self.screen, self.BLUE,
                             (gx + self.TILE_SIZE // 2 + 5, gy + self.TILE_SIZE // 2 - 5), 2)

        # 绘制分数
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        # 游戏结束/胜利画面
        if self.game_over:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.win:
                msg = "YOU WIN! 🎉"
                color = self.GREEN
            else:
                msg = "GAME OVER"
                color = self.RED

            font_large = pygame.font.SysFont(None, 64)
            font_small = pygame.font.SysFont(None, 32)
            game_over_text = font_large.render(msg, True, color)
            restart_text = font_small.render("Press R to Restart | ESC to Exit", True, self.YELLOW)

            self.screen.blit(game_over_text,
                           (self.SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                            self.SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text,
                           (self.SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                            self.SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

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
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif not self.game_over:
                        # 方向键控制
                        if event.key == pygame.K_RIGHT:
                            self.next_dir = 0
                        elif event.key == pygame.K_DOWN:
                            self.next_dir = 1
                        elif event.key == pygame.K_LEFT:
                            self.next_dir = 2
                        elif event.key == pygame.K_UP:
                            self.next_dir = 3

            if not running:
                break

            # 更新玩家方向（防止原地转向）
            if not self.game_over:
                # 尝试应用下一个方向
                self.player_dir = self.next_dir
                self.move_player()
                self.move_ghosts()
                self.check_collisions()

            # 绘制
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        return


if __name__ == "__main__":
    game = PacManGame()
    game.run()