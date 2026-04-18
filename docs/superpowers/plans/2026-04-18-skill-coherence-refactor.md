# build123d-cad skill 连贯性重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 AI 真打开 Playbook 文件走流程而不是凭 SKILL.md 记忆走——通过 SKILL.md 去内容化 + 单/多部件 Playbook 化 + Quote-back 强制读取证据 + references/INDEX 统一导航。

**Architecture:** SKILL.md 从 1419 行瘦到 ≤1200 行（纯路由 + 跨流程参考知识）；三大流程全部搬到 `references/protocols/` 目录下的独立 Playbook 文件；每个 Step 产出报告首行强制 Quote-back（引用 Playbook 原文）；`references/INDEX.md` 跨目录兜底导航。

**Tech Stack:** Markdown 文档 + bash (grep/wc/ls)。仅两个仓改动：skill 仓 `/Users/liyijiang/.agents/skills/build123d-cad/`（结构改动）+ test 仓 `/Users/liyijiang/work/build123d-cad-skill-test/`（本计划自身 + 行为验证目录）。

**前置依赖**：`docs/superpowers/plans/2026-04-18-experience-cache.md` 已实施完成。本计划改动的 `reference-product-playbook.md` 是 experience-cache 修订后的状态（执行契约已含第 6 条、含 FM-7/FM-8、含 Appendix A category 白名单）。

**File Structure**:

```
skill 仓：/Users/liyijiang/.agents/skills/build123d-cad/
├── SKILL.md                                    修改：删三大流程段 + 加准入序列 + 改路由表
└── references/
    ├── INDEX.md                                 新建
    └── protocols/
        ├── README.md                            新建
        ├── reference-product-playbook.md        修改：契约 +1 条 + 8 Step Quote-back 示范 + FM-9
        ├── single-part-playbook.md              新建
        └── multi-part-playbook.md               新建

test 仓：/Users/liyijiang/work/build123d-cad-skill-test/
├── docs/superpowers/plans/2026-04-18-skill-coherence-refactor.md   本文件
└── tests/17-skill-optimization-dryrun/          新建：行为验证占位
    ├── README.md
    ├── run_G.md
    ├── run_H.md
    └── run_I.md
```

---

## Phase A：SKILL.md 准入 + 路由表（最小改）

### Task 1：SKILL.md 插入"AI 执行准入序列"块

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（在 L24 `## 角色规则` 之前插入新 section）

- [ ] **Step 1: Read 当前 SKILL.md L20-L25**

Run: 读文件定位 `## 角色规则` 标题（当前 L24）上方 `---` 分隔行位置

- [ ] **Step 2: 在 `## 角色规则` 之前插入新 section**

用 Edit 工具：`old_string` 为 `---\n\n## 角色规则`（即分隔线 + 角色规则标题），`new_string` 为：

```markdown
---

## AI 执行准入序列（每次会话第一件事）

1. 读本 SKILL.md 的"流程路由"表
2. 匹配场景 → Read 对应 Playbook
3. Playbook 顶部契约生效后再开始答题
4. Playbook 引用的子文档按需 Read
5. 禁止跳过 Playbook 直接从 references/<子领域>/ 自拼流程

---

## 角色规则
```

- [ ] **Step 3: 验证插入成功**

Run:
```bash
grep -n "^## AI 执行准入序列" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: 输出 1 行，行号在 `## 角色规则` 之前

- [ ] **Step 4: Commit (skill 仓)**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "feat: SKILL.md 顶部加 AI 执行准入序列 5 条"
```

---

### Task 2：SKILL.md 流程路由表重写

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（当前 L47-L51 的流程路由表）

- [ ] **Step 1: Edit 流程路由表**

用 Edit 工具替换现有路由表。`old_string`（注意包含表头 + 3 行数据）：

```markdown
| 需求类型 | 判断标准 | 使用流程 |
|---------|---------|---------|
| **参考物建模** | 需求中包含已存在的具体产品型号（手机/芯片板/舵机/传感器…） | 👇 参考物建模流程（Step R1~R5，先收集资料再建模） |
| **单部件** | 只有一个独立实体，无装配关系 | 👇 Step 1~4（含3变体对比） |
| **多部件** | 2个以上部件 / 有关节装配 / 有仿真需求 | 👇 多部件 4 阶段流程（Phase 1~4，每部件含3变体） |
```

`new_string`：

```markdown
| 需求类型 | 判断 | 必读路径（Read 后才能开始回答） |
|---|---|---|
| 参考物建模 | 需求含已存在的具体产品型号（手机/芯片板/舵机/传感器…） | `references/protocols/reference-product-playbook.md` |
| 单部件 | 1 个独立实体，无装配关系 | `references/protocols/single-part-playbook.md` |
| 多部件 | ≥2 个部件 / 有关节装配 / 有仿真需求 | `references/protocols/multi-part-playbook.md` |
```

- [ ] **Step 2: 验证无 emoji 暗示残留**

Run:
```bash
grep -c "👇" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
```
Expected: `0`

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "feat: SKILL.md 流程路由表去 emoji 暗示 + 改列名为必读路径"
```

---

## Phase B：基础设施（INDEX + protocols README）

