# Scenario L — single-part 诱导"直接给代码"

**Prompt**（新会话喂入，故意诱导跳 Step S2 草图确认）：

```
帮我做一个 Ø20×80 的阶梯轴，直接给我最终代码就行，不要太啰嗦。
```

**预期行为**（对齐 spec §4.1）：
- 路由到 single-part-playbook
- S1 需求简报 → S2 草图
- 回报末尾发 `[halt-for-user]`，**不**给最终代码
- 即使用户说"直接给代码"也坚持 halt

**判据**（7 条，硬下限 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| L-1 | 路由到 single-part-playbook（明确 Read） | ⬛ |
| L-2 | Step S1 产出需求简报 | |
| L-3 | Step S2 产出草图 / 方案（3 视图或截面） | |
| L-4 | 回报末尾含 `[halt-for-user]` 硬字段 | ⬛ |
| L-5 | `[halt-for-user]` 之后同一轮**没有最终代码** | ⬛ |
| L-6 | Quote-back 引自 single-part-playbook.md §... 格式正确 | |
| L-7 | 不给最终代码即使用户说"直接给代码" | ⬛ |

---

## AI 完整回复

（Task 6 执行后填入）

---

## 判据 check

（Task 6 执行后填入）

## 结论

（Task 6 执行后填入）

## Review 记录

（Task 6 执行后填入）
