# 方案 F：AIGC 概念图 → 参数化设计图 设计文档

**日期**：2026-04-20
**作者**：liyijiang + Claude Code Opus 4.7（brainstorming 协作）
**前置设计**：
- `docs/superpowers/specs/2026-04-18-halt-gate-enforcement-design.md`（halt 契约已落地，方案 F 的两个 halt 直接复用）
- SKILL.md §概念草图说明（现有方案 A-E 定义）

---

## 1. 背景

### 1.1 问题

现有 5 方案（A 3视图 / B OCP Proxy / C 截面 / D 参考图标注 / E 参数合同表）覆盖了"几何明确"与"用户已有参考图"两大类建模前对齐需求。但以下场景仍有缺口：

> **用户描述含形态主观词**（仿生、流畅、科技感、异形、潮玩、ID 风格 等），用户脑中有"意象"但说不清尺寸、也没有参考图。

此时走方案 A（AI 自画 3 视图 ASCII）只能承载**结构**信息，无法承载**意象/风格**；走方案 D 需要用户先去外部生成图再回来，往返成本高。

### 1.2 观察到的 AI/用户共同痛点

- AI 文字描述 → 用户脑中画面 → 对齐轮：3-5 轮常见，且常"差不多但不对味"
- 用户自己用 AIGC 生成图再回来：流程割裂，skill 里不能闭环

### 1.3 方向

**由 skill 主动调用 AIGC MCP（已有 `mcp__doubao-mcp-server__text_to_image`）生成概念图**，AI 视觉解读 → 拟合成 3 视图 + 参数合同表 → 建模。本质是把方案 D 的"用户提供图"翻转为"AI 生成图"，闭环在 skill 内完成。

### 1.4 非目标（本轮不做）

- **不做** 方案 A/B/C/D/E 的定义改动；仅在触发逻辑加分支。
- **不做** SKILL.md L100~L1153 技术细节搬迁。
- **不做** reference-product-playbook 集成（该 Playbook 前提就是用户已提供参考图，方案 F 不适用）。
- **不做** image-to-video / image-to-image 后续 AIGC 能力扩展（先只用 text_to_image）。
- **不改** halt 契约本身（方案 F 的两个 halt 复用 §确认门执行契约）。

---

## 2. 架构

### 2.1 核心流程

```
用户需求
  │
  ▼
S1 / P1 需求解析（AI）
  │
  ├─ 检测形态主观词？─── 否 ──▶ 走方案 A（AI 自画 3 视图 ASCII）
  │                                      │
  ├─ 是                                   ▼
  │                               S2 / P2 建模
  ▼
方案 F 路径
  │
  ▼
调 mcp__doubao-mcp-server__text_to_image
生成 3 张概念图（不同风格/视角）
  │
  ▼
下载到 assets/concept/<slug>/<ts>-<n>.png
AI Read 自用 + URL 给用户
  │
  ▼
Gate F1 [halt-for-user]：选图 / reroll / 自己给
  │
  │── 用户选一张 ───────────┐
  │── reroll（换 prompt） ──┘ ◀── 循环（≤ 3 次）
  │── 自己给一张 ───────────┐
  │── MCP 不可用 / 3 次仍不满 ──▶ 降级方案 A
  │
  ▼
AI 视觉解读选中图 → 3 视图 ASCII（方案 A 模板）+ 参数合同表（方案 E 模板）
  │
  ▼
Gate F2 [halt-for-user]：确认尺寸数值 + 形态拟合度
  │
  ▼
S2 / P2 建模
```

### 2.2 主观词词表（触发条件）

**视觉风格类**：科技感、极简、工业风、复古、蒸汽朋克、赛博、仿 XX 风格（如"仿苹果风"）、高级感
**形态特征类**：流畅、仿生、异形、流线型、有机、雕塑感、灵动、柔和曲面
**产品门类类**：潮玩、角品、ID 产品、手办、艺术摆件、概念设计

触发逻辑：**任一词命中** → 走方案 F。
**明确尺寸关键词同时出现时**（如"Ø20×80 的阶梯轴，要科技感"），仍走 F（因"科技感"承载了形态意象，尺寸信息会合并进 Gate F2 参数表）。

词表**可扩展**，在 SKILL.md §方案 F 段以列表形式列出，允许 PR 追加。

### 2.3 MCP 调用规范

**工具**：`mcp__doubao-mcp-server__text_to_image`
**默认参数**：
- `prompt`：AI 根据需求拼接。模板：`<产品类型>, <形态主观词>, industrial design concept, product rendering, 4 views composition, white background, 4k`
- `size`：`1024x1024`（默认）
- `model`：`doubao-seedream-3-0-t2i-250415`（默认）

