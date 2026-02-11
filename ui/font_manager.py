"""字体管理器"""
import pygame


class FontManager:
    def __init__(self):
        self.font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
        ]
        self.cache = {}

    def get_font(self, size):
        """获取指定大小的字体"""
        if size in self.cache:
            return self.cache[size]

        for path in self.font_paths:
            try:
                font = pygame.font.Font(path, size)
                self.cache[size] = font
                return font
            except:
                continue

        # 回退到默认字体
        font = pygame.font.Font(None, size)
        self.cache[size] = font
        return font
