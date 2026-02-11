# 安静养鱼 - 自习神器

一个有趣的自律工具：保持安静，鱼才会留下来陪你学习 🎓

## 效果

- 🔇 **安静** → 鱼儿游来陪你
- 🔊 **太吵** → 鱼都跑光了

## 安装

```bash
# 克隆后
cd quiet_fish

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 依赖

- pygame >= 2.0
- PyAudio

## TODO

- [ ] 不同稀有度的鱼（金色鱼更难养）
- [ ] 安静时长统计/成就系统
- [ ] 背景白噪音
- [ ] 音效
