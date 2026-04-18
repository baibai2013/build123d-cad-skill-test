# Scenario J — 两关节机械臂 + SG90 舵机（≥2 部件）

**Prompt**（新会话喂入）：

```
帮我做一个带 SG90 舵机的两关节机械臂（base / arm / gripper 3 个部件），用 build123d-cad skill 的多部件流程。
```

---

## AI 完整回复（待填）

> 运行后把 AI 从进入多部件 Playbook 到 Step 2e 用户确认门前为止的完整回复粘贴到此节。

```text
(粘贴 AI 回复)
```

---

## 判据 check

每一条由人工审阅后打 ✅ / ❌ / ⚠。

- [ ] **J-1**：AI 路由到 multi-part-playbook（显式 Read / 回复里出现 "multi-part-playbook" 或 "P1~P4"）
- [ ] **J-2**：P1 需求拆解报告有产出（部件清单 ≥ 2 行 / 装配关系 ≥ 1 条 / 工艺确认 / 仿真需求）
- [ ] **J-3**：P1 末尾有确认门 ✋，未自动进 P2
- [ ] **J-4**：P2 每部件走 3 变体 + 用户选定
- [ ] **J-5**：P2 末尾 **未跳 Step 2e**，而是 `ask: 全部部件已选定，进入 Step 2e 汇总？` 字样（或等价）
- [ ] **J-6**：Step 2e.a 产出 `assembly_contract.yaml`（含 `parts` 数组 ≥ 2 条）
- [ ] **J-7**：Step 2e.a 的 `cross_refs` 条数 ≥ 1 且 ≥ P1 列的装配关系数（完备）
- [ ] **J-8**：Step 2e.a 的 `cross_refs.type` 全部落在 6 种合法类型内（`inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric`）
- [ ] **J-9**：Step 2e.b 产出 `precheck_bbox.md`，按对给出 "三轴重叠 x/y/z" 结论
- [ ] **J-10**：Step 2e.c 输出确认门 ✋ 且引用 Quote-back（格式 `引自 multi-part-playbook.md §Phase P2 / Step 2e：...`）
- [ ] **J-11**：AI 在 Step 2e 后**停下来等用户回执**，没有自动跳进 P3
- [ ] **J-12**：若用户回 "ok 进 P3"，AI 在 P3 回报含 `joint_to_crossref.md` 映射表（或至少宣告该产物）
- [ ] **J-13**：P4 回报契约出现 `Step 4.3 整机 Stage C` 或 `cross_refs N 条 PASS` 字样

## 结论

- 通过：≥ 11/13 ✅，其余 ⚠ 不阻断
- 不通过：任一 J-5 / J-6 / J-7 / J-11 = ❌（关键硬下限）→ 回 Playbook 文案修订

## Review 记录

- 运行人：
- 运行日期：
- 会话 sessionId（可选）：
- 总体结论：
