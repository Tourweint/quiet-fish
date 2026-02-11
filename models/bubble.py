"""气泡粒子模块"""
import pygame
import random
import math


class Bubble:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.size = random.randint(3, 8)
        self.speed = random.uniform(20, 45)
        self.wobble_offset = random.uniform(0, math.pi * 2)

    def update(self, dt, water_top):
        self.y -= self.speed * dt
        self.x += math.sin(self.y * 0.03 + self.wobble_offset) * 0.8

    def draw(self, surface, water_top):
        if self.y < water_top:
            return False
        # 气泡外圈
        pygame.draw.circle(surface, (200, 230, 255), (int(self.x), int(self.y)), self.size, 1)
        # 高光
        highlight = max(1, self.size // 4)
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(self.x - self.size * 0.3), int(self.y - self.size * 0.3)), highlight)
        return True
