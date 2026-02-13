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
    ACHIEVEMENTS, FISH_INITIAL_COUNT, FISH_BUBBLE_CHANCE,
    BUBBLE_SPAWN_CHANCE, NIGHT_START_HOUR, NIGHT_END_HOUR,
    RARITY, FISH_RARITY_WEIGHT, BASE_WEIGHT_INTERVAL,
    VOLUME_ADD_MULTIPLIER, VOLUME_REMOVE_MULTIPLIER
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
        
        # 权重系统：记录每种鱼的累计权重值
        self.fish_weights = {rarity: 0.0 for rarity in RARITY.keys()}
        self.last_weight_update = time.time()

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

        # 预计算随机边界，减少每帧计算
        self._bubble_x_range = (100, WIDTH - 100)
        self._bubble_small_x_range = (50, WIDTH - 50)

        # 初始鱼 - 只生成普通或稀有（不会出现史诗及以上）
        for _ in range(FISH_INITIAL_COUNT):
            fish = self._create_initial_fish()
            self.fish_list.append(fish)

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

    def _create_initial_fish(self):
        """创建初始鱼 - 只可能是普通或稀有"""
        import random
        # 只从普通和稀有中选择
        initial_rarities = ["common", "rare"]
        # 普通概率 70%，稀有概率 30%
        rarity = random.choices(initial_rarities, weights=[70, 30])[0]
        
        # 创建鱼并强制设置稀有度
        fish = Fish()
        fish.rarity = rarity
        data = RARITY[rarity]
        fish.color = random.choice(data["colors"])
        fish.size = random.randint(*data["size"])
        fish.speed = random.uniform(0.4, 0.7) * data["speed"]
        fish.threshold_mult = data["threshold"]
        fish.has_glow = data["glow"]
        fish.glow_color = data.get("glow_color", (255, 255, 255, 100))
        fish.points = data.get("points", 10)
        
        return fish

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

        # ========== 权重系统：基于权重的鱼数量动态调整 ==========
        fish_list = self.fish_list
        stats = self.stats
        
        # 计算时间差
        now = time.time()
        time_delta = now - self.last_weight_update
        self.last_weight_update = now
        
        # 根据声音计算加权/减权速度
        normalized_volume = min(1.0, volume / 100)  # 归一化到 0-1
        
        # 安静度：0-1，越安静越接近1
        quietness = 1 - (normalized_volume ** 0.5)
        
        # 计算净权重变化速度
        # 安静时：加权 > 减权，净增加
        # 吵闹时：减权 > 加权，净减少
        if quietness > 0.5:
            # 安静环境：慢慢积累鱼
            add_speed = quietness * VOLUME_ADD_MULTIPLIER
            remove_speed = (1 - quietness) * 0.3  # 减权很慢
        else:
            # 吵闹环境：快速失去鱼
            add_speed = quietness * 0.2  # 加权很慢
            remove_speed = (1 - quietness) * VOLUME_REMOVE_MULTIPLIER
        
        net_weight_change = (add_speed - remove_speed) * time_delta * 10  # 缩放因子
        
        # 更新每种鱼的权重
        for rarity in self.fish_weights:
            rarity_weight = FISH_RARITY_WEIGHT[rarity]
            # 权重高的鱼变化更快
            self.fish_weights[rarity] += net_weight_change * rarity_weight
            # 限制权重范围
            self.fish_weights[rarity] = max(-5, min(10, self.fish_weights[rarity]))
        
        # 统计当前各稀有度鱼的数量
        rarity_counts = {r: 0 for r in RARITY.keys()}
        for fish in fish_list:
            rarity_counts[fish.rarity] += 1
        
        # 计算目标鱼数量（基于安静度）
        target_total = MIN_FISH + int((MAX_FISH - MIN_FISH) * quietness)
        
        # === 加鱼逻辑：权重达到阈值时添加 ===
        if len(fish_list) < target_total and net_weight_change > 0:
            for rarity in ["common", "rare", "epic", "legendary", "mythic"]:
                threshold = BASE_WEIGHT_INTERVAL / FISH_RARITY_WEIGHT[rarity]
                if self.fish_weights[rarity] >= threshold:
                    # 权重足够，添加一条该稀有度的鱼
                    fish = Fish()
                    # 强制设置稀有度
                    fish.rarity = rarity
                    data = RARITY[rarity]
                    fish.color = random.choice(data["colors"])
                    fish.size = random.randint(*data["size"])
                    fish.speed = random.uniform(0.4, 0.7) * data["speed"]
                    fish.threshold_mult = data["threshold"]
                    fish.has_glow = data["glow"]
                    fish.glow_color = data.get("glow_color", (255, 255, 255, 100))
                    fish.points = data.get("points", 10)
                    
                    fish_list.append(fish)
                    stats.record_fish(fish)
                    self.fish_weights[rarity] -= threshold  # 消耗权重
                    
                    # 偶尔生成气泡
                    if random.random() < FISH_BUBBLE_CHANCE:
                        self.bubbles.append(Bubble(
                            random.randint(*self._bubble_x_range),
                            HEIGHT, WIDTH
                        ))
                    break  # 每帧最多加一条鱼
        
        # === 减鱼逻辑：权重为负时优先移除高品质鱼 ===
        elif len(fish_list) > MIN_FISH and net_weight_change < 0:
            # 按稀有度从高到低检查（优先移除高品质鱼）
            for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
                threshold = -BASE_WEIGHT_INTERVAL / FISH_RARITY_WEIGHT[rarity] * 0.5
                if self.fish_weights[rarity] <= threshold and rarity_counts[rarity] > 0:
                    # 找到并移除该稀有度的鱼
                    for i, fish in enumerate(fish_list):
                        if fish.rarity == rarity:
                            fish_list.pop(i)
                            self.fish_weights[rarity] -= threshold  # 消耗权重（变得更正）
                            break
                    break  # 每帧最多减一条鱼

        # 更新鱼
        for fish in fish_list:
            fish.update(volume, dt, WATER_TOP)

        # 更新气泡
        self.bubbles = [b for b in self.bubbles if b.draw(self.screen, WATER_TOP)]
        if random.random() < BUBBLE_SPAWN_CHANCE:
            self.bubbles.append(Bubble(
                random.randint(*self._bubble_small_x_range),
                HEIGHT, WIDTH
            ))

        # 检查成就 - 缓存当前时间
        current_hour = datetime.now().hour
        is_night = current_hour >= NIGHT_START_HOUR or current_hour < NIGHT_END_HOUR
        quiet_hours = stats.stats["total_quiet_seconds"] / 3600
        
        new_achs = stats.check_achievements(len(fish_list), quiet_hours, is_night)
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

        # 水面渐变 - 使用预计算颜色减少每帧计算
        water_height = HEIGHT - WATER_TOP
        for y in range(WATER_TOP, HEIGHT, 3):
            ratio = (y - WATER_TOP) / water_height
            color = (
                int(30 + ratio * 25),
                int(80 + ratio * 40),
                int(130 + ratio * 50)
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y), 3)

        # 水草
        current_time = time.time()
        for i in range(0, WIDTH, 90):
            base_height = WATER_TOP + 15 + 12 * (i % 3)
            sway = math.sin(current_time * 1.5 + i * 0.08) * 18
            points = [
                (i + 20, HEIGHT),
                (i + 28 + sway, HEIGHT - 70),
                (i + 35 + sway * 1.6, base_height)
            ]
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
