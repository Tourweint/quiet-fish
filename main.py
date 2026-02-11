"""
自习安静养鱼神器
声音越大，鱼跑得越多
"""

import pygame
import pyaudio
import math
import random
import time
from collections import deque

# ============ 配置 ============
WIDTH, HEIGHT = 800, 600
FPS = 60
BG_COLOR = (20, 30, 50)  # 深蓝色背景
WATER_COLOR = (30, 60, 100)
FISH_COLORS = [(255, 180, 50), (255, 100, 100), (100, 200, 255), (255, 150, 200)]

# 声音阈值配置
SILENCE_THRESHOLD = 500  # 安静阈值
MAX_FISH = 20            # 最大鱼数
MIN_FISH = 0             # 最小鱼数
FISH_FLEE_SPEED = 2.0    # 鱼逃跑速度系数


def get_font(size=36):
    """获取支持中文的字体"""
    # 尝试多个中文字体
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
    ]
    for path in font_paths:
        try:
            return pygame.font.Font(path, size)
        except:
            continue
    # 如果都找不到，回退到默认字体
    return pygame.font.Font(None, size)


# ============ 音频处理 =========---
class AudioMonitor:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        self.volume_history = deque(maxlen=30)  # 平滑处理

    def get_volume(self):
        """获取当前麦克风音量 (0-100)"""
        try:
            data = self.stream.read(1024, exception_on_overflow=False)
            samples = list(data)
            rms = math.sqrt(sum(s*s for s in samples) / len(samples))
            volume = min(100, int(rms / 50))  # 归一化到 0-100
            self.volume_history.append(volume)
            return sum(self.volume_history) / len(self.volume_history)
        except:
            return 0

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()


# ============ 鱼类 =========---
class Fish:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(100, HEIGHT - 50)
        self.speed = random.uniform(0.5, 1.5)
        self.direction = random.choice([-1, 1])
        self.color = random.choice(FISH_COLORS)
        self.size = random.randint(15, 25)
        self.wobble = random.uniform(0, math.pi * 2)
        self.is_fleeing = False
        self.flee_timer = 0

    def update(self, volume, dt):
        """更新鱼的状态"""
        self.wobble += 5 * dt

        if volume > SILENCE_THRESHOLD:
            self.is_fleeing = True
            self.flee_timer = 1.0
        elif self.flee_timer > 0:
            self.flee_timer -= dt
        else:
            self.is_fleeing = False

        if self.is_fleeing:
            # 逃跑模式：向右/左快速游动
            self.x += self.speed * FISH_FLEE_SPEED * self.direction * 60 * dt
            self.y += random.uniform(-1, 1)
        else:
            # 正常游动：左右摆动
            self.x += self.speed * self.direction * 30 * dt
            self.y += math.sin(self.wobble) * 0.5

        # 边界检测
        if self.x > WIDTH + 30:
            self.x = -30
            self.y = random.randint(100, HEIGHT - 50)
            self.direction = 1
        elif self.x < -30:
            self.x = WIDTH + 30
            self.y = random.randint(100, HEIGHT - 50)
            self.direction = -1

    def draw(self, surface):
        """绘制鱼"""
        # 身体
        pygame.draw.ellipse(surface, self.color,
                          (self.x, self.y - self.size//2,
                           self.size * 1.5, self.size))

        # 尾巴
        tail_x = self.x - (self.size * 0.8 if self.direction > 0 else -self.size * 0.3)
        tail_points = [
            (self.x - (self.size * 0.7 if self.direction > 0 else -self.size * 0.3), self.y),
            (self.x - (self.size * 1.3 if self.direction > 0 else -self.size * 0.7), self.y - self.size//2),
            (self.x - (self.size * 1.3 if self.direction > 0 else -self.size * 0.7), self.y + self.size//2)
        ]
        pygame.draw.polygon(surface, self.color, tail_points)

        # 眼睛
        eye_x = self.x + (self.size * 0.5 if self.direction > 0 else -self.size * 0.2)
        pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(self.y - 3)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x + (1 if self.direction > 0 else -1)), int(self.y - 3)), 2)


# ============ 主程序 ============
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("安静养鱼 - 自习神器")
    clock = pygame.time.Clock()
    font = get_font(36)

    # 初始化音频
    audio = AudioMonitor()
    fish_list = [Fish() for _ in range(10)]  # 初始 10 条鱼

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # 帧时间

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 获取音量
        volume = audio.get_volume()

        # 根据音量调整鱼数量
        target_fish = MIN_FISH + int((MAX_FISH - MIN_FISH) * (1 - volume / 150))
        target_fish = max(MIN_FISH, min(MAX_FISH, target_fish))

        # 补充或移除鱼
        while len(fish_list) < target_fish:
            fish_list.append(Fish())
        while len(fish_list) > target_fish:
            fish_list.pop()

        # 更新所有鱼
        for fish in fish_list:
            fish.update(volume, dt)

        # 绘制
        screen.fill(BG_COLOR)

        # 水背景
        pygame.draw.rect(screen, WATER_COLOR, (0, 80, WIDTH, HEIGHT - 80))

        # 画水草装饰
        for i in range(0, WIDTH, 60):
            height = 80 + 20 * math.sin(time.time() * 2 + i)
            pygame.draw.line(screen, (30, 100, 60), (i, HEIGHT), (i + 10, height), 4)

        # 画鱼
        for fish in fish_list:
            fish.draw(screen)

        # UI 显示
        vol_text = font.render(f"音量: {volume:.0f}", True, (255, 255, 255))
        fish_text = font.render(f"鱼: {len(fish_list)}/{MAX_FISH}", True, (255, 255, 255))
        screen.blit(vol_text, (20, 20))
        screen.blit(fish_text, (20, 55))

        # 安静提示
        if volume < SILENCE_THRESHOLD:
            hint = font.render("好安静，鱼儿都在~", True, (100, 255, 150))
        else:
            hint = font.render("太吵了！鱼都跑了！", True, (255, 100, 100))
        screen.blit(hint, (WIDTH - 300, 20))

        pygame.display.flip()

    audio.close()
    pygame.quit()


if __name__ == "__main__":
    main()
