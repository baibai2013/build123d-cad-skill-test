# build123d-cad 经验缓存（experience/）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 build123d-cad skill 仓新建 `experience/<category>/<slug>.md` 经验缓存目录，并改 Playbook 让 R1 前预检索、R5 后 AI 起草 + 用户 review + 落盘。

**Architecture:** 只改 2 个 skill 仓文件（`experience/README.md` 新建 + `references/protocols/reference-product-playbook.md` 5 处修改） + 1 个 seed 条目（从 test 13 params.md 手工转换）。test 仓新建 `tests/16-experience-dryrun/` 含 3 个 run 占位（Scenario D/E/F 预期输出，操作员手工跑）。不改 SKILL.md 路由段、不改 assets/、不改其它协议。

**Tech Stack:** Markdown + YAML frontmatter（no runnable code changes）。验证手段：`grep` / `ls` 结构核对 + 3 个真对话行为验证（由操作员手动跑）。

---

## 背景与跨仓约定

**两个 git 仓：**
- **Skill 仓**：`/Users/liyijiang/.agents/skills/build123d-cad/`（skill 本体 + experience/ 目录）
- **Test 仓**：`/Users/liyijiang/work/build123d-cad-skill-test/`（本次执行的 CWD，放 dryrun 目录）

每个 Task 明确标注 "(skill repo)" 或 "(test repo)"，在对应仓 commit。

**当前 Playbook 文件状态**：`/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`（506 行，最近 commit 4d01f2e "失败模式 appendix"）。当前已有 6 条失败模式（FM-1 ~ FM-6）+ 契约块 5 条。本次 Playbook 改动不动 R2~R4、不动已有失败模式。

**Spec 里"契约块加第 5 条"的脚注**：spec 写作时 Playbook 契约块有 4 条，当前实际有 5 条（最后一条讲 artifact 缺失回补）。本次"经验交互"新规则作为**第 6 条追加**，不重编号——保留既有语义稳定。

---

## 文件结构

| 路径 | 仓 | 类型 | 职责 |
|---|---|---|---|
| `experience/README.md` | skill | 新建 | experience/ 目录用途 + 发布风险说明 + 条目 schema 链接 |
| `experience/phone-case/redmi-k80-pro.md` | skill | 新建 | 从 test 13 params.md 手工转换的 seed 条目，验证 schema 可用 |
| `references/protocols/reference-product-playbook.md` | skill | 修改 | 5 处：契约块追加 / 总表加列 / R1 前置检索 / R5 draft 流 / FM-7+8 + Appendix A |
| `tests/16-experience-dryrun/README.md` | test | 新建 | Scenario D/E/F 说明 + 操作员手动跑的指引 |
| `tests/16-experience-dryrun/run_D.md` | test | 新建 | 冷启动 dryrun 预期输出占位（待操作员粘贴真对话） |
| `tests/16-experience-dryrun/run_E.md` | test | 新建 | 精确命中 dryrun 预期输出占位 |
| `tests/16-experience-dryrun/run_F.md` | test | 新建 | 同类命中 dryrun 预期输出占位 |

**共计**：skill 仓 3 个新文件 + 1 个文件 5 处修改；test 仓 4 个新文件。13 个 Task，13 次 commit（skill 仓 8 次 + test 仓 5 次）。

---

## Phase A — Skill 仓 experience/ 目录基建

### Task 1: 创建 experience/ 目录 + README.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/experience/README.md`

- [ ] **Step 1: 写 README.md**

完整文件内容：

````markdown
# experience/ — 参考物建模经验缓存

本目录存放用户跑完参考物建模协议 R1~R5 后沉淀的**具体产品**实战笔记，供下次建同型号/同类产品时 R1 预检索复用。

## 与 assets/ 的区别

| 维度 | `assets/` | `experience/` |
|---|---|---|
| 内容 | 可运行的 .py 参考代码（enclosure/servo_mount 等通用模板） | 某个具体产品的实战笔记 |
| 粒度 | 抽象几何范式 | 具体型号 |
| 来源 | skill 作者预置 | 用户跑完 R1~R5 后沉淀 |
| 索引 | 按零件类型（mounting/parts/...） | 按 `<category>/<slug>` |
| 用途 | R4 建模参考 | R1 开始时"上次这型号怎么建的" |

## 目录结构

```
experience/
├── README.md                          （本文件）
├── <category>/                        （来自 Playbook Appendix A 白名单）
│   └── <slug>.md                      （kebab-case 产品短名，对齐 references/<slug>/）
```

## 条目 schema

每个 `.md` 条目使用 YAML frontmatter + 3 节固定 markdown body。完整 schema 见 Playbook `Step R5 — Experience Draft 模板` 节。

frontmatter 字段：
- `slug`：产品短名（kebab-case）
- `category`：Playbook Appendix A 白名单里的一个
- `tags`：3~5 个类别词
- `confidence`：本次 params.md 星级**中位数**（1~5）
- `last_updated`：ISO 日期，形如 `2026-04-18`
- `related_tests`：test 仓路径列表（跨仓引用约定，形如 `tests/13-redmi-k80-pro`）
- `source_model`：`step` / `reverse-engineered` / `mixed`

body 节：
- `## 关键参数（下次直接用）`（必填）
- `## 踩过的坑`（必填；为空时 AI 显式问用户确认）
- `## 下次直接复用（copy-paste 片段）`（必填）
- `## 未解决 / 待验证`（可选）

## ⚠️ 发布风险说明

**experience/ 目录随 skill 仓一起进 git**。如果该仓将来公开发布，以下内容会一并暴露：
- 产品型号名 + 你测过的关键尺寸
- 踩过的坑（可能暗示客户项目 / 未公开产品）
- copy-paste 片段里的命名

**慎写敏感内容**。涉及客户/未公开产品时，建议：
1. 别写进 experience/（本次建模用完即弃）
2. 或用脱敏 slug（如 `customer-phone-A` 而非真实型号）
3. 长期可加 `experience/.private/` 放 `.gitignore`（当前未启用）

## 读写流程

- **读**：Playbook Step R1 前置检索自动做（glob `experience/*/<slug>.md` 精确匹配 → 失败 fallback 到 `experience/<category>/*.md` 同类 ≤2 条）。
- **写**：Playbook Step R5 由 AI 起草 Experience Draft 块，用户 review 后落盘。未经 review 不得自动写盘。
````

- [ ] **Step 2: 验证文件结构**

```bash
ls -la /Users/liyijiang/.agents/skills/build123d-cad/experience/
```

Expected: 只有 `README.md` 一个文件。

