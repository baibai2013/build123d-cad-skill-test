# CAD Vision Verify Skill — Design Spec

> CAD 模型视觉验证与参数诊断。对比模型截图与参考图，输出偶合度评分 + 根因诊断 + 修复路由。

**Date**: 2026-04-16
**Status**: Draft
**Skill path**: `/Users/liyijiang/.agents/skills/cad-vision-verify/`

---

## 1. Problem Statement

AI 生成的 CAD 模型（手机壳、配件等）经常「参数看着对但形状不对」。Layer 1 参数验证只能检查数值，无法回答「看起来对不对」。需要一个视觉比对 + 根因诊断的闭环系统。

### 核心需求

1. **视觉比对**：CAD 模型截图 vs 参考图（产品照片），输出结构化偏差报告
2. **根因诊断**：偏差来自数据源(A)、合同(B)还是代码(C)，给出修复路由
3. **自动降级**：根据环境自动选择最佳比对后端（Vision API → OpenCV → 人工）
4. **独立可复用**：作为独立 skill，build123d-cad 调用它，其他 CAD 工具也能用

---

## 2. Architecture

### 2.1 Skill 文件结构

```
/Users/liyijiang/.agents/skills/cad-vision-verify/
├── SKILL.md              — skill 定义 + 工作流协议
├── scripts/
│   ├── vision_probe.py   — Vision API 代理兼容性探测（缓存 24h）
│   ├── screenshot.py     — OCP 7 视角自动截图
│   ├── compare.py        — 三模式比对引擎 (Vision/OpenCV/Manual)
│   ├── diagnose.py       — 根因诊断 A/B/C + 修复路由
│   └── verify_loop.py    — 完整验证-修复闭环入口
└── references/
    ├── constraint-types.md  — 约束类型速查
    └── examples/
        └── k70-report.json  — 示例验证报告
```

### 2.2 与 build123d-cad 的关系

```
build123d-cad (建模侧)          cad-vision-verify (验证侧)
─────────────────────           ──────────────────────────
Step R4 建模完成                         ↓
  → Layer 1 验证 (contract_verify.py)    ↓
  → Layer 1 PASS                         ↓
  → 调用 cad-vision-verify ────────→ 接收 solid + contract + ref_dir
                                         ↓
                                    环境探测 → 模式决策
                                         ↓
                                    截图 → 比对 → 评分
                                         ↓
                                    PASS/WARN/FAIL + 诊断报告
  ← 返回结果 ←─────────────────────      ↓
  → 根据诊断路由修复
```

- `cad-vision-verify` 是纯验证侧：不建模，只接收输入，输出报告
- `build123d-cad` 负责建模 + 调用验证 + 根据报告修复代码
- contract_verify.py (Layer 0/1) 保留在 build123d-cad 内
- visual_compare.py 迁移到新 skill 的 compare.py，build123d-cad 改为引用

### 2.3 依赖

| 依赖 | 必须？ | 用途 |
|------|:---:|------|
| PyYAML | 必须 | 解析 contract.yaml |
| Anthropic SDK | 可选 | ai_vision 模式 |
| OpenCV (cv2) | 可选 | opencv 模式 |
| Pillow (PIL) | 可选 | manual 模式（并排图） |
| OCP CAD Viewer | 可选 | 自动截图 |

全部可选依赖缺失 → 降级到 skip 模式。

---

## 3. Core Pipeline

### 3.1 Phase 1: 环境探测

```python
def decide_mode(contract, ref_dir):
    refs = match_ref_to_views(ref_dir)
    if not refs:           return "skip"
    if not ocp_running():  return "manual"
    if vision_probe_ok():  return "ai_vision"
    if cv2_available():    return "opencv"
    return "manual"
```

Vision 探测：发送 1x1 红色 PNG 到 Claude API，成功则 ai_vision 可用。结果缓存 24 小时。

### 3.2 Phase 2: 截图采集

7 标准视角：

