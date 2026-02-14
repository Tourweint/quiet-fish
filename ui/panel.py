"""UI面板模块"""
import pygame
from config import RARITY, ACHIEVEMENTS, POMODORO_WORK_MINUTES, POMODORO_BREAK_MINUTES, SILENCE_THRESHOLD, WIDTH


class UIPanel:
    def __init__(self, font_manager):
        self.font_manager = font_manager
        # 调整字体大小，使中文显示更清晰
        self.font = font_manager.get_font(20)
        self.title_font = font_manager.get_font(22)
        self.small_font = font_manager.get_font(16)
        self.tiny_font = font_manager.get_font(14)
        self.icon_font = font_manager.get_font(18)

    def draw_panel(self, surface, x, y, width, height, title="", border_color=(100, 200, 255)):
        """绘制毛玻璃效果面板"""
        # 获取背景区域用于毛玻璃效果
        bg_area = surface.subsurface((x, y, width, height)).copy()

        # 毛玻璃效果：先模糊背景
        blurred = self._blur_surface(bg_area, 3)

        # 绘制模糊后的背景
        surface.blit(blurred, (x, y))

        # 半透明覆盖层（增强毛玻璃感）
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((30, 50, 80, 120))
        surface.blit(overlay, (x, y))

        # 内发光效果
        glow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # 顶部高光
        pygame.draw.line(glow_surf, (255, 255, 255, 30), (4, 2), (width - 4, 2), 2)
        # 左侧微光
        pygame.draw.line(glow_surf, (255, 255, 255, 15), (2, 4), (2, height - 4), 2)
        surface.blit(glow_surf, (x, y))

        # 边框（带渐变效果）
        pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=10)
        # 内边框
        inner_color = tuple(min(255, c + 40) for c in border_color)
        pygame.draw.rect(surface, inner_color, (x + 2, y + 2, width - 4, height - 4), 1, border_radius=8)

        # 标题
        if title:
            # 标题背景条
            title_bg = pygame.Surface((width - 20, 28), pygame.SRCALPHA)
            title_bg.fill((*border_color[:3], 40))
            surface.blit(title_bg, (x + 10, y + 6))

            title_surf = self.title_font.render(title, True, border_color)
            title_x = x + (width - title_surf.get_width()) // 2
            surface.blit(title_surf, (title_x, y + 8))

    def _blur_surface(self, surface, radius):
        """简单的表面模糊处理"""
        # 缩小再放大实现模糊效果
        size = surface.get_size()
        # 缩小
        small = pygame.transform.smoothscale(surface, (max(1, size[0] // radius), max(1, size[1] // radius)))
        # 放大回来
        blurred = pygame.transform.smoothscale(small, size)
        return blurred

    def draw_stats_panel(self, surface, stats_manager, volume, fish_count, is_quiet, pomodoro_state):
        """左侧统计面板"""
        panel_x, panel_y = 15, 15
        panel_width, panel_height = 220, 200
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "统计", (100, 200, 255))

        summary = stats_manager.get_summary()
        line_height = 26
        start_y = panel_y + 42

        # 等级和积分
        level_info = summary["level"]
        level_text = self.font.render(f"{level_info['name']} Lv.{level_info['level']}", True, (255, 215, 0))
        surface.blit(level_text, (panel_x + 12, start_y))

        points_text = self.small_font.render(f"积分: {summary['points']:,}", True, (200, 255, 200))
        surface.blit(points_text, (panel_x + 12, start_y + line_height))

        # 安静时长和番茄钟
        quiet_text = self.small_font.render(f"安静: {summary['quiet_hours']:.1f}小时", True, (150, 220, 255))
        surface.blit(quiet_text, (panel_x + 12, start_y + line_height * 2))

        pomodoro_text = self.small_font.render(f"番茄钟: {summary['pomodoro_count']}个", True, (255, 180, 150))
        surface.blit(pomodoro_text, (panel_x + 12, start_y + line_height * 3))

        # 连续天数和状态
        streak_text = self.small_font.render(f"连续: {summary['streak']}天", True, (200, 200, 255))
        surface.blit(streak_text, (panel_x + 12, start_y + line_height * 4))

    def draw_fish_panel(self, surface, fish_list, fish_weights=None, quiet_score=0, required_score=0, max_fish=50, session_time=0, is_quiet=True):
        """鱼类统计面板 - 优化版"""
        panel_x, panel_y = 15, 225
        panel_width, panel_height = 220, 280
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "鱼群", (100, 200, 255))

        # 统计各稀有度数量
        counts = {k: 0 for k in RARITY.keys()}
        for fish in fish_list:
            counts[fish.rarity] += 1

        y_offset = panel_y + 38

        # 简洁显示各品质数量（一行两个）
        rarity_list = list(RARITY.items())
        for i in range(0, len(rarity_list), 2):
            # 第一个
            key1, data1 = rarity_list[i]
            count1 = counts[key1]
            color1 = data1["colors"][0]
            text1 = self.small_font.render(f"{data1['name']}: {count1}", True, color1)
            surface.blit(text1, (panel_x + 12, y_offset))

            # 第二个（如果有）
            if i + 1 < len(rarity_list):
                key2, data2 = rarity_list[i + 1]
                count2 = counts[key2]
                color2 = data2["colors"][0]
                text2 = self.small_font.render(f"{data2['name']}: {count2}", True, color2)
                surface.blit(text2, (panel_x + 115, y_offset))

            y_offset += 22

        # 分隔线
        y_offset += 5
        pygame.draw.line(surface, (100, 100, 100), (panel_x + 10, y_offset), (panel_x + panel_width - 10, y_offset), 1)
        y_offset += 10

        # 累计安静时间
        minutes = int(session_time / 60)
        seconds = int(session_time % 60)
        time_text = self.small_font.render(f"本次专注: {minutes}分{seconds:02d}秒", True, (255, 255, 200))
        surface.blit(time_text, (panel_x + 12, y_offset))
        y_offset += 22

        # 已解锁品质（简洁显示）
        quiet_minutes = session_time / 60
        if quiet_minutes < 2:
            unlocked = "普通"
            next_unlock = "稀有"
            next_time = 2
        elif quiet_minutes < 5:
            unlocked = "普通/稀有"
            next_unlock = "史诗"
            next_time = 5
        elif quiet_minutes < 10:
            unlocked = "普通/稀有/史诗"
            next_unlock = "传说"
            next_time = 10
        elif quiet_minutes < 20:
            unlocked = "普通/稀有/史诗/传说"
            next_unlock = "神话"
            next_time = 20
        else:
            unlocked = "全部解锁"
            next_unlock = None
            next_time = 0

        unlocked_text = self.small_font.render(f"已解锁: {unlocked}", True, (200, 255, 200))
        surface.blit(unlocked_text, (panel_x + 12, y_offset))
        y_offset += 20

        # 下一个解锁提示
        if next_unlock:
            remain = next_time - quiet_minutes
            next_text = self.tiny_font.render(f"距{next_unlock}解锁: 约{remain:.0f}分钟", True, (180, 180, 180))
            surface.blit(next_text, (panel_x + 12, y_offset))
        else:
            next_text = self.tiny_font.render("已解锁全部品质", True, (255, 215, 0))
            surface.blit(next_text, (panel_x + 12, y_offset))
        y_offset += 24

        # 加鱼进度条
        bar_width = panel_width - 24
        bar_height = 14
        bar_x = panel_x + 12
        bar_y = y_offset

        # 进度条背景
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        # 进度填充
        if required_score > 0:
            progress = min(1.0, quiet_score / required_score)
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                # 渐变色：红->黄->绿
                if progress < 0.5:
                    r = 255
                    g = int(100 + 155 * (progress * 2))
                    b = 100
                else:
                    r = int(255 - 155 * ((progress - 0.5) * 2))
                    g = 255
                    b = 100
                color = (r, g, b)
                pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height), border_radius=3)

        # 进度条边框
        pygame.draw.rect(surface, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)

        # 进度文字
        progress_text = self.small_font.render(f"{quiet_score:.1f}/{required_score}", True, (255, 255, 255))
        text_x = bar_x + (bar_width - progress_text.get_width()) // 2
        surface.blit(progress_text, (text_x, bar_y - 1))
        y_offset += bar_height + 8

        # 鱼数量
        total_fish = len(fish_list)
        fish_count_text = self.font.render(f"鱼群: {total_fish}/{max_fish}", True, (200, 255, 255))
        surface.blit(fish_count_text, (panel_x + 12, y_offset))

        # 专注提示（当吵闹时显示）
        if not is_quiet:
            y_offset += 28
            hint_text = self.tiny_font.render("提示: 保持安静，专注学习", True, (255, 150, 150))
            surface.blit(hint_text, (panel_x + 12, y_offset))

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
            text_x = panel_x + (panel_width - time_text.get_width()) // 2
            surface.blit(time_text, (text_x, panel_y + 45))

            # 状态提示
            status = "休息中" if pomodoro_state["is_break"] else "专注中"
            status_color = (100, 255, 150) if pomodoro_state["is_break"] else (255, 200, 100)
            status_text = self.font.render(status, True, status_color)
            status_x = panel_x + (panel_width - status_text.get_width()) // 2
            surface.blit(status_text, (status_x, panel_y + 75))
        else:
            # 未开始提示
            hint_text = self.small_font.render("按空格开始", True, (200, 200, 200))
            hint_x = panel_x + (panel_width - hint_text.get_width()) // 2
            surface.blit(hint_text, (hint_x, panel_y + 50))

    def draw_volume_meter(self, surface, volume):
        """音量指示器"""
        bar_x, bar_y = WIDTH - 200, 130
        bar_width, bar_height = 180, 20

        # 背景
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # 音量条
        fill_width = min(bar_width, int(volume * 1.8))
        if volume < SILENCE_THRESHOLD:
            color = (100, 255, 100)  # 绿色-安静
        elif volume < SILENCE_THRESHOLD * 2:
            color = (255, 255, 100)  # 黄色-警告
        else:
            color = (255, 100, 100)  # 红色-吵闹

        if fill_width > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))

        # 阈值线
        threshold_x = bar_x + int(SILENCE_THRESHOLD * 1.8)
        pygame.draw.line(surface, (255, 255, 255), (threshold_x, bar_y - 2), (threshold_x, bar_y + bar_height + 2), 2)

        # 文字
        vol_text = self.small_font.render(f"音量: {volume:.0f}", True, (255, 255, 255))
        surface.blit(vol_text, (bar_x, bar_y - 22))

    def draw_rarity_legend(self, surface):
        """稀有度图例 - 简化版"""
        panel_x, panel_y = WIDTH - 200, 165
        panel_width, panel_height = 180, 140
        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "品质", (150, 150, 200))

        y_offset = panel_y + 35
        for key, data in RARITY.items():
            color = data["colors"][0]
            name = data["name"]
            text = self.small_font.render(f"● {name}", True, color)
            surface.blit(text, (panel_x + 12, y_offset))
            y_offset += 22

    def draw_help(self, surface):
        """帮助提示 - 简化版"""
        help_text = "[空格]番茄钟 [Q]退出 [S]截图"
        text_surf = self.small_font.render(help_text, True, (180, 180, 180))
        surface.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, 10))

    def draw_achievements(self, surface, achievements, flash_intensity):
        """成就通知"""
        if not achievements:
            return

        panel_width, panel_height = 300, 60
        panel_x = (WIDTH - panel_width) // 2
        panel_y = 50

        # 闪烁效果
        alpha = int(200 + 55 * flash_intensity)
        border_color = (255, 215, 0)

        self.draw_panel(surface, panel_x, panel_y, panel_width, panel_height, "成就解锁!", border_color)

        # 显示成就名称
        ach_id = achievements[-1]  # 显示最新的成就
        if ach_id in ACHIEVEMENTS:
            ach = ACHIEVEMENTS[ach_id]
            name_text = self.font.render(ach["name"], True, (255, 215, 0))
            name_x = panel_x + (panel_width - name_text.get_width()) // 2
            surface.blit(name_text, (name_x, panel_y + 35))