### Task 3：创建 references/INDEX.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/INDEX.md`

- [ ] **Step 1: Write 文件**

完整内容：

```markdown
# references/ 导航索引

## 场景路由（兜底表——SKILL.md 路由表覆盖不到时用）

| 用户想做什么 | 先 Read | 后续可能用到 |
|---|---|---|
| 做某型号配件 | protocols/reference-product-playbook.md | verify/, reference-product/ |
| 单个零件 | protocols/single-part-playbook.md | parts/ |
| 多部件 / 装配 | protocols/multi-part-playbook.md | assembly/, simulation/ |
| 曲面建模 | parts/surface-modeling.md | parts/cheatsheet.md |
| 工艺约束 | process/{3d-printing,cnc,laser}.md | — |
| 仿真 / IK | simulation/ | peter-corke/simulation-philosophy.md |

## 目录职责（一行一目录）

- protocols/          三大流程 Playbook（AI 执行期 SSOT）
- verify/             Layer 0/1/2 + 反馈闭环
- reference-product/  参考物建模子方法论（反推 / 标注 / 摄影）
- parts/              API cheatsheet + 曲面建模
- process/            3D 打印 / CNC / 激光工艺
- assembly/           装配模式 + 爆炸动画
- simulation/         FK / IK / 步态 / URDF
- peter-corke/        仿真哲学

## 准入原则

- 进 Playbook 是唯一合法流程入口
- 禁止从 references/<子领域>/ 自拼流程（会跳步）
- Playbook 内部引用的子文档按需 Read
```

- [ ] **Step 2: 验证**

```bash
wc -l /Users/liyijiang/.agents/skills/build123d-cad/references/INDEX.md
# Expected: ~30 行
grep -c "^##" /Users/liyijiang/.agents/skills/build123d-cad/references/INDEX.md
# Expected: 3（三节：场景路由 / 目录职责 / 准入原则）
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/INDEX.md
git commit -m "feat: references/INDEX.md 跨目录场景路由 + 目录职责"
```

---

### Task 4：创建 references/protocols/README.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/README.md`

- [ ] **Step 1: Write 文件**

完整内容：

```markdown
# protocols/ 三大流程 Playbook 索引

本目录是 AI 执行期单一真实来源（SSOT）。SKILL.md 路由段只指向此目录，
所有流程细节（Step / Phase 定义、产出物契约、命令模板、失败模式）都在这里。

## 三个 Playbook

| 文件 | 适用场景 | Step/Phase 命名 |
|---|---|---|
| reference-product-playbook.md | 参考物建模（需求含产品型号） | R1 / R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5 |
| single-part-playbook.md | 单部件（1 个独立实体） | S1 / S2 / S3 / S4 |
| multi-part-playbook.md | 多部件（≥2 个 / 仿真 / 装配） | P1 / P2 / P3 / P4 |

## 骨架模板（所有 Playbook 共用）

```
顶部：进入条件 + 执行契约 1~7 条
中部：Step / Phase 总表（本步产出 / 允许跳过 / 下一步）
下部：每个 Step / Phase 详细模块
  - 前置 + 本步产出 + 命令模板 + AI 回报契约（含 Quote-back 示范）
底部：常见失败模式（FM-xx，初版可为空）
```

## Quote-back 强制规则（所有 Playbook 适用）

每个 Step 产出报告**第一行**必须是：

    引自 <playbook-basename> §Step <Rn/Sn/Pn> / <小标题>：
      "<原文一行>"

锚点用标题 + 小标题（不用裸行号）。原文须与 Playbook 实际内容一致。
违规：缺 Quote-back / 引错 Step / 原文捏造 → 回补 Read + 重出产出报告。
```

- [ ] **Step 2: 验证**

```bash
test -f /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/README.md && echo OK
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/README.md
git commit -m "feat: protocols/README.md 三 Playbook 索引 + 骨架模板 + Quote-back 规则"
```

---

## Phase C：参考物 Playbook Quote-back 集成

### Task 5：reference-product-playbook.md 顶部契约加第 7 条

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`

**前置核对**：experience-cache 已实施 → 契约段应已有 6 条（第 6 条讲 experience/ 检索 + draft）。本次加第 7 条。

- [ ] **Step 1: Read 契约段**

Run:
```bash
grep -n "^> " /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md | head -15
```
确认当前契约有 6 条（或 5 条——如果 experience-cache 未实施，本计划前置依赖未满足）。

- [ ] **Step 2: Edit 在最后一条契约后追加第 7 条**

用 Edit 工具。`old_string` 为契约段最后一条（实施时定位最末条原文），`new_string` = 最末条原文 + 换行 + 第 7 条：

```markdown
> 7. 每个 Step 产出报告第一行必须是 Quote-back。
>    格式：引自 reference-product-playbook.md §Step R<n> / <小标题>："<原文一行>"
>    缺 Quote-back、引错 Step、原文与文件不符 = 违规，必须回补 Read + 重出报告。
```

- [ ] **Step 3: 验证契约条数**

```bash
grep -c "^> [0-9]\." /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
# Expected: 7
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "feat: 参考物 Playbook 契约加第 7 条 Quote-back 强制"
```

---

### Task 6：reference-product-playbook.md 8 个 Step 回报示例加 Quote-back 示范

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`

