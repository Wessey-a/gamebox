import pygame
import random
import math
import sys


class PlaneShooter:
    def __init__(self):
        pygame.init()

        # 屏幕设置
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('Airplane Battle - Arrow Keys Move, Space Shoot, ESC Exit')

        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.GREEN = (50, 255, 50)
        self.BLUE = (50, 100, 255)
        self.YELLOW = (255, 255, 50)
        self.PURPLE = (200, 50, 255)
        self.CYAN = (50, 255, 255)

        # 按钮颜色
        self.BUTTON_GREEN_NORMAL = (50, 150, 50)
        self.BUTTON_GREEN_HOVER = (70, 170, 70)
        self.BUTTON_RED_NORMAL = (150, 50, 50)
        self.BUTTON_RED_HOVER = (170, 70, 70)

        # 游戏状态
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)

        # 按钮悬停状态
        self.restart_button_hover = False
        self.exit_button_hover = False

        # 玩家设置
        self.player_width = 60
        self.player_height = 40
        self.player_x = self.SCREEN_WIDTH // 2
        self.player_y = self.SCREEN_HEIGHT - 80
        self.player_speed = 8
        self.player_color = self.BLUE

        # 子弹设置
        self.bullets = []
        self.bullet_speed = 12
        self.bullet_width = 6
        self.bullet_height = 20
        self.bullet_color = self.YELLOW
        self.shoot_delay = 200  # 毫秒
        self.last_shot_time = 0

        # 敌机设置
        self.enemies = []
        self.enemy_width = 50
        self.enemy_height = 40
        self.enemy_speed = 3
        self.enemy_spawn_delay = 1000  # 毫秒
        self.last_enemy_spawn = 0
        self.enemy_colors = [self.RED, self.GREEN, self.PURPLE]

        # 爆炸效果
        self.explosions = []

        # 星星背景
        self.stars = []
        self.create_stars(100)

        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.FPS = 60

    def create_stars(self, count):
        """创建星空背景"""
        for _ in range(count):
            x = random.randint(0, self.SCREEN_WIDTH)
            y = random.randint(0, self.SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            self.stars.append([x, y, size, color])

    def create_player(self):
        """绘制玩家飞机"""
        # 飞机主体
        pygame.draw.polygon(self.screen, self.player_color, [
            (self.player_x, self.player_y),  # 机头
            (self.player_x - self.player_width // 2, self.player_y + self.player_height),  # 左翼
            (self.player_x + self.player_width // 2, self.player_y + self.player_height)  # 右翼
        ])

        # 飞机驾驶舱
        pygame.draw.circle(self.screen, self.CYAN,
                           (self.player_x, self.player_y + 10), 10)

        # 飞机机翼装饰
        pygame.draw.rect(self.screen, self.WHITE,
                         (self.player_x - self.player_width // 2 + 5,
                          self.player_y + self.player_height - 10,
                          15, 8))
        pygame.draw.rect(self.screen, self.WHITE,
                         (self.player_x + self.player_width // 2 - 20,
                          self.player_y + self.player_height - 10,
                          15, 8))

    def create_bullet(self):
        """创建子弹"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y,
                'width': self.bullet_width,
                'height': self.bullet_height,
                'color': self.bullet_color
            })
            self.last_shot_time = current_time

    def update_bullets(self):
        """更新子弹位置"""
        bullets_to_remove = []

        for i, bullet in enumerate(self.bullets):
            bullet['y'] -= self.bullet_speed

            # 移除超出屏幕的子弹
            if bullet['y'] < 0:
                bullets_to_remove.append(i)

            # 检查是否击中敌机
            for j, enemy in enumerate(self.enemies):
                if (bullet['x'] > enemy['x'] - enemy['width'] // 2 and
                        bullet['x'] < enemy['x'] + enemy['width'] // 2 and
                        bullet['y'] > enemy['y'] - enemy['height'] // 2 and
                        bullet['y'] < enemy['y'] + enemy['height'] // 2):

                    # 击中敌机
                    bullets_to_remove.append(i)
                    self.create_explosion(enemy['x'], enemy['y'], enemy['color'])
                    self.enemies.pop(j)
                    self.score += 100 * self.level

                    # 每得1000分升一级
                    if self.score // 1000 + 1 > self.level:
                        self.level = self.score // 1000 + 1
                        self.enemy_speed = min(8, 3 + self.level * 0.5)  # 增加敌机速度

                    break

        # 移除需要删除的子弹（从后往前删除）
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)

    def draw_bullets(self):
        """绘制子弹"""
        for bullet in self.bullets:
            # 子弹主体
            pygame.draw.rect(self.screen, bullet['color'],
                             (bullet['x'] - bullet['width'] // 2,
                              bullet['y'],
                              bullet['width'],
                              bullet['height']))

            # 子弹光效
            pygame.draw.circle(self.screen, self.WHITE,
                               (bullet['x'], bullet['y'] + bullet['height'] // 2),
                               bullet['width'] // 2)

    def spawn_enemy(self):
        """生成敌机"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_spawn > self.enemy_spawn_delay:
            enemy_type = random.randint(0, 2)
            enemy_color = self.enemy_colors[enemy_type]

            self.enemies.append({
                'x': random.randint(self.enemy_width // 2,
                                    self.SCREEN_WIDTH - self.enemy_width // 2),
                'y': -self.enemy_height,
                'width': self.enemy_width,
                'height': self.enemy_height,
                'speed': self.enemy_speed + random.uniform(-0.5, 0.5),
                'color': enemy_color,
                'type': enemy_type,
                'wobble': random.uniform(0, math.pi * 2),  # 用于摆动效果
                'wobble_speed': random.uniform(0.02, 0.05)
            })

            # 随着等级提高，敌机生成更快
            self.enemy_spawn_delay = max(200, 1000 - self.level * 50)
            self.last_enemy_spawn = current_time

    def update_enemies(self):
        """更新敌机位置"""
        enemies_to_remove = []

        for i, enemy in enumerate(self.enemies):
            # 敌机摆动效果
            enemy['wobble'] += enemy['wobble_speed']
            wobble_offset = math.sin(enemy['wobble']) * 2

            # 更新位置
            enemy['y'] += enemy['speed']
            enemy['x'] += wobble_offset

            # 检查敌机是否超出屏幕底部
            if enemy['y'] > self.SCREEN_HEIGHT + self.enemy_height:
                enemies_to_remove.append(i)
                self.lives -= 1

                if self.lives <= 0:
                    self.game_over = True

            # 检查敌机是否撞到玩家
            player_rect = pygame.Rect(
                self.player_x - self.player_width // 2,
                self.player_y,
                self.player_width,
                self.player_height
            )

            enemy_rect = pygame.Rect(
                enemy['x'] - enemy['width'] // 2,
                enemy['y'] - enemy['height'] // 2,
                enemy['width'],
                enemy['height']
            )

            if player_rect.colliderect(enemy_rect):
                enemies_to_remove.append(i)
                self.create_explosion(enemy['x'], enemy['y'], enemy['color'])
                self.lives -= 1

                if self.lives <= 0:
                    self.game_over = True

        # 移除需要删除的敌机
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(self.enemies):
                self.enemies.pop(i)

    def draw_enemies(self):
        """绘制敌机"""
        for enemy in self.enemies:
            color = enemy['color']

            # 根据敌机类型绘制不同形状
            if enemy['type'] == 0:  # 类型0：三角形敌机
                pygame.draw.polygon(self.screen, color, [
                    (enemy['x'], enemy['y'] - enemy['height'] // 2),  # 顶部
                    (enemy['x'] - enemy['width'] // 2, enemy['y'] + enemy['height'] // 2),  # 左下
                    (enemy['x'] + enemy['width'] // 2, enemy['y'] + enemy['height'] // 2)  # 右下
                ])

            elif enemy['type'] == 1:  # 类型1：方形敌机
                pygame.draw.rect(self.screen, color,
                                 (enemy['x'] - enemy['width'] // 2,
                                  enemy['y'] - enemy['height'] // 2,
                                  enemy['width'],
                                  enemy['height']))

                # 方形敌机上的图案
                pygame.draw.circle(self.screen, self.BLACK,
                                   (enemy['x'], enemy['y']), 8)

            else:  # 类型2：菱形敌机
                points = [
                    (enemy['x'], enemy['y'] - enemy['height'] // 2),  # 上
                    (enemy['x'] + enemy['width'] // 2, enemy['y']),  # 右
                    (enemy['x'], enemy['y'] + enemy['height'] // 2),  # 下
                    (enemy['x'] - enemy['width'] // 2, enemy['y'])  # 左
                ]
                pygame.draw.polygon(self.screen, color, points)

                # 菱形敌机上的图案
                pygame.draw.line(self.screen, self.BLACK,
                                 (enemy['x'] - enemy['width'] // 4, enemy['y']),
                                 (enemy['x'] + enemy['width'] // 4, enemy['y']), 2)
                pygame.draw.line(self.screen, self.BLACK,
                                 (enemy['x'], enemy['y'] - enemy['height'] // 4),
                                 (enemy['x'], enemy['y'] + enemy['height'] // 4), 2)

    def create_explosion(self, x, y, color):
        """创建爆炸效果"""
        explosion_size = 30
        explosion_particles = []

        # 创建爆炸粒子
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            size = random.randint(2, 6)
            lifetime = random.randint(20, 40)

            explosion_particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime
            })

        self.explosions.append({
            'x': x,
            'y': y,
            'particles': explosion_particles,
            'timer': 0,
            'max_timer': 40
        })

    def update_explosions(self):
        """更新爆炸效果"""
        explosions_to_remove = []

        for i, explosion in enumerate(self.explosions):
            explosion['timer'] += 1

            # 更新爆炸粒子
            for particle in explosion['particles']:
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                particle['dy'] += 0.1  # 重力效果
                particle['lifetime'] -= 1

            # 移除过时的爆炸效果
            if explosion['timer'] > explosion['max_timer']:
                explosions_to_remove.append(i)

        # 移除需要删除的爆炸效果
        for i in sorted(explosions_to_remove, reverse=True):
            if i < len(self.explosions):
                self.explosions.pop(i)

    def draw_explosions(self):
        """绘制爆炸效果"""
        for explosion in self.explosions:
            for particle in explosion['particles']:
                if particle['lifetime'] > 0:
                    # 根据剩余寿命调整粒子大小和透明度
                    alpha = int(255 * particle['lifetime'] / particle['max_lifetime'])
                    size = int(particle['size'] * particle['lifetime'] / particle['max_lifetime'])

                    if size > 0:
                        # 创建临时surface来支持alpha
                        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(particle_surface,
                                           (*particle['color'][:3], alpha),
                                           (size, size), size)
                        self.screen.blit(particle_surface,
                                         (particle['x'] - size, particle['y'] - size))

    def draw_stars(self):
        """绘制星空背景"""
        for star in self.stars:
            x, y, size, color = star
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

            # 让星星缓慢移动
            star[1] += 0.5  # 向下移动
            if star[1] > self.SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, self.SCREEN_WIDTH)

    def draw_hud(self):
        """绘制游戏界面信息"""
        # 绘制分数
        score_text = self.font.render(f'Score: {self.score}', True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        # 绘制等级
        level_text = self.font.render(f'Level: {self.level}', True, self.WHITE)
        self.screen.blit(level_text, (10, 50))

        # 绘制生命值
        lives_text = self.font.render(f'Lives: {self.lives}', True, self.WHITE)
        self.screen.blit(lives_text, (10, 90))

        # 绘制生命图标
        for i in range(self.lives):
            pygame.draw.polygon(self.screen, self.BLUE, [
                (self.SCREEN_WIDTH - 100 + i * 30, 20),
                (self.SCREEN_WIDTH - 115 + i * 30, 40),
                (self.SCREEN_WIDTH - 85 + i * 30, 40)
            ])

        # 绘制控制提示
        controls_text = self.font.render('Arrow Keys Move, Space Shoot, ESC Exit', True, self.WHITE)
        self.screen.blit(controls_text,
                         (self.SCREEN_WIDTH // 2 - controls_text.get_width() // 2,
                          self.SCREEN_HEIGHT - 30))

    def draw_button(self, rect, text, normal_color, hover_color, is_hovering, font_size=28):
        """绘制按钮的通用函数"""
        # 选择按钮颜色
        button_color = hover_color if is_hovering else normal_color

        # 绘制按钮背景
        pygame.draw.rect(self.screen, button_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (220, 220, 220), rect, 2, border_radius=8)

        # 绘制按钮文字
        button_font = pygame.font.SysFont(None, font_size)
        button_text = button_font.render(text, True, (255, 255, 255))
        self.screen.blit(button_text,
                         (rect.centerx - button_text.get_width() // 2,
                          rect.centery - button_text.get_height() // 2))

        return rect

    def draw_game_over(self):
        """绘制游戏结束画面 - 左侧文字，右侧按钮"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 在中间绘制一条垂直分割线
        divider_x = self.SCREEN_WIDTH // 2
        pygame.draw.line(self.screen, (100, 100, 100, 150),
                         (divider_x, 150),
                         (divider_x, self.SCREEN_HEIGHT - 150), 2)

        # 左侧区域：游戏信息
        left_area_width = self.SCREEN_WIDTH // 2
        left_center_x = left_area_width // 2

        # 游戏结束文字
        game_over_text = self.big_font.render('Game Over', True, self.RED)
        self.screen.blit(game_over_text,
                         (left_center_x - game_over_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2 - 120))

        # 最终分数
        score_text = self.font.render(f'Final Score: {self.score}', True, self.WHITE)
        self.screen.blit(score_text,
                         (left_center_x - score_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2 - 40))

        # 最终等级
        level_text = self.font.render(f'Final Level: {self.level}', True, self.YELLOW)
        self.screen.blit(level_text,
                         (left_center_x - level_text.get_width() // 2,
                          self.SCREEN_HEIGHT // 2))

        # 右侧区域：按钮
        right_area_width = self.SCREEN_WIDTH // 2
        right_area_start_x = divider_x
        right_center_x = right_area_start_x + right_area_width // 2

        # 按钮布局
        button_width = 220
        button_height = 50
        button_margin = 30

        # 计算第一个按钮的y坐标，使其垂直居中于右侧区域
        right_area_height = self.SCREEN_HEIGHT - 300  # 留出上下边距
        total_buttons_height = button_height * 2 + button_margin
        first_button_y = 150 + (right_area_height - total_buttons_height) // 2

        # 重新开始按钮
        restart_button_rect = pygame.Rect(
            right_center_x - button_width // 2,
            first_button_y,
            button_width,
            button_height
        )
        self.restart_button_rect = self.draw_button(
            restart_button_rect,
            "PLAY AGAIN",
            self.BUTTON_GREEN_NORMAL,
            self.BUTTON_GREEN_HOVER,
            self.restart_button_hover,
            font_size=30
        )

        # 退出按钮
        exit_button_rect = pygame.Rect(
            right_center_x - button_width // 2,
            first_button_y + button_height + button_margin,
            button_width,
            button_height
        )
        self.exit_button_rect = self.draw_button(
            exit_button_rect,
            "EXIT TO LAUNCHER",
            self.BUTTON_RED_NORMAL,
            self.BUTTON_RED_HOVER,
            self.exit_button_hover,
            font_size=26
        )

        # 键盘提示（小字提示，放在底部）
        hint_font = pygame.font.SysFont(None, 20)
        hint_text = "(You can also press R to restart or ESC to exit)"
        hint_surface = hint_font.render(hint_text, True, (150, 150, 150))
        self.screen.blit(hint_surface,
                         (self.SCREEN_WIDTH // 2 - hint_surface.get_width() // 2,
                          self.SCREEN_HEIGHT - 30))

    def reset_game(self):
        """重置游戏状态"""
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.player_x = self.SCREEN_WIDTH // 2
        self.player_y = self.SCREEN_HEIGHT - 80
        self.bullets.clear()
        self.enemies.clear()
        self.explosions.clear()
        self.enemy_speed = 3
        self.enemy_spawn_delay = 1000
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.last_shot_time = 0
        # 重置按钮悬停状态
        self.restart_button_hover = False
        self.exit_button_hover = False

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE and not self.game_over:
                        self.create_bullet()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        # 检查是否点击了重新开始按钮
                        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(mouse_pos):
                            self.reset_game()
                        # 检查是否点击了退出按钮
                        elif hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(mouse_pos):
                            running = False
                elif event.type == pygame.MOUSEMOTION:
                    # 更新按钮悬停状态
                    if self.game_over:
                        if hasattr(self, 'restart_button_rect'):
                            self.restart_button_hover = self.restart_button_rect.collidepoint(mouse_pos)
                        if hasattr(self, 'exit_button_rect'):
                            self.exit_button_hover = self.exit_button_rect.collidepoint(mouse_pos)

            # 获取按键状态（持续移动）
            keys = pygame.key.get_pressed()
            if not self.game_over:
                if keys[pygame.K_LEFT] and self.player_x > self.player_width // 2:
                    self.player_x -= self.player_speed
                if keys[pygame.K_RIGHT] and self.player_x < self.SCREEN_WIDTH - self.player_width // 2:
                    self.player_x += self.player_speed
                if keys[pygame.K_UP] and self.player_y > self.SCREEN_HEIGHT // 2:
                    self.player_y -= self.player_speed
                if keys[pygame.K_DOWN] and self.player_y < self.SCREEN_HEIGHT - self.player_height:
                    self.player_y += self.player_speed

                # 按住空格连续射击
                if keys[pygame.K_SPACE]:
                    self.create_bullet()

            # 更新游戏状态 - 只有在游戏未结束时才更新
            if not self.game_over:
                self.spawn_enemy()
                self.update_bullets()
                self.update_enemies()
                self.update_explosions()

            # 绘制游戏
            self.screen.fill(self.BLACK)  # 黑色背景

            # 绘制星空
            self.draw_stars()

            # 绘制游戏元素
            self.draw_bullets()
            self.draw_enemies()
            self.draw_explosions()
            self.create_player()

            # 绘制界面信息
            self.draw_hud()

            # 如果游戏结束，显示结束画面
            if self.game_over:
                self.draw_game_over()

            # 更新屏幕
            pygame.display.flip()

            # 控制帧率
            self.clock.tick(self.FPS)

        # 退出游戏
        pygame.quit()
        return


# 单独测试用
if __name__ == "__main__":
    game = PlaneShooter()
    game.run()