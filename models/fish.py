"""鱼类模块"""
import pygame
import random
import math
import time
from config import RARITY, WIDTH, HEIGHT, SILENCE_THRESHOLD, FISH_FLEE_SPEED


class Fish:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(130, HEIGHT - 80)
        self.direction = random.choice([-1, 1])
        self.wobble = random.uniform(0, math.pi * 2)
        self.is_fleeing = False
        self.flee_timer = 0
        self.spawn_time = time.time()
        self.age = 0  # 在屏幕上的时间（秒）

        # 按权重选择稀有度
        rand = random.randint(1, 100)
        cumulative = 0
        rarity_key = "common"
        for key, data in RARITY.items():
            cumulative += data["weight"]
            if rand <= cumulative:
                rarity_key = key
                break

        self.rarity = rarity_key
        data = RARITY[rarity_key]

        self.color = random.choice(data["colors"])
        self.size = random.randint(*data["size"])
        self.speed = random.uniform(0.4, 0.7) * data["speed"]
        self.threshold_mult = data["threshold"]
        self.has_glow = data["glow"]
        self.glow_color = data.get("glow_color", (255, 255, 255, 100))
        self.points = data.get("points", 10)

    def update(self, volume, dt, water_top):
        self.age += dt
        self.wobble += 4 * dt

        threshold = SILENCE_THRESHOLD * self.threshold_mult

        if volume > threshold:
            self.is_fleeing = True
            self.flee_timer = 2.0
        elif self.flee_timer > 0:
            self.flee_timer -= dt
        else:
            self.is_fleeing = False

        if self.is_fleeing:
            self.x += self.speed * FISH_FLEE_SPEED * self.direction * 60 * dt
            self.y += random.uniform(-0.8, 0.8)
        else:
            self.x += self.speed * self.direction * 30 * dt
            self.y += math.sin(self.wobble) * 0.25

        # 边界检测
        if self.x > WIDTH + 60:
            self.x = -60
            self.y = random.randint(int(water_top + 40), HEIGHT - 80)
            self.direction = 1
        elif self.x < -60:
            self.x = WIDTH + 60
            self.y = random.randint(int(water_top + 40), HEIGHT - 80)
            self.direction = -1

    def draw(self, surface):
        # 发光效果
        if self.has_glow and self.age > 0.3:
            glow_size = self.size * 2.2
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, self.glow_color,
                               (glow_size * 0.3, glow_size * 0.3, glow_size * 1.4, glow_size * 1.4))
            surface.blit(glow_surf, (self.x - glow_size * 0.8, self.y - glow_size * 0.8))

        # 背鳍
        fin_x = self.x + (self.size * 0.3 if self.direction > 0 else -self.size * 0.8)
        fin_points = [
            (self.x + (self.size * 0.5 if self.direction > 0 else -self.size * 1.0), self.y),
            (fin_x, self.y - self.size * 0.65),
            (self.x + (self.size * 0.1 if self.direction > 0 else -self.size * 0.6), self.y + self.size * 0.2)
        ]
        pygame.draw.polygon(surface, self.color, fin_points)

        # 身体
        body_rect = (self.x, self.y - self.size//2, self.size * 1.6, self.size)
        pygame.draw.ellipse(surface, self.color, body_rect)

        # 尾巴
        tail_offset = self.size * 0.8 if self.direction > 0 else -self.size * 0.4
        tail_x = self.x - tail_offset
        tail_points = [
            (self.x - (self.size * 0.5 if self.direction > 0 else -self.size * 0.2), self.y),
            (self.x - (self.size * 1.45 if self.direction > 0 else -self.size * 1.15), self.y - self.size * 0.75),
            (self.x - (self.size * 1.45 if self.direction > 0 else -self.size * 1.15), self.y + self.size * 0.75)
        ]
        pygame.draw.polygon(surface, self.color, tail_points)

        # 腮红
        cheek_x = self.x + (self.size * 0.65 if self.direction > 0 else -self.size * 0.35)
        pygame.draw.ellipse(surface, (255, 150, 150, 100),
                           (cheek_x - self.size * 0.2, self.y - self.size * 0.1, self.size * 0.35, self.size * 0.28))

        # 眼睛
        eye_x = self.x + (self.size * 0.75 if self.direction > 0 else -self.size * 0.1)
        eye_size = max(4, self.size // 5)
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(self.y - 2)), eye_size)
        pupil_offset = 1 if self.direction > 0 else -1
        pygame.draw.circle(surface, (30, 30, 50), (int(eye_x + pupil_offset), int(self.y - 2)), eye_size // 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x + pupil_offset * 1.5), int(self.y - 4)), eye_size // 4)

        # 腹鳍
        belly_x = self.x + (self.size * 0.2 if self.direction > 0 else -self.size * 0.7)
        belly_points = [
            (belly_x, self.y + self.size * 0.2),
            (belly_x + (self.size * 0.35 if self.direction > 0 else -self.size * 0.35), self.y + self.size * 0.55),
            (belly_x, self.y + self.size * 0.45)
        ]
        pygame.draw.polygon(surface, [max(0, c - 35) for c in self.color], belly_points)