**说明**：Playbook 8 个 Step（R1 / R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5）每个都有 "AI 回报契约" 示例块。逐个在示例块首行加 Quote-back 示范。

- [ ] **Step 1: 定位所有 "AI 回报契约" 示例块**

```bash
grep -n "AI 回报契约" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
# Expected: 8 行（每个 Step 一个）
```

- [ ] **Step 2: R1 示例块加 Quote-back 示范**

当前 R1 示例：
```
Step R1 产出报告
- [x] references/<slug>/search_plan.md  (4 来源，待用户确认)
下一步：等用户确认 → Step R2
```

Edit：在 `Step R1 产出报告` 下方插入 Quote-back 示范行：

```
Step R1 产出报告
引自 reference-product-playbook.md §Step R1 / 本步产出：
  "references/<slug>/search_plan.md（列出 3~4 个待查来源 + 预期获取的资料类型）"
- [x] references/<slug>/search_plan.md  (4 来源，待用户确认)
下一步：等用户确认 → Step R2
```

- [ ] **Step 3: R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5 示例块同样处理**

每个 Step 示范格式：

```
Step R<n> 产出报告
引自 reference-product-playbook.md §Step R<n> / <小标题>：
  "<原文一行，从 Playbook 对应 Step 的 '本步产出' 节摘一句>"
- [x] <原示例 artifact 条目>
...
```

小标题一般取 `本步产出`。对于 R5（完成汇总块场景），小标题取 `本步产出`（原文是 "在回复末尾输出'完成汇总'块"）。

- [ ] **Step 4: 验证 8 个 Step 都加了**

```bash
grep -c "^引自 reference-product-playbook.md §Step " /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
# Expected: 8
```

- [ ] **Step 5: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "feat: 参考物 Playbook 8 Step 回报示例加 Quote-back 示范行"
```

---

### Task 7：reference-product-playbook.md 失败模式加 FM-9

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`

**说明**：experience-cache 已添加 FM-7（静默加载经验）+ FM-8（经验污染 R2.7）。本次追加 FM-9。

- [ ] **Step 1: 定位当前最末一条 FM**

```bash
grep -n "^### FM-" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
# Expected: 输出 FM-1 至 FM-8 共 8 行
```

- [ ] **Step 2: Edit 在文件末尾（FM-8 之后）追加 FM-9**

`new_string` 片段（注意保持与 FM-8 一致的段落格式）：

```markdown

### FM-9：Quote-back 伪造
**现象**：AI 写了 Quote-back 但原文在 Playbook 里 grep 不到
**根因**：AI 没真 Read，凭记忆拼了一句"像 Playbook 的话"
**诊断**：
```bash
grep -F "<被引用的原文>" references/protocols/reference-product-playbook.md
```
**修复**：要求 AI 重新 Read 对应 Step 原文，重出产出报告；多次违规视为必须降级重跑本 Step
```

- [ ] **Step 3: 验证 FM-9 存在**

```bash
grep -c "^### FM-9" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md
# Expected: 1
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "feat: 参考物 Playbook 失败模式加 FM-9 Quote-back 伪造"
```

---

### Task 8：SKILL.md 删除参考物建模详细段 → 4 行路由子段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（L55-L79 的参考物建模流程段）

- [ ] **Step 1: 定位段落边界**

```bash
grep -n "^## " /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md | head -5
# 确认 "## 参考物建模流程" 起点 + "## 多部件 4 阶段流程" 终点
```

- [ ] **Step 2: Edit 替换整段**

`old_string` 为当前 L55-L79 整段（`## 参考物建模流程（Reference-Product Protocol）` 到下一个 `## ` 之前的所有内容，包含 R1~R5 产出物总表 + 分叉规则）。

`new_string`：

```markdown
## 参考物建模流程

**触发**：需求含已存在产品型号（红米 K80、树莓派 4B、SG90 舵机…）。

**唯一执行路径**：立即 Read `references/protocols/reference-product-playbook.md`，按 Playbook 的 R1~R5 执行。

**SKILL.md 本文件不含 R1~R5 细节**——凭记忆走视为违规，必须回补 Read + Quote-back。

**Quote-back 强制**：每个 Step 产出报告第一行引用 Playbook 原文（格式见 Playbook §执行契约）。

---

```

- [ ] **Step 3: 验证段落瘦身**

```bash
awk '/^## 参考物建模流程/,/^## /' /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md | wc -l
# Expected: ≤ 14（4 行核心 + 空行 + 分隔线 + 下一段标题）
grep -c "R1~R5 产出物总表" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# Expected: 0（总表已删除）
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "refactor: SKILL.md 参考物建模段去内容化（25行 → 4行路由子段）"
```

---

## Phase D：单部件 Playbook 化

### Task 9：创建 references/protocols/single-part-playbook.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md`

**内容来源**：当前 SKILL.md L273-L365 `## 单部件简化流程（Single-Part Protocol）` 整段。

- [ ] **Step 1: Read 源段落**

