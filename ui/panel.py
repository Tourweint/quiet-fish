"""UI面板模块"""
import pygame
from config import RARITY, ACHIEVEMENTS, POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES, SILENCE_THRESHOLD, WIDTH


class UIPanel:
    def __init__(self, font_manager):
        self.font_manager = font_manager
        # 调整字体大小，使中文显示更清晰
        self.font = font_manager.get_font(20)  # 主字体 - 稍微减小以适应面板
        self.title_font = font_manager.get_font(22)  # 标题字体 - 增大
        self.small_font = font_manager.get_font(16)  # 小字体 - 增大
        self.icon_font = font_manager.get_font(18)  # 图标字体

    def draw_panel(self, surface, x, y, width, height, title="", border_color=(100, 200, 255)):
        """绘制面板背景"""
        # 半透明背景
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 160))
        surface.blit(panel_surf, (x, y))

        # 边框
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=8)

        # 标题（绘制在面板内部顶部居中）
        if title:
            title_surf = self.title_font.render(title, True, border_color)
            # 标题居中显示
            title_x = x + (width - title_surf.get_width()) // 2
            surface.blit(title_surf, (title_x, y + 8))

    def draw_stats_panel(self, surface, stats_manager, volume, fish_count, is_quiet, pomodoro_state):
        """左侧统计面板"""
        panel_x, panel_y = 15, 15
        panel_width, panel_height = 220, 240
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "统计", (100, 200, 255))

        summary = stats_manager.get_summary()
        line_height = 28  # 增加行高
        start_y = panel_y + 45  # 内容从标题下方开始，增加间距

        # 等级
        level_info = summary["level"]
        level_text = self.font.render(f"等级 {level_info['name']} (Lv.{level_info['level']})", True, (255, 215, 0))
        surface.blit(level_text, (panel_x + 12, start_y))

        # 积分
        points_text = self.font.render(f"积分 {summary['points']:,}", True, (200, 255, 200))
        surface.blit(points_text, (panel_x + 12, start_y + line_height))

        # 安静时长
        hours = summary["quiet_hours"]
        quiet_text = self.font.render(f"安静 {hours:.1f}小时", True, (150, 220, 255))
        surface.blit(quiet_text, (panel_x + 12, start_y + line_height * 2))

        # 番茄钟
        pomodoro_text = self.font.render(f"番茄钟 {summary['pomodoro_count']}个", True, (255, 180, 150))
        surface.blit(pomodoro_text, (panel_x + 12, start_y + line_height * 3))

        # 连续天数
        streak_text = self.font.render(f"连续 {summary['streak']}天", True, (200, 200, 255))
        surface.blit(streak_text, (panel_x + 12, start_y + line_height * 4))

        # 当前状态
        color = (100, 255, 150) if is_quiet else (255, 100, 100)
        state_text = self.font.render("安静中" if is_quiet else "太吵!", True, color)
        surface.blit(state_text, (panel_x + 12, start_y + line_height * 5))

    def draw_fish_panel(self, surface, fish_list, fish_weights=None, quiet_score=0, required_score=0, max_fish=50, session_time=0):
        """鱼类统计面板"""
        panel_x, panel_y = 15, 270
        panel_width, panel_height = 220, 240
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "鱼群", (100, 200, 255))

        # 统计各稀有度数量
        counts = {k: 0 for k in RARITY.keys()}
        for fish in fish_list:
            counts[fish.rarity] += 1

        y_offset = panel_y + 40  # 内容从标题下方开始
        line_height = 20
        for key, data in RARITY.items():
            count = counts[key]
            color = data["colors"][0]
            name = data["name"]
            text = self.small_font.render(f"{name}: {count}", True, color)
            surface.blit(text, (panel_x + 12, y_offset))
            y_offset += line_height

        # 显示累计安静时间
        y_offset += 3
        minutes = int(session_time / 60)
        seconds = int(session_time % 60)
        time_text = self.small_font.render(f"安静: {minutes}分{seconds}秒", True, (255, 255, 200))
        surface.blit(time_text, (panel_x + 12, y_offset))
        y_offset += 22

        # 显示已解锁品质
        quiet_minutes = session_time / 60
        if quiet_minutes < 2:
            unlocked = "普通"
        elif quiet_minutes < 5:
            unlocked = "普通/稀有"
        elif quiet_minutes < 10:
            unlocked = "普通/稀有/史诗"
        elif quiet_minutes < 20:
            unlocked = "普通/稀有/史诗/传说"
        else:
            unlocked = "全部解锁"
        unlock_text = self.small_font.render(f"解锁: {unlocked}", True, (200, 255, 200))
        surface.blit(unlock_text, (panel_x + 12, y_offset))
        y_offset += 24

        # 显示加鱼进度条
        # 进度条背景
        bar_width = panel_width - 24
        bar_height = 12
        bar_x = panel_x + 12
        bar_y = y_offset

        # 进度条边框
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

        # 进度填充
        if required_score > 0:
            progress = min(1.0, quiet_score / required_score)
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                # 根据进度改变颜色
                if progress < 0.3:
                    color = (255, 100, 100)  # 红色
                elif progress < 0.7:
                    color = (255, 255, 100)  # 黄色
                else:
                    color = (100, 255, 100)  # 绿色
                pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))

        # 进度文字
        progress_text = self.small_font.render(f"{quiet_score:.1f}/{required_score}", True, (255, 255, 255))
        text_x = bar_x + (bar_width - progress_text.get_width()) // 2
        surface.blit(progress_text, (text_x, bar_y - 1))

        # 鱼数量
        y_offset += bar_height + 6
        total_fish = len(fish_list)
        fish_count_text = self.font.render(f"鱼: {total_fish}/{max_fish}", True, (200, 255, 255))
        surface.blit(fish_count_text, (panel_x + 12, y_offset))

    def draw_pomodoro(self, surface, pomodoro_state):
        """番茄钟面板"""
        panel_width, panel_height = 180, 100
        panel_x = WIDTH - panel_width - 15
        panel_y = 15
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "番茄钟", (255, 150, 100))

        if pomodoro_state["active"]:
            remaining = max(0, pomodoro_state["end_time"] - pygame.time.get_ticks())
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000

            # 时间文字居中
            time_text = self.title_font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            time_x = panel_x + (panel_width - time_text.get_width()) // 2
            surface.blit(time_text, (time_x, panel_y + 42))

            # 状态提示居中
            status = "工作中" if not pomodoro_state["is_break"] else "休息中"
            status_text = self.small_font.render(status, True, (255, 200, 150))
            status_x = panel_x + (panel_width - status_text.get_width()) // 2
            surface.blit(status_text, (status_x, panel_y + 70))
        else:
            # 未激活时显示按钮提示，居中
            hint = self.small_font.render("按空格开启", True, (180, 180, 180))
            hint_x = panel_x + (panel_width - hint.get_width()) // 2
            surface.blit(hint, (hint_x, panel_y + 50))

    def draw_volume_meter(self, surface, volume):
        """音量条"""
        panel_width, panel_height = 180, 20
        panel_x = WIDTH - panel_width - 15
        panel_y = 130

        # 背景
        pygame.draw.rect(surface, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=4)

        # 进度条
        bar_width = int(panel_width * min(1.0, volume / 100))
        bar_color = (100, 255, 150) if volume < SILENCE_THRESHOLD else (255, 100, 100)
        if bar_width > 0:
            pygame.draw.rect(surface, bar_color, (panel_x + 2, panel_y + 2, bar_width - 4, panel_height - 4), border_radius=3)

        # 阈值线
        threshold_x = panel_x + int(panel_width * SILENCE_THRESHOLD / 100)
        pygame.draw.line(surface, (255, 255, 255), (threshold_x, panel_y), (threshold_x, panel_y + panel_height), 2)

        # 音量文字
        vol_text = self.small_font.render(f"音量 {volume:.0f}", True, (255, 255, 255))
        surface.blit(vol_text, (panel_x, panel_y + panel_height + 6))

    def draw_achievements(self, surface, new_achievements, achievement_flash_timer):
        """成就通知"""
        if not new_achievements:
            return

        # 弹窗通知
        alpha = min(255, int(255 * achievement_flash_timer))
        panel_width = 320
        panel_height = 70
        x = (WIDTH - panel_width) // 2
        y = 60 - (1 - achievement_flash_timer) * 40

        # 背景
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((50, 50, 80, min(220, alpha)))
        surface.blit(panel, (x, y))

        # 金色边框
        pygame.draw.rect(surface, (255, 215, 0, alpha), (x, y, panel_width, panel_height), 3, border_radius=10)

        # 成就文字居中
        for i, ach_key in enumerate(new_achievements[:1]):
            ach = ACHIEVEMENTS[ach_key]
            text = self.font.render(f"{ach['name']}: {ach['desc']}", True, (255, 255, 255))
            text_x = x + (panel_width - text.get_width()) // 2
            text_y = y + (panel_height - text.get_height()) // 2
            surface.blit(text, (text_x, text_y))

    def draw_rarity_legend(self, surface):
        """稀有度图例"""
        panel_width, panel_height = 150, 190
        panel_x = WIDTH - panel_width - 15
        panel_y = 175
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "稀有度", (255, 215, 0))

        y_offset = panel_y + 42
        line_height = 28
        for key, data in RARITY.items():
            color = data["colors"][0]
            # 小圆点
            pygame.draw.circle(surface, color, (panel_x + 15, int(y_offset + 8)), 6)
            # 名字
            text = self.font.render(f"{data['name']}", True, color)
            surface.blit(text, (panel_x + 28, y_offset))
            y_offset += line_height

    def draw_help(self, surface):
        """帮助提示"""
        panel_width, panel_height = 150, 90
        panel_x = WIDTH - panel_width - 15
        panel_y = 380
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "操作", (150, 200, 255))
        
        help_texts = [
            "空格: 番茄钟",
            "S: 截图",
            "Q: 退出"
        ]
        y_offset = panel_y + 42
        line_height = 22
        for text in help_texts:
            help_surf = self.small_font.render(text, True, (200, 200, 200))
            surface.blit(help_surf, (panel_x + 12, y_offset))
            y_offset += line_height