**调用次数**：一次 halt 循环内生成 3 张（3 次独立调用 / 或 1 次调用要求 4 视图合成图，v1 先用 3 次独立调用以保风格多样）。

**返回处理**：URL → 用 `curl` 或 `Bash` 下载 → 保存路径 `assets/concept/<slug>/<ts>-<n>.png`，`<slug>` 从 S1/P1 部件名 slugify 得到（例：`phone-stand`、`gripper-arm`）。

**AI 自读**：下载后 Read 图像文件（Claude 多模态可读），以便下一步视觉解读。

### 2.4 Gate F1：选图 halt

**产出**（回报模板末尾）：
```
[halt-for-user] ✋ AIGC 概念图 3 张已生成：
  ① assets/concept/<slug>/<ts>-1.png  风格：<风格词>  URL：<url-1>
  ② assets/concept/<slug>/<ts>-2.png  风格：<风格词>  URL：<url-2>
  ③ assets/concept/<slug>/<ts>-3.png  风格：<风格词>  URL：<url-3>

回 "选 ①/②/③" / "reroll <prompt 调整>" / "自己给图 <路径>"
```

halt 前三项自检：同 §确认门执行契约。

### 2.5 Gate F2：参数确认 halt

**产出**：3 视图 ASCII（复用方案 A 模板）+ 参数合同表（复用方案 E 模板）。表尾附：
```
[halt-for-user] ✋ 请确认：
（1）3 视图拟合 AIGC 图的形态是否准确？
（2）参数合同表每行数值是否接受？需改的直接给正确值。
回 "OK" / "改 <参数>=<值>"
```

### 2.6 降级策略

**触发降级**的情况：
- MCP 调用抛错 / 超时（>30s）
- 3 次 reroll 后用户仍不满
- 用户在 Gate F1 选 "自己给图"（此时直接跳到 AI 视觉解读，不走降级）

**降级动作**：AI 透明告知"AIGC 不可用/用户未选定，切换到方案 A"，继续方案 A 自画 3 视图路径，不阻塞。

### 2.7 与 halt 契约的关系

Gate F1 / Gate F2 都是 `[halt-for-user]` 硬字段，遵循 SKILL.md §确认门执行契约：
- halt 前三项自检（产出完整 / Quote-back / 未推进）
- 违规 = single-part FM-1 / multi-part FM-13「越权通过确认门」
- 通过条件：用户回 "选 N / reroll / 自己给 / OK"

**不新增 FM**（复用现有 FM）。

---

## 3. 变更清单

### 3.1 SKILL.md

**位置 1**：§概念草图说明 段（现 L122~L272），在方案 E 之后（L259 附近）追加方案 F 整段。

**方案 F 段内容**（预计 +70~90 行）：
- 触发词（主观词词表）
- MCP 调用描述（工具名 + 默认参数 + 3 张策略）
- Gate F1 回报模板
- 视觉解读 → 3 视图 + 参数表的过渡说明
- Gate F2 回报模板
- 降级策略说明
- "最适合" 一句：用户描述含形态主观词、无参考图、需先定意象的单/多部件

**位置 2**：§5 种方案选择速查表（L262-272）：
- 标题改为 "6 种方案选择速查"
- 追加 `F AIGC 概念图 → 参数合同 | 意象 + 尺寸 | 慢（API 调用）| 形态主观、无参考图`
- 可组合行追加说明：方案 F 已包含 A + E 的产出，单独使用即可，不需再叠 A/E。

**位置 3**：（可选，v1 先不做）方案 A 段的 "默认执行，无需用户开口" 与其他规则的一致性 review 是**另外一件事**，不在本 spec scope。本 spec 只确保方案 F 分支在 A 之前判定（主观词优先走 F，无主观词走 A）。

### 3.2 references/protocols/single-part-playbook.md

**位置**：§Phase S1 "需求简报" 段，在"参考资料问询"之后追加"形态评估"小节：

```markdown
**形态评估**（决定方案 F / A 分支）
- 需求含形态主观词（仿生 / 流畅 / 科技感 / 异形 / 潮玩 / ID 风格 等，完整词表见 SKILL.md §方案 F）→ 走方案 F（AIGC 概念图 → 3 视图 + 参数表）
- 否则 → 走方案 A（AI 自画 3 视图 ASCII）

**引 SKILL.md §方案 F**：...（Quote-back 引原文）
```

预计 +15~25 行。FM 不新增（复用 FM-1）。

### 3.3 references/protocols/multi-part-playbook.md

