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
    VOLUME_ADD_MULTIPLIER, VOLUME_REMOVE_MULTIPLIER,
    AUDIO_MAX_VOLUME
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
        # 安静积分：用于计算加鱼的全局进度
        self.quiet_score = 0
        # 当前阶段需要的积分
        self.current_required_score = 10
        # 本次安静累计时间（秒）
        self.session_quiet_time = 0
        # 最大鱼数
        self.max_fish_limit = 50

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

        # 水面光斑效果初始化
        self.light_spots = []
        self._init_light_spots()

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

    def _init_light_spots(self):
        """初始化水面光斑"""
        import random
        for _ in range(8):
            self.light_spots.append({
                'x': random.randint(50, WIDTH - 50),
                'y': random.randint(WATER_TOP + 30, HEIGHT - 50),
                'size': random.randint(20, 50),
                'speed': random.uniform(5, 15),
                'phase': random.uniform(0, math.pi * 2),
                'alpha': random.randint(20, 40)
            })

    def _update_and_draw_light_spots(self, dt):
        """更新并绘制水面光斑"""
        current_time = time.time()
        for spot in self.light_spots:
            # 缓慢移动
            spot['x'] += math.sin(current_time * 0.5 + spot['phase']) * spot['speed'] * dt
            spot['y'] += math.cos(current_time * 0.3 + spot['phase']) * spot['speed'] * 0.5 * dt

            # 边界检查
            if spot['x'] < 0:
                spot['x'] = WIDTH
            elif spot['x'] > WIDTH:
                spot['x'] = 0
            if spot['y'] < WATER_TOP:
                spot['y'] = HEIGHT - 50
            elif spot['y'] > HEIGHT - 50:
                spot['y'] = WATER_TOP + 30

            # 呼吸效果
            breathe = math.sin(current_time * 2 + spot['phase']) * 0.3 + 1
            current_size = spot['size'] * breathe
            current_alpha = int(spot['alpha'] * (0.7 + 0.3 * math.sin(current_time + spot['phase'])))

            # 绘制光斑
            spot_surf = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            # 多层渐变
            for layer in range(3):
                layer_size = current_size * (1 - layer * 0.25)
                layer_alpha = current_alpha // (layer + 1)
                color = (255, 255, 220, layer_alpha)
                pygame.draw.ellipse(spot_surf, color,
                                   (current_size - layer_size, current_size - layer_size,
                                    layer_size * 2, layer_size * 2))
            self.screen.blit(spot_surf, (int(spot['x'] - current_size), int(spot['y'] - current_size)))

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
        was_quiet = self.is_quiet
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
        normalized_volume = min(1.0, volume / AUDIO_MAX_VOLUME)  # 归一化到 0-1

        # 安静度：0-1，越安静越接近1
        quietness = 1 - (normalized_volume ** 0.5)

        # 统计当前各稀有度鱼的数量
        rarity_counts = {r: 0 for r in RARITY.keys()}
        for fish in fish_list:
            rarity_counts[fish.rarity] += 1

        # 检测从吵闹恢复到安静的状态转换
        if self.is_quiet and not was_quiet:
            # 刚刚恢复安静，清零安静积分，但保留本次会话累计时间
            self.quiet_score = 0

        # 计算净权重变化速度
        # 安静时：慢慢积累权重
        # 吵闹时：快速失去鱼，权重清零
        if self.is_quiet:
            # 安静环境：慢慢积累权重
            # [可调整] 如需修改积分积累速度，参见 doc/fish_probability.md 第6.5节
            # 基础积累速度：每秒积累 0.2-0.8 点权重（很慢）
            base_accumulation = 0.2 + quietness * 0.5  # [可调整] 0.3是最小速度，0.5是速度范围
            net_weight_change = base_accumulation * time_delta
            # 积累安静积分
            self.quiet_score += net_weight_change
            # 累计本次安静时间
            self.session_quiet_time += time_delta
        else:
            # 吵闹环境：清零所有权重和安静积分
            net_weight_change = 0
            for rarity in self.fish_weights:
                self.fish_weights[rarity] = 0
            self.quiet_score = 0

        # 更新每种鱼的权重（只在安静时积累）
        if self.is_quiet:
            for rarity in self.fish_weights:
                self.fish_weights[rarity] += net_weight_change
                self.fish_weights[rarity] = min(100, self.fish_weights[rarity])

        # === 基于累计安静时间的品质解锁系统 ===
        # 30分钟(1800秒)内渐进解锁高品质鱼
        # [可调整] 如需修改品质解锁时间，参见 doc/fish_probability.md 第6.1节
        quiet_minutes = self.session_quiet_time / 60

        # 根据累计安静时间确定可出现的最高品质
        # [可调整] 以下时间阈值控制各品质鱼的解锁时机
        # 0-2分钟：只有普通
        # 2-5分钟：解锁稀有
        # 5-10分钟：解锁史诗
        # 10-20分钟：解锁传说
        # 20-30分钟：解锁神话
        if quiet_minutes < 2:           # [可调整] 普通鱼解锁时间(分钟)
            max_unlocked_rarity = "common"
        elif quiet_minutes < 5:         # [可调整] 稀有鱼解锁时间(分钟)
            max_unlocked_rarity = "rare"
        elif quiet_minutes < 10:        # [可调整] 史诗鱼解锁时间(分钟)
            max_unlocked_rarity = "epic"
        elif quiet_minutes < 20:        # [可调整] 传说鱼解锁时间(分钟)
            max_unlocked_rarity = "legendary"
        else:                           # [可调整] 神话鱼解锁时间(分钟)
            max_unlocked_rarity = "mythic"

        # 构建允许的稀有度列表
        rarity_order = ["common", "rare", "epic", "legendary", "mythic"]
        max_index = rarity_order.index(max_unlocked_rarity)
        allowed_rarities = rarity_order[:max_index + 1]

        # 根据累计时间调整加鱼难度（越往后越难加，但品质越高）
        # [可调整] 如需修改加鱼难度规则，参见 doc/fish_probability.md 第6.4节
        # 基础需要积分：10点
        # 每过5分钟增加5点难度
        difficulty_increase = int(quiet_minutes / 5) * 5  # [可调整] 修改 /5 和 *5 改变难度增长
        self.current_required_score = 10 + difficulty_increase  # [可调整] 修改 10 改变基础难度

        # === 加鱼逻辑 ===
        if len(fish_list) < self.max_fish_limit and self.is_quiet and net_weight_change > 0:
            # 检查是否达到加鱼条件
            if self.quiet_score >= self.current_required_score:
                # 根据累计安静时间调整权重
                # 时间越长，高品质概率越高
                time_factor = min(1.0, quiet_minutes / 30)  # 0-1，30分钟达到最大

                # 基础权重 - 调整后30分钟高品质概率更高
                # [可调整] 如需修改基础权重，参见 doc/fish_probability.md 第6.2节
                base_weights = {
                    "common": 35,      # [可调整] 普通鱼基础权重
                    "rare": 30,        # [可调整] 稀有鱼基础权重
                    "epic": 20,        # [可调整] 史诗鱼基础权重
                    "legendary": 10,   # [可调整] 传说鱼基础权重
                    "mythic": 5        # [可调整] 神话鱼基础权重
                }

                # 根据时间调整权重（时间越长，高品质权重越高）
                # [可调整] 如需修改时间对权重的影响，参见 doc/fish_probability.md 第6.3节
                rarity_weights = {}
                for rarity in allowed_rarities:
                    if rarity == "common":
                        # 普通鱼权重随时间大幅降低
                        rarity_weights[rarity] = base_weights[rarity] * (1 - time_factor * 0.7)  # [可调整] 0.7控制普通鱼权重下降速度
                    elif rarity == "rare":
                        rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 0.2)  # [可调整] 0.2控制稀有鱼权重增长速度
                    elif rarity == "epic":
                        rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 0.6)  # [可调整] 0.6控制史诗鱼权重增长速度
                    elif rarity == "legendary":
                        # 传说鱼30分钟时权重翻倍
                        rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 4)    # [可调整] 4控制传说鱼权重增长速度
                    elif rarity == "mythic":
                        # 神话鱼30分钟时权重翻5倍
                        rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 8)    # [可调整] 8控制神话鱼权重增长速度

                # 只选择允许的稀有度
                available_rarities = [r for r in allowed_rarities]
                available_weights = [rarity_weights[r] for r in available_rarities]

                # 按权重随机选择
                chosen_rarity = random.choices(available_rarities, weights=available_weights)[0]

                # 创建指定稀有度的鱼
                fish = Fish()
                fish.rarity = chosen_rarity
                data = RARITY[chosen_rarity]
                fish.color = random.choice(data["colors"])
                fish.size = random.randint(*data["size"])
                fish.speed = random.uniform(0.4, 0.7) * data["speed"]
                fish.threshold_mult = data["threshold"]
                fish.has_glow = data["glow"]
                fish.glow_color = data.get("glow_color", (255, 255, 255, 100))
                fish.points = data.get("points", 10)

                fish_list.append(fish)
                stats.record_fish(fish)
                # 消耗安静积分，清零重新开始积累
                self.quiet_score = 0

                # occasional bubble
                if random.random() < FISH_BUBBLE_CHANCE:
                    self.bubbles.append(Bubble(
                        random.randint(*self._bubble_x_range),
                        HEIGHT, WIDTH
                    ))

        elif not self.is_quiet and len(fish_list) > 0:
            # 吵闹时：快速失去鱼，从高品质开始
            remove_chance = (1 - quietness) * dt * 2  # 每秒可能移除2条
            if random.random() < remove_chance:
                # 按稀有度从高到低移除
                for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
                    if rarity_counts[rarity] > 0:
                        # 找到并移除该稀有度的鱼
                        for i, fish in enumerate(fish_list):
                            if fish.rarity == rarity:
                                fish_list.pop(i)
                                break
                        break  # 每次只移除一条

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

        # 水面光斑 - 在鱼下面绘制
        self._update_and_draw_light_spots(1 / FPS)

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
        self.ui.draw_fish_panel(self.screen, self.fish_list, self.fish_weights,
                                self.quiet_score, self.current_required_score,
                                self.max_fish_limit, self.session_quiet_time, self.is_quiet)
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
