"""字体管理器"""
import os
import sys
import pygame


class FontManager:
    def __init__(self):
        # 根据操作系统选择字体路径
        self.font_paths = []
        
        if sys.platform == 'win32':
            # Windows 中文字体路径
            self.font_paths = [
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
                "C:/Windows/Fonts/simkai.ttf",  # 楷体
            ]
        else:
            # Linux 中文字体路径
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
        
        # 打印调试信息
        if self._available_fonts:
            print(f"[FontManager] 找到可用字体: {self._available_fonts[0]}")
        else:
            print("[FontManager] 警告: 未找到中文字体，将使用系统默认字体")

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
            except RuntimeError as e:
                print(f"[FontManager] 加载字体失败 {path}: {e}")
                continue

        # 回退到默认字体
        if font is None:
            try:
                # 尝试使用 pygame 默认字体
                font = pygame.font.Font(None, size)
                print(f"[FontManager] 使用 pygame 默认字体，大小 {size}")
            except Exception as e:
                print(f"[FontManager] 错误: 无法加载任何字体: {e}")
                # 最后的回退方案
                font = pygame.font.SysFont("arial", size)
        
        self.cache[size] = font
        return font