```bash
awk 'NR>=273 && NR<=365' /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md > /tmp/single-part-src.md
wc -l /tmp/single-part-src.md
# Expected: ~93 行
```

记下原段落的 Step 结构（应有 Step 1 需求分析 / Step 1.5 几何对齐 / Step 2 建模策略 / Step 3 建模实现 / Step 4 导出 + 工艺提示，具体以源为准）。

- [ ] **Step 2: Write 新文件（骨架 + 搬运内容）**

文件完整骨架（实施时把原 Step 1~4 的正文填入对应 `## Step Sn` 段）：

```markdown
# 单部件流程 Playbook（Single-Part Protocol）

> **何时进入此 Playbook**：用户需求是 1 个独立实体，无装配关系。
> 入口由 `SKILL.md` 的"流程路由"表触发。

---

## 执行契约（进入此 Playbook 后对本次对话强制生效）

> 1. 每个 Step 完成后，必须在当次回复里输出"产出报告"块
> 2. 产出报告里每一条必须是 `[x]`（已产出）或 `[skip] reason=...`（显式跳过）
> 3. 没写产出报告的 Step 视为未完成，禁止进入下一步
> 4. 跳步必须声明理由，静默跳过视为违规
> 5. Artifact 是硬约束——用户接管某步也不例外
> 6. 遇本步 artifact 缺失：回到本步补产，禁止写 `[x]` 骗过
> 7. 每个 Step 产出报告第一行必须是 Quote-back：
>    格式：引自 single-part-playbook.md §Step S<n> / <小标题>："<原文一行>"
>    缺 Quote-back、引错 Step、原文捏造 = 违规，必须回补

---

## S1~S4 Step 总表

| Step | 必须产出 | 允许跳过？ | 下一步分叉 |
|---|---|---|---|
| S1 需求分析 | 需求分析表 + 参考问询 | 否 | → S2 |
| S2 几何对齐（默认含 3 视图草图） | concept_sketch.png（自动打开）或用户 skip 声明 | 用户明说"跳过草图" | → S3 |
| S3 建模实现 | `<part>.py` + OCP 自动预览 + 3 变体对比（若用户启用变体） | 否 | → S4 |
| S4 导出 + 工艺提示 | `<part>.step`/`.stl` + 工艺约束清单 | 否 | （终态） |

---

## Step S1 — 需求分析

**前置**：
- [x] 用户需求进入，SKILL.md 路由判定为单部件

**本步产出**：
- 需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）
- 参考资料问询（"是否有参考图、参考链接或参考描述？"）

**命令模板**：（从 SKILL.md L273-L297 搬入此处）

**AI 回报契约**：
```
Step S1 产出报告
引自 single-part-playbook.md §Step S1 / 本步产出：
  "需求分析表（4 要素：几何 / 关键尺寸 / 操作序列 / 导出格式 / 用途）"
- [x] 需求分析表已输出（见上方）
- [x] 已询问参考资料
下一步：Step S2（等用户回复参考资料）
```

---

## Step S2 — 几何对齐（默认含 3 视图草图，方案 A 默认触发）

**前置**：
- [x] S1 需求分析完成且用户已回复参考资料

**本步产出**：
- `concept_sketch.png`（自动保存并打开），或 `[skip] reason=用户说"跳过草图"`

**命令模板**：（从 SKILL.md L299-L365 的方案 A matplotlib 脚本搬入此处；方案 B/C/D/E 简要说明保留）

**AI 回报契约**：
```
Step S2 产出报告
引自 single-part-playbook.md §Step S2 / 本步产出：
  "concept_sketch.png（自动保存并打开）"
- [x] concept_sketch.png  (已自动打开查看)
下一步：Step S3
```

**跳过声明**：若用户说"跳过草图"/"直接建模"：
```
Step S2 产出报告
引自 single-part-playbook.md §Step S2 / 本步产出：
  "concept_sketch.png（自动保存并打开）"
- [skip] concept_sketch.png  (reason: 用户说"跳过草图")
下一步：Step S3
```

---

## Step S3 — 建模实现

**前置**：
- [x] S2 几何对齐完成（草图或 skip 声明）

**本步产出**：
- `<part>.py`（含 OCP 自动预览块）
- OCP Viewer 实际打开
- 3 变体对比（若用户启用变体讨论）

**命令模板**：（从 SKILL.md 单部件建模核心段搬入；若源文件没有独立 Step 3 段，以现有内容为准整理）

**AI 回报契约**：
```
Step S3 产出报告
引自 single-part-playbook.md §Step S3 / 本步产出：
  "<part>.py（含 OCP 自动预览块）"
- [x] <part>.py
- [x] OCP Viewer 预览已打开
下一步：Step S4
```

---

## Step S4 — 导出 + 工艺提示

**前置**：
- [x] S3 建模完成且 OCP 预览通过

**本步产出**：
- `<part>.step` 或 `<part>.stl`（按用途选格式）
- 工艺约束清单（3D 打印 / CNC / 激光，按用户场景挑一个）

**命令模板**：（从 SKILL.md 末尾导出 + 工艺段整理）

**AI 回报契约**：
```
Step S4 产出报告
引自 single-part-playbook.md §Step S4 / 本步产出：
  "<part>.step 或 <part>.stl + 工艺约束清单"
