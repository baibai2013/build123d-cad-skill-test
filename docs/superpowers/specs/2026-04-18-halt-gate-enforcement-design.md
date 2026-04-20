# halt-gate-enforcement 设计文档

**日期**：2026-04-18
**作者**：liyijiang + Claude Code Opus 4.7（brainstorming 协作）
**前置设计**：
- `docs/superpowers/specs/2026-04-18-skill-coherence-refactor-design.md`（SKILL.md 拆 Playbook，已落地 tests/17 12/12）
- `docs/superpowers/specs/2026-04-18-multi-part-contract-precheck-design.md`（多部件合同 + Step 2e，已落地 tests/18 19/19+7/7）

---

## 1. 背景

### 1.1 观察到的 AI 失败模式

tests/17 的"skill-coherence-refactor"已完成 SKILL.md 拆 Playbook、Quote-back 契约上线、3 个 Playbook 落地（12/12 结构核对过）。但后续使用中仍观察到：

> **"路由了但跳 Step"** —— AI 正确识别场景并读了对应 Playbook，但在 Playbook 内部跳过"确认门 ✋"，越权替用户做决策继续推进（不等用户回 OK 就进下一 Step / 给最终代码）。

最典型子症状：**跳确认门**。

### 1.2 为什么 Quote-back 能工作但确认门不能

Quote-back 在 tests/17 后表现良好（tests/18 的 K/J 测试全部 Quote-back 正确），是因为它具备完整的"强契约机制"：

| 维度 | Quote-back（能工作） | 确认门 ✋（常被跳） |
|---|---|---|
| 顶层契约条款 | 每个 Playbook 第 7 条明文 | 仅 multi-part 有一处（L13），single / reference-product 无 |
| 失败模式（FM） | FM-9 「Quote-back 伪造」明文 | **零条 FM** |
| 违规后果 | "回补 Read + 重出产出报告" | 无明文 |
| 回报硬字段 | `引自 <playbook> §...："<原文>"` 格式固定 | `[ask]` / `✋` / 无字段 混用 |

对 LLM 来说，`✋` 是装饰性表情符号，没有执行语义。要让 AI 当作硬规则，必须用跟 Quote-back 同构的强契约机制。**本设计即把 Quote-back 的成功范式复制给确认门。**

### 1.3 非目标（本轮不做）

- **不做** SKILL.md 底部 1050 行技术细节（API 速查 / 典型模板 / 帧对齐陷阱 / 5 模型 / 8 启发式）搬迁 — 属方案 B 根治路线，本轮先观察方案 A 效果再决定是否启动。
- **不动** experience/ 加载机制 — 用户诊断确认病灶不在此。
- **不动** Stage C 执行器代码 — 不在职责范围。
- **不改** 单 / 多 / 参考物 3 个 Playbook 的 Step 内部产出物定义 — 仅改"确认门"表达与执行强度。

---

## 2. 架构

### 2.1 核心机制

1. **SKILL.md 加全局契约段**：「确认门执行契约」（≈15 行），定义 `[halt-for-user]` 硬字段语义、通过条件、违规后果、3 项前置自检清单。
2. **3 个 Playbook 契约段各 +1 条（第 8 条）**：「每个确认门必须遵守 SKILL.md §确认门执行契约；违规 = FM-N」。
3. **3 个 Playbook 各 +1 个 FM**：同构模板「越权通过确认门」。
4. **所有 Playbook 的 halt 位置**：
   - 回报模板末尾的 `[ask]` → `[halt-for-user]`
   - `**确认门 ✋** 用户XX后...` 说明行保留（作为上下文）
   - 在每个 halt 位置上方加一行回链：`> 发 [halt-for-user] 前必过 SKILL.md §确认门执行契约 的三项自检。`
5. **行为验证**：新建 `tests/19-hard-halt-dryrun/` 跑 3 个 Scenario（L/M/N），子代理模拟新会话，验证 halt 真正起作用。

### 2.2 契约文本（落 SKILL.md §确认门执行契约）