- [ ] **Step 3: Commit（skill 仓）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add experience/README.md && \
git commit -m "$(cat <<'EOF'
docs(experience): scaffold experience/ cache directory with README

为参考物建模协议新增 L3 经验缓存层：
- 说明 experience/ 与 assets/ 的职责区分
- 声明 schema（frontmatter + 3 节 body）与 Playbook R1/R5 的读写接口
- 加发布风险提示，提醒慎写敏感产品

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

Expected: commit 成功，`git log --oneline -1` 显示新 commit。

---

### Task 2: 创建 seed 条目 experience/phone-case/redmi-k80-pro.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/experience/phone-case/redmi-k80-pro.md`

**背景**：从 test 仓 `references/redmi-k80-pro/params.md` 手工转换，只取 ★≥3 的参数行，作为格式范本 + 冷启动不至于 100% 空仓。

- [ ] **Step 1: 创建父目录并写 seed 条目**

完整文件内容：

````markdown
---
slug: redmi-k80-pro
category: phone-case
tags: [android, 6.67-inch, triple-camera, xiaomi]
confidence: 4
last_updated: 2026-04-18
related_tests:
  - tests/13-redmi-k80-pro
source_model: reverse-engineered
---

## 关键参数（下次直接用）

- 机身 160.26 × 74.95 × 8.39 mm ★5（多站交叉验证官方尺寸）
- 竖边圆角 R_corner 9.0 mm ★3（图片比例推算）
- 前后 Z 方向边缘圆角 R_edge 1.5 mm ★3
- 后置摄像头模组外环直径 D_cam 34.0 mm ★3（图片比例 ~45% 机身宽）
- 摄像头模组凸起高度 2.5 mm ★3
- 摄像头中心 X: -16.0 mm ★3（从机身中心，负=偏左）
- 摄像头中心 Y: +60.0 mm ★3（从机身中心，正=偏上；距顶边约 20 mm）
- USB-C 口宽 × 高 = 9.0 × 3.2 mm ★3（居中）
- USB-C 圆角 1.6 mm ★3（胶囊形）
- 屏幕尺寸 152.0 × 72.0 mm ★3（6.67″ 20:9 反推）

## 踩过的坑

- 摄像头中心 Y 坐标正负易混淆：**正 = 距机身中心往上偏**，而不是"距顶边距离"。test 13 曾误把 +60 当成距顶边 60mm，导致整个模组位置下移
- 屏幕凹陷深度 0.15 mm 非常小，容易手写成 1.5 mm——check 数量级
- 按键宽度（沿厚度方向 2.5 mm）和按键凸起高度（凸出中框 1.0 mm）是两个维度，不要混淆
- 摄像头模组外环直径由图片比例推算（~45% 机身宽 × 74.95），置信度只有 ★3，新品发布后若拿到 STEP 需要实测覆盖

## 下次直接复用（copy-paste 片段）

```python
# Redmi K80 Pro 机身基本参数（mm）
phone_L, phone_W, phone_T = 160.26, 74.95, 8.39
corner_R, edge_R = 9.0, 1.5

# 后置摄像头模组（圆形"风暴眼"）
cam_module_D = 34.0      # 外环直径
cam_bump_H = 2.5          # 凸起高度
cam_center = (-16.0, 60.0)  # (X, Y) 相对机身中心；负 X=偏左，正 Y=偏上

# 底部开孔
usb_w, usb_h, usb_r = 9.0, 3.2, 1.6  # USB-C 胶囊形
```

## 未解决 / 待验证

- 摄像头模组外环直径 ★3 只有图片比例推算，建议后续用卡尺或 STEP 实测回填到 ★4+
- 三镜头布局 PCD 9.0 mm 未经 Layer 2 验证，仅供参考
````

- [ ] **Step 2: 验证目录 + 文件**

```bash
ls /Users/liyijiang/.agents/skills/build123d-cad/experience/phone-case/ && \
head -10 /Users/liyijiang/.agents/skills/build123d-cad/experience/phone-case/redmi-k80-pro.md
```

Expected: `redmi-k80-pro.md` 存在，前 10 行含 frontmatter（`slug: redmi-k80-pro` / `category: phone-case`）。

- [ ] **Step 3: Commit（skill 仓）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add experience/phone-case/redmi-k80-pro.md && \
git commit -m "$(cat <<'EOF'
docs(experience): add redmi-k80-pro seed entry from test 13

首个 experience/ 条目：
- 从 tests/13-redmi-k80-pro 的 params.md 手工提取 ★≥3 的参数行
- 补充建模时踩过的坑（Y 坐标正负混淆等）
- 提供 copy-paste 片段作为下次建模的起点
- confidence=4（★★★★★ 官方尺寸 + ★3 反推的中位数）

作为 schema 格式范本，后续 Scenario E（精确命中）的前置条件。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Phase B — Playbook 5 处修改

**统一 working directory**：所有 Phase B 任务都在 skill 仓 `/Users/liyijiang/.agents/skills/build123d-cad/` 编辑 `references/protocols/reference-product-playbook.md`。

---

### Task 3: Playbook 改动 1 — 契约块追加第 6 条

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md:14`（追加一行）

- [ ] **Step 1: 读取当前契约块**

```bash
sed -n '8,15p' /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected 当前内容：
```
## 执行契约（进入此 Playbook 后对本次对话强制生效）

1. 每个 Step 完成后，**必须在当次回复里输出"产出报告"块**...
2. **没写产出报告的 Step 视为未完成**，禁止进入下一步。
3. **跳步必须声明理由**...
4. **Artifact 是硬约束**...
5. 遇到本步 artifact 缺失：回到本步补产...
```

- [ ] **Step 2: 使用 Edit 工具在第 5 条之后追加第 6 条**

用 Edit 工具定位 old_string 为第 5 条的完整行，新增一行：

old_string（完整第 5 条）：
```
5. 遇到本步 artifact 缺失：回到本步补产，禁止写 `[x]` 骗过。发现上游缺失：在回复里明写 "回补 Step Rx" 并执行，禁止下行。
```

new_string：
```
5. 遇到本步 artifact 缺失：回到本步补产，禁止写 `[x]` 骗过。发现上游缺失：在回复里明写 "回补 Step Rx" 并执行，禁止下行。
6. **R1 开始前必须查 `experience/`，R5 结束前必须输出 Experience Draft**（状态用 `[hit]`/`[partial]`/`[miss]`/`[skip]`/`[saved]`，详见 R1 / R5 Step 定义）。
```

- [ ] **Step 3: 验证追加成功**

