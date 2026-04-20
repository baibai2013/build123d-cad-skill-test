# AIGC 概念图 → 参数化设计图 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 build123d-cad skill 中新增方案 F（AIGC 概念图 → 参数化设计图），作为既有 5 方案 A-E 的并列扩展，覆盖"用户描述含形态主观词、无参考图"的建模前对齐缺口。

**Architecture:** 在 SKILL.md §概念草图说明 段追加方案 F 完整定义（触发词 / MCP 调用 / Gate F1/F2 模板 / 降级），两个 Playbook（single / multi）§S1/§P1 加"形态评估"分支判定。halt 契约复用 §确认门执行契约，不新增 FM。MCP 使用 `mcp__doubao-mcp-server__text_to_image`，失败透明降级到方案 A。

**Tech Stack:** Markdown 文档编辑 / Bash grep 验证 / Agent 子代理 dry-run（行为验证）

**Repo 范围:**
- skill repo: `/Users/liyijiang/.agents/skills/build123d-cad/`
- test repo: `/Users/liyijiang/work/build123d-cad-skill-test/`

**依赖 spec:** `docs/superpowers/specs/2026-04-20-aigc-concept-to-param-design.md`（commit `bf809ee`）

---

## 文件结构

### skill repo（必做）

| 文件 | 改动 |
|---|---|
| `SKILL.md` | §概念草图说明 段追加方案 F 整段；§5 种方案速查表改 6 方案 |
| `references/protocols/single-part-playbook.md` | §Step S1 加"形态评估"小节 + 更新"本步产出" |
| `references/protocols/multi-part-playbook.md` | §Phase P1 加"形态评估"小节 + 更新"本步产出" |
| `assets/concept/.gitkeep` | 新建（占位保留目录） |
| `.gitignore` | 追加 `assets/concept/*` + `!assets/concept/.gitkeep` |

### test repo（可选，v1 若时间紧可跳过整组）

| 文件 | 改动 |
|---|---|
| `tests/20-aigc-concept-dryrun/README.md` | 新建 |
| `tests/20-aigc-concept-dryrun/run_P.md` | Scenario P 主观词触发 |
| `tests/20-aigc-concept-dryrun/run_Q.md` | Scenario Q 无主观词 |
| `tests/20-aigc-concept-dryrun/run_R.md` | Scenario R MCP 降级 |
| `tests/20-aigc-concept-dryrun/structure_check.md` | 结构核对 + 行为汇总 |

---

# Task Group A：skill repo（必做）

> **所有 Task 1~5 都在 `/Users/liyijiang/.agents/skills/build123d-cad/` 下执行**。每个 Task 独立 commit。

---

## Task 1: SKILL.md — 追加方案 F 整段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（方案 E 末尾 L259 附近，"5种方案选择速查"之前）

**Context:** §概念草图说明 段现有方案 A-E（L122~L259），§5 种方案速查表在 L262-L272。方案 F 整段插入点 = 方案 E "最适合" 行之后、"5种方案选择速查" 小标题之前。

- [ ] **Step 1: 用 Read 工具精确确认插入锚点**

Run:
```bash
grep -n "5种方案选择速查\|方案 E：参数约束表\|精度配合件" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected output 包含：
- `方案 E：参数约束表` 小标题行号（约 L236）
- `**最适合**：有精度要求的配合件、尺寸需要精确匹配时。`（方案 E 末尾，约 L258）
- `#### 5种方案选择速查`（约 L262）

记下方案 E "最适合" 那行 line number（N1）作为 old_string 锚点，下一行分隔线 `---`（N2）。

- [ ] **Step 2: Edit 在方案 E 之后插入方案 F 整段**

使用 Edit 工具，`old_string` 锚定方案 E 末尾 + 分隔线：

```
**最适合**：有精度要求的配合件、尺寸需要精确匹配时。

---

#### 5种方案选择速查
```

`new_string` 同上内容开头，在 `---` 之前插入方案 F 整段：

````
**最适合**：有精度要求的配合件、尺寸需要精确匹配时。

---

#### 方案 F：AIGC 概念图 → 参数化设计图

**触发词**：形态主观词命中（不需要用户主动开口）——

- 视觉风格类：科技感、极简、工业风、复古、蒸汽朋克、赛博、仿 XX 风格（如"仿苹果风"）、高级感
- 形态特征类：流畅、仿生、异形、流线型、有机、雕塑感、灵动、柔和曲面
- 产品门类类：潮玩、角品、ID 产品、手办、艺术摆件、概念设计

任一词命中 → 走方案 F。明确尺寸同时出现时仍走 F（尺寸并入 Gate F2 参数表）。词表可扩展，通过 PR 追加。

**MCP 调用规范**：

- 工具：`mcp__doubao-mcp-server__text_to_image`
- 默认参数：`size=1024x1024`，`model=doubao-seedream-3-0-t2i-250415`
- prompt 模板：`<产品类型>, <形态主观词>, industrial design concept, product rendering, 4 views composition, white background, 4k`
- 一次 halt 循环**生成 3 张**（3 次独立调用，分别对应不同风格/视角）
- 返回 URL → 用 Bash `curl -o` 下载到 `assets/concept/<slug>/<timestamp>-<n>.png`
- `<slug>` 从 S1/P1 部件名 slugify 得到（例：`phone-stand`、`gripper-arm`）
- AI 下载后用 Read 工具读图（Claude 多模态自读）供下一步视觉解读