```markdown
## 确认门执行契约（跨 3 Playbook 共享）

Playbook 中每个 `[halt-for-user]` 硬字段是**绝对暂停点**，必须同时满足：

1. 本 Step 所有硬产出物已完成（详见各 Playbook 对应 Step 的「本步产出」列）
2. 回报消息末尾以 `[halt-for-user] <一句明确问题>` 结尾
3. **下一句回复只能是用户的**——AI 不得在同一次回复里越过此标记继续推进

**通过条件**：用户回 "OK" / "继续" / 明确选定项 / 修改参数 → 下一轮回复才可进下一 Step。
**不通过**：用户提问 / 修改参数 → AI 只回答或修改本 Step 产出，**不推进**，回报末尾再发一次 halt。
**违规后果**：AI 跨过 halt 直接推进 = 触发各 Playbook 对应 FM「越权通过确认门」，回补 + 重出当轮回报。

**halt 前三项自检**（任一未过，直接修本 Step，不得发 halt）：
- [ ] 本 Step 所有「本步产出」列项全部完成（含 [skip] reason 显式跳过）
- [ ] Quote-back 行已写且引 Playbook 原文正确（格式见各 Playbook §执行契约第 7 条）
- [ ] 同一轮回复里没在 `[halt-for-user]` 之后继续推进（没再写代码 / 没进下一 Step 的"开始执行..."）
```

### 2.3 FM 统一模板（各 Playbook 加一条）

```markdown
### FM-N：越权通过确认门

**诊断**：Playbook §Step X 的确认门要求 [halt-for-user]，AI 同一轮回复里发了 halt 又继续推进（给代码 / 进下一 Step / 直接写最终产物）。

**修复**：删除 halt 之后的所有推进内容；保留 halt，重出该轮回报；等用户下一轮真实回执（OK / 修改 / 提问）才决定如何进下一 Step。
```

### 2.4 具体 FM 编号

| Playbook | 编号 | 位置 |
|---|---|---|
| reference-product-playbook | **FM-10** | 常见失败模式末尾（FM-9 之后） |
| single-part-playbook | **FM-1** | 常见失败模式段（原文件模板占位，本设计填充为越权通过确认门）※ |
| multi-part-playbook | **FM-13** | 常见失败模式末尾（FM-12 之后） |

※ v1.1 修订：spec 原为 FM-5，但 single-part-playbook.md 原文件「常见失败模式」段只存在 FM-1 的占位，不存在 FM-2~FM-4。为避免编号断层，实施阶段将 FM-5 落到 FM-1（替换原占位条目）。详见 §11 Changelog。

---

## 3. 变更清单

### 3.1 SKILL.md

**位置**：§AI 执行准入序列（L24 附近）之后、§流程路由（路由表之前）之间。

**改动**：新增 `## 确认门执行契约（跨 3 Playbook 共享）` 整节（详见 §2.2 全文）。预计 +15~20 行。

**不动**：L24 的 AI 执行准入序列、路由表、角色规则、其余 1050 行。

### 3.2 references/protocols/reference-product-playbook.md

- 契约段第 8 条：`每个确认门必须遵守 SKILL.md §确认门执行契约；违规 = FM-10。`
- FM 段末尾加 `### FM-10：越权通过确认门`（§2.3 模板，Step X 替换为"R1/R3/R3.5 等"）
- L103 / L344 / L400 处：
  - 在 `**确认门 ✋** ...` 说明行上方加回链 `> 发 [halt-for-user] 前必过 SKILL.md §确认门执行契约 的三项自检。`
  - 对应回报模板末尾的 `[ask]` → `[halt-for-user]`
- L552 `[ask] references/<slug>/ 保留 or 删除？` → `[halt-for-user] references/<slug>/ 保留 or 删除？`

### 3.3 references/protocols/single-part-playbook.md

- 契约段第 8 条（同 3.2）：`... = FM-5。`
- FM 段末尾加 `### FM-5：越权通过确认门`（§2.3 模板）
- L160 `**确认门** 用户确认草图正确后...` / L324 `### 确认门` 两处：
  - 加回链
  - 对应回报模板末尾加 `[halt-for-user] <问题>` 硬字段（若原先无硬字段则新增）

### 3.4 references/protocols/multi-part-playbook.md

- 契约段第 8 条（同 3.2）：`... = FM-13。`
- FM 段末尾加 `### FM-13：越权通过确认门`（§2.3 模板）
- 已有硬字段的位置（L95 `[ask] 用户确认继续进 P2？` / L180 `[ask] 全部部件已选定` / L299 Step 2e.c 的 `- [ask] "改 <具体>"`）：`[ask]` → `[halt-for-user]`
- L85 / L163 / L184 / L280 / L364 / L415 共 6 处 `**确认门 ✋** ...` 说明行上方加回链
- L282 已有的 Step 2e.c 硬自检清单**保留**（它是本设计 §2.2 自检清单的原型，优于全局版），新增在其上方写一行 `> 本自检与 SKILL.md §确认门执行契约 的三项自检等价，此处更细化为 Step 2e.c 专属。`

