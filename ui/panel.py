"""UI面板模块"""
import pygame
from config import RARITY, ACHIEVEMENTS, POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES, SILENCE_THRESHOLD, WIDTH


def get_font(font_manager, size=28):
    """获取支持中文的字体"""
    return font_manager.get_font(size)


class UIPanel:
    def __init__(self, font_manager):
        self.font = font_manager
        self.title_font = font_manager.get_font(22)
        self.small_font = font_manager.get_font(18)
        self.icon_font = font_manager.get_font(20)

    def draw_panel(self, surface, x, y, width, height, title="", border_color=(100, 200, 255)):
        """绘制面板背景"""
        # 半透明背景
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 160))
        surface.blit(panel_surf, (x, y))

        # 边框
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=8)

        # 标题
        if title:
            title_surf = self.title_font.render(title, True, border_color)
            surface.blit(title_surf, (x + 10, y - 8))

    def draw_stats_panel(self, surface, stats_manager, volume, fish_count, is_quiet, pomodoro_state):
        """左侧统计面板"""
        self.draw_panel(surface, 15, 15, 220, 200, "📊 统计", (100, 200, 255))

        summary = stats_manager.get_summary()

        # 等级
        level_info = summary["level"]
        level_text = self.font.render(f"等级: {level_info['name']} (Lv.{level_info['level']})", True, (255, 215, 0))
        surface.blit(level_text, (30, 40))

        # 积分
        points_text = self.font.render(f"积分: {summary['points']:,}", True, (200, 255, 200))
        surface.blit(points_text, (30, 68))

        # 安静时长
        hours = summary["quiet_hours"]
        quiet_text = self.font.render(f"安静: {hours:.1f}h", True, (150, 220, 255))
        surface.blit(quiet_text, (30, 96))

        # 番茄钟
        pomodoro_text = self.font.render(f"番茄钟: {summary['pomodoro_count']}个", True, (255, 180, 150))
        surface.blit(pomodoro_text, (30, 124))

        # 连续天数
        streak_text = self.font.render(f"连续: {summary['streak']}天", True, (200, 200, 255))
        surface.blit(streak_text, (30, 152))

        # 当前状态
        color = (100, 255, 150) if is_quiet else (255, 100, 100)
        state_text = self.font.render("✓ 安静中" if is_quiet else "✗ 太吵!", True, color)
        surface.blit(state_text, (30, 180))

    def draw_fish_panel(self, surface, fish_list):
        """鱼类统计面板"""
        self.draw_panel(surface, 15, 230, 220, 150, "🐟 鱼群", (100, 200, 255))

        # 统计各稀有度数量
        counts = {k: 0 for k in RARITY.keys()}
        for fish in fish_list:
            counts[fish.rarity] += 1

        y_offset = 55
        for key, data in RARITY.items():
            count = counts[key]
            if count > 0:
                color = data["colors"][0]
                name = data["name"]
                text = self.font.render(f"{name}: {count}", True, color)
                surface.blit(text, (30, y_offset))
                y_offset += 26

    def draw_pomodoro(self, surface, pomodoro_state):
        """番茄钟面板"""
        self.draw_panel(surface, WIDTH - 200, 15, 185, 100, "🍅 番茄钟", (255, 150, 100))

        if pomodoro_state["active"]:
            remaining = max(0, pomodoro_state["end_time"] - pygame.time.get_ticks())
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000

            time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            surface.blit(time_text, (WIDTH - 160, 55))

            # 状态提示
            status = "工作中" if not pomodoro_state["is_break"] else "休息中"
            status_text = self.small_font.render(status, True, (255, 200, 150))
            surface.blit(status_text, (WIDTH - 140, 85))
        else:
            # 未激活时显示按钮提示
            hint = self.small_font.render("按 SPACE 开启", True, (180, 180, 180))
            surface.blit(hint, (WIDTH - 160, 60))

    def draw_volume_meter(self, surface, volume):
        """音量条"""
        x, y = WIDTH - 200, 130
        width, height = 165, 25

        # 背景
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height), border_radius=5)

        # 进度条
        bar_width = int(width * min(1.0, volume / 100))
        bar_color = (100, 255, 150) if volume < SILENCE_THRESHOLD else (255, 100, 100)
        if bar_width > 0:
            pygame.draw.rect(surface, bar_color, (x + 2, y + 2, bar_width - 4, height - 4), border_radius=4)

        # 阈值线
        threshold_x = x + int(width * SILENCE_THRESHOLD / 100)
        pygame.draw.line(surface, (255, 255, 255), (threshold_x, y), (threshold_x, y + height), 2)

        # 音量文字
        vol_text = self.small_font.render(f"音量: {volume:.0f}", True, (255, 255, 255))
        surface.blit(vol_text, (x, y + 30))

    def draw_achievements(self, surface, new_achievements, achievement_flash_timer):
        """成就通知"""
        if not new_achievements:
            return

        # 弹窗通知
        alpha = min(255, int(255 * achievement_flash_timer))
        panel_width = 350
        x = (WIDTH - panel_width) // 2
        y = 80 - (1 - achievement_flash_timer) * 50

        # 背景
        panel = pygame.Surface((panel_width, 80), pygame.SRCALPHA)
        panel.fill((50, 50, 80, min(220, alpha)))
        surface.blit(panel, (x, y))

        # 金色边框
        pygame.draw.rect(surface, (255, 215, 0, alpha), (x, y, panel_width, 80), 3, border_radius=10)

        # 成就图标和名字
        for i, ach_key in enumerate(new_achievements[:3]):  # 最多显示3个
            ach = ACHIEVEMENTS[ach_key]
            text = self.font.render(f"{ach['icon']} {ach['name']} - {ach['desc']}", True, (255, 255, 255, alpha))
            surface.blit(text, (x + 20, y + 25 + i * 22))

    def draw_rarity_legend(self, surface):
        """稀有度图例"""
        self.draw_panel(surface, WIDTH - 160, 200, 145, 200, "✨ 稀有度", (255, 215, 0))

        y_offset = 55
        for key, data in RARITY.items():
            color = data["colors"][0]
            # 小圆点
            pygame.draw.circle(surface, color, (WIDTH - 145, int(y_offset + 8)), 6)
            # 名字
            text = self.title_font.render(f"{data['name']}", True, color)
            surface.blit(text, (WIDTH - 130, y_offset))
            y_offset += 30

    def draw_help(self, surface):
        """帮助提示"""
        self.draw_panel(surface, WIDTH - 160, 415, 145, 80, "⌨️ 操作", (150, 200, 255))
        help_texts = [
            "SPACE: 番茄钟",
            "S: 保存/截图",
            "Q: 退出"
        ]
        y_offset = 55
        for text in help_texts:
            help_surf = self.small_font.render(text, True, (200, 200, 200))
            surface.blit(help_surf, (WIDTH - 145, y_offset))
            y_offset += 20
