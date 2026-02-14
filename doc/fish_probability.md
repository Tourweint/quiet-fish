# 安静养鱼 - 鱼出现概率文档

## 概述
本文档详细说明游戏中各个时间段不同稀有度鱼的出现概率，方便开发者针对不同情况进行调整。

---

## 一、品质解锁系统（基于累计安静时间）

| 累计安静时间 | 解锁品质 | 说明 |
|-------------|---------|------|
| 0-2分钟 | 普通 (common) | 只有最基础的鱼 |
| 2-5分钟 | 稀有 (rare) | 解锁稀有品质 |
| 5-10分钟 | 史诗 (epic) | 解锁史诗品质 |
| 10-20分钟 | 传说 (legendary) | 解锁传说品质 |
| 20-30分钟 | 神话 (mythic) | 解锁最高品质 |

**代码位置**: [main.py#L210-L225](file:///d:\Gitproject\quiet-fish\main.py#L210-L225)

```python
# === 基于累计安静时间的品质解锁系统 ===
# 30分钟(1800秒)内渐进解锁高品质鱼
quiet_minutes = self.session_quiet_time / 60

# 根据累计安静时间确定可出现的最高品质
# 0-2分钟：只有普通
# 2-5分钟：解锁稀有
# 5-10分钟：解锁史诗
# 10-20分钟：解锁传说
# 20-30分钟：解锁神话
if quiet_minutes < 2:
    max_unlocked_rarity = "common"
elif quiet_minutes < 5:
    max_unlocked_rarity = "rare"
elif quiet_minutes < 10:
    max_unlocked_rarity = "epic"
elif quiet_minutes < 20:
    max_unlocked_rarity = "legendary"
else:
    max_unlocked_rarity = "mythic"
```

---

## 二、各时间段鱼出现概率

### 2.1 基础权重配置

**代码位置**: [main.py#L237-L243](file:///d:\Gitproject\quiet-fish\main.py#L237-L243)

```python
# 基础权重 - 调整后30分钟高品质概率更高
base_weights = {
    "common": 35,
    "rare": 30,
    "epic": 20,
    "legendary": 10,
    "mythic": 5
}
```

### 2.2 各时间段实际概率计算

概率计算公式：
- `time_factor = min(1.0, quiet_minutes / 30)` （0-1之间，30分钟达到最大）
- 各品质权重会根据时间因子动态调整
- 最终概率 = 该品质权重 / 所有可用品质权重之和

#### 时间段 1: 0-2分钟（仅普通鱼）

| 品质 | 权重 | 概率 |
|-----|------|------|
| 普通 | 35 | **100%** |
| 稀有 | 未解锁 | 0% |
| 史诗 | 未解锁 | 0% |
| 传说 | 未解锁 | 0% |
| 神话 | 未解锁 | 0% |

#### 时间段 2: 2-5分钟（普通 + 稀有）

**时间因子**: 0.067 - 0.167

| 品质 | 权重计算公式 | 近似权重 | 概率 |
|-----|-------------|---------|------|
| 普通 | 35 × (1 - time_factor × 0.7) | 33.2 - 34.2 | **53-55%** |
| 稀有 | 30 × (1 + time_factor × 0.2) | 30.4 - 31.0 | **48-50%** |
| 史诗 | 未解锁 | - | 0% |
| 传说 | 未解锁 | - | 0% |
| 神话 | 未解锁 | - | 0% |

#### 时间段 3: 5-10分钟（普通 + 稀有 + 史诗）

**时间因子**: 0.167 - 0.333

| 品质 | 权重计算公式 | 近似权重 | 概率 |
|-----|-------------|---------|------|
| 普通 | 35 × (1 - time_factor × 0.7) | 26.8 - 30.9 | **35-41%** |
| 稀有 | 30 × (1 + time_factor × 0.2) | 31.0 - 32.0 | **40-42%** |
| 史诗 | 20 × (1 + time_factor × 0.6) | 22.0 - 24.0 | **28-32%** |
| 传说 | 未解锁 | - | 0% |
| 神话 | 未解锁 | - | 0% |

#### 时间段 4: 10-20分钟（普通 + 稀有 + 史诗 + 传说）

**时间因子**: 0.333 - 0.667

| 品质 | 权重计算公式 | 近似权重 | 概率 |
|-----|-------------|---------|------|
| 普通 | 35 × (1 - time_factor × 0.7) | 18.7 - 26.8 | **22-32%** |
| 稀有 | 30 × (1 + time_factor × 0.2) | 32.0 - 34.0 | **37-40%** |
| 史诗 | 20 × (1 + time_factor × 0.6) | 24.0 - 28.0 | **28-33%** |
| 传说 | 10 × (1 + time_factor × 4) | 23.3 - 36.7 | **27-43%** |
| 神话 | 未解锁 | - | 0% |

#### 时间段 5: 20-30分钟（全品质解锁）

**时间因子**: 0.667 - 1.0

| 品质 | 权重计算公式 | 近似权重 | 概率 |
|-----|-------------|---------|------|
| 普通 | 35 × (1 - time_factor × 0.7) | 10.5 - 18.7 | **11-20%** |
| 稀有 | 30 × (1 + time_factor × 0.2) | 34.0 - 36.0 | **36-38%** |
| 史诗 | 20 × (1 + time_factor × 0.6) | 28.0 - 32.0 | **30-34%** |
| 传说 | 10 × (1 + time_factor × 4) | 36.7 - 50.0 | **39-53%** |
| 神话 | 5 × (1 + time_factor × 8) | 31.7 - 45.0 | **33-48%** |

---

## 三、加鱼难度系统

### 3.1 所需积分计算

**代码位置**: [main.py#L227-L230](file:///d:\Gitproject\quiet-fish\main.py#L227-L230)

```python
# 根据累计时间调整加鱼难度（越往后越难加，但品质越高）
# 基础需要积分：10点
# 每过5分钟增加5点难度
difficulty_increase = int(quiet_minutes / 5) * 5
self.current_required_score = 10 + difficulty_increase
```

| 累计安静时间 | 所需安静积分 | 说明 |
|-------------|-------------|------|
| 0-5分钟 | 10 | 基础难度 |
| 5-10分钟 | 15 | 难度增加 |
| 10-15分钟 | 20 | 难度继续增加 |
| 15-20分钟 | 25 | 较高难度 |
| 20-25分钟 | 30 | 高难度 |
| 25-30分钟 | 35 | 最高难度 |

### 3.2 积分积累速度

**代码位置**: [main.py#L183-L195](file:///d:\Gitproject\quiet-fish\main.py#L183-L195)

```python
# 安静度：0-1，越安静越接近1
quietness = 1 - (normalized_volume ** 0.5)

# 基础积累速度：每秒积累 0.3-0.8 点权重（很慢）
base_accumulation = 0.3 + quietness * 0.5
net_weight_change = base_accumulation * time_delta
```

- **最安静时** (volume=0): 每秒积累 0.8 点
- **半安静时** (volume=20): 每秒积累约 0.55 点
- **接近阈值时** (volume=35): 每秒积累约 0.35 点

---

## 四、稀有度配置详情

**代码位置**: [config.py#L55-L103](file:///d:\Gitproject\quiet-fish\config.py#L55-L103)

| 品质 | 中文名 | 尺寸 | 速度 | 发光 | 积分 |
|-----|-------|------|------|------|------|
| common | 普通 | 18-26 | 0.8x | 否 | 10 |
| rare | 稀有 | 22-30 | 1.0x | 是 | 50 |
| epic | 史诗 | 28-38 | 1.2x | 是 | 200 |
| legendary | 传说 | 35-45 | 1.5x | 是 | 1000 |
| mythic | 神话 | 42-55 | 1.8x | 是 | 5000 |

---

## 五、吵闹时鱼的移除规则

**代码位置**: [main.py#L317-L330](file:///d:\Gitproject\quiet-fish\main.py#L317-L330)

```python
elif not self.is_quiet and len(fish_list) > 0:
    # 吵闹时：快速失去鱼，从高品质开始
    remove_chance = (1 - quietness) * dt * 2  # 每秒可能移除2条
    if random.random() < remove_chance:
        # 按稀有度从高到低移除
        for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
            if rarity_counts[rarity] > 0:
                # 找到并移除该稀有度的鱼
                for i, fish in enumerate(fish_list):
                    if fish.rarity == rarity:
                        fish_list.pop(i)
                        break
                break  # 每次只移除一条
```

**移除优先级**: 神话 → 传说 → 史诗 → 稀有 → 普通

---

## 六、开发者调整指南

### 6.1 调整品质解锁时间

如需修改某个品质解锁所需的安静时间，编辑 [main.py#L210-L225](file:///d:\Gitproject\quiet-fish\main.py#L210-L225)：

```python
if quiet_minutes < 2:      # ← 修改这里的分钟数
    max_unlocked_rarity = "common"
elif quiet_minutes < 5:    # ← 修改这里的分钟数
    max_unlocked_rarity = "rare"
# ... 以此类推
```

### 6.2 调整基础权重

如需修改各品质的基础出现权重，编辑 [main.py#L237-L243](file:///d:\Gitproject\quiet-fish\main.py#L237-L243)：

```python
base_weights = {
    "common": 35,      # ← 修改数值
    "rare": 30,        # ← 修改数值
    "epic": 20,        # ← 修改数值
    "legendary": 10,   # ← 修改数值
    "mythic": 5        # ← 修改数值
}
```

### 6.3 调整时间对权重的影响

如需修改随着时间推移各品质权重的变化幅度，编辑 [main.py#L248-L262](file:///d:\Gitproject\quiet-fish\main.py#L248-L262)：

```python
if rarity == "common":
    rarity_weights[rarity] = base_weights[rarity] * (1 - time_factor * 0.7)  # ← 修改 0.7
elif rarity == "rare":
    rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 0.2)  # ← 修改 0.2
elif rarity == "epic":
    rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 0.6)  # ← 修改 0.6
elif rarity == "legendary":
    rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 4)    # ← 修改 4
elif rarity == "mythic":
    rarity_weights[rarity] = base_weights[rarity] * (1 + time_factor * 8)    # ← 修改 8
```

### 6.4 调整加鱼难度

如需修改加鱼所需的积分增长规则，编辑 [main.py#L227-L230](file:///d:\Gitproject\quiet-fish\main.py#L227-L230)：

```python
# 基础需要积分：10点
# 每过5分钟增加5点难度  ← 修改这里的数值
difficulty_increase = int(quiet_minutes / 5) * 5
self.current_required_score = 10 + difficulty_increase
```

### 6.5 调整积分积累速度

如需修改安静时积分积累的速度，编辑 [main.py#L188-L189](file:///d:\Gitproject\quiet-fish\main.py#L188-L189)：

```python
# 基础积累速度：每秒积累 0.3-0.8 点权重（很慢）
base_accumulation = 0.3 + quietness * 0.5  # ← 修改 0.3 和 0.5
```

---

## 七、总结

| 时间段 | 可获得的最高品质 | 加鱼难度 | 高品质概率 |
|-------|----------------|---------|-----------|
| 0-2分钟 | 普通 | 10积分 | 极低 |
| 2-5分钟 | 稀有 | 10积分 | 低 |
| 5-10分钟 | 史诗 | 15积分 | 中 |
| 10-20分钟 | 传说 | 20-25积分 | 较高 |
| 20-30分钟 | 神话 | 30-35积分 | 高 |

**设计意图**：
1. 鼓励用户保持长时间安静
2. 随着安静时间增加，鱼的数量增长变慢但品质提升
3. 吵闹会优先移除高品质鱼，形成正向激励