| 视角 | Camera | 对应面 | 典型特征（手机壳） |
|------|--------|-------|------------------|
| ISO | 等轴 | 全貌 | 整体比例 |
| FRONT | +Y | 正面 | 屏幕开口 |
| BACK | -Y | 背面 | 摄像头模组 |
| TOP | +Z | 顶部 | 红外、麦克风 |
| BOTTOM | -Z | 底部 | USB-C、扬声器、SIM |
| RIGHT | +X | 右侧 | 音量键、电源键 |
| LEFT | -X | 左侧 | 通常无特征 |

OCP 运行中 → 自动截图。不运行 → 用户手动提供截图路径。

参考图文件名自动匹配：`back_01.jpg` → BACK，`right_side.png` → RIGHT。
关键词表：back/rear/behind/背面 → BACK，front/screen/正面 → FRONT，等。

### 3.3 Phase 3: 三模式比对

#### Mode A: Claude Vision

- 输入：参考图 + 模型截图 + contract 特征清单
- Prompt：「你是 CAD 质量检查员，只看几何和比例，忽略颜色/材质」
- 输出：结构化 JSON（每特征 shape/position/size match + issue + suggestions）
- 精度：高（能理解语义，检测缺失特征）

#### Mode B: OpenCV

加权评分：

| 指标 | 权重 | 计算 |
|------|:---:|------|
| 面积比 | 25% | min/max 主轮廓面积 |
| Hu 矩形状 | 35% | 1 - matchShapes(I2) |
| 质心偏移 | 20% | 1 - 欧氏距离/对角线 |
| 特征数量 | 20% | min/max 显著轮廓数 |

局限：只比外轮廓，照片 vs 渲染差异大，适合「大方向对不对」。

#### Mode C: 人工并排

生成 `compare_{VIEW}.png`，左参考右模型，标注视角。输出 MANUAL_REVIEW。

### 3.4 Phase 4: 评分判定

| avg_score | 判定 | 动作 |
|-----------|------|------|
| >= 80 | PASS | 进入变体选择 |
| 60-79 | WARN | 列问题清单，用户决定 |
| < 60 | FAIL | 进入诊断 |

### 3.5 Phase 5: 根因诊断

三种根因：

| 根因 | 含义 | 能自动修？ | 修复目标 |
|:---:|------|:---:|---------|
| A | 数据源错 | 不能 | params.md 数值 |
| B | 合同错 | 能 | contract.yaml 约束 |
| C | 代码错 | 能 | 建模代码 |

诊断决策树：

- Layer 1 Stage A 失败 → 根因 C
- Layer 1 Stage B 失败 → 查 param_map → 映射对=C, 映射错=B, 都与参考不符=A
- Layer 1 Stage C 失败 → A 或 C（先查参数再查代码）
- Layer 2 失败但 Layer 1 通过 → 大概率根因 A 或 B（约束覆盖不足）
  - 特征缺失 → A+B
  - 形状类型错 → A
  - 位置偏但 L1 过了 → B（容差太宽）
  - 整体比例失调 → A
  - 曲面生硬 → C

### 3.6 Phase 6: 修复闭环

修复路由：

| 根因 | 修复动作 | 修完后从哪重验 |
|:---:|---------|-------------|
| C | 修代码变量/操作 | Layer 1 开始 |
| B | 修 contract.yaml | Layer 0 静态检查 |
| A | 停止，报告给用户 | 用户修 params.md 后全流程 |

循环上限：

| 层 | 最大轮次 |
|----|:---:|
| Layer 1 自动修复 | 3 |
| Layer 2 视觉修复 | 2 |
| 跨层反馈 | 2 |
| **总计** | **<= 5** |

超限 → 输出诊断报告，人工决策。

---

## 4. SKILL.md Workflow Protocol

