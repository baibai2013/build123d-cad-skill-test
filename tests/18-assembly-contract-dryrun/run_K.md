# Scenario K — cross_refs 漏翻译触发 FM-12

**Prompt**（新会话喂入，**故意**列 3 条装配关系让 AI 易漏一条）：

```
做一个手机支架：底座（base）+ 支撑杆（rod）+ 夹持头（clamp），要求
1) base 和 rod 同轴
2) rod 和 clamp 成 ordering（rod 在下 clamp 在上）
3) clamp 的夹口中心线和 base 平行

走多部件流程。
```

## 预期行为

- P1 需求拆解报告应列出 3 条装配关系
- Step 2e.a 翻译 cross_refs 时，若漏掉第 3 条（`colinear` 类型少见，易被 AI 忽略），应在 Step 2e.c 的 Quote-back 自检或用户提示后触发 **FM-12**：cross_refs 覆盖不全
- AI 回 Step 2e.a 补齐第 3 条 `colinear` 约束，重新产出 `assembly_contract.yaml` 后才进 P3

---

## AI 完整回复（待填）

> 包含首次产出 + 用户指出漏条后 AI 的回补过程。

```text
(粘贴 AI 回复)
```

**(可选) 触发话术**：如果 AI 自己未发现漏翻译，用户回复：

```
你的 cross_refs 数量对得上 P1 拆解里的 3 条装配关系吗？
```

---

## 判据 check

- [ ] **K-1**：P1 拆解报告列了 3 条装配关系（条目数与 prompt 对齐）
- [ ] **K-2**：Step 2e.a 首次产出的 `cross_refs` 要么齐（≥3 条）要么漏（<3 条）—— 记录实际数字
- [ ] **K-3**：若漏条，AI 能在自检或用户提示下**明确引用 FM-12**（"cross_refs 覆盖不全"）
- [ ] **K-4**：修复后 `cross_refs` 条数 ≥ P1 拆解装配关系数（即 ≥ 3）
- [ ] **K-5**：修复后的第 3 条 type 合理（`colinear` 或等价语义）
- [ ] **K-6**：修复过程未强行进 P3 / 未自动跳过 Step 2e.c 确认门
- [ ] **K-7**：修复后的 Quote-back 格式正确（引自 multi-part-playbook.md §Phase P2 / Step 2e）

## 结论

- 通过：K-1 / K-4 / K-6 全 ✅；K-3 部分 ✅（AI 自察觉更佳，用户提示亦可）
- 不通过：漏条未被 catch，AI 直接进 P3 / cross_refs 空 → 回 FM-12 文案修订

## Review 记录

- 运行人：
- 运行日期：
- FM-12 是否主动触发：AI 自察觉 / 需用户提示 / 未触发
- 总体结论：
