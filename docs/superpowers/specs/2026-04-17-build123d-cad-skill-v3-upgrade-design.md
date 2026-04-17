# build123d-cad Skill v3 升级设计

**日期**：2026-04-17
**触发背景**：test 13（Redmi K80 Pro 手机壳）和 test 14（Xiaomi K70 手机壳）的参考物建模实战暴露了 skill 的三类缺口：视觉验证工具是一次性脚本、没有 STEP 模型时的反推方法论没沉淀、SKILL.md 已达 1556 行有组织压力。

---

## 1. 升级目标

把 test 13 实战中开发的临时工具和方法论，按 P0→P2 优先级固化成 skill 的复用资产。**不做 SKILL.md 骨架重构**，只做增量升级。

### 1.1 交付边界

- ✅ SKILL.md 小幅修改 + 新增 references/scripts
- ❌ 不重写 SKILL.md 整体架构
- ❌ 不做 cad-vision-verify 姊妹 skill 的实现（已有独立设计文档）

### 1.2 升级后预期

- test 13 output 目录里的 4 个脚本 → skill 标准工具链，后续任何参考物建模都能调用
- 参考物反推尺寸的方法论从 "K80 Pro 案例" → 可复用的 5 种手段
- SKILL.md 从 1556 行 → 约 900 行（P2 可选）

---

## 2. 架构总览

```
build123d-cad/
├── SKILL.md                               # 主文档（P2 可选瘦身）
├── scripts/
│   └── visual/                            # 🆕 P0 新增目录
│       ├── multi_view_screenshot.py       # 🆕 P0 标准 6+1 视图
│       ├── skybox_unfold.py               # 🆕 P0 十字展开
│       ├── visual_compare.py              # 🆕 P0 边缘对比 + 差异热图
│       ├── pixel_measure.py               # 🆕 P0 像素测量反推
│       └── annotate_reference.py          # 🆕 P1 参考图标注模板
└── references/
    ├── verify/
    │   ├── multi-view-protocol.md         # 🆕 P0 7 视图规范
    │   └── edge-comparison.md             # 🆕 P0 判定阈值表
    ├── reference-product/                 # 🆕 P1 新增目录
    │   ├── reverse-engineering.md         # 🆕 P1 5 种反推手段
    │   └── photo-annotation.md            # 🆕 P1 标注规范
    └── parts/
        ├── geometric-alignment.md         # 🆕 P2 抽 Step 1.5 代码
        └── pitfalls.md                    # 🆕 P2 抽坑点详解
```

### 2.1 模块关系

```
收到参考物需求
    │
    ├──► Step R1~R3 收集资料 (SKILL.md 原流程)
    │
    ├──► Step R2.5 无 STEP 时反推 ──► references/reference-product/reverse-engineering.md
    │                                  │
    │                                  ├──► scripts/visual/annotate_reference.py
    │                                  └──► scripts/visual/pixel_measure.py
    │
    ├──► Step R3.5 合同生成 (SKILL.md 原流程)
    │
    ├──► Step R4 建模 + Layer 0/1 验证 (SKILL.md 原流程)
    │
    └──► Step R4.5 Layer 2 视觉验证 🆕
             │
             ├──► scripts/visual/multi_view_screenshot.py  (生成 7 视图)
             ├──► scripts/visual/skybox_unfold.py          (拼十字全景)
             └──► scripts/visual/visual_compare.py         (边缘对比)
                     │
                     └──► references/verify/edge-comparison.md (判定阈值)
```

---

## 3. P0 详细设计：视觉验证工具链

### 3.1 `multi_view_screenshot.py`

**CLI 接口**：
```bash
python3 scripts/visual/multi_view_screenshot.py <input.step | input.py> [--output-dir PATH] [--name NAME] [--views FRONT,BACK,...]
```

**实现要点**：
- 依赖运行中的 OCP Viewer（`get_ports()` + `port_check()` 探测端口）
- 6 个正交视图用 OCP `Camera.FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM`，无需旋转模型
- ISO 视图用 `Camera.ISO`
- 每次 show 后 `time.sleep(0.8~1.0)` 等渲染
- 用 `save_screenshot()` API
- 文件命名：`{name}_{VIEW}.png`，VIEW ∈ {FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, ISO}

**不使用的方案**（已验证不走这条路）：
- ❌ VTK 离屏渲染：引入新依赖，违反 skill 零新依赖原则
- ❌ matplotlib 3D：建模精度不够，不是为 CAD 渲染设计

### 3.2 `skybox_unfold.py`