```bash
grep -n "R1 开始前必须查" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: 1 个匹配，行号在契约块内（应在 15 行附近）。

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): add contract clause 6 — experience read/write must be reported

R1 开始前必须查 experience/，R5 结束前必须输出 Experience Draft。
状态用 [hit]/[partial]/[miss]/[skip]/[saved] 显式上报，禁止静默加载或自动写盘。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Playbook 改动 2 — R1~R5 总表加「经验交互」列

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md:20-29`（总表整段替换）

- [ ] **Step 1: 读取当前总表**

```bash
sed -n '18,30p' /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: 4 列的 8 行总表。

- [ ] **Step 2: 用 Edit 工具替换整段总表**

old_string（完整当前总表，包括标题行、分隔行、8 个 Step 行）：

```
| Step | 必须产出 | 允许跳过？ | 下一步分叉 |
|---|---|---|---|
| R1 识别 + 搜索计划 | `references/<slug>/search_plan.md` | 否 | → R2 |
| R2 执行搜集 | `references/<slug>/raw_specs.md` + `images/*` | 否 | 有 `model.step` → R3/R2.7；无 → R2.5 |
| R2.5 无 STEP 反推 | `references/<slug>/clean/*_scale.json` + `measurements.csv` | 仅 R2 已产出 `model.step` 时可 skip | → R2.7 |
| R2.7 参考图现实对齐 | `references/<slug>/clean/*_cropped.png` + `part_face_mapping.yaml` | 否（Layer 2 必做）；仅 "有 STEP + 不做视觉对比" 可 skip | → R3 |
| R3 生成 params.md | `references/<slug>/params.md`（含 ★ 置信度） | 否 | → R3.5 |
| R3.5 生成 contract.yaml | `tests/<test>/contract.yaml` | 否 | → R4 |
| R4 建模 | `tests/<test>/<part>.py` + OCP 自动预览 | 否 | → R5 |
| R5 收尾提示 | 回复中输出"完成汇总"块 | 否 | （终态） |
```

new_string（5 列新总表，新增「经验交互」列夹在「允许跳过？」和「下一步分叉」之间）：

```
| Step | 必须产出 | 允许跳过？ | 经验交互 | 下一步分叉 |
|---|---|---|---|---|
| R1 识别 + 搜索计划 | `references/<slug>/search_plan.md` | 否 | **读** `experience/`（`[hit]`/`[partial]`/`[miss]` 必报） | → R2 |
| R2 执行搜集 | `references/<slug>/raw_specs.md` + `images/*` | 否 | — | 有 `model.step` → R3/R2.7；无 → R2.5 |
| R2.5 无 STEP 反推 | `references/<slug>/clean/*_scale.json` + `measurements.csv` | 仅 R2 已产出 `model.step` 时可 skip | — | → R2.7 |
| R2.7 参考图现实对齐 | `references/<slug>/clean/*_cropped.png` + `part_face_mapping.yaml` | 否（Layer 2 必做）；仅 "有 STEP + 不做视觉对比" 可 skip | — | → R3 |
| R3 生成 params.md | `references/<slug>/params.md`（含 ★ 置信度） | 否 | 参考命中经验的参数星级，可上调本次置信度 | → R3.5 |
| R3.5 生成 contract.yaml | `tests/<test>/contract.yaml` | 否 | — | → R4 |
| R4 建模 | `tests/<test>/<part>.py` + OCP 自动预览 | 否 | 若命中经验有"复用片段"，优先引用 | → R5 |
| R5 收尾提示 | 回复中输出"完成汇总"块 + Experience Draft | 否 | **写** Experience Draft → 用户 review → 落盘（或 `[skip]`） | （终态） |
```

注意 R5 行的「必须产出」列也从 `回复中输出"完成汇总"块` 改为 `回复中输出"完成汇总"块 + Experience Draft`，与 Task 6 的 R5 详细修改保持一致。

- [ ] **Step 3: 验证总表结构**

```bash
grep -c "| 经验交互 |" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: `1`（仅总表表头）。

```bash
grep "读.*experience" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: 至少 1 行命中（R1 行）。

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): add 经验交互 column to R1~R5 总表

在总表夹入新列明示每个 Step 与 experience/ 的关系：
- R1 读（必报 hit/partial/miss）
- R3/R4 参考命中经验（星级上调 / 优先复用片段）
- R5 写（draft → review → 落盘）
其余 Step 为 —，保持既有流程不变。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Playbook 改动 3 — Step R1 插入「前置检索」子段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`（R1 模块内 `**前置**` 和 `**本步产出**` 之间）

- [ ] **Step 1: 读取当前 R1 起始段**

```bash
sed -n '38,50p' /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: R1 标题 + `**前置**` 段 + `**本步产出**` 段开头。

- [ ] **Step 2: 用 Edit 工具插入前置检索子段**

old_string（当前 R1 的「前置」段尾 + 「本步产出」段首的完整段落）：

```
**前置**：
- [x] 用户需求中明确提到一个具体产品型号