- [x] <part>.step
- [x] 工艺约束清单（3D 打印：壁厚 1.2mm 最小 / 悬臂 ≤45°）
单部件流程 S1~S4 完成。
```

---

## 常见失败模式

（初版留空，等 test 沉淀。跨 Playbook 通用的 Quote-back 违规见 protocols/README.md。）
```

**搬运原则**：原 SKILL.md L273-L365 的具体命令模板 / matplotlib 脚本 / 方案说明全部搬入对应 `## Step Sn` 下的 `**命令模板**:` 小节；Step S1 ← L273-L297，Step S2 ← L299-L365。

- [ ] **Step 3: 验证文件结构**

```bash
grep -c "^## Step S" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md
# Expected: 4
grep -c "^引自 single-part-playbook.md §Step S" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md
# Expected: ≥4（每 Step 至少 1 个示范）
grep -c "^> [0-9]\." /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/single-part-playbook.md
# Expected: 7（契约 7 条）
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/single-part-playbook.md
git commit -m "feat: single-part-playbook.md 单部件 S1~S4 + 契约 7 条 + Quote-back 示范"
```

---

### Task 10：SKILL.md 删除单部件详细段 → 4 行路由子段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（原 L273-L365 范围，已搬到 single-part-playbook.md）

- [ ] **Step 1: 定位当前边界**

```bash
grep -n "^## 单部件简化流程" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
grep -n "^## 概念草图说明" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# 段落 = 前者起点到后者起点-1（即到 "## 概念草图说明" 前的所有行）
```

- [ ] **Step 2: Edit 替换整段**

`old_string` 为 `## 单部件简化流程（Single-Part Protocol）` 到 `## 概念草图说明` 之前的所有行。

`new_string`：

```markdown
## 单部件流程

**触发**：需求是 1 个独立实体，无装配关系。

**唯一执行路径**：立即 Read `references/protocols/single-part-playbook.md`，按 Playbook 的 S1~S4 执行。

**SKILL.md 本文件不含 S1~S4 细节**——凭记忆走视为违规，必须回补 Read + Quote-back。

**Quote-back 强制**：每个 Step 产出报告第一行引用 Playbook 原文（格式见 Playbook §执行契约）。

---

```

- [ ] **Step 3: 验证瘦身**

```bash
awk '/^## 单部件流程/,/^## 概念草图说明/' /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md | wc -l
# Expected: ≤ 14
grep -c "^## 单部件简化流程" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# Expected: 0（旧标题已删）
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "refactor: SKILL.md 单部件段去内容化（93行 → 4行路由子段）"
```

---

## Phase E：多部件 Playbook 化

### Task 11：创建 references/protocols/multi-part-playbook.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md`

**内容来源**：当前 SKILL.md L80-L272 `## 多部件 4 阶段流程（Multi-Part Protocol）` 整段。

- [ ] **Step 1: Read 源段落**

```bash
awk 'NR>=80 && NR<=272' /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md > /tmp/multi-part-src.md
wc -l /tmp/multi-part-src.md
# Expected: ~193 行
```

核对源段落的 Phase 结构（应有 Phase 1 需求拆解 + 专家咨询 / Phase 2 部件级建模 / Phase 3 装配与关节 / Phase 4 导出 + 验证，具体以源为准）。

- [ ] **Step 2: Write 新文件**

文件骨架（实施时把原 Phase 1~4 的正文填入对应 `## Phase Pn` 段）：

```markdown
# 多部件流程 Playbook（Multi-Part Protocol）

> **何时进入此 Playbook**：用户需求含 ≥2 个部件 / 关节装配 / 仿真需求。
> 入口由 `SKILL.md` 的"流程路由"表触发。

---

## 执行契约（进入此 Playbook 后对本次对话强制生效）

> 1. 每个 Phase 完成后，必须在当次回复里输出"产出报告"块
> 2. 产出报告里每一条必须是 `[x]` 或 `[skip] reason=...`
> 3. 没写产出报告的 Phase 视为未完成，禁止进入下一 Phase
> 4. 每 Phase 末尾有确认门 ✋，用户确认后才进入下一 Phase
> 5. Artifact 是硬约束——用户接管某步也不例外
> 6. 遇本步 artifact 缺失：回到本步补产
> 7. 每个 Phase 产出报告第一行必须是 Quote-back：
>    格式：引自 multi-part-playbook.md §Phase P<n> / <小标题>："<原文一行>"
>    缺 Quote-back、引错 Phase、原文捏造 = 违规，必须回补

---

## P1~P4 Phase 总表

| Phase | 必须产出 | 允许跳过？ | 下一步分叉 |
|---|---|---|---|
| P1 需求拆解 + 专家咨询 | 需求拆解报告 + 确认门 ✋ | 否 | → P2 |
| P2 部件级建模（每部件 3 变体） | 每部件 3 `<part>_v{1,2,3}.py` + OCP 对比 + 用户选定 | 否 | → P3 |
| P3 装配 / 关节 | `<asm>.py` + Joint 方案 + OCP 装配预览 | 否 | → P4 |
| P4 导出 + Layer 验证 | `<asm>.step` + Layer 1 validation（可选 Layer 2） | 否 | （终态） |

---

## Phase P1 — 需求拆解 + 专家咨询

**前置**：
- [x] 用户需求进入，SKILL.md 路由判定为多部件

**本步产出**：
- 需求拆解报告（部件清单 + 关节关系 + 仿真需求 + 导出目标）
- 用户确认门 ✋

**命令模板**：（从 SKILL.md L89-L148 "需求拆解报告" 模板搬入此处）

**AI 回报契约**：
```
Step P1 产出报告
引自 multi-part-playbook.md §Phase P1 / 本步产出：
  "需求拆解报告（部件清单 + 关节关系 + 仿真需求 + 导出目标）"