**CLI 接口**：
```bash
python3 scripts/visual/skybox_unfold.py <input.step | input.py> [--output-dir PATH] [--center FRONT]
```

**核心算法**（test 13 实测可行）：**相机固定 + 旋转模型**

```python
face_rotations = {
    "FRONT": [(Axis.X, 90)],
    "BACK":  [(Axis.X, 90), (Axis.Z, 180)],   # 第二步 Z 翻转避免摄像头左右镜像
    "UP":    [(Axis.X, 180)],
    "DOWN":  [],
    "LEFT":  [(Axis.Z, 90)],
    "RIGHT": [(Axis.Z, -90)],
}
for face, rots in face_rotations.items():
    m = model
    for axis, deg in rots:
        m = m.rotate(axis, deg)
    show(m, names=[f"skybox_{face}"], reset_camera=Camera.FRONT)
    time.sleep(0.8)
    save_screenshot(f"skybox_{face}.png")
```

**为什么这样**：保证 6 张图的光照/透视完全一致，对比时不会有相机参数偏差。

**后处理**：
- PIL 加载 → 自动裁白边（`mask < 250` 阈值 + pad=20）
- 统一每格尺寸（最大 700×500，画布上限 2800×1500）
- 十字布局拼接：
  ```
          [  TOP  ]
  [LEFT ][ FRONT ][RIGHT][ BACK]
          [BOTTOM ]
  ```
- 输出 `skybox_unfolded.png`

### 3.3 `visual_compare.py`

**CLI 接口**：
```bash
python3 scripts/visual/visual_compare.py <rendered.png> <reference.png> [--mode MODE] [--output PATH]
# MODE: side_by_side | edge_overlay | diff_heatmap
```

**3 种模式**：

1. **side_by_side**：Matplotlib subplot(1,2)，左=渲染图，右=参考图，图像尺寸对齐
2. **edge_overlay**：Canny 边缘提取 → 红色（参考）+ 蓝色（模型）叠加 → 吻合处显紫色
3. **diff_heatmap**：灰度差绝对值 → colormap='hot' 热图

**Canny 参数**（实测可行）：`low=50, high=150`，高斯模糊 `sigma=1.0`

### 3.4 `pixel_measure.py`

**CLI 接口**：
```bash
python3 scripts/visual/pixel_measure.py <image.png> --scale "162.2mm/<pixel>" [--interactive]
```

**两种工作模式**：
- **interactive**：matplotlib 点击事件收集坐标，实时显示"点击点 → 实际毫米"
- **batch**：CLI 提供像素坐标列表 → 输出 CSV

**需要人工输入的**：比例尺（通常是"已知手机总长 = XXX mm = YYY 像素"）

### 3.5 `references/verify/multi-view-protocol.md`

**内容大纲**：
- 7 视图的规范和命名（FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM/ISO）
- 何时用 skybox（多特征、全面审查）vs 只用 ISO（单部件快速预览）
- 分辨率 800×800 / 背景白色 / 光照标准
- 模型旋转 vs 相机移动的取舍

### 3.6 `references/verify/edge-comparison.md`

**核心是判定阈值表**：

| 指标 | 通过 ✅ | 警告 ⚠️ | 失败 ❌ |
|---|---|---|---|
| 边缘 IoU | ≥ 0.85 | 0.70~0.85 | < 0.70 |
| 尺寸偏差（bbox） | ≤ 2% | 2%~5% | > 5% |
| 关键特征位置 | ≤ 2mm | 2~5mm | > 5mm |

**附带内容**：失败诊断路径（尺寸错 → 回 R3；位置错 → 回 R3.5；比例错 → 回 R2）

**注**：阈值为第一版建议值，test 14/15 积累更多案例后应复核调整。

### 3.7 SKILL.md 的 P0 修改

**位置**：Step R4 / Layer 2 视觉比对段落

**新增内容**：
```markdown
### Layer 2 视觉验证标准工具链（test 13 沉淀）

生成 7 视图 + skybox + 参考图对比：

```bash
# Step 1: 生成 7 张标准视图
python3 scripts/visual/multi_view_screenshot.py <step_path> --output-dir output/

# Step 2: 拼成 skybox 十字全景
python3 scripts/visual/skybox_unfold.py <step_path> --output-dir output/

# Step 3: 渲染图 vs 参考图边缘对比
python3 scripts/visual/visual_compare.py \
    output/xxx_FRONT.png refs/front.png \
    --mode edge_overlay \
    --output output/compare_front.png
