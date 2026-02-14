"""鱼类模块"""
import pygame
import random
import math
import time

from config import (
    RARITY, RARITY_WEIGHTS, WIDTH, HEIGHT, 
    SILENCE_THRESHOLD, FISH_FLEE_SPEED, FISH_GLOW_AGE_THRESHOLD
)


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

        # 使用预计算的权重列表快速选择稀有度
        self.rarity = random.choice(RARITY_WEIGHTS)
        data = RARITY[self.rarity]

        self.color = random.choice(data["colors"])
        self.size = random.randint(*data["size"])
        self.speed = random.uniform(0.4, 0.7) * data["speed"]
        self.threshold_mult = data["threshold"]
        self.has_glow = data["glow"]
        self.glow_color = data.get("glow_color", (255, 255, 255, 100))
        self.points = data.get("points", 10)
        
        # 动画参数
        self.tail_phase = random.uniform(0, math.pi * 2)
        self.fin_phase = random.uniform(0, math.pi * 2)

    def update(self, volume, dt, water_top):
        self.age += dt
        self.wobble += 4 * dt
        self.tail_phase += 8 * dt  # 尾巴摆动
        self.fin_phase += 6 * dt   # 鳍摆动

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
        size = self.size
        d = 1 if self.direction > 0 else -1
        
        # 计算摆动
        tail_wag = math.sin(self.tail_phase) * 8
        fin_wag = math.sin(self.fin_phase) * 3
        
        # 发光效果
        if self.has_glow and self.age > FISH_GLOW_AGE_THRESHOLD:
            glow_size = size * 2.5
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            # 多层发光
            for layer in range(3):
                layer_alpha = self.glow_color[3] // (layer + 1)
                layer_size = glow_size * (1 + layer * 0.3)
                glow_color = (*self.glow_color[:3], layer_alpha)
                pygame.draw.ellipse(glow_surf, glow_color,
                                   (glow_size * 0.3, glow_size * 0.3, 
                                    glow_size * 1.4 - layer * 10, 
                                    glow_size * 1.4 - layer * 10))
            surface.blit(glow_surf, (self.x - glow_size * 0.8, self.y - glow_size * 0.8))

        # 背鳍 - 带摆动
        fin_base_x = self.x + size * 0.2 * d
        fin_tip_x = fin_base_x + size * 0.5 * d + tail_wag * 0.3 * d
        fin_points = [
            (self.x + size * 0.3 * d, self.y),
            (fin_tip_x, self.y - size * 0.7 + fin_wag * d),
            (self.x + size * 0.1 * d, self.y + size * 0.15)
        ]
        pygame.draw.polygon(surface, self._darken_color(self.color, 30), fin_points)

        # 身体 - 使用渐变效果
        body_width = size * 1.7
        body_height = size * 0.9
        body_x = self.x - body_width // 2 + tail_wag * 0.2 * d
        body_y = self.y - body_height // 2

        # 绘制渐变身体（从上到下渐变）
        self._draw_gradient_body(surface, body_x, body_y, body_width, body_height, self.color, d)

        # 身体高光（让鱼看起来更有立体感）
        highlight_rect = (
            self.x - body_width // 3 + tail_wag * 0.2 * d,
            self.y - body_height // 3,
            body_width // 2,
            body_height // 3
        )
        highlight_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.ellipse(surface, highlight_color, highlight_rect)

        # 鱼鳞纹理效果
        self._draw_scales(surface, body_x, body_y, body_width, body_height, self.color, d)

        # 尾巴 - 带摆动动画
        tail_base_x = self.x - size * 0.7 * d
        tail_points = [
            (tail_base_x, self.y),
            (tail_base_x - size * 1.0 * d + tail_wag, self.y - size * 0.7),
            (tail_base_x - size * 1.2 * d + tail_wag * 1.5, self.y),
            (tail_base_x - size * 1.0 * d + tail_wag, self.y + size * 0.7)
        ]
        pygame.draw.polygon(surface, self._darken_color(self.color, 15), tail_points)

        # 腮红 - 侧边
        cheek_x = self.x + size * 0.5 * d
        cheek_rect = (cheek_x - size * 0.2, self.y - size * 0.1, size * 0.3, size * 0.25)
        cheek_color = (255, 130, 130, 80)
        pygame.draw.ellipse(surface, cheek_color, cheek_rect)

        # 眼睛
        eye_x = self.x + size * 0.55 * d
        eye_size = max(4, size // 4)
        
        # 眼白
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(self.y - 2)), eye_size)
        
        # 瞳孔
        pupil_x = eye_x + size * 0.08 * d
        pygame.draw.circle(surface, (20, 20, 40), (int(pupil_x), int(self.y - 2)), eye_size // 2)
        
        # 眼神高光
        pygame.draw.circle(surface, (255, 255, 255), 
                          (int(pupil_x + size * 0.05 * d), int(self.y - 4)), eye_size // 4)

        # 胸鳍 - 带摆动
        fin_start_x = self.x + size * 0.1 * d
        fin_points = [
            (fin_start_x, self.y + size * 0.2),
            (fin_start_x + size * 0.4 * d + fin_wag * d, self.y + size * 0.5),
            (fin_start_x + size * 0.1 * d, self.y + size * 0.4)
        ]
        pygame.draw.polygon(surface, self._darken_color(self.color, 25), fin_points)

        # 腹鳍
        belly_x = self.x - size * 0.2 * d
        belly_points = [
            (belly_x, self.y + size * 0.35),
            (belly_x + size * 0.25 * d, self.y + size * 0.55),
            (belly_x - size * 0.1 * d, self.y + size * 0.5)
        ]
        pygame.draw.polygon(surface, self._darken_color(self.color, 35), belly_points)

    def _darken_color(self, color, amount):
        """使颜色变暗"""
        return tuple(max(0, c - amount) for c in color)

    def _lighten_color(self, color, amount):
        """使颜色变亮"""
        return tuple(min(255, c + amount) for c in color)

    def _draw_gradient_body(self, surface, x, y, width, height, color, direction):
        """绘制渐变色鱼身体"""
        # 创建渐变表面
        body_surf = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)

        # 顶部颜色（较亮）
        top_color = self._lighten_color(color, 30)
        # 底部颜色（较暗）
        bottom_color = self._darken_color(color, 20)

        # 垂直渐变
        for row in range(int(height)):
            ratio = row / height
            # 线性插值
            grad_color = tuple(
                int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
                for i in range(3)
            )
            pygame.draw.line(body_surf, grad_color, (0, row), (width, row))

        # 裁剪成椭圆形状
        mask = pygame.Surface((int(width), int(height)), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, width, height))
        body_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(body_surf, (int(x), int(y)))

    def _draw_scales(self, surface, x, y, width, height, color, direction):
        """绘制鱼鳞纹理"""
        scale_color = (*self._lighten_color(color, 40)[:3], 40)  # 半透明的亮色
        scale_size = min(width, height) * 0.12

        # 只绘制部分鱼鳞，避免太密集
        rows = 3
        cols = 4
        for row in range(rows):
            for col in range(cols):
                # 交错排列
                offset_x = (row % 2) * (scale_size * 0.5)
                scale_x = x + width * 0.2 + col * scale_size * 1.2 + offset_x
                scale_y = y + height * 0.25 + row * scale_size * 0.8

                # 确保在身体范围内
                if scale_x + scale_size < x + width * 0.8 and scale_y + scale_size < y + height * 0.8:
                    # 绘制单个鱼鳞（小椭圆）
                    scale_rect = (
                        int(scale_x),
                        int(scale_y),
                        int(scale_size),
                        int(scale_size * 0.6)
                    )
                    pygame.draw.ellipse(surface, scale_color, scale_rect)
