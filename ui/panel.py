"""UI面板模块"""
import pygame
from config import RARITY, ACHIEVEMENTS, POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES, SILENCE_THRESHOLD, WIDTH


class UIPanel:
    def __init__(self, font_manager):
        self.font_manager = font_manager
        self.font = font_manager.get_font(26)  # 主字体
        self.title_font = font_manager.get_font(20)
        self.small_font = font_manager.get_font(16)
        self.icon_font = font_manager.get_font(18)

    def draw_panel(self, surface, x, y, width, height, title="", border_color=(100, 200, 255)):
        """绘制面板背景"""
        # 半透明背景
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 160))
        surface.blit(panel_surf, (x, y))

        # 边框
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=8)

        # 标题（去掉emoji）
        if title:
            # 移除emoji字符
            title_clean = title
            title_surf = self.title_font.render(title_clean, True, border_color)
            surface.blit(title_surf, (x + 10, y - 6))

    def draw_stats_panel(self, surface, stats_manager, volume, fish_count, is_quiet, pomodoro_state):
        """左侧统计面板"""
        self.draw_panel(surface, 15, 15, 210, 230, "Statistics", (100, 200, 255))

        summary = stats_manager.get_summary()
        line_height = 28
        start_y = 45

        # 等级
        level_info = summary["level"]
        level_text = self.font.render(f"Level: {level_info['name']} (Lv.{level_info['level']})", True, (255, 215, 0))
        surface.blit(level_text, (25, start_y))

        # 积分
        points_text = self.font.render(f"Points: {summary['points']:,}", True, (200, 255, 200))
        surface.blit(points_text, (25, start_y + line_height))

        # 安静时长
        hours = summary["quiet_hours"]
        quiet_text = self.font.render(f"Quiet: {hours:.1f}h", True, (150, 220, 255))
        surface.blit(quiet_text, (25, start_y + line_height * 2))

        # 番茄钟
        pomodoro_text = self.font.render(f"Pomodoro: {summary['pomodoro_count']}", True, (255, 180, 150))
        surface.blit(pomodoro_text, (25, start_y + line_height * 3))

        # 连续天数
        streak_text = self.font.render(f"Streak: {summary['streak']} days", True, (200, 200, 255))
        surface.blit(streak_text, (25, start_y + line_height * 4))

        # 当前状态
        color = (100, 255, 150) if is_quiet else (255, 100, 100)
        state_text = self.font.render("[QUIET]" if is_quiet else "[NOISY]", True, color)
        surface.blit(state_text, (25, start_y + line_height * 5))

    def draw_fish_panel(self, surface, fish_list):
        """鱼类统计面板"""
        self.draw_panel(surface, 15, 260, 210, 160, "Fish School", (100, 200, 255))

        # 统计各稀有度数量
        counts = {k: 0 for k in RARITY.keys()}
        for fish in fish_list:
            counts[fish.rarity] += 1

        y_offset = 50
        line_height = 26
        for key, data in RARITY.items():
            count = counts[key]
            if count > 0:
                color = data["colors"][0]
                name = data["name"]
                text = self.font.render(f"{name}: {count}", True, color)
                surface.blit(text, (25, y_offset))
                y_offset += line_height

    def draw_pomodoro(self, surface, pomodoro_state):
        """番茄钟面板"""
        self.draw_panel(surface, WIDTH - 190, 15, 175, 90, "Pomodoro", (255, 150, 100))

        if pomodoro_state["active"]:
            remaining = max(0, pomodoro_state["end_time"] - pygame.time.get_ticks())
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000

            time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            surface.blit(time_text, (WIDTH - 155, 50))

            # 状态提示
            status = "Working" if not pomodoro_state["is_break"] else "Break"
            status_text = self.small_font.render(status, True, (255, 200, 150))
            surface.blit(status_text, (WIDTH - 135, 78))
        else:
            # 未激活时显示按钮提示
            hint = self.small_font.render("SPACE to start", True, (180, 180, 180))
            surface.blit(hint, (WIDTH - 160, 55))

    def draw_volume_meter(self, surface, volume):
        """音量条"""
        x, y = WIDTH - 190, 120
        width, height = 165, 22

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
        vol_text = self.small_font.render(f"Vol: {volume:.0f}", True, (255, 255, 255))
        surface.blit(vol_text, (x, y + 26))

    def draw_achievements(self, surface, new_achievements, achievement_flash_timer):
        """成就通知"""
        if not new_achievements:
            return

        # 弹窗通知
        alpha = min(255, int(255 * achievement_flash_timer))
        panel_width = 320
        x = (WIDTH - panel_width) // 2
        y = 70 - (1 - achievement_flash_timer) * 50

        # 背景
        panel = pygame.Surface((panel_width, 70), pygame.SRCALPHA)
        panel.fill((50, 50, 80, min(220, alpha)))
        surface.blit(panel, (x, y))

        # 金色边框
        pygame.draw.rect(surface, (255, 215, 0, alpha), (x, y, panel_width, 70), 3, border_radius=10)

        # 成就名字（去掉emoji）
        for i, ach_key in enumerate(new_achievements[:2]):  # 最多显示2个
            ach = ACHIEVEMENTS[ach_key]
            # 移除emoji
            name_clean = ach['name'].replace(ach['icon'], "").strip()
            text = self.font.render(f"{name_clean}: {ach['desc']}", True, (255, 255, 255, alpha))
            surface.blit(text, (x + 15, y + 20 + i * 24))

    def draw_rarity_legend(self, surface):
        """稀有度图例"""
        self.draw_panel(surface, WIDTH - 150, 190, 135, 180, "Rarity", (255, 215, 0))

        y_offset = 45
        line_height = 28
        for key, data in RARITY.items():
            color = data["colors"][0]
            # 小圆点
            pygame.draw.circle(surface, color, (WIDTH - 135, int(y_offset + 7)), 6)
            # 名字
            text = self.small_font.render(f"{data['name']}", True, color)
            surface.blit(text, (WIDTH - 120, y_offset))
            y_offset += line_height

    def draw_help(self, surface):
        """帮助提示"""
        self.draw_panel(surface, WIDTH - 150, 385, 135, 70, "Controls", (150, 200, 255))
        help_texts = [
            "SPACE: Timer",
            "S: Screenshot",
            "Q: Quit"
        ]
        y_offset = 45
        for text in help_texts:
            help_surf = self.small_font.render(text, True, (200, 200, 200))
            surface.blit(help_surf, (WIDTH - 140, y_offset))
            y_offset += 18