```

判定阈值见 `references/verify/edge-comparison.md`
```

---

## 4. P1 详细设计：参考物反推方法论

### 4.1 `references/reference-product/reverse-engineering.md`

**核心表格——5 种反推手段按置信度**：

| 手段 | 输入 | 精度 | 适用场景 | 对应脚本 |
|---|---|---|---|---|
| A. STEP 导入 | model.step | ★★★★★ | GrabCAD 能搜到 | `import_step()` |
| B. 三视图比例反推 | 官方三视图 PNG | ★★★★ | 官网有高清产品图 | `pixel_measure.py` |
| C. 已知基准测量 | 实拍 + 已知尺寸 | ★★★ | 电商详情页实拍 | `pixel_measure.py` |
| D. 特征比例推断 | 单张正面图 | ★★ | 只有一张图 | 手动估算 |
| E. 拆解视频截帧 | 拆机视频帧 | ★★★ | iFixit/B站拆解 | `pixel_measure.py` |

**每种手段的完整操作步骤**（以 B 为例）：
```
1. 找到官方三视图 PNG（背景纯色，无透视畸变）
2. 用 pixel_measure.py 标注 4 个角点，获取图像到实际毫米的比例
3. 标注关键特征（摄像头、按键）的像素坐标
4. 换算成以部件中心为原点的 (cx, cy) 坐标
5. 写入 params.md 的"摄像头模组位置"行，标 ★★★★ 置信度
```

**失败兜底**：5 种手段全部不可用时，让用户手动测量 + 提供测量位置清单。

### 4.2 `references/reference-product/photo-annotation.md`

**标注规范**（和 test 13 的 `photo_annotated.png` / `side_annotated.png` 对齐）：

- Matplotlib 在原图上叠加：坐标原点、尺寸标注线、特征区域框
- **颜色约定**：
  - 🔵 蓝色 = 已确认尺寸（来自官网）
  - 🔴 红色 = 反推尺寸（来自像素测量）
  - 🟡 黄色 = 待确认
- **产出文件命名**：`{face}_annotated.png`（back/side/front/bottom）

### 4.3 `scripts/visual/annotate_reference.py`

**CLI 接口**：
```bash
python3 scripts/visual/annotate_reference.py <photo.png> --annotations FILE.json [--output PATH]
```

**annotations.json 示例**：
```json
{
  "scale": {"pixels": 1080, "mm": 162.2},
  "origin": [540, 820],
  "features": [
    {"name": "摄像头模组", "center_px": [320, 150], "size_mm": [38, 38], "confidence": 4, "color": "red"},
    {"name": "电源键", "center_px": [1000, 500], "size_mm": [6, 20], "confidence": 5, "color": "blue"}
  ]
}
```

脚本渲染成 `{photo}_annotated.png`（Matplotlib 叠加）。

### 4.4 SKILL.md 的 P1 修改

**位置**：Step R2 兜底段下方

**新增 Step R2.5**：
```markdown
### Step R2.5 — 没有 STEP 模型时的反推流程

官网未提供 STEP 且 GrabCAD 未收录时，按以下顺序尝试：

1. 先跑手段 B（三视图比例反推）— 成本最低，通常够用
2. 再跑手段 C（已知基准测量）— 用电商详情页实拍补关键特征
3. 兜底 D（特征比例推断）— 精度 ★★，务必标注低置信度

反推完成后，params.md 的置信度列必须如实填写（不要伪造 ★★★★★）。

详见 references/reference-product/reverse-engineering.md
```

---

## 5. P2 详细设计：SKILL.md 局部瘦身（可选）

### 5.1 抽出内容表

| 当前位置（SKILL.md） | 行范围 | 目标位置 |
|---|---|---|
| Step 1.5 方案 A~E 完整代码 | L446~657（~210 行） | `references/parts/geometric-alignment.md` |
| 大型非凸多边形章节 | L1021~1071（~50 行） | `references/parts/pitfalls.md` |
| RevoluteJoint 帧对齐陷阱 | L1298~1347（~50 行） | `references/parts/pitfalls.md` |
| OCP Animation 关节路径规则 | L1349~1368（~20 行） | `references/parts/pitfalls.md` |

### 5.2 SKILL.md 保留形式

Step 1.5 简化为触发词表 + 一句话描述 + 链接：