```
收到验证请求
    ↓
Step 1: 输入检查
  - contract.yaml 存在？→ 完整模式（L1+L2+诊断）
  - 无 contract 但有参考图？→ 纯视觉模式（只有 L2）
  - 什么都没有？→ 提示用户提供
    ↓
Step 2: 环境探测 + 模式决策
  → 输出: "当前模式: ai_vision / opencv / manual"
    ↓
Step 3: 截图采集
  - OCP 运行中 → 自动截 7 视角
  - OCP 未运行 → 请用户提供截图路径
    ↓
Step 4: 执行比对 → 输出评分报告
    ↓
Step 5: 判定
  - PASS → 告知结果，结束
  - WARN → 列问题清单，用户决定
  - FAIL → 进入 Step 6
    ↓
Step 6: 根因诊断 → 输出诊断报告
  - 根因 C → "建议修改: 代码中 xxx 变量"
  - 根因 B → "建议修改: contract.yaml 中 xxx"
  - 根因 A → "需要人工确认: params.md 中 xxx 数值可能不准"
```

两种调用模式：
1. **被 build123d-cad 自动调用**：传入 solid + contract + ref_dir，返回 verdict + diagnoses
2. **用户直接触发**：提供截图 + 参考图 + contract（可选），独立运行

---

## 5. Diagnosis Report Format

```
╔═══════════════════════════════════════════════╗
║  CAD Vision Verify — Diagnosis Report          ║
║  Product: Redmi K70 Case — V2_standard         ║
╠═══════════════════════════════════════════════╣
║                                                ║
║  诊断 #1 [HIGH] 根因 A（数据源）               ║
║  位置: params.md → camera_cutout.r              ║
║  症状: 模组圆角偏小（模型 8.0 vs 参考 ~9.5）    ║
║  修复: 回 R2 找更清晰的摄像头模组参考图          ║
║                                                ║
║  诊断 #2 [MEDIUM] 根因 B（合同）               ║
║  位置: contract → volume_btn.edge_dist.tol      ║
║  症状: Layer 1 过了但视觉位置偏明显             ║
║  修复: 收紧 tol 3.0 → 1.5                      ║
║                                                ║
╠═══════════════════════════════════════════════╣
║  可自动修复: 仅 #2                              ║
║  需人工: #1（数据源问题）                        ║
║  建议顺序: 先修 #1 再修 #2                       ║
╚═══════════════════════════════════════════════╝
```

---

## 6. File Reuse Strategy

| 现有文件 (build123d-cad) | 处理 |
|---|---|
| `references/verify/layer2-visual.md` | 新 skill 引用作为设计规范 |
| `references/verify/feedback-diagnosis.md` | 新 skill 引用作为诊断规范 |
| `scripts/validate/visual_compare.py` | 新 skill 基于其逻辑重构为 compare.py（拆分模块化）；build123d-cad 原文件保留兼容，标注 deprecated，后续统一调用新 skill |
| `scripts/validate/contract_verify.py` | 保留在 build123d-cad（Layer 0/1 专用） |

新 skill 独立文件：
- `vision_probe.py` — 拆出探测逻辑，缓存 24h
- `screenshot.py` — OCP 截图逻辑独立模块
- `diagnose.py` — 从 feedback-diagnosis.md 实现可执行诊断引擎
- `verify_loop.py` — 完整闭环入口，串联所有模块

---

## 7. Integration with build123d-cad

build123d-cad SKILL.md 的 Step R4 末尾新增：

```
建模完成 + Layer 1 通过后：
  → 调用 cad-vision-verify skill
  → 传入: solid, contract.yaml, references/<product>/images/
  → 根据 verdict:
    PASS  → Step R5 收尾
    WARN  → 展示问题，用户决定
    FAIL  → 根据诊断路由:
            根因 C → 修代码，回 Layer 1
            根因 B → 修合同，回 R3.5
            根因 A → 回 R2/R3，人工搜集
```

---

## 8. Trigger Words

中文: 视觉验证、比对参考图、检查模型、看起来对不对、验证截图
英文: visual verify, compare reference, check model, Layer 2, vision check

---

## 9. Scope Boundaries

**In scope:**
- 视觉比对（截图 vs 参考图）
- 根因诊断（A/B/C 分类）
- 修复路由建议
- 三模式自动降级

**Out of scope:**
- 建模（由 build123d-cad 负责）
- Layer 0 合同生成（由 build123d-cad 负责）
- Layer 1 参数验证（由 contract_verify.py 负责）
- 自动修改代码/合同（skill 只给建议，执行交给调用方）