**Gate F1 回报模板**（选图 halt）：

```
[halt-for-user] ✋ AIGC 概念图 3 张已生成：
  ① assets/concept/<slug>/<ts>-1.png  风格：<风格词>  URL：<url-1>
  ② assets/concept/<slug>/<ts>-2.png  风格：<风格词>  URL：<url-2>
  ③ assets/concept/<slug>/<ts>-3.png  风格：<风格词>  URL：<url-3>

回 "选 ①/②/③" / "reroll <prompt 调整>" / "自己给图 <路径>"
```

> 发 `[halt-for-user]` 前必过 SKILL.md §确认门执行契约 的三项自检。

**视觉解读过渡**：用户选定后，AI 用 Read 工具读选中图，拟合出：

- 正/侧/俯 3 视图 ASCII（复用方案 A 模板）
- 关键尺寸参数合同表（复用方案 E 模板）

**Gate F2 回报模板**（参数确认 halt）：

```
[halt-for-user] ✋ 请确认：
（1）3 视图拟合 AIGC 图的形态是否准确？
（2）参数合同表每行数值是否接受？需改的直接给正确值。
回 "OK" / "改 <参数>=<值>"
```

> 发 `[halt-for-user]` 前必过 SKILL.md §确认门执行契约 的三项自检。

**降级策略**：

- 触发：MCP 抛错 / 超时（>30s） / 3 次 reroll 后用户仍不满
- 动作：AI 透明告知"AIGC 不可用 / 用户未选定，切换到方案 A"，继续方案 A 自画 3 视图路径，不阻塞
- 例外：用户在 Gate F1 主动选"自己给图"时**不走降级**，直接跳到视觉解读

**契约**：Gate F1 / Gate F2 均为 `[halt-for-user]` 硬字段，遵循 SKILL.md §确认门执行契约；违规 = single-part FM-1 / multi-part FM-13「越权通过确认门」。**不新增 FM**。

**最适合**：用户描述含形态主观词、无参考图、需先定意象的单 / 多部件。

---

#### 5种方案选择速查
````

- [ ] **Step 3: Verify — grep 方案 F 段已就位**

Run:
```bash
grep -cE "方案 F|text_to_image|Gate F1|Gate F2|halt-for-user.*AIGC" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: ≥ 5（方案 F 标题 1 + text_to_image 1 + Gate F1 1 + Gate F2 1 + halt-for-user 带 AIGC 上下文 1）

Run:
```bash
grep -n "方案 F：AIGC\|#### 5种方案选择速查" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: 方案 F 行号 < 5 种方案速查行号（F 在速查表之前）

- [ ] **Step 4: Commit（skill repo）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add SKILL.md && git commit -m "$(cat <<'EOF'
docs(skill): SKILL.md 追加方案 F (AIGC 概念图 → 参数化设计图)

在 §概念草图说明 段方案 E 之后追加方案 F 整段：触发词（形态主观词）/
MCP 调用规范（doubao text_to_image, 3 张/循环）/ Gate F1 选图 halt /
视觉解读过渡 / Gate F2 参数确认 halt / 降级策略（MCP 不可用→方案 A）。
halt 契约复用 §确认门执行契约 + FM-1/FM-13，不新增 FM。

对应 spec: docs/superpowers/specs/2026-04-20-aigc-concept-to-param-design.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: SKILL.md — 5 种方案速查表改 6 方案

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（L262-L272 §5 种方案选择速查 段）

**Context:** Task 1 完成后，表格仍是"5种"，需改标题 + 追加方案 F 行 + 补可组合说明。

- [ ] **Step 1: Edit 速查表标题 + 表格 + 可组合行**

使用 Edit 工具，`old_string`：

```
#### 5种方案选择速查

| 方案 | 对齐的是什么 | 生成开销 | 最适合场景 |
|------|------------|---------|-----------|
| A 3视图草图 | 整体形状 | 中（Matplotlib） | 复杂单体，无参考图 |
| B OCP快速原型 | 3D比例+装配位置 | 快（build123d） | 多部件装配 |
| C 关键截面草图 | 截面轮廓 | 中（Matplotlib） | Revolve / Sweep 件 |
| D 参考图标注 | AI对图的理解 | 极快（纯文字） | 有参考图时 |
| E 参数约束表 | 关键尺寸数值 | 极快（表格） | 精度配合件 |

> **可组合**：多部件设计推荐 B（整体比例）+ D（参考图理解）+ E（参数锁定）三连。
```

`new_string`：

```
#### 6 种方案选择速查

| 方案 | 对齐的是什么 | 生成开销 | 最适合场景 |
|------|------------|---------|-----------|
| A 3视图草图 | 整体形状 | 中（Matplotlib） | 复杂单体，无参考图 |
| B OCP快速原型 | 3D比例+装配位置 | 快（build123d） | 多部件装配 |
| C 关键截面草图 | 截面轮廓 | 中（Matplotlib） | Revolve / Sweep 件 |
| D 参考图标注 | AI对图的理解 | 极快（纯文字） | 有参考图时 |
| E 参数约束表 | 关键尺寸数值 | 极快（表格） | 精度配合件 |
| F AIGC 概念图 → 参数合同 | 意象 + 尺寸 | 慢（MCP API 调用） | 形态主观词、无参考图 |

> **可组合**：多部件设计推荐 B（整体比例）+ D（参考图理解）+ E（参数锁定）三连。
> **方案 F 独立使用**：F 已包含 A（3 视图）+ E（参数表）的产出形态，单独使用即可，不需再叠加。
```

