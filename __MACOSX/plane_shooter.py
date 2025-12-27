import pygame
import random
import math
import sys

class PlaneShooter:
    def __init__(self):
        # 初始化pygame（注意：如果游戏盒子已初始化，这里可能会重复，但通常无害）
        pygame.init()
        # 以下将原全局变量定义为实例属性
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Plane Shooter - Use Arrow Keys, Space | ESC to Exit')
        self.icon = pygame.image.load('ufo.png')
        pygame.display.set_icon(self.icon)

        # 加载素材
        self.bgImg = pygame.image.load('bg.png')
        self.playerImg = pygame.image.load('player.png')
        self.enemy_img = pygame.image.load('enemy.png')  # 注意：类内部变量名与之前Enemy类内的属性名区分开
        self.bullet_img = pygame.image.load('bullet.png')

        # 加载音频
        pygame.mixer.music.load('bg.wav')
        self.bao_sound = pygame.mixer.Sound('exp.wav')

        # 游戏状态变量
        self.score = 0
        self.is_over = False
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.over_font = pygame.font.Font('freesansbold.ttf', 64)

        # 玩家属性
        self.playerX = 400
        self.playerY = 500
        self.playerStep = 0

        # 初始化敌人和子弹容器
        self.number_of_enemies = 6
        self.enemies = []
        self.bullets = []
        self.reset_game()  # 调用重置来初始化敌人

    # ---------------------- 辅助函数 ----------------------
    def distance(self, bx, by, ex, ey):
        a = bx - ex
        b = by - ey
        return math.sqrt(a * a + b * b)

    def show_score(self):
        text = f'Score: {self.score}'
        score_render = self.font.render(text, True, (255, 0, 0))
        self.screen.blit(score_render, (10, 10))

    def check_is_over(self):
        if self.is_over:
            text = "Game Over"
            render = self.over_font.render(text, True, (255, 0, 0))
            self.screen.blit(render, (200, 250))

    def move_player(self):
        self.playerX += self.playerStep
        if self.playerX > 736:  # 800 - 64 (假设图片宽度)
            self.playerX = 736
        if self.playerX < 0:
            self.playerX = 0

    # ---------------------- 敌人类 ----------------------
    class Enemy:
        def __init__(self, outer):  # 传入外部类的引用以使用共享资源
            self.outer = outer
            self.img = outer.enemy_img  # 使用外部类加载的图片
            self.x = random.randint(200, 600)
            self.y = random.randint(50, 250)
            self.step = random.randint(2, 6)

        def reset(self):
            self.x = random.randint(200, 600)
            self.y = random.randint(50, 200)

        def move(self):
            self.x += self.step
            if self.x > 736 or self.x < 0:
                self.step *= -1
                self.y += 40
                if self.y > 450:
                    self.outer.is_over = True

    def show_enemies(self):
        for e in self.enemies:
            self.screen.blit(e.img, (e.x, e.y))
            e.move()  # 调用敌人的移动方法

    # ---------------------- 子弹类 ----------------------
    class Bullet:
        def __init__(self, outer, playerX, playerY):
            self.outer = outer
            self.img = outer.bullet_img
            self.x = playerX + 16
            self.y = playerY + 10
            self.step = 10

        def hit(self):
            for e in self.outer.enemies:
                if self.outer.distance(self.x, self.y, e.x, e.y) < 30:
                    self.outer.bao_sound.play()
                    # 从外部类的子弹列表中移除自己需要一些技巧，这里我们让外部类处理
                    self.outer.bullets_to_remove.append(self)
                    e.reset()
                    self.outer.score += 1
                    return True  # 表示击中
            return False

        def update(self):
            self.y -= self.step
            # 如果子弹飞出屏幕，标记为待移除
            if self.y < 0 or self.hit():  # 如果击中，也由外部逻辑处理移除
                self.outer.bullets_to_remove.append(self)

    def show_bullets(self):
        # 先更新所有子弹
        for b in self.bullets:
            b.update()
        # 移除需要删除的子弹
        for b in self.bullets_to_remove:
            if b in self.bullets:
                self.bullets.remove(b)
        self.bullets_to_remove.clear()  # 清空待移除列表
        # 绘制所有子弹
        for b in self.bullets:
            self.screen.blit(b.img, (b.x, b.y))

    # ---------------------- 游戏控制 ----------------------
    def reset_game(self):
        """重置游戏状态"""
        self.score = 0
        self.is_over = False
        self.playerX = 400
        self.playerY = 500
        self.playerStep = 0
        self.enemies.clear()
        for i in range(self.number_of_enemies):
            self.enemies.append(self.Enemy(self))  # 创建内部类实例时传入self
        self.bullets.clear()
        self.bullets_to_remove = []  # 用于临时存储待移除子弹

    def run(self):
        """游戏主循环，这是被游戏盒子调用的入口"""
        # 确保游戏状态重置
        self.reset_game()
        # 播放背景音乐（循环）
        pygame.mixer.music.play(-1)

        clock = pygame.time.Clock()
        running = True

        while running:
            # 1. 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False  # ESC键退出游戏，返回启动器
                    elif event.key == pygame.K_r and self.is_over:
                        self.reset_game()  # 游戏结束后按R键重来
                    elif not self.is_over:
                        if event.key == pygame.K_RIGHT:
                            self.playerStep = 5
                        elif event.key == pygame.K_LEFT:
                            self.playerStep = -5
                        elif event.key == pygame.K_SPACE:
                            # 创建一颗子弹
                            self.bullets.append(self.Bullet(self, self.playerX, self.playerY))
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                        self.playerStep = 0

            # 2. 更新游戏状态
            self.move_player()

            # 3. 绘制
            self.screen.blit(self.bgImg, (0, 0))
            self.screen.blit(self.playerImg, (self.playerX, self.playerY))
            self.show_enemies()
            self.show_bullets()
            self.show_score()
            self.check_is_over()

            pygame.display.update()
            clock.tick(60)  # 控制帧率

        # 循环结束，清理并退出
        pygame.mixer.music.stop()
        pygame.quit()
        # 注意：这里不调用sys.exit()，因为我们要返回启动器


# 以下代码用于单独测试这个游戏
if __name__ == "__main__":
    game = PlaneShooter()
    game.run()