"""UI面板模块"""
import pygame
from config import RARITY, ACHIEVEMENTS, POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES, SILENCE_THRESHOLD, WIDTH


class UIPanel:
    def __init__(self, font_manager):
        self.font_manager = font_manager
        self.font = font_manager.get_font(24)  # 主字体
        self.title_font = font_manager.get_font(18)
        self.small_font = font_manager.get_font(14)
        self.icon_font = font_manager.get_font(16)

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
            surface.blit(title_surf, (x + 10, y - 5))

    def draw_stats_panel(self, surface, stats_manager, volume, fish_count, is_quiet, pomodoro_state):
        """左侧统计面板"""
        self.draw_panel(surface, 15, 15, 200, 220, "统计", (100, 200, 255))

        summary = stats_manager.get_summary()
        line_height = 26
        start_y = 40

        # 等级
        level_info = summary["level"]
        level_text = self.font.render(f"等级 {level_info['name']} (Lv.{level_info['level']})", True, (255, 215, 0))
        surface.blit(level_text, (25, start_y))

        # 积分
        points_text = self.font.render(f"积分 {summary['points']:,}", True, (200, 255, 200))
        surface.blit(points_text, (25, start_y + line_height))

        # 安静时长
        hours = summary["quiet_hours"]
        quiet_text = self.font.render(f"安静 {hours:.1f}小时", True, (150, 220, 255))
        surface.blit(quiet_text, (25, start_y + line_height * 2))

        # 番茄钟
        pomodoro_text = self.font.render(f"番茄钟 {summary['pomodoro_count']}个", True, (255, 180, 150))
        surface.blit(pomodoro_text, (25, start_y + line_height * 3))

        # 连续天数
        streak_text = self.font.render(f"连续 {summary['streak']}天", True, (200, 200, 255))
        surface.blit(streak_text, (25, start_y + line_height * 4))

        # 当前状态
        color = (100, 255, 150) if is_quiet else (255, 100, 100)
        state_text = self.font.render("安静中" if is_quiet else "太吵!", True, color)
        surface.blit(state_text, (25, start_y + line_height * 5))

    def draw_fish_panel(self, surface, fish_list):
        """鱼类统计面板"""
        self.draw_panel(surface, 15, 250, 200, 150, "鱼群", (100, 200, 255))

        # 统计各稀有度数量
        counts = {k: 0 for k in RARITY.keys()}
        for fish in fish_list:
            counts[fish.rarity] += 1

        y_offset = 45
        line_height = 24
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
        self.draw_panel(surface, WIDTH - 180, 15, 165, 85, "番茄钟", (255, 150, 100))

        if pomodoro_state["active"]:
            remaining = max(0, pomodoro_state["end_time"] - pygame.time.get_ticks())
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000

            time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            surface.blit(time_text, (WIDTH - 145, 48))

            # 状态提示
            status = "工作中" if not pomodoro_state["is_break"] else "休息中"
            status_text = self.small_font.render(status, True, (255, 200, 150))
            surface.blit(status_text, (WIDTH - 125, 72))
        else:
            # 未激活时显示按钮提示
            hint = self.small_font.render("按空格开启", True, (180, 180, 180))
            surface.blit(hint, (WIDTH - 150, 50))

    def draw_volume_meter(self, surface, volume):
        """音量条"""
        x, y = WIDTH - 180, 115
        width, height = 155, 20

        # 背景
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height), border_radius=4)

        # 进度条
        bar_width = int(width * min(1.0, volume / 100))
        bar_color = (100, 255, 150) if volume < SILENCE_THRESHOLD else (255, 100, 100)
        if bar_width > 0:
            pygame.draw.rect(surface, bar_color, (x + 2, y + 2, bar_width - 4, height - 4), border_radius=3)

        # 阈值线
        threshold_x = x + int(width * SILENCE_THRESHOLD / 100)
        pygame.draw.line(surface, (255, 255, 255), (threshold_x, y), (threshold_x, y + height), 2)

        # 音量文字
        vol_text = self.small_font.render(f"音量 {volume:.0f}", True, (255, 255, 255))
        surface.blit(vol_text, (x, y + 24))

    def draw_achievements(self, surface, new_achievements, achievement_flash_timer):
        """成就通知"""
        if not new_achievements:
            return

        # 弹窗通知
        alpha = min(255, int(255 * achievement_flash_timer))
        panel_width = 300
        x = (WIDTH - panel_width) // 2
        y = 65 - (1 - achievement_flash_timer) * 40

        # 背景
        panel = pygame.Surface((panel_width, 60), pygame.SRCALPHA)
        panel.fill((50, 50, 80, min(220, alpha)))
        surface.blit(panel, (x, y))

        # 金色边框
        pygame.draw.rect(surface, (255, 215, 0, alpha), (x, y, panel_width, 60), 3, border_radius=10)

        # 成就文字
        for i, ach_key in enumerate(new_achievements[:1]):  # 最多显示1个
            ach = ACHIEVEMENTS[ach_key]
            text = self.font.render(f"{ach['name']}: {ach['desc']}", True, (255, 255, 255, alpha))
            surface.blit(text, (x + 15, y + 18))

    def draw_rarity_legend(self, surface):
        """稀有度图例"""
        self.draw_panel(surface, WIDTH - 145, 180, 130, 170, "稀有度", (255, 215, 0))

        y_offset = 42
        line_height = 26
        for key, data in RARITY.items():
            color = data["colors"][0]
            # 小圆点
            pygame.draw.circle(surface, color, (WIDTH - 130, int(y_offset + 6)), 5)
            # 名字
            text = self.small_font.render(f"{data['name']}", True, color)
            surface.blit(text, (WIDTH - 115, y_offset))
            y_offset += line_height

    def draw_help(self, surface):
        """帮助提示"""
        self.draw_panel(surface, WIDTH - 145, 365, 130, 65, "操作", (150, 200, 255))
        help_texts = [
            "空格: 番茄钟",
            "S: 截图",
            "Q: 退出"
        ]
        y_offset = 40
        for text in help_texts:
            help_surf = self.small_font.render(text, True, (200, 200, 200))
            surface.blit(help_surf, (WIDTH - 135, y_offset))
            y_offset += 16