**位置**：§Phase P1 "需求拆解" 段，在"参考资料问询"之后加同样的"形态评估"分支（单部件 / 部件组装整体形态，两层都检测主观词）。

预计 +15~25 行。FM 不新增（复用 FM-13）。

### 3.4 assets/concept/（新建目录约定）

约定：`assets/concept/<slug>/<ts>-<n>.png` 存放 AIGC 生成图。`.gitignore` 考虑：
- 生成图**不入 git**（避免仓库膨胀 + 外部 URL 可能过期）
- 在 `assets/concept/.gitkeep` 占位保留目录存在

在 SKILL.md §方案 F 段明文规定存储路径与 .gitignore 约定。

### 3.5 tests/20-aigc-concept-dryrun/（新建，可选）

仅行为验证，不实际跑 MCP（避免 API 消耗 + dry-run 一致性）：

```
tests/20-aigc-concept-dryrun/
├── README.md
├── run_P.md               # Scenario P：主观词触发 → 走方案 F
├── run_Q.md               # Scenario Q：无主观词 → 走方案 A（不触发 F）
├── run_R.md               # Scenario R：MCP 不可用 → 降级方案 A
└── structure_check.md
```

v1 **可选**，如果时间紧可先跳过，靠真实会话跑 test 13/14/18 + 新用例（含主观词的真实需求）验证。

### 3.6 不变

- 方案 A / B / C / D / E 定义
- halt 契约 / FM-1 / FM-13 / §确认门执行契约
- Step 内部产出物（S1-S4 / P1-P4）
- reference-product-playbook（方案 F 不适用）
- Stage A/B/C 执行器
- experience/ 目录

---

## 4. Scenario 设计（tests/20，可选）

### 4.1 Scenario P — 主观词触发方案 F

**Prompt**：
```
帮我做一个仿生风格的手机支架，要流畅有设计感。
```

**判据**（7 条，硬下限 ⬛）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| P-1 | 路由到 single-part-playbook | ⬛ |
| P-2 | S1 形态评估识别主观词 "仿生 / 流畅 / 设计感"，判定走方案 F | ⬛ |
| P-3 | AI 调 `mcp__doubao-mcp-server__text_to_image` 3 次 | ⬛ |
| P-4 | 生成图下载到 `assets/concept/phone-stand/*.png` | |
| P-5 | Gate F1 回报末尾含 `[halt-for-user]` 硬字段 + 3 张图 URL | ⬛ |
| P-6 | `[halt-for-user]` 之后同一轮**没有 3 视图 / 参数表 / 建模代码** | ⬛ |
| P-7 | Quote-back 引 SKILL.md §方案 F 原文正确 | |

### 4.2 Scenario Q — 无主观词走方案 A

**Prompt**：
```
做一个 Ø20×80 的阶梯轴。
```

**判据**（5 条）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| Q-1 | 路由到 single-part-playbook | ⬛ |
| Q-2 | S1 形态评估判定**无主观词**，走方案 A（**不**调 MCP） | ⬛ |
| Q-3 | 按方案 A 自画 3 视图 ASCII | |
| Q-4 | S2 halt 正常发出 | ⬛ |
| Q-5 | Quote-back 正确 | |

### 4.3 Scenario R — MCP 降级

**Prompt**：同 P，但子代理 Scenario prompt 里明确注入"假设 `mcp__doubao-mcp-server__text_to_image` 抛错 / 不可用"的前置约束，子代理按该约束执行不真实调 MCP。

**判据**（5 条）：

| 编号 | 检查 | 硬下限 |
|---|---|---|
| R-1 | AI 识别主观词，尝试调 MCP | |
| R-2 | MCP 返回错误后，AI 透明告知"AIGC 不可用，切换方案 A" | ⬛ |
| R-3 | 不阻塞，继续走方案 A 路径 | ⬛ |
| R-4 | 未在同一轮越过 halt 推进建模 | ⬛ |
| R-5 | 降级过程有 Quote-back 引 §方案 F "降级策略" | |

---

## 5. 实施顺序

1. **skill 仓（build123d-cad）**：
   - Step 1：SKILL.md 加方案 F 整段 + 速查表改 6 方案
   - Step 2：single-part-playbook.md §S1 加形态评估分支
   - Step 3：multi-part-playbook.md §P1 加形态评估分支
   - Step 4：assets/concept/ 目录约定（.gitkeep + .gitignore）
   - 每 Step 独立 commit

2. **test 仓**（可选，v1 若时间紧可跳过）：
   - Step 5：新建 tests/20-aigc-concept-dryrun/ 目录 + README + 3 Scenario run_P/Q/R
   - Step 6：跑 3 Scenario（子代理模拟 MCP，Scenario R 注入 MCP 失败）
   - Step 7：structure_check.md 汇总