- [ ] **Step 2: Verify — 速查表改 6 种且方案 F 行存在**

Run:
```bash
grep -c "6 种方案选择速查\|F AIGC 概念图\|方案 F 独立使用" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: ≥ 3

Run:
```bash
grep -c "5种方案选择速查" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: 0（旧标题应已被替换）

- [ ] **Step 3: Commit（skill repo）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add SKILL.md && git commit -m "$(cat <<'EOF'
docs(skill): 速查表改 6 种方案 + 方案 F 独立使用说明

§概念草图说明 速查表：5种 → 6种，追加方案 F 行（意象 + 尺寸 / 慢 MCP /
形态主观词场景）。可组合行补充"方案 F 独立使用即可，已含 A+E 产出"说明。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: single-part-playbook.md — §S1 加形态评估

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md`（§Step S1，L34~L74）

**Context:** §Step S1 "本步产出"（L39-41）、"参考资料问询"命令模板（L58-63）、"AI 回报契约"（L65-74）。形态评估小节插入在"参考资料问询"命令模板之后、"AI 回报契约"之前。同时 "本步产出" 清单追加一项。

- [ ] **Step 1: Edit 更新 §S1 "本步产出" 清单（追加形态评估项）**

使用 Edit 工具，`old_string`：

```
**本步产出**：
- 需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）
- 参考资料问询（"是否有参考图、参考链接或参考描述？"）
```

`new_string`：

```
**本步产出**：
- 需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）
- 参考资料问询（"是否有参考图、参考链接或参考描述？"）
- 形态评估结论（命中的形态主观词列举 + S2 路径判定：走方案 F / 走方案 A）
```

- [ ] **Step 2: Edit 在 AI 回报契约之前插入形态评估小节**

**锚点选择**：`**AI 回报契约**：` 在每个 Step 都出现，需用更长上下文确保 S1 唯一。用 "AI 回报契约 + blank + ``` + Step S1 产出报告 + Quote-back 原文行" 作锚点（S1 独有）。

使用 Edit 工具，`old_string`（注意空行数，对齐 single-part-playbook.md 实际文件 L65-70）：

````
**AI 回报契约**：

```
Step S1 产出报告
引自 single-part-playbook.md §Step S1 / 本步产出：
  "需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）"
````

`new_string`：

````
**形态评估**（决定 S2 分支：方案 F vs 方案 A）

检测需求文本是否含形态主观词（完整词表见 SKILL.md §方案 F：AIGC 概念图 → 参数化设计图 / 触发词）：

- 视觉风格类：科技感、极简、工业风、复古、仿 XX 风格、高级感
- 形态特征类：流畅、仿生、异形、流线型、有机、雕塑感、灵动、柔和曲面
- 产品门类类：潮玩、角品、ID 产品、手办、艺术摆件、概念设计

**任一词命中** → S2 走方案 F（AIGC 生成概念图 → Gate F1 选图 → 视觉解读 → 3 视图 + 参数合同表 → Gate F2 确认 → 建模）
**未命中** → S2 走方案 A（AI 自画 3 视图 ASCII，沿原流程）

**引 SKILL.md §方案 F / 触发词**：任一主观词命中 → 走方案 F；未命中走方案 A。

**AI 回报契约**：

```
Step S1 产出报告
引自 single-part-playbook.md §Step S1 / 本步产出：
  "需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）"
````

- [ ] **Step 3: Edit 更新 §S1 AI 回报契约示例（加形态评估一行）**

使用 Edit 工具，`old_string`：

```
Step S1 产出报告
引自 single-part-playbook.md §Step S1 / 本步产出：
  "需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）"
- [x] 需求分析表已输出（见上方）
- [x] 已询问参考资料
下一步：Step S2（等用户回复参考资料）
```

`new_string`：

```
Step S1 产出报告
引自 single-part-playbook.md §Step S1 / 本步产出：
  "需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）"
- [x] 需求分析表已输出（见上方）
- [x] 已询问参考资料
- [x] 形态评估结论：<命中词列举 或"未命中">，S2 走 <方案 F / 方案 A>
下一步：Step S2（等用户回复参考资料）
```

- [ ] **Step 4: Verify — 形态评估段已就位**

Run:
```bash
grep -c "形态评估" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md
```
Expected: ≥ 3（小节标题 1 + 本步产出项 1 + AI 回报契约示例 1）

Run:
```bash
grep -c "方案 F / 触发词\|走方案 F\|走方案 A" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md
```
Expected: ≥ 3

- [ ] **Step 5: Commit（skill repo）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/single-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(skill): single-part-playbook §S1 加形态评估分支

