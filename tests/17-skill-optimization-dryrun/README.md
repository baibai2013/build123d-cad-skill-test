# tests/17-skill-optimization-dryrun

验证 skill-coherence-refactor（SKILL.md 去内容化 + Quote-back 强制）是否达成设计目标。

**验证目标**：AI 在新会话接到三类需求时，是否真正 Read Playbook 后按 Step/Phase 走，每步产出报告首行含 Quote-back。

## 三个场景

### Scenario G — 参考物建模
- **用户输入**：`做一个红米 K80 Pro 的手机壳`（或任意已存在产品型号）
- **预期行为**：
  1. AI 立即 Read `references/protocols/reference-product-playbook.md`
  2. R1~R5 完整执行，每 Step 产出报告首行含 `引自 reference-product-playbook.md §Step R<n> / <小标题>："<原文>"`
  3. R1 查 `experience/` 并报 `[hit]/[partial]/[miss]`
  4. R5 输出 Experience Draft，用户 review 后落盘
- **失败判据**：
  - 没 Read Playbook（直接凭 SKILL.md 记忆走）
  - 缺 Quote-back 首行
  - Quote-back 原文与 Playbook 实际不符（捏造）
  - 跳 Step（例如跳过 R2.7 Layer 2 视觉对齐）
- **保存**：粘贴 AI 完整回复到 `run_G.md`

### Scenario H — 单部件建模
- **用户输入**：`做一个齿轮`（或任意独立实体需求）
- **预期行为**：
  1. AI 立即 Read `references/protocols/single-part-playbook.md`
  2. S1~S4 完整执行，每 Step 产出报告首行含 `引自 single-part-playbook.md §Step S<n> / <小标题>："<原文>"`
  3. S2 生成 3 变体 + OCP 对比 + 用户选定
  4. S4 导出 STEP/STL + 工艺提示
- **失败判据**：
  - 照当前 SKILL.md 记忆走（跳过 Playbook）
  - 直接给代码不走 Step 流程
  - 缺 Quote-back
  - 不生成 3 变体直接定稿
- **保存**：粘贴 AI 完整回复到 `run_H.md`

### Scenario I — 多部件装配
- **用户输入**：`做一个带舵机的机械臂`（或任意 ≥2 件 / 仿真 / 装配需求）
- **预期行为**：
  1. AI 立即 Read `references/protocols/multi-part-playbook.md`
  2. P1~P4 完整执行，每 Phase 产出报告首行含 `引自 multi-part-playbook.md §Phase P<n> / <小标题>："<原文>"`
  3. P1 / P2 后有确认门 ✋
  4. P3 装配触发 OCP 预览
  5. P4 装配体 Layer 1/2 验证
- **失败判据**：
  - 跳 Phase
  - 缺确认门
  - 缺 Quote-back
  - P3 不触发 OCP 预览
- **保存**：粘贴 AI 完整回复到 `run_I.md`

## 运行说明

每个 Scenario 在**全新的 Claude 会话**里跑（避免 skill 已加载的缓存）：

1. 开新会话
2. 粘贴 Scenario 的"用户输入"
3. AI 执行完毕后，整段复制回复粘进 `run_<X>.md`
4. 用 README.md 的"失败判据"清单逐条打勾 / 打叉
5. 全 pass → 本次 refactor 达成验证目标

## 回归验证（额外）

- **test 13（红米 K80 Pro 手机壳）重跑**：R1~R5 能走完，不因路由段瘦身而跳步
- **test 14（小米 K70 手机壳）重跑**：R2.7 仍必做、face_mapping.yaml 仍生成
