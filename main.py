"""
安静养鱼 - 自习神器
主程序入口
"""

import pygame
import random
import math
import time
from datetime import datetime

# 导入配置
from config import (
    WIDTH, HEIGHT, FPS, BG_COLOR, WATER_TOP,
    SILENCE_THRESHOLD, MAX_FISH, MIN_FISH,
    POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES,
    ACHIEVEMENTS
)

# 导入模块
from models.audio import AudioMonitor
from models.fish import Fish
from models.bubble import Bubble
from models.stats import StatsManager
from ui.font_manager import FontManager
from ui.panel import UIPanel


class QuietFishApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("安静养鱼 - 自习神器")
        self.clock = pygame.time.Clock()

        # 初始化模块
        self.font_manager = FontManager()
        self.ui = UIPanel(self.font_manager)
        self.audio = AudioMonitor()
        self.stats = StatsManager()

        # 游戏状态
        self.fish_list = []
        self.bubbles = []
        self.quiet_time_this_session = 0
        self.last_time = time.time()
        self.is_quiet = True

        # 番茄钟状态
        self.pomodoro = {
            "active": False,
            "is_break": False,
            "start_time": 0,
            "end_time": 0
        }

        # 成就通知
        self.new_achievements = []
        self.achievement_flash_timer = 0

        # 检查连续天数
        self.stats.check_streak()

        # 初始鱼
        for _ in range(6):
            self.fish_list.append(Fish())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.toggle_pomodoro()
                elif event.key == pygame.K_s:
                    self.save_screenshot()

        return True

    def toggle_pomodoro(self):
        """切换番茄钟"""
        now = pygame.time.get_ticks()
        if self.pomodoro["active"]:
            # 停止番茄钟
            self.pomodoro["active"] = False
            self.pomodoro["is_break"] = False
        else:
            # 开始工作番茄钟
            self.pomodoro["active"] = True
            self.pomodoro["is_break"] = False
            self.pomodoro["start_time"] = now
            self.pomodoro["end_time"] = now + POMODORO_WORK_MINUTES * 60 * 1000

    def check_pomodoro_complete(self):
        """检查番茄钟是否完成"""
        if not self.pomodoro["active"]:
            return

        now = pygame.time.get_ticks()
        if now >= self.pomodoro["end_time"]:
            if self.pomodoro["is_break"]:
                # 休息结束，回到工作
                self.pomodoro["is_break"] = False
                self.pomodoro["start_time"] = now
                self.pomodoro["end_time"] = now + POMODORO_WORK_MINUTES * 60 * 1000
            else:
                # 工作结束
                self.stats.record_pomodoro()
                self.new_achievements.append("focus_warrior")
                self.achievement_flash_timer = 2.0
                # 开始休息
                self.pomodoro["is_break"] = True
                self.pomodoro["start_time"] = now
                self.pomodoro["end_time"] = now + POMODORO_BREAK_MINUTES * 60 * 1000

    def save_screenshot(self):
        """保存截图"""
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pygame.image.save(self.screen, filename)

    def update(self, dt):
        # 获取音量
        volume = self.audio.get_volume()
        self.is_quiet = volume < SILENCE_THRESHOLD

        # 安静时间统计
        if self.is_quiet:
            self.quiet_time_this_session += dt
            self.stats.record_quiet_time(dt)

        # 番茄钟检查
        self.check_pomodoro_complete()

        # 根据音量调整鱼数量
        target_fish = MIN_FISH + int((MAX_FISH - MIN_FISH) * (1 - volume / 150))
        target_fish = max(MIN_FISH, min(MAX_FISH, target_fish))

        # 补充或移除鱼
        while len(self.fish_list) < target_fish:
            fish = Fish()
            self.fish_list.append(fish)
            self.stats.record_fish(fish)
            # 偶尔生成气泡
            if random.random() < 0.25:
                self.bubbles.append(Bubble(random.randint(100, WIDTH-100), HEIGHT, WIDTH))

        while len(self.fish_list) > target_fish:
            self.fish_list.pop()

        # 更新鱼
        for fish in self.fish_list:
            fish.update(volume, dt, WATER_TOP)

        # 更新气泡
        self.bubbles = [b for b in self.bubbles if b.draw(self.screen, WATER_TOP)]
        if random.random() < 0.015:
            self.bubbles.append(Bubble(random.randint(50, WIDTH-50), HEIGHT, WIDTH))

        # 检查成就
        is_night = 23 <= datetime.now().hour <= 6 or 0 <= datetime.now().hour < 6
        quiet_hours = self.stats.stats["total_quiet_seconds"] / 3600
        new_achs = self.stats.check_achievements(len(self.fish_list), quiet_hours, is_night)
        if new_achs:
            self.new_achievements.extend(new_achs)
            self.achievement_flash_timer = 2.0

        # 更新成就通知计时
        if self.achievement_flash_timer > 0:
            self.achievement_flash_timer -= dt
            if self.achievement_flash_timer < 0:
                self.new_achievements = []

    def draw_background(self):
        """绘制背景"""
        self.screen.fill(BG_COLOR)

        # 水面渐变
        for y in range(WATER_TOP, HEIGHT, 3):
            ratio = (y - WATER_TOP) / (HEIGHT - WATER_TOP)
            color = (
                int(30 + ratio * 25),
                int(80 + ratio * 40),
                int(130 + ratio * 50)
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y), 3)

        # 水草
        for i in range(0, WIDTH, 90):
            base_height = WATER_TOP + 15 + 12 * (i % 3)
            sway = math.sin(time.time() * 1.5 + i * 0.08) * 18
            points = [(i + 20, HEIGHT), (i + 28 + sway, HEIGHT - 70),
                      (i + 35 + sway * 1.6, base_height)]
            pygame.draw.lines(self.screen, (45, 150, 90), False, points, 4)

    def draw(self):
        self.draw_background()

        # 画鱼
        for fish in self.fish_list:
            fish.draw(self.screen)

        # UI
        volume = self.audio.get_volume()
        self.ui.draw_stats_panel(self.screen, self.stats, volume, len(self.fish_list),
                                 self.is_quiet, self.pomodoro)
        self.ui.draw_fish_panel(self.screen, self.fish_list)
        self.ui.draw_pomodoro(self.screen, self.pomodoro)
        self.ui.draw_volume_meter(self.screen, volume)
        self.ui.draw_rarity_legend(self.screen)
        self.ui.draw_help(self.screen)

        # 成就通知
        if self.new_achievements and self.achievement_flash_timer > 0:
            self.ui.draw_achievements(self.screen, self.new_achievements, self.achievement_flash_timer / 2.0)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.last_time = time.time()

            running = self.handle_events()
            self.update(dt)
            self.draw()

        # 保存数据
        self.stats.save_stats()
        self.audio.close()
        pygame.quit()


def main():
    app = QuietFishApp()
    app.run()


if __name__ == "__main__":
    main()