在 §Step S1 本步产出 + 命令模板追加"形态评估"小节：检测主观词 →
判定 S2 走方案 F (AIGC 概念图) / 方案 A (AI 自画 3 视图)。
AI 回报契约示例同步加形态评估结论一行。
FM 复用 FM-1，不新增。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: multi-part-playbook.md — §P1 加形态评估

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md`（§Phase P1，L34~L100）

**Context:** §Phase P1 "本步产出"（L40-42）、"需求拆解报告"命令模板（L45-77）、"几何对齐" 段（L79-84，推荐 D+B+E 三连）、"确认门 ✋"（L86-88）、"AI 回报契约"（L90-100）。形态评估插入在"几何对齐"段之后、"确认门 ✋"之前（或合并到几何对齐段内作为前置判定）。采用插入独立小节、位置：几何对齐段之后、确认门之前。

- [ ] **Step 1: Edit 更新 §P1 "本步产出" 清单**

使用 Edit 工具，`old_string`：

```
**本步产出**：
- 需求拆解报告（部件清单 + 装配关系 + 工艺确认 + 仿真需求 + 可选专家意见）
- 用户确认门 ✋
```

`new_string`：

```
**本步产出**：
- 需求拆解报告（部件清单 + 装配关系 + 工艺确认 + 仿真需求 + 可选专家意见）
- 形态评估结论（命中的形态主观词列举 + P2 路径判定：走方案 F / 走方案 A）
- 用户确认门 ✋
```

- [ ] **Step 2: Edit 在"几何对齐"段之后、"确认门 ✋"之前插入形态评估小节**

使用 Edit 工具，`old_string`（锚点 = 几何对齐段末尾 "AI 不主动触发，必须用户开口要求。" + halt 回链 + 确认门 ✋ 行）：

```
AI 不主动触发，必须用户开口要求。

> 发 `[halt-for-user]` 前必过 SKILL.md §确认门执行契约 的三项自检。

**确认门 ✋** 用户回复「OK」或修改部件清单后，才进入 Phase P2。
```

`new_string`：

```
AI 不主动触发，必须用户开口要求。

**形态评估**（决定 P2 分支：方案 F vs 方案 A）

检测需求文本（整机及各部件描述）是否含形态主观词（完整词表见 SKILL.md §方案 F：AIGC 概念图 → 参数化设计图 / 触发词）：

- 视觉风格类：科技感、极简、工业风、复古、仿 XX 风格、高级感
- 形态特征类：流畅、仿生、异形、流线型、有机、雕塑感、灵动、柔和曲面
- 产品门类类：潮玩、角品、ID 产品、手办、艺术摆件、概念设计

**任一词命中**（整机或任一部件）→ P2 走方案 F（AIGC 整机 / 关键外观部件概念图 → Gate F1 选图 → 视觉解读 → 3 视图 + 参数合同表 → Gate F2 确认 → 建模）
**未命中** → P2 走方案 A（AI 自画 3 视图 ASCII，沿原流程）

**引 SKILL.md §方案 F / 触发词**：任一主观词命中 → 走方案 F；未命中走方案 A。

> 发 `[halt-for-user]` 前必过 SKILL.md §确认门执行契约 的三项自检。

**确认门 ✋** 用户回复「OK」或修改部件清单后，才进入 Phase P2。
```

- [ ] **Step 3: Edit 更新 §P1 AI 回报契约示例（加形态评估一行）**

使用 Edit 工具，`old_string`：

```
Phase P1 产出报告
引自 multi-part-playbook.md §Phase P1 / 本步产出：
  "需求拆解报告（部件清单 + 装配关系 + 工艺确认 + 仿真需求 + 可选专家意见）"
- [x] 需求拆解报告已输出（部件清单 3 项 / 装配链 2 个关节 / 工艺=3D打印）
- [x] 已询问参考图（用户提供 1 张正视图）
- [halt-for-user] ✋ 确认部件清单和装配关系正确，回 "OK" 进 P2 / 或指出修改项
```

`new_string`：

```
Phase P1 产出报告
引自 multi-part-playbook.md §Phase P1 / 本步产出：
  "需求拆解报告（部件清单 + 装配关系 + 工艺确认 + 仿真需求 + 可选专家意见）"
- [x] 需求拆解报告已输出（部件清单 3 项 / 装配链 2 个关节 / 工艺=3D打印）
- [x] 已询问参考图（用户提供 1 张正视图）
- [x] 形态评估结论：<命中词列举 或"未命中">，P2 走 <方案 F / 方案 A>
- [halt-for-user] ✋ 确认部件清单和装配关系正确，回 "OK" 进 P2 / 或指出修改项
```

- [ ] **Step 4: Verify — 形态评估段已就位**

Run:
```bash
grep -c "形态评估" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md
```
Expected: ≥ 3

Run:
```bash
grep -c "方案 F / 触发词\|走方案 F\|走方案 A" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md
```
Expected: ≥ 3

- [ ] **Step 5: Commit（skill repo）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(skill): multi-part-playbook §P1 加形态评估分支

在 §Phase P1 本步产出 + 几何对齐段之后插入"形态评估"小节：检测整机 /
各部件描述的主观词 → 判定 P2 走方案 F (AIGC 概念图) / 方案 A。
AI 回报契约示例同步加形态评估结论一行。FM 复用 FM-13，不新增。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: assets/concept/ 目录 + .gitignore

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/assets/concept/.gitkeep`（空文件占位）
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/.gitignore`（追加 2 行）

**Context:** 方案 F 生成图按约定保存在 `assets/concept/<slug>/<ts>-<n>.png`。生成图**不入 git**（URL 可能过期 + 仓库膨胀），但保留目录存在需要 `.gitkeep`。

- [ ] **Step 1: 创建 assets/concept/.gitkeep**

```bash
mkdir -p /Users/liyijiang/.agents/skills/build123d-cad/assets/concept && touch /Users/liyijiang/.agents/skills/build123d-cad/assets/concept/.gitkeep
```

- [ ] **Step 2: Edit .gitignore 追加 assets/concept 规则**

使用 Edit 工具，`old_string`（定位到现有 .gitignore 末尾区段）：

```
# Cache
.mypy_cache/
__pycache__/
```

`new_string`：

```
# Cache
.mypy_cache/
__pycache__/

