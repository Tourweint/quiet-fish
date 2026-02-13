"""字体管理器"""
import os
import pygame


class FontManager:
    def __init__(self):
        # 常用中文字体路径
        self.font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
        ]
        self.cache = {}
        
        # 预检查可用字体
        self._available_fonts = [p for p in self.font_paths if os.path.exists(p)]

    def get_font(self, size):
        """获取指定大小的字体"""
        if size in self.cache:
            return self.cache[size]

        font = None
        
        # 尝试使用可用字体
        for path in self._available_fonts:
            try:
                font = pygame.font.Font(path, size)
                if font:
                    break
            except RuntimeError:
                continue

        # 回退到默认字体
        if font is None:
            font = pygame.font.Font(None, size)
        
        self.cache[size] = font
        return font