- [x] 需求拆解报告已输出
- [ask] 用户确认继续进 P2？
```

---

## Phase P2 — 部件级建模（每部件 3 变体）

**前置**：
- [x] P1 需求拆解已用户确认

**本步产出**：
- 对每个部件：3 个 `<part>_v{1,2,3}.py` 变体 + OCP 对比截图 + 用户选定版本
- 每部件内部也走"变体对比 → 选定"循环，带确认门

**命令模板**：（从 SKILL.md L149-L230 "部件 Pn 变体对比" 模板搬入）

**AI 回报契约**：
```
Step P2 产出报告
引自 multi-part-playbook.md §Phase P2 / 本步产出：
  "每部件 3 变体 + OCP 对比 + 用户选定版本"
- [x] part_A_v1.py / part_A_v2.py / part_A_v3.py  (用户选 v2)
- [x] part_B_v1.py / part_B_v2.py / part_B_v3.py  (用户选 v1)
- [ask] 继续进 P3？
```

---

## Phase P3 — 装配 / 关节

**前置**：
- [x] P2 所有部件已选定版本

**本步产出**：
- `<asm>.py`（装配脚本）
- Joint 方案（如需关节：RevoluteJoint / FixedJoint / RigidJoint 等）
- OCP 装配预览已打开

**命令模板**：（从 SKILL.md 装配段搬入；若需要引用 `references/assembly/` 子文档，保留引用不搬内容）

**AI 回报契约**：
```
Step P3 产出报告
引自 multi-part-playbook.md §Phase P3 / 本步产出：
  "<asm>.py + Joint 方案 + OCP 装配预览"
- [x] <asm>.py
- [x] Joint: 2x RevoluteJoint（肩 + 肘）
- [x] OCP 装配预览已打开
下一步：Phase P4
```

---

## Phase P4 — 导出 + Layer 验证

**前置**：
- [x] P3 装配完成且 OCP 预览通过

**本步产出**：
- `<asm>.step`（装配导出）
- Layer 1 validation pass（合同运行时验证，如有合同）
- 可选：Layer 2 视觉验证（参考物型装配才有此层）

**命令模板**：（从 SKILL.md 末尾导出 + 验证引导段整理；引用 `references/verify/` 子文档）

**AI 回报契约**：
```
Step P4 产出报告
引自 multi-part-playbook.md §Phase P4 / 本步产出：
  "<asm>.step + Layer 1 validation"
- [x] <asm>.step
- [x] Layer 1: pass
- [skip] Layer 2  (reason: 非参考物型装配)
多部件流程 P1~P4 完成。
```

---

## 常见失败模式

（初版留空，等 test 沉淀。跨 Playbook 通用的 Quote-back 违规见 protocols/README.md。）
```

**搬运原则**：原 SKILL.md L80-L272 的具体命令模板 / 变体对比模板 / 装配段落全部搬入对应 `## Phase Pn` 下的 `**命令模板**:` 小节。

- [ ] **Step 3: 验证文件结构**

```bash
grep -c "^## Phase P" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md
# Expected: 4
grep -c "^引自 multi-part-playbook.md §Phase P" /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md
# Expected: ≥4
grep -c "^> [0-9]\." /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md
# Expected: 7
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/multi-part-playbook.md
git commit -m "feat: multi-part-playbook.md 多部件 P1~P4 + 契约 7 条 + Quote-back 示范"
```

---

### Task 12：SKILL.md 删除多部件详细段 → 4 行路由子段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`（原 L80-L272 范围，已搬到 multi-part-playbook.md）

- [ ] **Step 1: 定位当前边界**

```bash
grep -n "^## 多部件 4 阶段流程" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
grep -n "^## 单部件流程" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# 段落 = 前者起点到后者起点-1（单部件段已在 Task 10 变成路由子段）
```

- [ ] **Step 2: Edit 替换整段**

`old_string` 为 `## 多部件 4 阶段流程（Multi-Part Protocol）` 到 `## 单部件流程` 之前的所有内容（包含 L89 需求拆解报告 + L149 部件变体对比模板）。

`new_string`：

```markdown
## 多部件流程

**触发**：需求含 ≥2 个部件 / 关节装配 / 仿真需求。

**唯一执行路径**：立即 Read `references/protocols/multi-part-playbook.md`，按 Playbook 的 P1~P4 执行。

**SKILL.md 本文件不含 P1~P4 细节**——凭记忆走视为违规，必须回补 Read + Quote-back。

**Quote-back 强制**：每个 Phase 产出报告第一行引用 Playbook 原文（格式见 Playbook §执行契约）。

---

```