# 方案 F AIGC 生成的概念图（URL 可能过期 + 仓库膨胀，不入 git）
assets/concept/*
!assets/concept/.gitkeep
```

- [ ] **Step 3: Verify — .gitignore 规则生效**

Run:
```bash
ls -la /Users/liyijiang/.agents/skills/build123d-cad/assets/concept/.gitkeep
```
Expected: 文件存在

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && echo "test" > assets/concept/test.png && git check-ignore -v assets/concept/test.png ; rm assets/concept/test.png
```
Expected: `.gitignore:N:assets/concept/* assets/concept/test.png`（被 ignore）

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git check-ignore -v assets/concept/.gitkeep ; echo "EXIT:$?"
```
Expected: 无输出 + `EXIT:1`（.gitkeep **不**被 ignore，因为 `!assets/concept/.gitkeep` 例外规则生效）

- [ ] **Step 4: Commit（skill repo）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add .gitignore assets/concept/.gitkeep && git commit -m "$(cat <<'EOF'
chore(skill): assets/concept/ 目录 + .gitignore 规则

为方案 F 准备 AIGC 生成图存放目录 assets/concept/<slug>/<ts>-<n>.png。
生成图不入 git（URL 可能过期 + 仓库膨胀），但保留 .gitkeep 占位目录。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

# Task Group B：test repo 行为验证（可选）

> **Task 6~8 都在 `/Users/liyijiang/work/build123d-cad-skill-test/` 下执行**。若时间紧可跳过整组，靠用户新会话手动跑回归验证方案 F。如果做，三个 Scenario 用 Agent 子代理（`subagent_type=general-purpose`）模拟新会话执行。

---

## Task 6: tests/20 骨架 — README + 3 Scenario 描述

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/README.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_P.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_Q.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_R.md`

**Context:** 参考 tests/19（halt-gate-enforcement）的骨架格式：每个 run_*.md 含 Prompt / 预期行为 / 判据表 / AI 完整回复占位（由 Task 7 的 Agent 填充）/ 判据 check / 结论 / Review 记录。

- [ ] **Step 1: 创建 tests/20 目录 + README.md**

```bash
mkdir -p /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun
```

使用 Write 工具创建 `README.md`：

```markdown
# tests/20 — 方案 F AIGC 概念图 → 参数化设计图 dry-run 行为验证

对应设计文档：`docs/superpowers/specs/2026-04-20-aigc-concept-to-param-design.md`
对应 plan：`docs/superpowers/plans/2026-04-20-aigc-concept-to-param-plan.md`

## Scenario 清单

| Scenario | 诱因 | 期望路径 |
|---|---|---|
| **P** 主观词触发 | "仿生风格 / 流畅 / 设计感" | S1 形态评估命中 → S2 走方案 F → 调 MCP → Gate F1 halt |
| **Q** 无主观词 | "Ø20×80 阶梯轴" | S1 形态评估未命中 → S2 走方案 A → 不调 MCP |
| **R** MCP 降级 | 同 P，但约束 "MCP 不可用" | 尝试调 MCP 失败 → 透明降级到方案 A |

## 运行方式

每个 Scenario 通过 Agent 子代理（`subagent_type=general-purpose`）模拟新会话：
- 子代理必须 Read SKILL.md 开始按启动序列执行
- 子代理记录完整 AI 回复（含 Read 动作、路由判定、本步产出、halt）写入对应 `run_*.md`
- 主代理对照判据表 check 每条，填 ✅ / ⚠ / ❌

## 判据汇总

详见 `structure_check.md`。合计 17 条判据（P 7 + Q 5 + R 5），**硬下限 11/17**。

## dry-run 注意

- Scenario R **不真实调 MCP**（节省 API + 保一致），而是子代理 prompt 里注入"假设 text_to_image 抛错"
- Scenario P **可选真实调 MCP**（消耗 3 次 API）或同样 dry-run（注入"假设生成 3 张图"），v1 建议 dry-run 保一致
- 判据侧重路由与 halt 契约，非图像质量
```

- [ ] **Step 2: 创建 run_P.md（Scenario P 骨架，AI 回复段暂留占位 `(待 Task 7 Agent 填充)`）**

使用 Write 工具创建 `run_P.md`：

````markdown
# Scenario P — 主观词触发方案 F

**Prompt**（新会话喂入）：

```
帮我做一个仿生风格的手机支架，要流畅有设计感。
```

**预期行为**（对齐 spec §4.1）：
- 路由到 single-part-playbook
- S1 形态评估识别主观词 "仿生 / 流畅 / 设计感"，判定走方案 F
- AI 调 `mcp__doubao-mcp-server__text_to_image` 3 次（可 dry-run 注入"假设生成 3 张"）
- 生成图下载到 `assets/concept/phone-stand/*.png`
- Gate F1 回报末尾发 `[halt-for-user]` + 3 张 URL
- 同一轮 halt 之后**没有 3 视图 / 参数表 / 建模代码**

**判据**（7 条，硬下限 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| P-1 | 路由到 single-part-playbook（明确 Read） | ⬛ |
| P-2 | S1 形态评估识别主观词 "仿生 / 流畅 / 设计感"，判定走方案 F | ⬛ |
| P-3 | AI 调（或 dry-run 模拟调）`text_to_image` 3 次 | ⬛ |
| P-4 | 生成图下载路径为 `assets/concept/phone-stand/*.png` | |
| P-5 | Gate F1 回报末尾含 `[halt-for-user]` + 3 张 URL | ⬛ |
| P-6 | `[halt-for-user]` 之后同一轮**没有 3 视图 / 参数表 / 建模代码** | ⬛ |
| P-7 | Quote-back 引 SKILL.md §方案 F 正确（含"触发词"或"MCP 调用规范"等子标题） | |

---

## AI 完整回复

(待 Task 7 Agent 填充)

---

## 判据 check

(待 Task 7 Agent 填充)

## 结论

(待 Task 7 Agent 填充)

## Review 记录

(待 Task 7 Agent 填充)
````

- [ ] **Step 3: 创建 run_Q.md（Scenario Q 骨架）**

使用 Write 工具创建 `run_Q.md`：

````markdown
# Scenario Q — 无主观词走方案 A

**Prompt**：

```
做一个 Ø20×80 的阶梯轴。
```

**预期行为**（对齐 spec §4.2）：
- 路由到 single-part-playbook
- S1 形态评估判定**无主观词**（Ø20×80 / 阶梯轴都是几何词）
- S2 走方案 A（AI 自画 3 视图 ASCII），**不**调 MCP
- S2 halt 正常发出

**判据**（5 条，硬下限 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| Q-1 | 路由到 single-part-playbook | ⬛ |
| Q-2 | S1 形态评估判定**无主观词**，S2 走方案 A（**不**调 MCP） | ⬛ |
| Q-3 | 按方案 A 自画 3 视图 ASCII / Matplotlib 说明 | |
| Q-4 | S2 halt 正常发出（`[halt-for-user]`） | ⬛ |
| Q-5 | Quote-back 格式正确 | |

---

## AI 完整回复

(待 Task 7 Agent 填充)

---

## 判据 check

(待 Task 7 Agent 填充)

## 结论

(待 Task 7 Agent 填充)

## Review 记录

(待 Task 7 Agent 填充)
````

- [ ] **Step 4: 创建 run_R.md（Scenario R 骨架）**

使用 Write 工具创建 `run_R.md`：

````markdown
# Scenario R — MCP 降级

**Prompt**（子代理 Scenario prompt 里明确注入"假设 `mcp__doubao-mcp-server__text_to_image` 抛错 / 不可用"）：

```
帮我做一个仿生风格的手机支架，要流畅有设计感。

[Scenario R 约束：假设 text_to_image MCP 工具抛错/不可用，子代理按该约束执行，不真实调 MCP]
```

**预期行为**（对齐 spec §4.3）：
- AI 识别主观词，尝试调 MCP（描述"假设调 text_to_image → 抛错"）
- AI 透明告知"AIGC 不可用，切换到方案 A"
- 不阻塞，继续走方案 A 自画 3 视图路径
- 未在同一轮越过 halt 推进建模

**判据**（5 条，硬下限 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| R-1 | AI 识别主观词，尝试调 MCP（至少描述 text_to_image 调用 + 抛错结果） | |
| R-2 | MCP 返回错误后，AI 透明告知"AIGC 不可用，切换方案 A" | ⬛ |
| R-3 | 不阻塞，继续走方案 A 路径 | ⬛ |
| R-4 | 未在同一轮越过 halt 推进建模 | ⬛ |
| R-5 | 降级过程有 Quote-back 引 §方案 F "降级策略" | |

---

## AI 完整回复

(待 Task 7 Agent 填充)

---

## 判据 check

(待 Task 7 Agent 填充)

## 结论

(待 Task 7 Agent 填充)

## Review 记录

(待 Task 7 Agent 填充)
````

- [ ] **Step 5: Verify — tests/20 骨架齐全**

Run:
```bash
ls /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/
```
Expected: `README.md` / `run_P.md` / `run_Q.md` / `run_R.md` 四个文件

- [ ] **Step 6: Commit（test repo）**

```bash
git add tests/20-aigc-concept-dryrun/README.md tests/20-aigc-concept-dryrun/run_P.md tests/20-aigc-concept-dryrun/run_Q.md tests/20-aigc-concept-dryrun/run_R.md && git commit -m "$(cat <<'EOF'
test(20): 方案 F AIGC dry-run 骨架 (README + P/Q/R 占位)

对应 spec §4 行为验证三个 Scenario：
- P 主观词触发走方案 F（仿生手机支架）
- Q 无主观词走方案 A（Ø20×80 阶梯轴）
- R MCP 不可用降级（P 约束 + "假设 text_to_image 抛错"）

AI 回复段留占位，待 Task 7 Agent 子代理模拟新会话填充。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: 用 Agent 子代理跑 3 Scenario 填充 run_*.md

**Files:**
- Modify: `tests/20-aigc-concept-dryrun/run_P.md`（填充 AI 完整回复 + 判据 check + 结论 + Review 记录）
- Modify: `tests/20-aigc-concept-dryrun/run_Q.md`（同上）
- Modify: `tests/20-aigc-concept-dryrun/run_R.md`（同上）

**Context:** 每个 Scenario 用一个 Agent 子代理（`subagent_type=general-purpose`）模拟新会话执行。子代理从 Read `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md` 开始，按 §AI 执行准入序列 + §概念草图说明（含新方案 F）+ 相应 Playbook 执行。

子代理 prompt 模板（每 Scenario 替换具体 prompt + 约束）：

```
你是一个新会话的 Claude Code Opus 4.7。按 /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md 的 §AI 执行准入序列开始执行。

用户需求：<SCENARIO_PROMPT>

<SCENARIO_CONSTRAINTS>

输出要求：
1. Read 动作总结（列出 Read 过的文件 + 关键段）
2. 路由判定（引 SKILL.md §流程路由 + 形态评估判定）
3. 按对应 Playbook Step S1/P1 执行，产出完整报告
4. 回报末尾发 [halt-for-user]（若契约要求）
5. 不跨 halt 推进；halt 前三项自检完整

dry-run 约定：Scenario P 可选择描述"假设调 text_to_image 返回 3 个 URL"而不真实调 MCP；Scenario R 必须注入"假设 text_to_image 抛错"；Scenario Q 不应触发 MCP。

回报我你的完整 AI 回复（包括 Read 动作总结 + 路由判定 + Step 产出 + halt），格式参考 tests/19 的 run_L/M/N。
```

- [ ] **Step 1: 用 Agent 跑 Scenario P，填充 run_P.md**

dispatch 一个 `subagent_type=general-purpose` Agent：

```
description: "Scenario P dry-run"
prompt: <按上方模板填入 Scenario P 的 prompt "帮我做一个仿生风格的手机支架，要流畅有设计感。" + 约束"假设调 text_to_image 返回 3 个 URL（mock）">
```

得到 AI 完整回复后，Edit `run_P.md` 把 `(待 Task 7 Agent 填充)` 段替换为：
- **AI 完整回复** 段：粘贴子代理完整输出
- **判据 check** 段：根据 AI 输出逐条 check 7 条判据，标 `[x] ⬛` / `[x]` / `[⚠]` / `[ ]`
- **结论** 段：`**通过**：<N>/7 ✅（硬下限 <X>/<Y> 全过）` 等
- **Review 记录** 段：运行人 / 日期 / 执行范围 / 总体结论

- [ ] **Step 2: 用 Agent 跑 Scenario Q，填充 run_Q.md**

同 Step 1，prompt 换成 "做一个 Ø20×80 的阶梯轴。"，约束为空（确认无主观词 → 不应触发 MCP）。

Edit `run_Q.md` 填充 5 条判据 check + 结论 + Review 记录。

- [ ] **Step 3: 用 Agent 跑 Scenario R，填充 run_R.md**

同 Step 1，prompt 加 "[Scenario R 约束：假设 text_to_image MCP 工具抛错/不可用]"。

Edit `run_R.md` 填充 5 条判据 check + 结论 + Review 记录。

- [ ] **Step 4: Verify — 3 个 run 文件占位全部清空**

Run:
```bash
grep -c "待 Task 7 Agent 填充" /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_P.md /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_Q.md /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_R.md
```
Expected: 每个文件 0 次（全部已替换）

Run:
```bash
grep -c "通过\|Review 记录\|AI 完整回复" /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/run_P.md
```
Expected: ≥ 3

- [ ] **Step 5: Commit（test repo）**

```bash
git add tests/20-aigc-concept-dryrun/run_P.md tests/20-aigc-concept-dryrun/run_Q.md tests/20-aigc-concept-dryrun/run_R.md && git commit -m "$(cat <<'EOF'
test(20): Scenario P/Q/R 行为验证结果填充

用 Agent 子代理 (subagent_type=general-purpose) 模拟新会话跑 3 Scenario：
- P 主观词触发走方案 F：验证路由 + MCP 调用描述 + Gate F1 halt
- Q 无主观词走方案 A：验证不调 MCP + 方案 A 3 视图
- R MCP 降级：验证透明降级到方案 A 不阻塞

判据 check + 结论 + Review 记录已填入各 run_*.md。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: tests/20 structure_check.md 汇总

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/structure_check.md`

**Context:** 对照 spec §6.1 结构核对 7 条 + §6.2 行为验证 3 Scenario 合计 17 条判据（硬下限 11），汇总成 tests/20 最终产物，格式参考 tests/19 structure_check.md。

- [ ] **Step 1: Write structure_check.md**

使用 Write 工具创建 `/Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/structure_check.md`：

```markdown
# tests/20 结构核对

运行日期：2026-04-20

对应设计文档 `docs/superpowers/specs/2026-04-20-aigc-concept-to-param-design.md` §6.1 与 §6.2。

## 结构核对检查（spec §6.1）

| # | 检查项 | 期望 | 实际 | 结果 |
|---|---|---|---|---|
| 1 | `grep -c "方案 F" SKILL.md` | ≥ 3 | <填> | <填> |
| 2 | `grep -c "text_to_image" SKILL.md` | ≥ 1 | <填> | <填> |
| 3 | `grep -c "形态评估" single-part-playbook.md` | ≥ 1 | <填> | <填> |
| 4 | `grep -c "形态评估" multi-part-playbook.md` | ≥ 1 | <填> | <填> |
| 5 | `ls assets/concept/.gitkeep` | 存在 | <填> | <填> |
| 6 | 5种方案速查表改为 6 种 | ✅ | <填> | <填> |
| 7 | tests/20 文件齐全 | 5/5 | 5/5 | ✅ |

## 行为验证 Scenario P/Q/R 结果

| Scenario | 诱因 | 判据通过 | 硬下限 | 结论 |
|---|---|---|---|---|
| **P** 主观词触发 | "仿生 / 流畅 / 设计感" | <N>/7 | P-1/P-2/P-3/P-5/P-6 | <填> |
| **Q** 无主观词 | "Ø20×80 阶梯轴" | <N>/5 | Q-1/Q-2/Q-4 | <填> |
| **R** MCP 降级 | P + 约束"text_to_image 抛错" | <N>/5 | R-2/R-3/R-4 | <填> |

**合计**：<N>/17 ✅（spec §6.2 阈值 14/17 ✅ 为 PASS，硬下限 11/11 全 ✅ 为更强信号）

## 文件改动清单

### skill 仓 `/Users/liyijiang/.agents/skills/build123d-cad/`

| commit | 文件 | 要点 |
|---|---|---|
| <sha> | SKILL.md | +方案 F 整段（触发词 / MCP 规范 / Gate F1/F2 / 降级）|
| <sha> | SKILL.md | 速查表 5→6 种 + 方案 F 行 + 可组合说明 |
| <sha> | references/protocols/single-part-playbook.md | §S1 加形态评估分支 |
| <sha> | references/protocols/multi-part-playbook.md | §P1 加形态评估分支 |
| <sha> | .gitignore + assets/concept/.gitkeep | 方案 F 图片存放目录约定 |

### test 仓 `/Users/liyijiang/work/build123d-cad-skill-test/`

- `docs/superpowers/specs/2026-04-20-aigc-concept-to-param-design.md`（commit bf809ee）
- `docs/superpowers/plans/2026-04-20-aigc-concept-to-param-plan.md`
- `tests/20-aigc-concept-dryrun/README.md`
- `tests/20-aigc-concept-dryrun/run_P.md` / `run_Q.md` / `run_R.md`
- `tests/20-aigc-concept-dryrun/structure_check.md`（本文件）

## 回归验证待执行（用户新会话手动跑）

- **test 13/14**（single-part Ø20×80 / 手机壳类几何明确件）→ 验证不调 MCP、方案 A 路径无回退
- **新建任务**（含主观词，如"仿生风格手机支架"）→ 验证方案 F 全流程（MCP 3 张 / Gate F1 选图 / 3 视图参数表 / Gate F2 / 建模）

## 结论

- 结构核对 **<N>/7 ✅**
- 行为验证 P/Q/R 合计 **<N>/17 ✅**（硬下限 <X>/11 ✅）
- 方案 F 在"主观词 / 无主观词 / MCP 降级"三类典型诱因下路由正确、halt 契约生效
- 可推进 push remote，通告用户在新会话跑 test 13/14 + 新含主观词任务回归
```

- [ ] **Step 2: 填充实际检查结果**

对 structure_check.md 中的每个 `<填>` 替换为实际值：

Run 6 次 grep 检查：
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "方案 F" SKILL.md
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "text_to_image" SKILL.md
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "形态评估" references/protocols/single-part-playbook.md
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "形态评估" references/protocols/multi-part-playbook.md
ls /Users/liyijiang/.agents/skills/build123d-cad/assets/concept/.gitkeep
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "6 种方案选择速查" SKILL.md
```

根据结果 Edit structure_check.md 填入每个"实际"列的数值和 "结果" ✅/❌。

从 run_P.md / run_Q.md / run_R.md 读 "通过" 段，填入"行为验证"表的"判据通过"与"结论"列。

获取 skill 仓各 commit sha：
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git log --oneline -6
```
填入文件改动清单的 `<sha>` 列。

- [ ] **Step 3: Verify — 所有占位已替换**

Run:
```bash
grep -c "<填>\|<sha>\|<N>\|<X>" /Users/liyijiang/work/build123d-cad-skill-test/tests/20-aigc-concept-dryrun/structure_check.md
```
Expected: 0（全部替换完毕）

- [ ] **Step 4: Commit（test repo）**

```bash
git add tests/20-aigc-concept-dryrun/structure_check.md && git commit -m "$(cat <<'EOF'
test(20): structure_check 汇总 — 结构 + 行为 17 判据

对照 spec §6.1 结构核对 7 条 + §6.2 行为验证 Scenario P/Q/R 合计 10 条，
汇总 tests/20 最终结果。附 skill 仓 5 次 commit 改动清单 + 回归待执行说明。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

# 验收

完成所有 Task 后确认：

- [ ] **skill repo** 5 次 commit（Task 1~5 各一），`git log --oneline -5` 显示方案 F 相关
- [ ] **test repo** 3 次 commit（Task 6/7/8 各一，若做 Task Group B），`git log --oneline -3` 显示 tests/20 相关
- [ ] **plan 自身**（本文件）也要 commit 到 test repo：
  ```bash
  git add docs/superpowers/plans/2026-04-20-aigc-concept-to-param-plan.md && git commit -m "docs: add halt-gate-enforcement AIGC plan"
  ```
- [ ] spec §6.1 结构核对 7/7 通过
- [ ] spec §6.2 行为验证（若做 Task Group B）≥ 14/17 ✅，硬下限 11/11 全 ✅
- [ ] 用户新会话手动回归 test 13/14 + 新含主观词任务确认无回退
- [ ] 推送 remote（两个仓分别 `git push`）

---

# 执行顺序建议

**单日完成（0.5-1 天，不做 tests/20）**：
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → plan 自身 commit → skill repo push → test repo push → 用户手动回归

**单日完成（1-1.5 天，含 tests/20）**：
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → plan commit → 两仓 push

Task 1~5 每个 commit 独立，失败可单独 revert。Task 6~8 是 test repo 独立变更，与 skill repo 解耦。