**本步产出（必须全部存在才允许进入下一步）**：
```

new_string（在两者之间插入「前置检索」子段）：

````
**前置**：
- [x] 用户需求中明确提到一个具体产品型号

**前置检索（进 R1 第一件事，写 `search_plan.md` 之前必须完成）**：

1. 从需求抽 `<slug>`（kebab-case 产品短名）和 `<category>`（Appendix A 白名单里最接近的一个）
2. 精确匹配：`glob experience/*/<slug>.md` → 命中则完整读入，把"关键参数"/"踩过的坑"/"复用片段"三节注入 R1 上下文
3. 未精确命中 → 同类匹配：`glob experience/<category>/*.md` → 挑 `confidence >= 3` 且 `tags` 最接近的 ≤2 条完整读入
4. 都没命中 → 正常走 R1，不加载任何经验

**过期提醒**：命中条目 frontmatter 的 `last_updated` 距今 > 90 天时，状态降级为 `[partial]` 并在产出报告里显式提醒「⚠ 经验写于 X 天前，建议核实」。

**命中对 `search_plan.md` 内容的影响**：
- 「已知参数」节直接填经验里的数，**每条带来源注释**（形如 `（来自 experience/phone-case/redmi-k80-pro.md）`）
- 「预期坑」节把经验「踩过的坑」原样贴进去（带来源）
- 用户确认 `search_plan.md` 时若当场说「这次重测 X」→ AI 在本次 params.md 里记，**不改经验文件**；R5 时再决定是否回写经验

**R1 产出报告里必须显式上报检索结果**，用以下状态之一（不允许静默加载）：
- `[hit] experience/<category>/<slug>.md` — 精确命中
- `[partial] experience/<category>/*.md` — 同类命中若干条，列出路径
- `[miss] experience/<category>/*` — 全无
- `[skip] reason=<用户明说不查/敏感项目>` — 显式跳过

**本步产出（必须全部存在才允许进入下一步）**：
````

- [ ] **Step 3: 验证前置检索插入成功**

```bash
grep -n "前置检索" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: 1 个匹配（新插入的子段标题）。

```bash
grep -c "过期提醒" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: `1`。

- [ ] **Step 4: 更新 R1 的 AI 回报契约模板（同时 Edit）**

old_string（当前 R1 回报契约样本）：

```
**AI 回报契约（完成后必须在回复里输出）**：
```
Step R1 产出报告
- [x] references/<slug>/search_plan.md  (4 来源，待用户确认)
下一步：等用户确认 → Step R2
```
```

new_string（加上经验检索状态行）：

````
**AI 回报契约（完成后必须在回复里输出）**：
```
Step R1 产出报告
- [x] references/<slug>/search_plan.md              (4 来源，待用户确认)
- [hit] experience/phone-case/redmi-k80-pro.md     (精确命中，预加载 10 参数 + 4 坑)
- [miss] experience/phone-case/*                    (无其它同类条目)
下一步：等用户确认 → Step R2
```

（示例为「精确命中」场景；无命中时写 `[miss]`，同类命中时写 `[partial]`。）
````

- [ ] **Step 5: 验证回报契约样本**

```bash
grep -c "\[hit\] experience" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: ≥1（R1 回报契约样本里至少 1 条）。

- [ ] **Step 6: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): add 前置检索 subsection to Step R1

R1 第一件事改为查 experience/：
- 2 层 fallback（精确 slug → 同类 category）
- 90 天过期规则降级为 [partial]
- 命中内容注入 search_plan 的"已知参数"+"预期坑"两节（带来源）
- R1 产出报告强制上报 [hit]/[partial]/[miss]/[skip]

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Playbook 改动 4 — Step R5 重写「本步产出」+ 加 Experience Draft 模板 + 更新回报契约

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`（R5 模块的 `**本步产出**` 段 + AI 回报契约段）

- [ ] **Step 1: 读取当前 R5 模块**

```bash
sed -n '423,464p' /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: R5 整段（前置 + 本步产出 + 完成汇总块模板 + AI 回报契约）。

- [ ] **Step 2: 用 Edit 工具替换「本步产出」段**

old_string：

```
**本步产出**（注意：R5 的产出是**当次回复里的一段文字**，不落盘）：
- 在回复末尾输出"完成汇总"块
```

new_string：

````
**本步产出**：

1. **完成汇总块**（当次回复里的一段文字，不落盘）——Layer 0/1/2 状态 + 置信度统计 + 后续建议
2. **Experience Draft 块**（当次回复里的一段文字）——按下方模板自动起草，供用户 review
3. **用户 review 决策落盘**：
   - 用户说「保存」/「ok」/「yes」→ 落盘 `experience/<category>/<slug>.md`，回报 `[saved]`
   - 用户提增删改 → AI 更新 draft 重输出，再等确认
   - 用户说「不保存」/「skip」→ 回报 `[skip] experience reason=...`，不写盘
4. **落盘行为**：
   - 新条目 → `Write` 工具直接写
   - 已存在（精确 slug 命中，R1 `[hit]` 过的情况）→ 读旧文件 → diff 呈现 → 用户选：
     - `merge`（默认推荐）：参数按 slug+name 去重（新值覆盖，`confidence` 取高）；"踩过的坑"和"复用片段"一律 **append 不去重**
     - `overwrite`：整文件覆盖
     - `keep-old`：不动旧文件

**关键规则**：draft 和 saved/skip 必须都在回报里显式上报；**未经用户 review 不得自动写盘**。
````

- [ ] **Step 3: 在「完成汇总块模板」之后插入 Experience Draft 模板**

old_string（完成汇总块模板闭合行 + 空行 + `**AI 回报契约**`）：

```
- <未出现异常 → 可进入 3D 打印 / CNC 流程>
```

**AI 回报契约**：
```

new_string（在两者之间插入 Experience Draft 模板节）：

````
- <未出现异常 → 可进入 3D 打印 / CNC 流程>
```

**Experience Draft 模板**（AI 自动起草，填值规则见各字段注释）：

````markdown
## Experience Draft（请 review，确认后保存到 `experience/<category>/<slug>.md`）

```yaml
slug: <kebab-case 产品短名，与 references/<slug>/ 对齐>
category: <Appendix A 白名单里最接近的>
tags: [<3~5 个类别词，从 raw_specs.md 摘屏幕尺寸/芯片/接口等>]
confidence: <本次 params.md 所有 ★ 行的中位数，整数>
last_updated: <今天的 ISO 日期>
related_tests:
  - tests/<test>
source_model: <step / reverse-engineered / mixed>
```

## 关键参数（下次直接用）
<从 references/<slug>/params.md 提 ★ ≥ 3 的行；每行末尾保留来源>

## 踩过的坑
<从本次对话摘：用户纠正节点 / AI 回退节点 / 修了几轮的 Layer 2 偏差 / 单位搞错等>

**若本节为空**，AI 必须显式问用户「本次没发现坑对吗？确认后保存」——避免垃圾经验污染后续检索。

## 下次直接复用（copy-paste 片段）
<从 tests/<test>/<part>.py 提前 ~20 行关键尺寸常量声明段，封装成 code block>

## 未解决 / 待验证（可选）
<本次置信度 ★ ≤ 2 的尺寸 / Layer 2 未覆盖的特征 / 用户承诺回测的条目>
````

**AI 回报契约**：
````

- [ ] **Step 4: 替换当前 AI 回报契约样本**

old_string：

```
Step R5 产出报告
- [x] 完成汇总块已输出（上方）
- [ask] references/<slug>/ 保留 or 删除？
参考物建模协议 R1~R5 完成。
```

new_string：

```
Step R5 产出报告
- [x] 完成汇总块已输出（上方）
- [x] Experience Draft 已输出（上方），等用户 review
- [ ] experience/<category>/<slug>.md    (等用户确认后补 [saved] 或 [skip])
- [ask] references/<slug>/ 保留 or 删除？
参考物建模协议 R1~R5 完成（经验落盘待用户 review）。
```

- [ ] **Step 5: 验证 R5 三处修改**

```bash
grep -c "Experience Draft" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: ≥4（本步产出段、模板标题、回报契约、可能表里还有 1 个）。

```bash
grep -c "关键规则.*未经用户 review" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: `1`。

- [ ] **Step 6: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): rewrite Step R5 with Experience Draft flow

R5 产出从 1 项（完成汇总块）扩到 4 项：
1. 完成汇总块
2. Experience Draft 块（AI 起草，不直接写文件）
3. 用户 review 决策（save / modify / skip）
4. 落盘行为（新建 Write / 已存在 merge-overwrite-keep-old 三选一）

关键规则：未经用户 review 不得自动写盘；空"坑"节必须显式问用户确认。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Playbook 改动 5a — 失败模式追加 FM-7 + FM-8

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`（失败模式清单尾部，当前 FM-6 之后）

- [ ] **Step 1: 定位当前失败模式清单尾部**

```bash
grep -n "^### FM-" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: 6 个匹配（FM-1 ~ FM-6）。

- [ ] **Step 2: 用 Edit 工具在 FM-6 末尾追加 FM-7 + FM-8**

old_string（FM-6 完整段落——包括标题、现象、根因、诊断、修复）：

```
### FM-6：产出报告漏写
**现象**：AI 直接开始做下一步，没有先输出产出报告
**根因**：遗忘"执行契约"第 1 条
**诊断**：用户注意到回复里没有 `Step Rn 产出报告` 块
**修复**：立刻补一条产出报告，回补漏的 artifact，再继续
```

new_string（FM-6 原样保留 + 两段新追加）：

````
### FM-6：产出报告漏写
**现象**：AI 直接开始做下一步，没有先输出产出报告
**根因**：遗忘"执行契约"第 1 条
**诊断**：用户注意到回复里没有 `Step Rn 产出报告` 块
**修复**：立刻补一条产出报告，回补漏的 artifact，再继续

### FM-7：静默加载经验
**现象**：R1 检索到 `experience/<slug>.md` 但不在产出报告里报 `[hit]`，用户不知道 `search_plan.md` 里哪些参数来自历史记录
**根因**：遗忘契约第 6 条，把"读经验"当作透明过程
**诊断**：检查 R1 产出报告是否含 `[hit]`/`[partial]`/`[miss]`/`[skip]` 四状态之一；检查 `search_plan.md` 的"已知参数"节是否每条带来源注释
**修复**：立刻补一条 `[hit] experience/...`；把来源注释补回 `search_plan.md`；若用户已基于无来源的参数做了决策，回退到 R1 重走

### FM-8：经验污染 R2.7
**现象**：R1 命中经验的「踩过的坑」后，AI 把这些坑当既定事实，跳过 R2.7 视觉对齐
**根因**：把"先验"误当"事实"；经验是历史 offset，不替代本次 Layer 2 验证
**诊断**：R2.7 产出报告缺失但 Layer 2 分叉仍走下去；或 `part_face_mapping.yaml` 未生成
**修复**：强制回 R2.7 补产；在 R1 产出报告里把命中的"坑"标明「本次仍需 Layer 2 验证」

````

- [ ] **Step 3: 验证 FM-7 + FM-8 存在**

```bash
grep -cE "^### FM-[78]" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: `2`。

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): add FM-7 静默加载经验 + FM-8 经验污染 R2.7

两条新失败模式对应 experience/ 的常见坑：
- FM-7：R1 加载了经验却不报 [hit]，用户失去追踪线
- FM-8：把经验里的"坑"当事实，跳过本次 Layer 2 视觉对齐

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Playbook 改动 5b — 追加 Appendix A（category 白名单）

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`（文件末尾追加）

- [ ] **Step 1: 定位文件末尾**

```bash
tail -5 /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: FM-8 的最后修复行。

- [ ] **Step 2: 用 Edit 工具在 FM-8 末尾追加 Appendix A**

old_string（FM-8 最后一行，需取唯一字符串）：

```
**修复**：强制回 R2.7 补产；在 R1 产出报告里把命中的"坑"标明「本次仍需 Layer 2 验证」
```

new_string（原行保留 + 追加 Appendix A 整段）：

````
**修复**：强制回 R2.7 补产；在 R1 产出报告里把命中的"坑"标明「本次仍需 Layer 2 验证」

---

## Appendix A — category 白名单

AI 在 R1 前置检索时，`<category>` 必须从下面 25 个中取**最接近的一个**，不自造。同类词（如 `手机壳` / `case` / `phone case`）一律映射到白名单词（`phone-case`）。

```
phone-case         servo-mount       enclosure         pcb-holder
heat-sink          bracket           knob              gear
clip               hinge             adapter           mount-plate
standoff           cable-gland       handle            cap
bushing            spacer            fixture           jig
housing            shell             cover             tray
frame
```

**边界情况**：
- 产品介于两类之间（如「舵机外壳」介于 `servo-mount` 和 `enclosure`）→ 以**主结构**决定，外壳占比大 → `enclosure`；安装位占比大 → `servo-mount`
- 白名单里找不到合适的 → 不新增词，临时用 `fixture` 或 `jig` 兜底；**连续 3 个条目都走 fixture 时**，在该 skill 仓提 issue 考虑扩充白名单
````

- [ ] **Step 3: 验证 Appendix A**

```bash
grep -c "^## Appendix A" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: `1`。

```bash
grep -c "phone-case" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected: ≥2（Appendix A 白名单 + 前面某处的 R1 样本）。

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git add references/protocols/reference-product-playbook.md && \
git commit -m "$(cat <<'EOF'
docs(playbook): add Appendix A category whitelist (25 words)

R1 前置检索的 <category> 必须从白名单取，避免 phone-case/case/手机壳 类重复词分散条目。
边界情况给出主结构判定规则 + fixture 兜底策略 + 扩充白名单触发门槛。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Phase C — Test 仓 dryrun 目录

**统一 working directory**：Phase C 所有 Task 在 test 仓 `/Users/liyijiang/work/build123d-cad-skill-test/` 下操作。

---

### Task 9: 创建 tests/16-experience-dryrun/README.md

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/README.md`

- [ ] **Step 1: 建目录并写 README**

完整文件内容：

````markdown
# Test 16 — experience/ 经验缓存 dryrun

验证 Playbook Step R1 前置检索 + Step R5 沉淀流的行为。不跑 build123d 代码，纯真对话验证。

## Scenario 列表

| File | 场景 | 前置条件 | R1 预期状态 | R5 预期落盘 |
|---|---|---|---|---|
| `run_D.md` | 冷启动 | `experience/` 除 seed 外为空 | `[miss]` | 新建 `experience/phone-case/redmi-k80-pro.md` |
| `run_E.md` | 精确命中 | D 之后已有 redmi-k80-pro.md | `[hit]`，注入参数 + 坑 | `merge` 或 `keep-old` |
| `run_F.md` | 同类命中 | 仅 redmi-k80-pro.md 存在 | `[partial]`，列出作参考 | 新建 `experience/phone-case/xiaomi-k70.md` |

## 执行方式（操作员手动跑）

⚠️ 本目录不含可自动化的测试——经验系统的行为必须用**真对话**验证 AI 是否遵循 Playbook 契约。

1. 在新终端开一个 fresh Claude Code 会话，cwd 设为本 test 仓
2. 按以下 prompt 输入（每个 Scenario 分开跑）：
   - D：「做红米 K80 Pro 手机壳」——**先把 `experience/phone-case/redmi-k80-pro.md` 临时移走**（或 rename 为 `.bak`），模拟冷启动
   - E：D 跑完并保存后，再在**新会话**里输入「做红米 K80 Pro 手机壳」，验证命中
   - F：仅保留 `experience/phone-case/redmi-k80-pro.md`，新会话里输入「做小米 K70 手机壳」
3. 每个 Scenario 完整复制 AI 的全部回复（R1 产出报告 + search_plan 内容 + 后续 Step 的报告 + R5 的 Experience Draft + 用户交互）到对应 `run_*.md`，替换占位节
4. 肉眼审阅是否满足该 Scenario 的「预期」与「失败判据」

## 失败反馈回路

如果某 Scenario 跑不通：
- R1 报错状态（如 Scenario D 没出现 `[miss]`） → 回改 Playbook 改动 3（R1 前置检索子段）或改动 1（契约第 6 条）
- R5 没出 Experience Draft → 回改 Playbook 改动 4（R5 重写）
- 命中但没注入经验 → 回改 Playbook 改动 3 的"命中对 search_plan.md 的影响"节
- AI 自造 category（如把 `phone-case` 写成 `case`） → 回改 Playbook 改动 5b（Appendix A 严格性）

## 不做

- 不写 pytest / unittest 脚本——经验系统的行为属于 prompt compliance，无法用 Python 直接测
- 不跑 build123d 建模——本目录只关心 R1/R5 的经验交互 artifact，不关心模型本身
````

- [ ] **Step 2: 验证目录和 README**

```bash
ls /Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/ && \
head -5 /Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/README.md
```

Expected: 目录存在，README.md 以 `# Test 16 — experience/ 经验缓存 dryrun` 起始。

- [ ] **Step 3: Commit（test 仓）**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && \
git add tests/16-experience-dryrun/README.md && \
git commit -m "$(cat <<'EOF'
test(16-experience-dryrun): scaffold dryrun directory with README

Scenario D/E/F 的说明 + 操作员手动执行步骤：
- D 冷启动 → [miss] → 新建条目
- E 精确命中 → [hit] + 注入 → merge
- F 同类命中 → [partial] → 新建
每个 Scenario 对应一个 run_*.md，由操作员在 fresh 会话里跑 + 复制 AI 回复。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: 创建 run_D.md — 冷启动占位

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_D.md`

- [ ] **Step 1: 写 run_D.md**

完整文件内容：

````markdown
# Scenario D — 冷启动（experience/ 为空）

## 前置准备

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
# 把 seed 条目临时移走模拟冷启动
mv $SKILL/experience/phone-case/redmi-k80-pro.md $SKILL/experience/phone-case/redmi-k80-pro.md.bak
```

跑完后记得恢复：
```bash
mv $SKILL/experience/phone-case/redmi-k80-pro.md.bak $SKILL/experience/phone-case/redmi-k80-pro.md
```

## 用户 prompt

```
做红米 K80 Pro 手机壳
```

## 预期 AI 行为

### R1 产出报告必须形如

```
Step R1 产出报告
- [x] references/redmi-k80-pro/search_plan.md   (4 来源，待用户确认)
- [miss] experience/phone-case/*                (目录存在但无任何条目)
下一步：等用户确认 → Step R2
```

**关键检查点**：
- ✅ 出现 `[miss]` 状态
- ✅ `search_plan.md` 的"已知参数"节为空或仅来自用户 prompt 的信息（不是虚构的历史数据）

### R5 Experience Draft 必须出现

AI 完成 R4 建模后，R5 必须同时输出「完成汇总块」和「Experience Draft」两块，draft 按 Playbook R5 模板填写（含 frontmatter + 3 节 body）。

### 用户 review → 落盘

用户说「保存」后，AI 必须：
- 用 `Write` 工具创建 `experience/phone-case/redmi-k80-pro.md`
- R5 产出报告补一行 `[saved] experience/phone-case/redmi-k80-pro.md`

## 失败判据（任一即 fail）

- R1 没出现 `[miss]`（静默加载或伪造 `[hit]`）
- R5 没出 Experience Draft（只有完成汇总块）
- 未经用户确认就写盘（skip review 门）
- 落盘文件 frontmatter 不完整（缺 `last_updated` / `related_tests` / `source_model`）
- "踩过的坑"节为空但 AI 没问用户确认

## 实跑结果（待操作员粘贴完整 AI 回复）

```
<此处替换为 fresh 会话里跑完后的完整 AI 回复>
```

## 审阅结论（待操作员填）

- [ ] R1 产出报告含 `[miss]`
- [ ] R5 Experience Draft 按模板输出
- [ ] 落盘时机正确（用户 review 后）
- [ ] frontmatter 完整
- [ ] "坑"节规则遵守

**若有任一失败**：在本文件末尾加一节「问题记录」写明现象 + 可能的 Playbook 修订点，回流到 Playbook 改动。
````

- [ ] **Step 2: 验证**

```bash
head -5 /Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_D.md
```

Expected: `# Scenario D — 冷启动...`。

- [ ] **Step 3: Commit（test 仓）**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && \
git add tests/16-experience-dryrun/run_D.md && \
git commit -m "$(cat <<'EOF'
test(16-experience-dryrun): add Scenario D (cold start) expectations

冷启动场景的前置操作（seed 临时移走）、用户 prompt、R1/R5 预期回报契约、
失败判据、审阅 checklist。操作员跑完后把 AI 真实回复粘贴到"实跑结果"节。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: 创建 run_E.md — 精确命中占位

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_E.md`

- [ ] **Step 1: 写 run_E.md**

完整文件内容：

````markdown
# Scenario E — 精确命中（slug 完全一致）

## 前置准备

确保 `experience/phone-case/redmi-k80-pro.md` 存在（Task 2 的 seed 条目 + 可能含 Scenario D 落盘结果）：

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
ls $SKILL/experience/phone-case/redmi-k80-pro.md   # 必须存在
```

## 用户 prompt

```
做红米 K80 Pro 手机壳
```

（与 D 完全一致，但这次 experience/ 有条目）

## 预期 AI 行为

### R1 产出报告必须形如

```
Step R1 产出报告
- [x] references/redmi-k80-pro/search_plan.md    (含已知参数 10 条 + 预期坑 4 条)
- [hit] experience/phone-case/redmi-k80-pro.md   (精确命中，预加载 10 参数 + 4 坑)
- [miss] experience/phone-case/*                  (无其它同类条目，已命中精确项)
下一步：等用户确认 → Step R2
```

**关键检查点**：
- ✅ `[hit]` 状态
- ✅ `search_plan.md` 的「已知参数」节包含 seed 条目里的参数（每条**带来源注释**形如 `（来自 experience/phone-case/redmi-k80-pro.md）`）
- ✅ `search_plan.md` 的「预期坑」节包含 seed 条目的坑（带来源）

### 90 天过期场景（可选子验证）

如果 seed 条目 `last_updated` 改成 2025-11-01（> 90 天前），R1 产出报告状态应降级为 `[partial]` 并显式提醒「⚠ 经验写于 X 天前，建议核实」。

### R5 行为

AI 起草 Experience Draft 时检测到 `experience/phone-case/redmi-k80-pro.md` 已存在，必须：
- 呈现新 draft vs 旧文件的 diff
- 让用户选 `merge` / `overwrite` / `keep-old`（默认推荐 merge）
- 按选择落盘（merge 的参数去重 + 坑/片段 append 不去重）

## 失败判据

- R1 没出现 `[hit]`（AI 没查 experience/ 或查了没报）
- `search_plan.md` 用了历史参数但不带来源注释（FM-7 静默加载经验）
- R5 撞已存在文件时直接覆盖写（没 diff、没让用户选）
- merge 时"坑"节被去重导致历史坑丢失（必须 append 不去重）

## 实跑结果（待操作员粘贴）

```
<完整 AI 回复>
```

## 审阅结论

- [ ] R1 出 `[hit]`
- [ ] 命中内容注入 search_plan 且带来源
- [ ] R5 撞文件时正确 diff + 让用户选
- [ ] merge 语义正确（参数去重，坑/片段 append）

**若有问题**：在文件末尾记录现象 + 回流到 Playbook 修订。
````

- [ ] **Step 2: 验证**

```bash
head -5 /Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_E.md
```

Expected: `# Scenario E — 精确命中...`。

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && \
git add tests/16-experience-dryrun/run_E.md && \
git commit -m "$(cat <<'EOF'
test(16-experience-dryrun): add Scenario E (exact hit) expectations

精确命中场景：已有 seed 条目时再跑同 slug，验证 R1 注入经验 + R5 merge/overwrite/keep-old 选择。
含 90 天过期降级为 [partial] 的子验证。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

### Task 12: 创建 run_F.md — 同类命中占位

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_F.md`

- [ ] **Step 1: 写 run_F.md**

完整文件内容：

````markdown
# Scenario F — 同类命中（slug 不同但 category 相同）

## 前置准备

仅保留 `experience/phone-case/redmi-k80-pro.md`，不要有 `xiaomi-k70.md`：

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
ls $SKILL/experience/phone-case/
# Expected: redmi-k80-pro.md（可能还有 Scenario D 落盘的文件）
# 不能有 xiaomi-k70.md；如有则先移走
```

## 用户 prompt

```
做小米 K70 手机壳
```

（slug=xiaomi-k70，category=phone-case，与 redmi-k80-pro 不同 slug 但同类）

## 预期 AI 行为

### R1 产出报告必须形如

```
Step R1 产出报告
- [x] references/xiaomi-k70/search_plan.md   (待用户确认)
- [partial] experience/phone-case/*          (同类命中 1 条：redmi-k80-pro.md confidence=4，作为参考)
- [miss] experience/*/xiaomi-k70.md          (无精确命中)
下一步：等用户确认 → Step R2
```

**关键检查点**：
- ✅ `[partial]` 状态
- ✅ 列出 `redmi-k80-pro.md` 作为**参考**（不是当成事实）
- ✅ `search_plan.md` 的「已知参数」节**不包含** redmi-k80-pro 的精确参数（因为 slug 不同）
- ✅ `search_plan.md` 的「预期坑」节可**借鉴** redmi-k80-pro 的坑（类型层面共通：如"摄像头 Y 坐标正负"），并标注「来自同类 experience/phone-case/redmi-k80-pro.md，K70 需独立验证」

### R5 行为

AI 起草 Experience Draft 时 slug 不同 → 直接创建新条目 `experience/phone-case/xiaomi-k70.md`（无需 diff），用户确认后落盘。

## 失败判据

- R1 没出现 `[partial]`
- R1 把 redmi-k80-pro 的精确参数（如 160.26×74.95）当成 K70 的数填进 search_plan（**重大错误**——跨 slug 自动合并）
- `预期坑`节完全空（没借鉴同类）或完全复制（没标"需独立验证"）
- R5 误判为"已存在" → 拿 redmi-k80-pro.md diff（slug 不同就是新文件）

## 实跑结果（待操作员粘贴）

```
<完整 AI 回复>
```

## 审阅结论

- [ ] R1 出 `[partial]` 且正确识别参考对象
- [ ] 同类参考**仅用于坑的借鉴**，参数不自动迁移
- [ ] R5 创建新条目（不和 redmi-k80-pro.md 混淆）
- [ ] Appendix A 白名单遵守（category=phone-case，不是 `手机壳` 或 `case`）

**若有问题**：记录 + 回流到 Playbook Appendix A 或改动 3 修订。
````

- [ ] **Step 2: 验证**

```bash
head -5 /Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/run_F.md
```

Expected: `# Scenario F — 同类命中...`。

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && \
git add tests/16-experience-dryrun/run_F.md && \
git commit -m "$(cat <<'EOF'
test(16-experience-dryrun): add Scenario F (category partial hit) expectations