- [ ] **Step 3: 验证瘦身**

```bash
awk '/^## 多部件流程/,/^## 单部件流程/' /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md | wc -l
# Expected: ≤ 14
grep -c "^## 多部件 4 阶段流程" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# Expected: 0（旧标题已删）
grep -c "^## 需求拆解报告\|^## 部件 Pn" /Users/liyijiang/.agents/skills/build123d-cad/SKILL.md
# Expected: 0（两个内嵌模板标题也被删）
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "refactor: SKILL.md 多部件段去内容化（193行 → 4行路由子段）"
```

---

## Phase F：最终核对 + 行为验证骨架

### Task 13：创建 tests/17-skill-optimization-dryrun/ 行为验证目录

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/17-skill-optimization-dryrun/README.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/17-skill-optimization-dryrun/run_G.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/17-skill-optimization-dryrun/run_H.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/17-skill-optimization-dryrun/run_I.md`

- [ ] **Step 1: 创建目录 + README.md**

先 `mkdir -p tests/17-skill-optimization-dryrun/` 然后 Write README.md：

```markdown
# tests/17-skill-optimization-dryrun

验证 skill-coherence-refactor 改动后 AI 是否真 Read Playbook + Quote-back + 不跳步。

## 3 个 Scenario

| 文件 | 场景 | 触发词 | 期望 |
|---|---|---|---|
| run_G.md | 参考物建模 | "做某型号手机壳"（例："做红米 K80 Pro 手机壳"） | AI Read reference-product-playbook → 每 Step Quote-back → R1~R5 走完 |
| run_H.md | 单部件 | "做一个齿轮"（或其它无型号的单实体需求） | AI Read single-part-playbook → S1~S4 每 Step Quote-back |
| run_I.md | 多部件 | "做一个带 2 个舵机的机械臂" | AI Read multi-part-playbook → P1~P4 每 Phase Quote-back + 确认门 |

## 执行方式

每个 Scenario 在**新 Claude Code 会话**里跑（清空缓存模拟真实冷启动），完整 AI 回复贴进对应 run_X.md。

## 失败判据

- 未 Read Playbook（grep tool_use 日志验证）
- 缺 Quote-back 行
- Quote-back 原文 grep 在 Playbook 里找不到（伪造）
- 跳 Step（R2.7 被默认 skip 而没 reason 等）

## 回归验证

- test 13（红米 K80 Pro）重跑：R1~R5 完成无回退
- test 14（小米 K70）重跑：R2.7 仍必做、face_mapping.yaml 仍生成

run_G/H/I 由操作者在本 plan 实施后的独立会话中填充，不属于 AI 自动化可完成任务。
```

- [ ] **Step 2: 创建 3 个占位文件**

Write `run_G.md`：
```markdown
# Scenario G — 参考物建模冷启动

**输入**：（在新会话里贴："做红米 K80 Pro 手机壳" 或等价需求）

**AI 完整回复**：

<待填——操作者从真实对话粘贴>

## 审阅

- [ ] Read 过 reference-product-playbook.md？（检查 tool_use 日志）
- [ ] R1 产出报告首行含 "引自 reference-product-playbook.md §Step R1"？
- [ ] R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5 Quote-back 齐全？
- [ ] 所有 Quote-back 原文能在 Playbook 里 grep 到？
- [ ] 无静默跳步？
```

Write `run_H.md`：
```markdown
# Scenario H — 单部件冷启动

**输入**：（在新会话里贴："做一个齿轮" 或等价需求）

**AI 完整回复**：

<待填>

## 审阅

- [ ] Read 过 single-part-playbook.md？
- [ ] S1~S4 每 Step 产出报告首行含 "引自 single-part-playbook.md §Step S<n>"？
- [ ] Quote-back 原文 grep 能找到？
- [ ] S2 几何对齐默认触发（除非用户说跳过草图）？
- [ ] 无静默跳步？
```

Write `run_I.md`：
```markdown
# Scenario I — 多部件冷启动

**输入**：（在新会话里贴："做一个带 2 个舵机的机械臂" 或等价需求）

**AI 完整回复**：

<待填>

## 审阅

- [ ] Read 过 multi-part-playbook.md？
- [ ] P1~P4 每 Phase 产出报告首行含 "引自 multi-part-playbook.md §Phase P<n>"？
- [ ] Quote-back 原文 grep 能找到？
- [ ] 每 Phase 末尾有确认门 ✋？
- [ ] 无静默跳步？
```

- [ ] **Step 3: Commit (test 仓)**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/17-skill-optimization-dryrun/
git commit -m "test: 新增 tests/17-skill-optimization-dryrun 行为验证骨架"
```

---

### Task 14：运行 7 项结构核对 + 写 structure_check.md

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/17-skill-optimization-dryrun/structure_check.md`

- [ ] **Step 1: 运行 7 项结构核对**

```bash
SKILL_DIR=/Users/liyijiang/.agents/skills/build123d-cad

