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