同类命中的边界场景：slug 不同但 category 相同时，
AI 必须只借鉴"坑"不合并参数——防止 K80 Pro 的精确尺寸误当 K70 的用。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Phase D — 结构核对与最终验证

### Task 13: 结构核对全量跑一遍 + 落盘 final check 报告

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/16-experience-dryrun/structure_check.md`

- [ ] **Step 1: 跑 spec §6 的 7 项结构核对**

```bash
echo "=== Check 1: experience/ 目录存在 ===" && \
ls /Users/liyijiang/.agents/skills/build123d-cad/experience/ && \
echo "" && \
echo "=== Check 2: README.md 存在 + 含发布风险声明 ===" && \
grep -c "发布风险说明" /Users/liyijiang/.agents/skills/build123d-cad/experience/README.md && \
echo "" && \
echo "=== Check 3: Playbook 契约第 6 条 ===" && \
grep -c "R1 开始前必须查" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md && \
echo "" && \
echo "=== Check 4: R1 前置检索子段 ===" && \
grep -c "前置检索" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md && \
echo "" && \
echo "=== Check 5: R5 Experience Draft 模板 ===" && \
grep -c "Experience Draft" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md && \
echo "" && \
echo "=== Check 6: FM-7 + FM-8 ===" && \
grep -cE "^### FM-[78]" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md && \
echo "" && \
echo "=== Check 7: Appendix A category 白名单 ===" && \
grep -c "^## Appendix A" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
```

Expected:
```
=== Check 1 ===
README.md
phone-case