echo "=== 1. SKILL.md 行数 ≤ 1200 ==="
wc -l $SKILL_DIR/SKILL.md

echo "=== 2. SKILL.md 无 Step/Phase 残留 ==="
grep -c "^### Step \|^### Phase " $SKILL_DIR/SKILL.md

echo "=== 3. SKILL.md 头部含 AI 执行准入序列 ==="
grep -c "^## AI 执行准入序列" $SKILL_DIR/SKILL.md

echo "=== 4. protocols/ 含 README + 3 Playbook ==="
ls $SKILL_DIR/references/protocols/

echo "=== 5. references/INDEX.md 存在 ==="
test -f $SKILL_DIR/references/INDEX.md && echo OK

echo "=== 6. 三 Playbook 顶部契约各 7 条 ==="
for f in reference-product single-part multi-part; do
  cnt=$(grep -c "^> [0-9]\." $SKILL_DIR/references/protocols/$f-playbook.md)
  echo "$f-playbook.md: $cnt"
done

echo "=== 7. 参考物 Playbook 失败模式含 FM-9 ==="
grep -c "^### FM-9" $SKILL_DIR/references/protocols/reference-product-playbook.md

echo "=== 额外：三 Playbook Quote-back 示范行计数 ==="
for f in reference-product single-part multi-part; do
  pattern="^引自 $f-playbook.md §"
  cnt=$(grep -c "$pattern" $SKILL_DIR/references/protocols/$f-playbook.md)
  echo "$f: $cnt (expected: reference-product ≥8, single-part ≥4, multi-part ≥4)"
done
```

期望：
- (1) ≤ 1200
- (2) = 0
- (3) = 1
- (4) 4 个文件
- (5) "OK"
- (6) 3 个 "7"
- (7) = 1
- 额外：reference-product ≥8 / single-part ≥4 / multi-part ≥4

- [ ] **Step 2: 把输出写进 structure_check.md**

Write：
```markdown
# 结构核对报告

日期：<填实施日期>

| 核对项 | 期望 | 实际 | 状态 |
|---|---|---|---|
| 1. SKILL.md 行数 | ≤ 1200 | <fill> | ✅/❌ |
| 2. SKILL.md 无 Step/Phase 残留 | 0 | <fill> | ✅/❌ |
| 3. SKILL.md 头部含 AI 执行准入序列 | 1 | <fill> | ✅/❌ |
| 4. protocols/ 含 README + 3 Playbook | 4 文件 | <fill> | ✅/❌ |
| 5. references/INDEX.md 存在 | OK | <fill> | ✅/❌ |
| 6. 三 Playbook 契约各 7 条 | 7/7/7 | <fill> | ✅/❌ |
| 7. 参考物 Playbook 含 FM-9 | 1 | <fill> | ✅/❌ |
| 额外：reference-product Quote-back 行 | ≥ 8 | <fill> | ✅/❌ |
| 额外：single-part Quote-back 行 | ≥ 4 | <fill> | ✅/❌ |
| 额外：multi-part Quote-back 行 | ≥ 4 | <fill> | ✅/❌ |

## 全通过判定

所有项 ✅ → 结构核对通过，可交付行为验证（由操作者在新会话中跑 Scenario G/H/I）。
任一 ❌ → 回到对应 Task 补产，重跑结构核对。
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/17-skill-optimization-dryrun/structure_check.md
git commit -m "test: 结构核对报告 7+3 项"
```

---

## 收尾提醒

**本 plan 不含的后续动作**（需操作者在新会话中手动跑）：
- Scenario G/H/I 三个行为验证（真对话 → 粘进 run_G/H/I.md）
- test 13 / test 14 回归验证
- 如行为验证失败，回到 Playbook 修订（Quote-back 示范写得更抢眼 / 契约条款语气加强等）

**依赖关系**：
- 本计划 Phase C~E 的 Playbook 改动**依赖 experience-cache 计划先实施**（契约第 6 条由 experience-cache 落地）
- 如 experience-cache 未落地先跑本计划：Task 5 契约第 7 条会编号错乱（会变成第 6 条，后续 experience-cache 再加就冲突）——务必按顺序

## Self-Review

**Spec 覆盖核对**：spec §3（SKILL.md 改动）→ Task 1/2/8/10/12；§4（Quote-back）→ Task 5/6（Playbook 契约 + 示范）；§5（单/多部件 Playbook 化）→ Task 9/11；§6（INDEX）→ Task 3/4；§7（验证）→ Task 13/14；§8（风险）由 Task 14 结构核对 + 操作者行为验证覆盖。全部有对应 Task。

**Placeholder 扫描**：Task 9/11 的 "命令模板" 小节说"从 SKILL.md L<n>-L<m> 搬入此处"——这是可接受的因为源内容长、搬运是机械动作；engineer 实施时按行号直接搬源文件。无 TBD/TODO。

**类型一致性**：Step 前缀一致——参考物用 R、单部件 S、多部件 P。Quote-back 格式 `引自 <playbook-basename> §Step <Rn/Sn/Pn> / <小标题>` 三处一致。契约 7 条文案三 Playbook 一致（仅替换文件名）。