```markdown
### Step 1.5：几何对齐（5 种方案）

触发方式：方案 A（3视图草图）默认执行；B/C/D/E 需用户触发。

| 方案 | 触发词 | 最适合 | 参考 |
|---|---|---|---|
| A. 3视图草图 | 默认 | 所有场景 | alignment.md#A |
| B. OCP 占位块 | 「先看比例」 | 多部件装配 | alignment.md#B |
| C. 关键截面 | 「画截面」 | 旋转/扫掠件 | alignment.md#C |
| D. 参考图标注 | 「解读一下图」 | 有参考图时 | alignment.md#D |
| E. 参数合同 | 「先确认参数」 | 精度配合 | alignment.md#E |

完整代码模板见 references/parts/geometric-alignment.md
```

### 5.3 行数预估

- 当前：1556 行
- P2 后：~900 行
- 降幅：~42%

### 5.4 P2 的取舍风险

- ⚠️ SKILL.md 现在是一个整体文档，LLM 读起来流畅；拆开后 LLM 要多跳转 references 才能完整理解
- ⚠️ 跳转成本 vs 加载成本：目前 1556 行仍在 context 可接受范围，做 P2 瘦身不是刚需

**建议**：P0 + P1 完成后再评估 P2 是否执行。

---

## 6. 风险 & 诚实边界

### 6.1 已识别风险

1. **P0 依赖运行中的 OCP Viewer**：无头 CI 环境跑不了，但 skill 本来就定位"人在环"工作流，可接受
2. **P1 反推方法论只有 K80 Pro N=1 样本**：test 14/15 完成后应回顾方法论并补充案例
3. **P0 判定阈值是第一版**：IoU ≥ 0.85 / 偏差 ≤ 2% 等数值需积累更多实测后复核
4. **P2 可能降低 LLM 阅读连贯性**：建议延后决策

### 6.2 非目标

- 不做完全无头渲染（需要 VTK/matplotlib-3d 新依赖，违反零依赖原则）
- 不实现 cad-vision-verify 姊妹 skill（有独立设计文档）
- 不重写 SKILL.md 整体架构

---

## 7. 完整升级清单

| 优先级 | 新增/修改文件 | 改动量 |
|---|---|---|
| P0 | `scripts/visual/multi_view_screenshot.py` | 新增 ~200 行 |
| P0 | `scripts/visual/skybox_unfold.py` | 新增 ~150 行（含 PIL 拼接） |
| P0 | `scripts/visual/visual_compare.py` | 新增 ~250 行 |
| P0 | `scripts/visual/pixel_measure.py` | 新增 ~120 行 |
| P0 | `references/verify/multi-view-protocol.md` | 新增 |
| P0 | `references/verify/edge-comparison.md` | 新增 |
| P0 | SKILL.md Layer 2 桥接段 | 改 ~15 行 |
| P1 | `references/reference-product/reverse-engineering.md` | 新增 |
| P1 | `references/reference-product/photo-annotation.md` | 新增 |
| P1 | `scripts/visual/annotate_reference.py` | 新增 ~150 行 |
| P1 | SKILL.md Step R2.5 新段 | 新增 ~30 行 |
| P2（可选） | `references/parts/geometric-alignment.md` | 抽取 ~210 行 |
| P2（可选） | `references/parts/pitfalls.md` | 抽取 ~120 行 |
| P2（可选） | SKILL.md 对应段落瘦身 | 删 ~600 行，加 40 行链接 |

---

## 8. 实施顺序建议

1. **先做 P0 的 4 个脚本**（核心收益，改动隔离）
2. **并行做 P0 的两份 references**
3. **更新 SKILL.md P0 桥接段**（这一步让工具真正被 skill 引用）
4. **用当前 test 14（K70 案例）实测 P0 工具链**，确保开箱能用
5. **P1 随 test 15 的新案例一起做**（有实战样本才能写准方法论）
6. **P2 延后到 P0+P1 完成后再评估**

---

## 9. 验收标准

- ✅ 在 test 14（K70）目录下可直接调用 P0 工具链生成 7 视图 + skybox + 对比图，不需要再写一次性脚本
- ✅ P1 references 文档能直接指导"只有照片没有 STEP"场景的下一个参考物建模
- ✅ SKILL.md 的 Step R2.5 和 Layer 2 桥接段能被 LLM 正确触发调用对应工具
- ✅ 所有新脚本在代码末尾都有 OCP 自动预览块（沿用 skill 现有规则）

---

## 10. 参考资料

- test 13 实战产出：`/Users/liyijiang/work/build123d-cad-skill-test/tests/13-redmi-k80-pro/`
- 现有 skill：`/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（1556 行）
- 姊妹 skill 设计：cad-vision-verify（独立文档）
