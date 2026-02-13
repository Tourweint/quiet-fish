"""
安静养鱼 - 自习神器
模块化重构版
"""

# ============ 窗口配置 ============
WIDTH, HEIGHT = 900, 650
FPS = 60
BG_COLOR = (20, 30, 50)
WATER_TOP = 90

# ============ 番茄钟配置 ============
POMODORO_WORK_MINUTES = 25
POMODORO_BREAK_MINUTES = 5

# ============ 声音配置 ============
SILENCE_THRESHOLD = 500
MAX_FISH = 25
MIN_FISH = 0
FISH_FLEE_SPEED = 2.5

# ============ 音频监控配置 ============
AUDIO_SAMPLE_RATE = 44100
AUDIO_BUFFER_SIZE = 1024
AUDIO_SMOOTH_FRAMES = 30
AUDIO_RMS_DIVISOR = 50  # 用于将 RMS 转换为 0-100 的音量
AUDIO_MAX_VOLUME = 100

# ============ 鱼的行为配置 ============
FISH_INITIAL_COUNT = 6
FISH_BUBBLE_CHANCE = 0.25
BUBBLE_SPAWN_CHANCE = 0.015
FISH_GLOW_AGE_THRESHOLD = 0.3  # 鱼需要显示多久后才显示发光效果

# ============ 时间配置 ============
NIGHT_START_HOUR = 23
NIGHT_END_HOUR = 6

# ============ 文件路径 ============
DATA_DIR = "data"
STATS_FILE = "stats.json"
ACHIEVEMENTS_FILE = "achievements.json"

# ============ 稀有度定义 ============
RARITY = {
    "common": {
        "name": "普通",
        "colors": [(100, 200, 255), (100, 255, 200), (150, 200, 150)],
        "size": (18, 26),
        "weight": 55,
        "threshold": 1.0,
        "speed": 0.8,
        "glow": False,
        "points": 10
    },
    "rare": {
        "name": "稀有",
        "colors": [(180, 130, 255), (130, 180, 255)],
        "size": (22, 30),
        "weight": 25,
        "threshold": 0.85,
        "speed": 1.0,
        "glow": True,
        "glow_color": (200, 150, 255, 100),
        "points": 50
    },
    "epic": {
        "name": "史诗",
        "colors": [(255, 100, 150), (255, 150, 100)],
        "size": (28, 38),
        "weight": 12,
        "threshold": 0.7,
        "speed": 1.2,
        "glow": True,
        "glow_color": (255, 100, 100, 120),
        "points": 200
    },
    "legendary": {
        "name": "传说",
        "colors": [(255, 215, 0)],
        "size": (35, 45),
        "weight": 5,
        "threshold": 0.5,
        "speed": 1.5,
        "glow": True,
        "glow_color": (255, 215, 0, 150),
        "points": 1000
    },
    "mythic": {
        "name": "神话",
        "colors": [(255, 255, 255), (0, 255, 255)],
        "size": (42, 55),
        "weight": 3,
        "threshold": 0.35,
        "speed": 1.8,
        "glow": True,
        "glow_color": (0, 255, 255, 180),
        "points": 5000
    }
}

# 稀有度权重列表（用于快速查找）
RARITY_WEIGHTS = []
for key, data in RARITY.items():
    for _ in range(data["weight"]):
        RARITY_WEIGHTS.append(key)

# ============ 成就定义 ============
ACHIEVEMENTS = {
    "first_fish": {"name": "初次见面", "desc": "获得第一条鱼", "icon": "🐟"},
    "rare_hunter": {"name": "稀有猎人", "desc": "获得第一条稀有鱼", "icon": "💎"},
    "collector_10": {"name": "鱼类收藏家", "desc": "同时拥有10条鱼", "icon": "📗"},
    "collector_20": {"name": "水族馆馆长", "desc": "同时拥有20条鱼", "icon": "📚"},
    "legendary_sight": {"name": "见证传说", "desc": "获得第一条传说鱼", "icon": "👑"},
    "quiet_master": {"name": "安静大师", "desc": "累计安静1小时", "icon": "🕊️"},
    "focus_warrior": {"name": "专注战士", "desc": "完成5个番茄钟", "icon": "⚔️"},
    "night_owl": {"name": "夜猫子", "desc": "深夜时段（23-6点）使用", "icon": "🦉"},
    "streak_3": {"name": "三天打鱼", "desc": "连续3天使用", "icon": "📅"},
    "total_fish_100": {"name": "百鱼斩", "desc": "累计获得100条鱼", "icon": "🔪"},
}

# ============ 等级定义 ============
LEVELS = [
    {"level": 1, "name": "新手", "min_points": 0},
    {"level": 2, "name": "学徒", "min_points": 500},
    {"level": 3, "name": "修士", "min_points": 1500},
    {"level": 4, "name": "术士", "min_points": 3000},
    {"level": 5, "name": "大法师", "min_points": 6000},
    {"level": 6, "name": "安静之神", "min_points": 12000},
]