3. **回归**：
   - test 13（redmi K80 Pro）/ test 14（xiaomi K70）用户在新会话手动重跑验证无主观词 → 走方案 A（不多调 MCP）
   - 新建一个含主观词的真实需求任务验证方案 F 全流程（用户新会话）

---

## 6. 验收标准

### 6.1 结构核对（若做 tests/20）

| # | 检查项 | 期望 |
|---|---|---|
| 1 | `grep -c "方案 F" SKILL.md` | ≥ 3（标题 + 速查表 + 内联引用） |
| 2 | `grep -c "text_to_image" SKILL.md` | ≥ 1 |
| 3 | `grep -c "形态评估" single-part-playbook.md` | ≥ 1 |
| 4 | `grep -c "形态评估" multi-part-playbook.md` | ≥ 1 |
| 5 | `ls assets/concept/.gitkeep` | 存在 |
| 6 | 5种方案速查表改为 6 种 | ✅ |
| 7 | tests/20 文件齐全 | 5/5 |

### 6.2 行为验证（若做 tests/20）

- Scenario P：≥ 6/7 ✅（硬下限 P-1/P-2/P-3/P-5/P-6 全过）
- Scenario Q：≥ 4/5 ✅（硬下限 Q-1/Q-2/Q-4 全过）
- Scenario R：≥ 4/5 ✅（硬下限 R-2/R-3/R-4 全过）
- 合计：**14/17 ✅** 为 PASS 阈值，硬下限 11/11 全 ✅ 为更强信号。

### 6.3 回归验证（用户新会话）

- test 13/14（single-part，Ø20×80 类几何明确件）：不走方案 F、不调 MCP、方案 A 路径无变化 → 无回退。
- 新建含主观词任务（如"仿生手机支架"）：走方案 F 完整流程、Gate F1/F2 halt 正常、参数表到建模顺畅。

---

## 7. 失败处置

- 若 Scenario P **P-3 或 P-5 失败**（MCP 没调或 Gate F1 没发）→ spec 核心假设不成立，回退本设计。
- 若 Scenario Q **Q-2 失败**（无主观词也误调 MCP）→ 触发逻辑过宽，收紧主观词词表或改成"主观词 + 无明确尺寸"的与条件。
- 若 Scenario R **R-2/R-3 失败**（降级不透明或阻塞）→ 降级策略在 SKILL.md §方案 F 里写得不够硬，强化为"必 Quote-back §降级策略原文"。
- 若回归 test 13/14 出现回退 → 方案 F 分支逻辑侵入了无主观词路径，定位并收紧触发。

---

## 8. 开放问题

- **主观词词表边界**：初始词表约 15-20 词，实际使用中会发现遗漏。建议在 SKILL.md §方案 F 段写 "词表可扩展，通过 PR 追加"，并记录追加历史。
- **API 消耗控制**：每次触发 3 次调用，用户可 reroll 最多 3 次 = 最多 12 次/任务。若未来发现消耗过大，可降为 1 次 + 用户主动要求再生成。
- **图像呈现方式**：v1 给 URL 让用户自己点开查看；未来可考虑 chrome MCP 自动打开、或 OCP viewer 集成。
- **prompt 模板质量**：初版 prompt 模板比较粗糙（"industrial design concept, product rendering, 4 views composition"），可能生成的图不够贴需求。若实际使用发现偏差，把 prompt 工程抽成可配置段。
- **方案 A 触发规则一致性**：SKILL.md L134 写"默认执行，无需用户开口"，与 commit 7982280 新增的"概念草图只在显式请求时触发"规则可能矛盾。**不在本 spec scope**，建议 skill 维护者单独提 PR 对齐。方案 F 本身触发条件独立（检测主观词），不受此问题影响。

---

## 9. 变更不涉及

- 方案 A / B / C / D / E 的定义、触发词、模板
- halt 契约 / FM 编号 / §确认门执行契约
- Stage A/B/C 执行器代码
- experience/ 目录
- reference-product-playbook
- Step S1-S4 / P1-P4 内部产出物定义

---

## 10. 里程碑

- spec 批准 → 进 writing-plans
- plan 批准 → 执行（预计 0.5-1 天完成 skill 仓改动；若加 tests/20 追加 0.5 天）
- 验收 PASS → commit + push + 通告用户在新会话跑 test 13/14 + 新含主观词任务回归

---

## 11. Changelog

### v1.0 — 2026-04-20
- 初版 spec，brainstorming 批准。