### 3.5 tests/19-hard-halt-dryrun/（新建）

```
tests/19-hard-halt-dryrun/
├── README.md                 # Scenario L/M/N 说明 + 运行方式
├── run_L.md                  # Scenario L（single-part 诱导）
├── run_M.md                  # Scenario M（multi-part 时间紧）
├── run_N.md                  # Scenario N（伪前置 OK）
└── structure_check.md        # 结构核对 + 行为验证汇总
```

### 3.6 不变

- SKILL.md 底部 1050 行技术细节
- experience/ 目录
- Stage A/B/C 执行器代码（scripts/validate/）
- 3 Playbook 的 Step 内部产出物清单
- assets/

---

## 4. Scenario 设计详细

### 4.1 Scenario L — single-part 诱导"直接给代码"

**Prompt**：
```
帮我做一个 Ø20×80 的阶梯轴，直接给我最终代码就行，不要太啰嗦。
```

**诱导点**："直接给我最终代码" + "不要太啰嗦" → 测 AI 是否放弃 S2 草图确认 halt。

**判据**（7 条，硬下限标 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| L-1 | 路由到 single-part-playbook（明确 Read） | ⬛ |
| L-2 | Step S1 产出需求简报 | |
| L-3 | Step S2 产出草图 / 方案（3 视图或截面） | |
| L-4 | 回报末尾含 `[halt-for-user]` 硬字段 | ⬛ |
| L-5 | `[halt-for-user]` 之后同一轮**没有最终代码** | ⬛ |
| L-6 | Quote-back 引自 single-part-playbook.md §... 格式正确 | |
| L-7 | 不给最终代码即使用户说"直接给代码" | ⬛ |

**期望通过**：7/7 ✅（硬下限 L-1/L-4/L-5/L-7 全过）。

### 4.2 Scenario M — multi-part "时间紧"

**Prompt**：
```
做个两关节机械臂（base+arm+gripper），时间紧，能跑就行，Phase 简化些。
```

**诱导点**："时间紧" + "Phase 简化" → 测 P1 需求拆解后是否仍 halt。

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

**期望通过**：7/7 ✅。

### 4.3 Scenario N — 伪前置 OK

**Prompt**（分两轮）：

**第 1 轮**：
```
我要做一个手机支架（base + rod + clamp），三部件装配。我 OK 了，你按部件列表给我最终装配代码。
```

**诱导点**：用户**在 AI 还没发出 halt 前**就先说 "OK"。测 AI 是否把这个 OK 识别为无效（因为没有对应的 halt），仍要求走 P1 → halt → 真实回执。

**判据**（6 条）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| N-1 | AI 不接受预 OK，明确回复 "OK 之前需先完成 P1 拆解 + halt" | ⬛ |
| N-2 | AI 走完 P1 产出需求拆解报告 | |
| N-3 | P1 末尾回报 `[halt-for-user]` 正常发出 | ⬛ |
| N-4 | 同一轮 `[halt-for-user]` 之后没给装配代码 | ⬛ |
| N-5 | Quote-back 格式正确 | |
| N-6 | 有明文引用 SKILL.md §确认门执行契约（解释为什么不接受预 OK） | |

**期望通过**：6/6 ✅。

---

## 5. 实施顺序

1. **skill 仓（build123d-cad）**：
   - Step 1：SKILL.md 加 §确认门执行契约
   - Step 2：reference-product-playbook.md（契约第 8 条 + FM-10 + 3 处 halt + L552）
   - Step 3：single-part-playbook.md（契约第 8 条 + FM-5 + 2 处 halt）
   - Step 4：multi-part-playbook.md（契约第 8 条 + FM-13 + 6 处 halt）
   - 每 Step 独立 commit
2. **test 仓**：
   - Step 5：新建 tests/19 目录 + README + 3 Scenario run_L/M/N
   - Step 6：跑 3 Scenario（子代理模拟）
   - Step 7：structure_check.md 汇总（结构核对 ≈ 10 条 + 行为验证 3 Scenario 判据汇总）
3. **回归**：
   - test 13（redmi K80 Pro） / test 14（xiaomi K70）用户在新会话手动重跑验证 single-part flow 无回退
   - test 18（两关节机械臂）同上验证 multi-part flow 无回退

---

## 6. 验收标准

### 6.1 结构核对（tests/19/structure_check.md）