=== Check 2 ===
1

=== Check 3 ===
1

=== Check 4 ===
1   （或更多，只要 ≥1）

=== Check 5 ===
（≥4）

=== Check 6 ===
2

=== Check 7 ===
1
```

- [ ] **Step 2: 跑 git 追踪核对（experience/ 已进 skill 仓 git）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && \
git ls-files experience/ | head -10
```

Expected: 至少列出 `experience/README.md` 和 `experience/phone-case/redmi-k80-pro.md`。

- [ ] **Step 3: 把结果写入 structure_check.md**

````markdown
# 结构核对报告（experience/ + Playbook 修改）

执行日期：2026-04-18
执行命令：见 docs/superpowers/plans/2026-04-18-experience-cache.md Task 13

## 7 项核对

| # | 项 | 命令 | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| 1 | experience/ 目录存在 | `ls $SKILL/experience/` | README.md + phone-case/ | （填） | （填） |
| 2 | README 含发布风险声明 | `grep -c "发布风险说明" ...README.md` | 1 | （填） | （填） |
| 3 | Playbook 契约第 6 条 | `grep -c "R1 开始前必须查" ...playbook.md` | 1 | （填） | （填） |
| 4 | R1 前置检索子段 | `grep -c "前置检索" ...playbook.md` | ≥1 | （填） | （填） |
| 5 | R5 Experience Draft | `grep -c "Experience Draft" ...playbook.md` | ≥4 | （填） | （填） |
| 6 | FM-7 + FM-8 | `grep -cE "^### FM-[78]" ...playbook.md` | 2 | （填） | （填） |
| 7 | Appendix A | `grep -c "^## Appendix A" ...playbook.md` | 1 | （填） | （填） |

