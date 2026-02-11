"""数据统计模块"""
import json
import os
from datetime import datetime, timedelta
from config import ACHIEVEMENTS, LEVELS


class StatsManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.stats_file = os.path.join(data_dir, "stats.json")
        self.achievements_file = os.path.join(data_dir, "achievements.json")

        self.stats = self.load_stats()
        self.achievements = self.load_achievements()

    def load_stats(self):
        default = {
            "total_quiet_seconds": 0,
            "total_fish_caught": 0,
            "fish_by_rarity": {},
            "pomodoro_completed": 0,
            "streak_days": 0,
            "last_used_date": None,
            "total_sessions": 0,
            "points": 0
        }
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 合并默认配置，确保新字段存在
                    for key in default:
                        if key not in data:
                            data[key] = default[key]
                    return data
            except:
                pass
        return default

    def save_stats(self):
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def load_achievements(self):
        default = {k: False for k in ACHIEVEMENTS.keys()}
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key in default:
                        if key in data:
                            default[key] = data[key]
            except:
                pass
        return default

    def save_achievements(self):
        with open(self.achievements_file, 'w', encoding='utf-8') as f:
            json.dump(self.achievements, f, ensure_ascii=False, indent=2)

    def record_quiet_time(self, seconds):
        self.stats["total_quiet_seconds"] += seconds
        self.stats["points"] += seconds // 10  # 每10秒安静得1分

    def record_fish(self, fish):
        self.stats["total_fish_caught"] += 1
        rarity = fish.rarity
        if rarity not in self.stats["fish_by_rarity"]:
            self.stats["fish_by_rarity"][rarity] = 0
        self.stats["fish_by_rarity"][rarity] += 1
        self.stats["points"] += fish.points

    def record_pomodoro(self):
        self.stats["pomodoro_completed"] += 1
        self.stats["points"] += 300  # 番茄钟完成得300分

    def check_streak(self):
        today = datetime.now().date()
        if self.stats["last_used_date"]:
            last_date = datetime.fromisoformat(self.stats["last_used_date"]).date()
            if last_date == today:
                return
            elif (today - last_date).days == 1:
                self.stats["streak_days"] += 1
            else:
                self.stats["streak_days"] = 1
        else:
            self.stats["streak_days"] = 1
        self.stats["last_used_date"] = today.isoformat()
        self.stats["total_sessions"] += 1

    def get_level(self):
        points = self.stats["points"]
        for level in reversed(LEVELS):
            if points >= level["min_points"]:
                return level
        return LEVELS[0]

    def check_achievements(self, fish_count, quiet_hours_total, is_night=False):
        new_achievements = []

        # 检查新成就
        checks = [
            ("first_fish", self.stats["total_fish_caught"] >= 1),
            ("rare_hunter", self.stats["fish_by_rarity"].get("rare", 0) >= 1),
            ("collector_10", fish_count >= 10),
            ("collector_20", fish_count >= 20),
            ("legendary_sight", self.stats["fish_by_rarity"].get("legendary", 0) >= 1),
            ("quiet_master", quiet_hours_total >= 3600),
            ("focus_warrior", self.stats["pomodoro_completed"] >= 5),
            ("night_owl", is_night),
            ("streak_3", self.stats["streak_days"] >= 3),
            ("total_fish_100", self.stats["total_fish_caught"] >= 100),
        ]

        for key, condition in checks:
            if condition and not self.achievements.get(key, False):
                self.achievements[key] = True
                new_achievements.append(key)

        if new_achievements:
            self.save_achievements()
            self.save_stats()

        return new_achievements

    def get_summary(self):
        return {
            "level": self.get_level(),
            "points": self.stats["points"],
            "quiet_hours": self.stats["total_quiet_seconds"] / 3600,
            "total_fish": self.stats["total_fish_caught"],
            "pomodoro_count": self.stats["pomodoro_completed"],
            "streak": self.stats["streak_days"],
            "achievements_unlocked": sum(1 for v in self.achievements.values() if v),
            "total_achievements": len(ACHIEVEMENTS)
        }
