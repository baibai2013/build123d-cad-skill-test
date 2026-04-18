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
