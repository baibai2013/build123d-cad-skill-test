# build123d-cad 参考物建模协议（R1~R5）Playbook 化重构设计

**日期**：2026-04-18
**范围**：build123d-cad skill 的参考物建模协议（Step R1~R5）
**不改动**：Multi-Part Protocol / Single-Part Protocol / 验证方法 / 参考资源
**驱动问题**：v3 升级后 AI "跳步 / 漏步"——读了 SKILL.md 但执行时凭记忆走，R2.7 这类关键步骤最容易漏。
**核心机制**：Artifact Gates（强制产出物）——每步定死必须产出的文件路径，下一步命令依赖上一步产出。

---

## 1. 问题陈述

SKILL.md 当前 1619 行，R1~R5 混在主文件里讲了 ~225 行。根因假设：
1. 信息密度过高，AI 加载后执行时凭压缩记忆走，扫读就漏
2. R2.5 / R2.7 是 v3 新增，夹在既有 R1~R5 中间，没有显式"必做门"
3. 步骤叙述多，但没有"产出什么文件"的硬约束，跳步无惩罚

## 2. 架构

```
/Users/liyijiang/.agents/skills/build123d-cad/
├── SKILL.md                                   R1~R5 段从 225 行瘦到 ~30 行，只剩路由 + 产出物总表
└── references/
    └── protocols/                             新目录
        └── reference-product-playbook.md      新文件：R1~R5 Checklist 本体
```

**分工约定：**
- SKILL.md 只负责"这是不是参考物建模？是的话打开 Playbook"。
- Playbook 是 AI 执行期的单一真实来源。进入 Playbook 后 SKILL.md 的其它内容不再影响决策。
- 现有 `references/verify/` `references/reference-product/` 等 v3 子文档原地不动，Playbook 按需引用。

**删除**：SKILL.md L55~L280 的 R1~R5 详细叙述。
**新增**：`references/protocols/reference-product-playbook.md`。

## 3. Playbook 每个 Step 的统一模板

````markdown
## Step Rn — <名称>

**前置**：
- [x] R(n-1) 已产出 <file>

**本步产出（必须全部存在才允许进入下一步）**：
- `<path1>`
- `<path2>`

**命令模板**：
```bash
# 可复制样本，但产出文件路径是硬约束
```

**AI 回报契约（完成后必须在回复里输出这一段，逐条勾）**：
```
Step Rn 产出报告
- [x] <path1>     (备注)
- [skip] <path2>  (reason: ...)
下一步：Step R(n+1) 或 分叉去 Rx
```
````

**Playbook 顶部全局契约块**（第一屏放在 Playbook 开头）：

```markdown
> **执行契约**（进入此 Playbook 后对本次对话强制生效）：
> 1. 每个 Step 完成后必须在回复里输出"产出报告"块
> 2. 产出报告里每一条必须是 `[x]`（已产出）或 `[skip] reason=...`（显式跳过）
> 3. 没写产出报告的 Step 视为未完成，禁止进入下一步
> 4. 跳步必须说理由，不能静默 skip
```

## 4. R1~R5 产出物契约总表

| Step | 本步必须产出 | 前置 | 允许跳过？ | 下一步分叉 |
|---|---|---|---|---|
| **R1** 识别 + 搜索计划 | `refs/<slug>/search_plan.md` | （无） | 否 | → R2（等用户确认） |
| **R2** 执行搜集 | `refs/<slug>/raw_specs.md` + `refs/<slug>/images/*`（≥1 张） | R1 | 否 | 有 `model.step` → R3；无 → R2.5 |
| **R2.5** 无 STEP 反推 | `refs/<slug>/clean/<stem>_scale.json` + `measurements.csv`（≥1 条关键尺寸） | R2 且 model.step 缺失 | 仅 R2 产出 `model.step` 时可 skip | → R2.7 |
| **R2.7** 参考图现实对齐 | `refs/<slug>/clean/<stem>_cropped.png`（每张要进 Layer 2 的图）+ `<slug>/part_face_mapping.yaml` | R2（或 R2.5） | 否（Layer 2 必做）；仅 "有 STEP + 不做视觉对比" 时可 skip | → R3 |
| **R3** 生成 params.md | `refs/<slug>/params.md`（含置信度 ★1~★5 列） | R2.7（或有 STEP 走 R2→R3） | 否 | → R3.5 |
| **R3.5** 生成 contract.yaml | `tests/<test>/contract.yaml` | R3 | 否 | → R4 |
| **R4** 建模 | `tests/<test>/<part>.py` + OCP 自动预览触发 | R3.5 | 否 | → 单/多部件流程 + R5 |
| **R5** 收尾提示 | 在回复中输出"完成汇总"块（Layer 0/1/2 状态 + 置信度统计 + 后续建议） | R4 | 否 | （终态） |

**术语约定**：
- `<slug>` = 产品短名（如 `redmi-k80-pro`），与 test 13/14 现有 `references/<slug>/` 惯例一致
- `<test>` = 测试目录名（如 `14-xiaomi-k70-case`）

## 5. SKILL.md 瘦身路由段（替换 L55~L280）

````markdown
## 参考物建模流程（Reference-Product Protocol）

**触发条件**：需求中包含已存在的具体产品型号，例如：
「做红米 K80 的手机壳」「给树莓派 4B 做散热壳」「SG90 舵机安装座」