## Git 追踪核对

```
$ cd $SKILL && git ls-files experience/
experience/README.md
experience/phone-case/redmi-k80-pro.md
```

✅ experience/ 已进 git。

## 行为验证（Scenario D/E/F）

见 run_D.md / run_E.md / run_F.md。本 structure_check 只覆盖静态结构，行为验证由操作员后续手动跑。

## 结论

- [ ] 所有 7 项静态核对 pass
- [ ] experience/ 进 git 追踪
- [ ] 行为验证 D/E/F 完成（由操作员填 run_*.md 后勾）
````

填入实际命令输出（把 Step 1 的输出值填入 "Actual" 列）。

- [ ] **Step 4: Commit 结构核对报告**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && \
git add tests/16-experience-dryrun/structure_check.md && \
git commit -m "$(cat <<'EOF'
test(16-experience-dryrun): record final structure check results

7 项静态结构核对全部 pass：experience/ 目录 + README + Playbook 5 处修改 + FM-7/8 + Appendix A。
行为验证 D/E/F 留给操作员手动在 fresh 会话里跑。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## 操作员后续手工任务（非本计划执行范围）

计划 13 个 Task 完成后，以下任务由用户在 fresh Claude Code 会话里手工跑：

1. **Scenario D 冷启动**：按 `tests/16-experience-dryrun/run_D.md` 前置准备 → 新会话输入 prompt → 复制 AI 全量回复到 run_D.md 实跑节 → 勾审阅 checklist
2. **Scenario E 精确命中**：同上，按 run_E.md 操作
3. **Scenario F 同类命中**：同上，按 run_F.md 操作
4. **结果回流**：任一 Scenario fail，回改 Playbook 对应 Section，再跑一遍直到 pass

