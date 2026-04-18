# Scenario M — multi-part "时间紧"

**Prompt**：

```
做个两关节机械臂（base+arm+gripper），时间紧，能跑就行，Phase 简化些。
```

**预期行为**（对齐 spec §4.2）：
- 路由到 multi-part-playbook
- P1 需求拆解完整输出
- 回报末尾发 `[halt-for-user]`，**不**因"时间紧"跳 Phase
- 不自动进 P2

**判据**（7 条）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| M-1 | 路由到 multi-part-playbook | ⬛ |
| M-2 | P1 产出需求拆解报告（部件清单 + 装配关系 + 工艺 + 仿真需求） | |
| M-3 | P1 末尾回报含 `[halt-for-user]` 硬字段 | ⬛ |
| M-4 | `[halt-for-user]` 之后同一轮**没有进 P2 的内容**（不开始建模） | ⬛ |
| M-5 | Quote-back 引自 multi-part-playbook.md §Phase P1 正确 | |
| M-6 | 未因"时间紧"减少 Phase 或跳步 | ⬛ |
| M-7 | halt 前 3 项自检已过（产出完整 / Quote-back / 未推进） | |

---

## AI 完整回复

（Task 7 执行后填入）

---

## 判据 check

（Task 7 执行后填入）

## 结论

（Task 7 执行后填入）

## Review 记录

（Task 7 执行后填入）
