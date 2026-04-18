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