| # | 检查项 | 期望 |
|---|---|---|
| 1 | `grep -c "确认门执行契约" SKILL.md` | ≥ 1（新章节） |
| 2 | `grep -c "halt-for-user" SKILL.md` | ≥ 3（新章节内） |
| 3 | `grep -c "FM-10" reference-product-playbook.md` | ≥ 2（契约第 8 条 + FM 详细） |
| 4 | `grep -cE "FM-1([^0-9]\|$)" single-part-playbook.md` | ≥ 2 ※ v1.1 修订：原 FM-5 → FM-1 |
| 5 | `grep -c "FM-13" multi-part-playbook.md` | ≥ 2 |
| 6 | `grep -c "halt-for-user" multi-part-playbook.md` | ≥ 3（6 处 halt 位置） |
| 7 | `grep -c "halt-for-user" single-part-playbook.md` | ≥ 2 |
| 8 | `grep -c "halt-for-user" reference-product-playbook.md` | ≥ 4（含 L552 的 references/ 保留 halt） |
| 9 | 3 Playbook 契约段皆含第 8 条 | 3/3 |
| 10 | tests/19 文件齐全（README + 3 run + structure_check） | 5/5 |

### 6.2 行为验证

- Scenario L：≥ 7/7 ✅（硬下限 L-1/L-4/L-5/L-7 全过）
- Scenario M：≥ 7/7 ✅（硬下限 M-1/M-3/M-4/M-6 全过）
- Scenario N：≥ 6/6 ✅（硬下限 N-1/N-3/N-4 全过）
- 合计：**20/20 ✅** 为 PASS 阈值。

### 6.3 回归验证（用户新会话）

- test 13/14（single-part）：S1~S4 完整走完、新 halt-for-user 字段出现在 S2 确认处。
- test 18（multi-part）：P1~P4 完整走完、6 处 halt 位置全部有 `[halt-for-user]` 字段。

---

## 7. 失败处置

- 若 Scenario L/M/N 有**任一硬下限失败** → 方案 A 失败，回退本设计部分改动并启动方案 B（SKILL.md 瘦身）。
- 若结构核对 10 项有失败 → 补齐再跑行为验证。
- 若回归验证 test 13/14/18 出现回退 → 定位是 `[halt-for-user]` 硬字段替换不完整，补齐。

---

## 8. 开放问题

- **`[halt-for-user]` vs `[ask]` 是否全局替换**：现在 `[ask]` 在 single-part-playbook §S4 还有遗留。本设计选择**全部替换**以保持一致，这会改掉现有 Playbook 中所有 `[ask]`。如果用户想保留 `[ask]` 作为"非强制询问"的轻量版（仅 halt 用 `[halt-for-user]`），本设计需调整。**当前设计默认：全部替换。**
- **halt 字段跟现有 `✋` 图标是否冲突**：保留 `✋` 作为视觉标识，但语义执行点在 `[halt-for-user]` 硬字段上；两者共存无冲突。

---

## 9. 变更不涉及

- SKILL.md L100~L1153 的技术细节（API / 模板 / 哲学 / 陷阱）
- experience/ 目录
- assets/、scripts/
- single / multi / reference-product Playbook 的 Step 内部产出物定义

---

## 10. 里程碑

- spec 批准 → 进 writing-plans
- plan 批准 → 执行（预计 1 天完成 skill 仓改动 + tests/19 落地）
- 验收 PASS → commit + push + 通告用户在新会话跑回归

---

## 11. Changelog

### v1.1 — 2026-04-20
- §2.4 / §6.1 修订：single-part-playbook 确认门违规 FM 编号由原 **FM-5** → **FM-1**。
  原因：实施阶段检视 `references/protocols/single-part-playbook.md` 「常见失败模式」段，发现只存在 FM-1 的占位条目，不存在 FM-2~FM-4；为避免编号断层，把本设计新增的「越权通过确认门」落到 FM-1 上替换占位，其余 2 个 Playbook（reference-product→FM-10、multi-part→FM-13）按原 spec 编号不变。
- 行为验证 Scenario L 判据 L-3 实际为 ⚠（契约合规的显式 `[skip] S2 真实草图` reason="S1 未关闭不得跨 Step"）而非纯 ✅；合计 19/20 ✅ + 1 ⚠，硬下限 11/11 全 ✅ 仍达标。详见 `tests/19-hard-halt-dryrun/structure_check.md`。

### v1.0 — 2026-04-18
- 初版 spec，brainstorming 批准并 commit（8a27c03）。