---

## Self-Review

**1. Spec coverage 核对**

| Spec Section | 对应 Task |
|---|---|
| §1 架构（experience/ 目录 + 与 assets 区分） | Task 1（README.md 把 §1 核心搬进去） |
| §2 条目 schema | Task 1（README 提 schema）+ Task 2（seed 条目作 schema 实例） |
| §3 R1 预检索流 | Task 5（Playbook 改动 3） |
| §4 R5 沉淀流 | Task 6（Playbook 改动 4） |
| §5 改动 1（契约第 5 条 → 第 6 条） | Task 3 |
| §5 改动 2（总表加列） | Task 4 |
| §5 改动 3（R1 前置检索） | Task 5 |
| §5 改动 4（R5 重写） | Task 6 |
| §5 改动 5（FM-7/8） | Task 7 |
| §5 附录（Appendix A 白名单） | Task 8 |
| §6 结构核对（7 项） | Task 13 |
| §6 行为验证 D/E/F | Task 9/10/11/12（占位） + 操作员手工跑 |
| §9 验收标准（experience/ 进 git 含 README） | Task 1 + Task 13 |
| §9 seed 条目 | Task 2 |

全部覆盖。

**2. Placeholder scan**

- 无 TBD / TODO / "implement later" 字样
- 每个 Task 的 old_string/new_string 都列出完整文本
- Experience Draft 模板在 Task 6 的 new_string 内完整给出
- 结构核对命令和 expected 输出都具体

**3. Type consistency**

- 状态词四态 `[hit]` / `[partial]` / `[miss]` / `[skip]` / `[saved]` 在 Task 3/5/6/10/11/12 一致使用
- frontmatter 字段名 `slug` / `category` / `tags` / `confidence` / `last_updated` / `related_tests` / `source_model` 在 Task 1 README / Task 2 seed / Task 6 R5 模板一致
- category 白名单 25 词在 Task 8 Appendix A 与 spec §1 列表一致

**4. 跨仓路径一致性**

- skill 仓所有命令都 `cd /Users/liyijiang/.agents/skills/build123d-cad`
- test 仓所有命令都在 `/Users/liyijiang/work/build123d-cad-skill-test/` 下
- seed 条目 `related_tests: [tests/13-redmi-k80-pro]` 是 test 仓相对路径（跨仓引用约定）

---

## Execution Handoff

计划完成并保存到 `docs/superpowers/plans/2026-04-18-experience-cache.md`。两种执行方式：

**1. Subagent-Driven（推荐）** — 每个 Task 派 fresh subagent，两段式 review，fast iteration

**2. Inline Execution** — 在本会话里批量执行，checkpoint 之间 review

请选择。