**执行方式**：进入 `references/protocols/reference-product-playbook.md` 按 checklist 走完 R1~R5。
Playbook 里的"执行契约"对本次对话强制生效——**每步必须在回复中输出产出报告，禁止静默跳步**。

**R1~R5 产出物总表**（详细契约见 Playbook）：

| Step | 必须产出 | 允许跳过？ |
|---|---|---|
| R1 识别 + 搜索计划 | `refs/<slug>/search_plan.md` | 否 |
| R2 执行搜集 | `refs/<slug>/raw_specs.md` + `images/*` | 否 |
| R2.5 无 STEP 反推 | `refs/<slug>/clean/*_scale.json` + `measurements.csv` | 仅 R2 已产出 `model.step` 时可 skip |
| R2.7 参考图现实对齐 | `refs/<slug>/clean/*_cropped.png` + `part_face_mapping.yaml` | 否（Layer 2 必做） |
| R3 params.md | `refs/<slug>/params.md`（带置信度） | 否 |
| R3.5 contract.yaml | `tests/<test>/contract.yaml` | 否 |
| R4 建模 | `tests/<test>/<part>.py` + 自动预览 | 否 |
| R5 收尾 | 回复中输出完成汇总块 | 否 |

**分叉规则**：R2 完成后，有 `model.step` → R3；无 `model.step` → R2.5 → R2.7 → R3。

---
````

**收益**：SKILL.md 从 1619 行 → 约 1410 行（R1~R5 段 225 → 30 行）。

## 6. Skip / 错误处理策略

**合法 skip**（唯一 1 种）：
- **R2.5 + R2.7** 当 R2 已产出高质量 `model.step` 时可同时 skip
  - 理由：STEP 提供精确尺寸 + 正交几何，不需从照片反推，也不需现实对齐
  - 声明格式：`[skip] R2.5 reason=已有 model.step` + `[skip] R2.7 reason=已有 model.step 无需参考图对比`
  - 例外：用户仍要求 Layer 2 视觉对比 → R2.7 变回必做

**非法 skip**：R1 / R2 / R3 / R3.5 / R4 / R5 任何情况都必做。

**产出缺失处理**：
- 本步 artifact 没生成 → 必须回到本步补产，不允许写 `[x]` 骗过
- 发现上游 artifact 缺失（如 R3 时发现 R2.7 漏了）→ 回复中明写"回补 Step Rx"并执行，禁止往下走

**人工干预例外**：
- 用户明确说"跳过 R3.5 我直接给你 contract" → AI 写 `[skip] R3.5 reason=用户直接提供`，并把用户给的内容落盘到 `tests/<test>/contract.yaml`
- 关键：skip 改变的是"谁来做"，不是"artifact 要不要存在"。artifact 始终是硬约束。

**失败模式清单**：Playbook 末尾加一节"常见失败模式"，搬运 test 13/14 已沉淀的真实坑（bbox 越界 / mm/px 反算 / face_mapping 写反），每条带诊断提示。不新造。

## 7. 验证方法

不是 unittest 而是跑真对话看 AI 行为。

**结构核对**（自动可查）：
- `grep -n "^### Step R" SKILL.md` 输出 0 条
- `wc -l SKILL.md` ≤ 1420 行
- `references/protocols/reference-product-playbook.md` 存在，含 8 个 Step 模块 + 顶部契约块 + 末尾失败模式清单

**行为验证 A — 复现 test 14 K70 壳**：
- 新对话输入"做小米 K70 手机壳"
- 预期 AI 进入 Playbook，逐步输出产出报告 8 次（R1/R2/R2.5/R2.7/R3/R3.5/R4/R5）
- 关键：**R2.7 不能漏**
- 失败判据：任一 Step 没产出报告 → 回改 Playbook 契约强度

**行为验证 B — 走 STEP 捷径**：
- 新对话输入"做红米 K80 Pro 手机壳"（假设 GrabCAD 有 STEP）
- 预期 R2 拿到 `model.step` 后，R2.5 + R2.7 正确 skip（带 reason）
- 失败判据：硬跑 R2.5 或静默 skip → 回改 Section 6 声明格式

**行为验证 C — Layer 2 必做陷阱**：
- 用户给了 STEP 又要求"跟官方照片对比"
- 预期：R2.5 skip，R2.7 必做（部分产出：仅 `part_face_mapping.yaml` + 预处理官图）
- 失败判据：AI 把"有 STEP"等同于"跳 R2.7" → Playbook 加提醒

**验证位置**：
- `tests/15-playbook-dryrun/` 新测试目录
- 每个对话完整 AI 回复保存为 `run_A.md` / `run_B.md` / `run_C.md` 供人工审阅
- 审阅后问题回流为 Playbook 修订

**不做**：
- Playbook 格式 linter
- Step 产出物自动化校验脚本（那是 Approach C 的事，本次放弃）

## 8. Out of Scope

- Multi-Part / Single-Part Protocol 的 Playbook 化 — 留待参考物协议验证成功后再推广
- references/ 目录结构整理 — 本次不动
- 新增 precheck 脚本 — 本次不做
- AI 自检子 Agent — 本次不做

## 9. 验收标准

- SKILL.md R1~R5 段压缩到 ≤ 30 行，grep 验证 0 个 `### Step R` 残留
- Playbook 存在且符合 Section 3 模板
- 行为验证 A/B/C 三个场景跑通：产出报告必须出现 8 / 6 / 7 次（A 全做、B skip 两个、C skip 一个）
- test 14 之前漏 R2.7 的失败模式在新流程下被 Playbook 强制召回
