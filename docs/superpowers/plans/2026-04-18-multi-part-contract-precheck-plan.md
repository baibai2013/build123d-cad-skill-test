# 多部件 assembly_contract + bbox 预检实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 multi-part 流程在 P2 末尾沉淀整机 `assembly_contract.yaml` + bbox 预检 + 用户确认门；P3 / P4 引用 cross_refs 指导装配与验证。

**Architecture:** 纯文档改动 + test 仓 dryrun 占位。改动 2 个 skill 仓文件（multi-part-playbook.md 加 Step 2e / P3 前置 / P4 Step 4.3 / FM-10~12；layer0-contract.md 追加 Appendix B），新建 1 个 test 目录（tests/18-assembly-contract-dryrun/，含 README + run_J + run_K + structure_check）。Stage C 执行器代码改动**不在本计划**——Playbook 仅要求产出 yaml，执行器按既有 `contract.features[].constraints[]` 遍历机制跑，新增 cross_refs 入口由后续计划决定。

**Tech Stack:** Markdown / YAML（schema 描述） / grep（结构核对） / git

**仓库边界：**
- skill 仓（主改）：`/Users/liyijiang/.agents/skills/build123d-cad/`
- test 仓（dryrun + plan/spec 托管）：`/Users/liyijiang/work/build123d-cad-skill-test/`
- 跨仓提交：各自 commit，各自 push

**Out of Scope（本计划不做，spec §8 已列）：**
- single-part-playbook.md / reference-product-playbook.md 任何改动
- SKILL.md 路由段任何改动
- Layer 1 Stage A/B/C 执行器代码改动
- cross_refs 自动翻译脚本 / bbox 预检精度提升 / schema linter / Joint 自动生成

**Spec 引用：** `docs/superpowers/specs/2026-04-18-multi-part-contract-precheck-design.md`

---

## 文件结构

**修改（skill 仓）：**
- `references/verify/layer0-contract.md` — 末尾追加 `## Appendix B: 整机扩展字段（多部件专用）` 节，描述 parts / cross_refs 两个可选顶层字段
- `references/protocols/multi-part-playbook.md` — 5 处改动：
  1. Phase 总表 P2 行增加 Step 2e 标注
  2. P2 模块末尾插入 `### Step 2e — Layer 0 合同化 + bbox 预检 + 确认门`（含 2e.a / 2e.b / 2e.c 三子步）
  3. P3 前置改 "STEP 齐全 + assembly_contract.yaml 已确认"，P3 内部加 Joint↔cross_refs 映射说明，P3 产出报告样例加 joint_to_crossref.md 行
  4. P4 加 `### Step 4.3 — 整机 Stage C 验证`
  5. "常见失败模式"节追加 FM-10 / FM-11 / FM-12

**新建（test 仓）：**
- `tests/18-assembly-contract-dryrun/README.md` — Scenario J / K 定义 + 运行说明
- `tests/18-assembly-contract-dryrun/run_J.md` — 两关节机械臂 dryrun 占位 + 13 条判据
- `tests/18-assembly-contract-dryrun/run_K.md` — cross_refs 遗漏故意触发 FM-12 占位 + 7 条判据
- `tests/18-assembly-contract-dryrun/structure_check.md` — 5 项结构核对表（提交到最后 Task 10 时写）

---

## Task 1: layer0-contract.md 追加 Appendix B

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/verify/layer0-contract.md`（末尾追加）

- [ ] **Step 1: 确认当前文件末尾位置**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && tail -5 references/verify/layer0-contract.md
```
Expected: 最后一行是 `验证脚本见 scripts/validate/contract_verify.py。`

- [ ] **Step 2: 追加 Appendix B 节**

用 Edit 工具在 `验证脚本见 scripts/validate/contract_verify.py。` 之后追加：

```markdown

---

## Appendix B: 整机扩展字段（多部件专用）

以下两节为 `multi-part-playbook.md` §Phase P2 Step 2e 使用，Single-Part / 参考物流程可缺省。两者均为 **顶层可选字段**，不影响现有 Schema（§2 YAML Schema）。

### parts（顶层，可选数组）

每条装配部件一项：

| 字段 | 必填 | 含义 |
|---|---|---|
| `slug` | 是 | 短名，与 `<part>.py` 文件 stem 对齐 |
| `file` | 是 | `.py` 相对路径（相对 test 仓根） |
| `bbox` | 是 | `{x, y, z}` 三轴包围盒尺寸（最终变体粗估即可，单位 mm） |
| `placement` | 是 | `{anchor: str, offset: [x, y, z]}`，P1 拆解里的大致装配位 |

示例：

```yaml
parts:
  - slug: arm
    file: arm.py
    bbox: {x: 80, y: 20, z: 8}
    placement:
      anchor: "底座 servo horn 中心"
      offset: [0, 0, 6]
```

### cross_refs（顶层，可选数组）

跨部件约束，**类型限定为 Layer 1 Stage C 已支持的 6 种**（见 §5c / `references/verify/layer1-verification.md §Stage C`）：
`inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric`

每条字段参考 §5c 对应 constraint 定义，多一个必填字段 `parts: [slug, slug]` 指明参与约束的部件。

示例：

```yaml
cross_refs:
  - id: axle_center_match
    type: concentric
    parts: [arm, horn]
    feature: "axle_hole"
    tolerance: 0.1
```

**硬规则**：多部件装配 `cross_refs` 条数 ≥ 1；零跨部件关系 = 不应走多部件流程。
```

- [ ] **Step 3: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "^## Appendix B" references/verify/layer0-contract.md
```
Expected: `1`

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "^### parts（顶层，可选数组）\|^### cross_refs（顶层，可选数组）" references/verify/layer0-contract.md
```
Expected: `2`

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/verify/layer0-contract.md && git commit -m "$(cat <<'EOF'
docs(layer0-contract): 追加 Appendix B 整机扩展字段 parts / cross_refs

为 multi-part-playbook P2 Step 2e 产出 assembly_contract.yaml 提供 schema 说明；
类型沿用 Stage C 已支持的 6 种跨特征约束，不新增类型。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: multi-part-playbook.md — 更新 Phase 总表

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md:27`

- [ ] **Step 1: 定位 P2 行**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && sed -n '26,30p' references/protocols/multi-part-playbook.md
```
Expected 当前第 27 行：
```
| P2 部件级建模（每部件 3 变体） | 每部件 3 变体（V1/V2/V3）+ OCP 并排对比 + 自动断言 + 用户选定 | 否 | → P3 |
```

- [ ] **Step 2: 替换 P2 行**

用 Edit：

old_string:
```
| P2 部件级建模（每部件 3 变体） | 每部件 3 变体（V1/V2/V3）+ OCP 并排对比 + 自动断言 + 用户选定 | 否 | → P3 |
```

new_string:
```
| P2 部件级建模（每部件 3 变体） | 每部件 3 变体（V1/V2/V3）+ OCP 并排对比 + 自动断言 + 用户选定 + Step 2e（assembly_contract.yaml + precheck_bbox.md + 确认门 ✋） | 否 | → P3 |
```

- [ ] **Step 3: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "Step 2e" references/protocols/multi-part-playbook.md
```
Expected: `1`（本任务刚加的一处；后续 Task 3 会让这个计数涨到 ≥3）

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(multi-part): P2 总表标注 Step 2e 产出

Step 2e 细节由后续 commit 加入 P2 模块正文。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: multi-part-playbook.md — P2 模块末尾插入 Step 2e 详细段

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md`（P2 回报契约块之后，`---` 分隔线之前；约 L183 附近）

- [ ] **Step 1: 定位插入点**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && sed -n '180,187p' references/protocols/multi-part-playbook.md
```
Expected 看到：
```
- [ask] 全部部件已选定，继续进 P3？
下一步：等用户确认 → Phase P3
```
...然后 ``` 结束 / 空行 / `---` / 空行 / `## Phase P3: 装配 / 关节`

记录 `---` 所在行号（P3 之前那一条分隔线），下一步插入在它前面。

- [ ] **Step 2: 插入 Step 2e 详细段**

用 Edit：

old_string（包含 P2 回报契约块的结尾三反引号 + 空行 + 分隔线 + 空行 + P3 标题）：
```
- [ask] 全部部件已选定，继续进 P3？
下一步：等用户确认 → Phase P3
```

---

## Phase P3: 装配 / 关节
```

new_string：
````
- [ask] Step 2d 全部部件已选定，继续 Step 2e 合同化？
下一步：进入 Step 2e
```

### Step 2e — Layer 0 合同化 + bbox 预检 + 确认门 ✋

**前置**：
- [x] Step 2d 每部件最终变体已选定并导出 STEP
- [x] P1 需求拆解报告"装配关系"节内容可复用

**本步产出**：
- `tests/<test>/assembly_contract.yaml`（parts + cross_refs，schema 见 `references/verify/layer0-contract.md` §Appendix B）
- `tests/<test>/precheck_bbox.md`（两两 AABB 重叠粗检报告）
- 用户确认门 ✋

**命令模板**：

#### Step 2e.a — 汇总 `assembly_contract.yaml`

- parts 节：每个部件最终变体的 bbox（粗估 OK）+ placement（anchor 来自 P1 拆解，offset 来自变体选定后的大致装配位）
- cross_refs 节：从 P1 需求拆解报告"装配关系"节翻译，类型从 Stage C 已支持的 6 种取：`inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric`
- **硬规则**：cross_refs 条数 ≥ 1，且不少于 P1 拆解里列出的装配关系条数（漏翻即 FM-12）

示例骨架：

```yaml
version: "1.0"
meta:
  name: <asm_name>
  source: multi-part-playbook P2 Step 2e
  date: YYYY-MM-DD
globals:
  unit: mm
parts:
  - slug: arm
    file: arm.py
    bbox: {x: 80, y: 20, z: 8}
    placement:
      anchor: "底座 servo horn 中心"
      offset: [0, 0, 6]
cross_refs:
  - id: axle_center_match
    type: concentric
    parts: [arm, horn]
    feature: "axle_hole"
    tolerance: 0.1
features: []
param_map: {}
variants: []
```

#### Step 2e.b — bbox 预检

**算法**：对 `parts` 节每对 (i, j) 做 AABB 三轴重叠判定：

```
x 轴重叠 = (bbox_i.x + bbox_j.x) / 2 > |offset_i.x - offset_j.x|
(y / z 同理)
三轴都重叠 → ⚠ 疑似碰撞；任一轴不重叠 → ✅ 无碰撞风险
```

疑似碰撞**不阻断**——标注即可；P3 装配后由 `do_children_intersect()` 做权威判定。

**产出** `precheck_bbox.md` 骨架：

```markdown
# P2 bbox 预检（简化 AABB）

配对数：N
疑似碰撞：K

## <part_a> ↔ <part_b>
- placement 距离：(dx, dy, dz)
- 三轴重叠：x ✓/✗  y ✓/✗  z ✓/✗
- 结论：✅ 无碰撞风险 / ⚠ 疑似碰撞，P3 装配时 <具体处理建议>
```

#### Step 2e.c — 用户确认门 ✋

**AI 回报契约**：

```
Step 2e 产出报告
引自 multi-part-playbook.md §Phase P2 / Step 2e — Layer 0 合同化 + bbox 预检 + 确认门 ✋：
  "Step 2e.c 用户确认门 ✋"
- [x] tests/<test>/assembly_contract.yaml       (parts: N，cross_refs: M)
- [x] tests/<test>/precheck_bbox.md             (疑似碰撞 K 处)
请 review 两份产物，回：
  - "ok 进 P3"：继续装配
  - "改 <具体>"：回 P2 对应 Step（2a/2b/2d）调整或补 cross_refs
下一步：等用户回执
```

**重要**：未收到用户"ok 进 P3"之前不得写任何 P3 装配代码；收到"改"字样回退 P2 对应子步骤。

---

## Phase P3: 装配 / 关节
````

- [ ] **Step 3: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "Step 2e" references/protocols/multi-part-playbook.md
```
Expected: `≥ 5`（总表 1 + 2e 标题 1 + 2e.a / 2e.b / 2e.c 各 1 + 回报契约 1）

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "assembly_contract.yaml" references/protocols/multi-part-playbook.md
```
Expected: `≥ 2`

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(multi-part): P2 末尾新增 Step 2e 合同化 + bbox 预检 + 确认门

Step 2e.a 汇总 assembly_contract.yaml（parts + cross_refs）；
Step 2e.b AABB 三轴重叠预检输出 precheck_bbox.md；
Step 2e.c 用户确认门 ✋，未确认不得进 P3。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: multi-part-playbook.md — P3 前置 + Joint↔cross_refs 映射

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md` P3 模块

- [ ] **Step 1: 更新 P3 前置行**

用 Edit：

old_string:
```
## Phase P3: 装配 / 关节

**前置**：
- [x] P2 所有部件已各自选定变体并导出 STEP
```

new_string:
```
## Phase P3: 装配 / 关节

**前置**：
- [x] P2 所有部件已各自选定变体并导出 STEP
- [x] P2 Step 2e 已产出 `assembly_contract.yaml` + `precheck_bbox.md` 并通过用户确认门
```

- [ ] **Step 2: 在 Step 3a 之前插入 cross_refs 映射说明**

用 Edit：

old_string:
```
**命令模板**：

### Step 3a — 装配方案脑图（先讨论，不写装配代码）
```

new_string:
```
**命令模板**：

**Joint ↔ cross_refs 映射规则**：Step 3a 脑图和 Step 3b 装配代码必须把 `assembly_contract.yaml` 的每条 cross_ref 映射到具体 Joint 实现。参考对应关系：

| cross_ref.type | Joint 推荐实现 |
|---|---|
| `concentric` | `RigidJoint.concentric(edge_or_face_a, edge_or_face_b)` 或沿同轴 `RigidJoint` + Location 对齐 |
| `inter_dist(d=D)` | `RigidJoint(offset=Location((dx, dy, dz)))`，其中 `|offset|` 对齐 D；若为关节动态距离用 `LinearJoint` 行程覆盖 D |
| `ordering` | 选择装配基准时沿指定 axis 保证 part 顺序；`RigidJoint` offset 符号检查 |
| `colinear` | `RigidJoint` 的参考边方向对齐 |
| `same_face` | 两部件在同一基准面贴合 |
| `symmetric_pair` | 成对 `RigidJoint` 左右镜像 |

映射结果落到 `tests/<test>/joint_to_crossref.md`（简单表格，非严格 schema）。

### Step 3a — 装配方案脑图（先讨论，不写装配代码）
```

- [ ] **Step 3: 更新 P3 产出报告样例**

用 Edit：

old_string:
```
- [x] do_children_intersect() = False            (无碰撞)
- [skip] 爆炸动画                                (reason: 仅 3 部件，装配关系已直观可见)
- [skip] Step 3c 仿真规划                        (reason: P1 勾选"无需仿真")
下一步：Phase P4
```

new_string:
```
- [x] do_children_intersect() = False            (无碰撞)
- [x] tests/<test>/joint_to_crossref.md          (Joint 覆盖 assembly_contract.cross_refs 全部 M 条)
- [skip] 爆炸动画                                (reason: 仅 3 部件，装配关系已直观可见)
- [skip] Step 3c 仿真规划                        (reason: P1 勾选"无需仿真")
下一步：Phase P4
```

- [ ] **Step 4: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "assembly_contract.yaml" references/protocols/multi-part-playbook.md
```
Expected: `≥ 3`（Task 3 产出 2 处，本任务 P3 前置 + Step 2e 引用各 1）

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "joint_to_crossref.md" references/protocols/multi-part-playbook.md
```
Expected: `≥ 2`

- [ ] **Step 5: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(multi-part): P3 前置加 assembly_contract 确认 + Joint↔cross_refs 映射

P3 必须引用 Step 2e 产出的 cross_refs 指导 Joint 设计；
产出 joint_to_crossref.md 做 cross_ref → Joint 映射表。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: multi-part-playbook.md — P4 新增 Step 4.3 整机 Stage C 验证

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md` P4 模块（Step 4c 之后，P4 回报契约之前）

- [ ] **Step 1: 更新 P4 本步产出清单**

用 Edit：

old_string:
```
**本步产出**：
- `<asm>.step`（装配体 STEP 导出，主流 CAD 通用格式）
- `<asm>.stl`（可选，3D 打印用）
- Layer 1 几何验证通过（装配体 BRep 有效 / 体积合理 / STEP 精度回读）
- （可选）Layer 2 装配体视觉验证（仅参考物型装配；非参考物型可 `[skip]`）
```

new_string:
```
**本步产出**：
- `<asm>.step`（装配体 STEP 导出，主流 CAD 通用格式）
- `<asm>.stl`（可选，3D 打印用）
- Layer 1 几何验证通过（装配体 BRep 有效 / 体积合理 / STEP 精度回读）
- **Step 4.3 整机 Stage C 验证**：对装配体运行 `assembly_contract.cross_refs`
- （可选）Layer 2 装配体视觉验证（仅参考物型装配；非参考物型可 `[skip]`）
```

- [ ] **Step 2: 在 Step 4c 之后插入 Step 4.3 段**

用 Edit：

old_string:
```
**Layer 2 失败反馈**：IoU < 0.85 时按 `references/verify/feedback-diagnosis.md` 分根因回退：
- 根因 A（数据源错）→ 回补 `reference-product-playbook.md` §R2/R3
- 根因 B（合同错）→ 回 `reference-product-playbook.md` §R3.5 改 contract.yaml
- 根因 C（代码错）→ 回 P2 改对应部件，或回 P3 改装配/关节
- 修复上限：L1×3 + L2×2 + 跨层×2 = 总计 ≤ 5 轮

**AI 回报契约**：
```

new_string:
````
**Layer 2 失败反馈**：IoU < 0.85 时按 `references/verify/feedback-diagnosis.md` 分根因回退：
- 根因 A（数据源错）→ 回补 `reference-product-playbook.md` §R2/R3
- 根因 B（合同错）→ 回 `reference-product-playbook.md` §R3.5 改 contract.yaml
- 根因 C（代码错）→ 回 P2 改对应部件，或回 P3 改装配/关节
- 修复上限：L1×3 + L2×2 + 跨层×2 = 总计 ≤ 5 轮

### Step 4.3 — 整机 Stage C 验证

**输入**：
- 装配体（`assembly.compound()`）
- `tests/<test>/assembly_contract.yaml`（P2 Step 2e 产出）

**执行**：对 `cross_refs` 每条，按其 type 提取相关 parts 的 face / edge / point，套用 Layer 1 Stage C 已支持的判定逻辑（见 `references/verify/layer1-verification.md §Stage C`）。6 种类型逐条跑：`inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric`。

**输出**：`tests/<test>/output/stage_c_assembly.md` — 每条 cross_ref 一行 PASS / FAIL + 实测值 + 容差。

**硬规则**：
- 任一 cross_ref FAIL → P4 不通过（按 feedback-diagnosis 走根因回退）
- `do_children_intersect()` 仍保留作几何侵入兜底（P3 已跑）；Stage C 是语义约束层，两者互补不替代

**执行器集成**：`cross_refs` 复用现有 Stage C 判定代码，scope 变为 parts 而非 features；执行器入口扩展属 Out of Scope（见本计划顶部），本 Step 的 AI 行为约定产出 Markdown 报告即可——如本次对话尚无集成好的执行器，AI 在 dryrun 下用人工逐条判定 + 手写 stage_c_assembly.md 也可。

**AI 回报契约**：
```

**AI 回报契约**：
````

- [ ] **Step 3: 更新 P4 回报报告样例**

用 Edit：

old_string:
```
- [x] Layer 1: BRep 有效 / 体积合理 / STEP 精度 全过
- [skip] Layer 2 视觉验证                  (reason: 非参考物型装配)
多部件流程 P1~P4 完成。
```

new_string:
```
- [x] Layer 1: BRep 有效 / 体积合理 / STEP 精度 全过
- [x] Step 4.3 整机 Stage C: cross_refs 全部 PASS (tests/<test>/output/stage_c_assembly.md)
- [skip] Layer 2 视觉验证                  (reason: 非参考物型装配)
多部件流程 P1~P4 完成。
```

- [ ] **Step 4: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "Step 4.3" references/protocols/multi-part-playbook.md
```
Expected: `≥ 3`（本步产出 1 + 标题 1 + 回报 1）

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -c "stage_c_assembly.md" references/protocols/multi-part-playbook.md
```
Expected: `≥ 2`

- [ ] **Step 5: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(multi-part): P4 新增 Step 4.3 整机 Stage C 验证

对装配体运行 assembly_contract.cross_refs；
复用 Layer 1 Stage C 已支持的 6 种判定，不新增类型；
任一 FAIL 触发 feedback-diagnosis 根因回退。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: multi-part-playbook.md — 追加 FM-10 / FM-11 / FM-12

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/multi-part-playbook.md` — 末尾"常见失败模式"节

- [ ] **Step 1: 定位失败模式节**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -n "^## 常见失败模式" references/protocols/multi-part-playbook.md
```
Expected: 返回一行，形如 `381:## 常见失败模式`

- [ ] **Step 2: 替换该节**

用 Edit：

old_string:
```
## 常见失败模式

（等 test 沉淀 / TBD。跨 Playbook 通用的 Quote-back 违规见 `protocols/README.md`。）
```

new_string:
```
## 常见失败模式

### FM-10：缺 assembly_contract 就进 P3

- **诊断**：P3 开始但 `tests/<test>/assembly_contract.yaml` 不存在，或 Step 2e 确认门未执行
- **修复**：回 P2 Step 2e 补齐 assembly_contract.yaml + precheck_bbox.md，重走确认门，收到"ok 进 P3"后才继续 P3

### FM-11：bbox 预检疑似碰撞未记录

- **诊断**：`precheck_bbox.md` 有 ⚠ 标记的部件对，但 P3 `joint_to_crossref.md` 对该对没有对应的 Joint 策略说明
- **修复**：P3 装配后针对该对跑 `do_children_intersect(include_children=[part_a, part_b])`；若真碰撞，回 `assembly_contract.yaml` 补对应的 `inter_dist(parts=[...], d_min=...)` 约束

### FM-12：cross_refs 覆盖不全

- **诊断**：P1 需求拆解报告"装配关系"节列的关系数 > `assembly_contract.cross_refs` 条数；或关系描述有但 `cross_refs` 缺失对应 id
- **修复**：回 Step 2e.a 补全翻译；**硬下限** `cross_refs` ≥ 1 条，且不少于 P1 装配关系条数

跨 Playbook 通用的 Quote-back 违规见 `protocols/README.md`。
```

- [ ] **Step 3: 结构核对**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && grep -cE "^### FM-1[012]" references/protocols/multi-part-playbook.md
```
Expected: `3`

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git add references/protocols/multi-part-playbook.md && git commit -m "$(cat <<'EOF'
docs(multi-part): 追加 FM-10 / FM-11 / FM-12 三条失败模式

FM-10 缺 assembly_contract；FM-11 bbox 预检疑似碰撞未记录；FM-12 cross_refs 覆盖不全。
与 Step 2e / P3 Joint 映射 / cross_refs 硬下限联动。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: test 仓新建 tests/18-assembly-contract-dryrun/ + README

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/README.md`

- [ ] **Step 1: 确认目录不存在，创建目录**

Run:
```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && ls tests/18-assembly-contract-dryrun 2>&1 | head -3
```
Expected: `ls: cannot access 'tests/18-assembly-contract-dryrun'`（不存在）

Run:
```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && mkdir -p tests/18-assembly-contract-dryrun
```

- [ ] **Step 2: 写 README.md**

Write `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/README.md`:

```markdown
# test 18 — multi-part assembly_contract + bbox 预检 dryrun

**目的**：验证 `multi-part-playbook.md` 的 Step 2e / P3 前置 / P4 Step 4.3 / FM-10~12 在真对话里能被 AI 正确触发与执行。

**对应 spec**：`docs/superpowers/specs/2026-04-18-multi-part-contract-precheck-design.md`
**对应 plan**：`docs/superpowers/plans/2026-04-18-multi-part-contract-precheck-plan.md`

## Scenario 清单

| Scenario | 需求 | 验证目标 |
|---|---|---|
| J | 做带 SG90 舵机的两关节机械臂（≥2 部件） | P2 末尾产 assembly_contract + precheck_bbox；P3 引用 cross_refs；P4 Step 4.3 Stage C PASS |
| K | 故意让 P1 拆解列 3 条装配关系，但 AI Step 2e.a 只翻译 2 条 | FM-12 触发，AI 回补 |

## 运行方式

两个 Scenario 都在**新 Claude 会话**里跑，模型 = Opus 4.6 或 4.7，skill 装好 build123d-cad。

对每个 Scenario：
1. 输入对应起始 prompt（见 run_X.md 顶部 "起始 prompt" 块）
2. 完整回复粘到 `run_X.md` 对应占位
3. 按 `run_X.md` 底部的判据清单逐条打勾 / 写反例

## 判据规则

- ✅ = 判据满足
- ❌ = 判据失败（必须补一句说明失败现象）
- N/A = 本 Scenario 该判据不适用（附原因）

所有判据 ≥ 80% 通过 = Scenario pass；任何一条 ❌ = Scenario fail，回 spec / plan 查根因。

## 后续

结果由 `structure_check.md` 汇总结构核对 + Scenario J/K 结论。
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && git add tests/18-assembly-contract-dryrun/README.md && git commit -m "$(cat <<'EOF'
test(18): 新增 multi-part assembly_contract dryrun 目录 + README

Scenario J (两关节机械臂) + K (FM-12 故意触发) 占位。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: run_J.md — Scenario J 占位 + 13 条判据

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/run_J.md`

- [ ] **Step 1: 写 run_J.md**

Write `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/run_J.md`:

```markdown
# Scenario J — 两关节机械臂 assembly_contract dryrun

## 起始 prompt

```
做一个带 SG90 舵机的两关节机械臂：底座 + 大臂 + 小臂。
大臂长 80mm，小臂长 60mm，都是 20×8 mm 截面。
底座 50×50×15 mm，顶面有 SG90 舵机槽。
关节 1（底座↔大臂）绕 Z 转动，关节 2（大臂↔小臂）绕 Y 转动。
```

## AI 完整回复

<!-- 粘贴新会话里 AI 的完整回复到这里，从 "Phase P1 产出报告" 开始到多部件流程 P1~P4 完成 -->

（未运行占位）

---

## 判据清单（13 条）

### P1 判据（2 条）

- [ ] J1. P1 产出报告首行含 Quote-back（`引自 multi-part-playbook.md §Phase P1 / ...`）
- [ ] J2. 需求拆解报告"装配关系"节列出 ≥2 条装配关系（至少底座↔大臂、大臂↔小臂）

### P2 判据（6 条）

- [ ] J3. P2 每部件 3 变体都有（底座 × 3 + 大臂 × 3 + 小臂 × 3）
- [ ] J4. Step 2d 每部件用户选定变体后，Step 2e 被触发（不是直接跳 P3）
- [ ] J5. Step 2e 产出 `assembly_contract.yaml`，含 `parts` 节（条数 = 部件数）+ `cross_refs` 节（条数 ≥ P1 装配关系数）
- [ ] J6. `assembly_contract.yaml` 的 `cross_refs.type` 只在 6 种白名单里（`inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric`）
- [ ] J7. Step 2e 产出 `precheck_bbox.md`，每对都有三轴重叠判定 + 结论（✅ / ⚠）
- [ ] J8. Step 2e 产出报告首行含 Quote-back，**AI 停下等用户确认"ok 进 P3"**（而非自动跑 P3）

### P3 判据（3 条）

- [ ] J9. P3 前置检查显式列出"assembly_contract.yaml 已确认"
- [ ] J10. P3 产出 `joint_to_crossref.md`，每条 cross_ref 都有对应 Joint 实现映射
- [ ] J11. `do_children_intersect() = False`（或如有 ⚠ 疑似碰撞，P3 有对应处理说明）

### P4 判据（2 条）

- [ ] J12. P4 执行 Step 4.3 整机 Stage C 验证，产出 `output/stage_c_assembly.md`
- [ ] J13. Step 4.3 每条 cross_ref 都有 PASS / FAIL 判定 + 实测值

## 总结

- 通过条数：_/13
- 结论：（待运行）
- 失败根因（如有）：
```

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && git add tests/18-assembly-contract-dryrun/run_J.md && git commit -m "$(cat <<'EOF'
test(18): Scenario J 两关节机械臂占位 + 13 条判据清单

覆盖 P1/P2/P3/P4 全流程，含 Step 2e assembly_contract 产出 / 用户确认门 /
cross_refs 类型白名单 / P3 Joint 映射 / P4 Step 4.3 Stage C 验证。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: run_K.md — Scenario K 占位 + 7 条判据

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/run_K.md`

- [ ] **Step 1: 写 run_K.md**

Write `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/run_K.md`:

```markdown
# Scenario K — cross_refs 遗漏触发 FM-12

## 起始 prompt

```
做一个三段机械臂：底座 + 大臂 + 小臂 + 夹爪（共 4 部件）。
装配关系：
1. 底座↔大臂：底座顶面 SG90 槽 concentric 大臂根部轴孔
2. 大臂↔小臂：大臂末端孔 concentric 小臂根部轴
3. 小臂↔夹爪：小臂末端孔 concentric 夹爪根部轴
4. 大臂↔小臂：关节 2 角度限位使 小臂 ordering 相对大臂在 z 轴方向
```

**人工诱导**：在 Step 2e.a 开始前，追加一条提示：`"请在 assembly_contract.cross_refs 里**只写前 2 条关系**（底座↔大臂、大臂↔小臂 concentric），跳过后面 2 条"`

## AI 完整回复

<!-- 粘贴新会话里 AI 的完整回复到这里 -->

（未运行占位）

---

## 判据清单（7 条）

### 诱导执行（2 条）

- [ ] K1. AI 在 Step 2e.a 按人工诱导**只写了 2 条 cross_refs**（验证诱导生效）
- [ ] K2. `precheck_bbox.md` 仍正常产出（bbox 预检独立于 cross_refs 覆盖率）

### FM-12 触发（3 条）

- [ ] K3. AI 在 Step 2e 结束前或 P3 开始前**自检发现** P1 装配关系数（4）> cross_refs 条数（2），触发 FM-12
- [ ] K4. AI 回报里显式提到"FM-12"或"cross_refs 覆盖不全"
- [ ] K5. AI **回 Step 2e.a 补全** cross_refs 到 4 条（小臂↔夹爪 + 大臂↔小臂 ordering）

### 回补后收敛（2 条）

- [ ] K6. 补全后 cross_refs.type 仍在 6 种白名单里
- [ ] K7. 补全后用户确认门重走（AI 再次出 Step 2e 产出报告并等 "ok 进 P3"）

## 总结

- 通过条数：_/7
- 结论：（待运行）
- 失败根因（如有）：
```

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && git add tests/18-assembly-contract-dryrun/run_K.md && git commit -m "$(cat <<'EOF'
test(18): Scenario K FM-12 触发占位 + 7 条判据清单

故意让 AI 在 Step 2e.a 只翻译 2 条 cross_refs（缺 2 条）；
期望 AI 自检触发 FM-12，回 Step 2e.a 补全并重走确认门。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: 结构核对 + structure_check.md + 双仓 push

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/structure_check.md`

- [ ] **Step 1: 跑全部结构核对命令收集结果**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && echo "=== 1. Appendix B 标题 ===" && grep -c "^## Appendix B" references/verify/layer0-contract.md && echo "=== 2. parts/cross_refs 子标题 ===" && grep -cE "^### parts|^### cross_refs" references/verify/layer0-contract.md && echo "=== 3. Step 2e 出现次数 ===" && grep -c "Step 2e" references/protocols/multi-part-playbook.md && echo "=== 4. assembly_contract.yaml 出现次数 ===" && grep -c "assembly_contract.yaml" references/protocols/multi-part-playbook.md && echo "=== 5. joint_to_crossref.md 出现次数 ===" && grep -c "joint_to_crossref.md" references/protocols/multi-part-playbook.md && echo "=== 6. Step 4.3 出现次数 ===" && grep -c "Step 4.3" references/protocols/multi-part-playbook.md && echo "=== 7. stage_c_assembly.md 出现次数 ===" && grep -c "stage_c_assembly.md" references/protocols/multi-part-playbook.md && echo "=== 8. FM-10/11/12 ===" && grep -cE "^### FM-1[012]" references/protocols/multi-part-playbook.md
```

Expected：
```
=== 1. === 1
=== 2. === 2
=== 3. === ≥ 5
=== 4. === ≥ 3
=== 5. === ≥ 2
=== 6. === ≥ 3
=== 7. === ≥ 2
=== 8. === 3
```

- [ ] **Step 2: 写 structure_check.md**

Write `/Users/liyijiang/work/build123d-cad-skill-test/tests/18-assembly-contract-dryrun/structure_check.md`:

```markdown
# test 18 结构核对

运行日期：YYYY-MM-DD（跑 Task 10 时填）
对应 spec §6.1 / plan Task 10。

## 检查结果

| # | 检查项 | 期望 | 实际 | 结果 |
|---|---|---|---|---|
| 1 | `grep -c "^## Appendix B" layer0-contract.md` | 1 | _ | _ |
| 2 | `grep -cE "^### parts\|^### cross_refs" layer0-contract.md` | 2 | _ | _ |
| 3 | `grep -c "Step 2e" multi-part-playbook.md` | ≥5 | _ | _ |
| 4 | `grep -c "assembly_contract.yaml" multi-part-playbook.md` | ≥3 | _ | _ |
| 5 | `grep -c "joint_to_crossref.md" multi-part-playbook.md` | ≥2 | _ | _ |
| 6 | `grep -c "Step 4.3" multi-part-playbook.md` | ≥3 | _ | _ |
| 7 | `grep -c "stage_c_assembly.md" multi-part-playbook.md` | ≥2 | _ | _ |
| 8 | `grep -cE "^### FM-1[012]" multi-part-playbook.md` | 3 | _ | _ |

## skill 仓 commits

（按 Task 1~6 顺序填 skill 仓 git log --oneline 最近 6 条）

## test 仓 commits

（按 Task 7~10 顺序填 test 仓 git log --oneline 最近 4~5 条）

## 行为验证（Scenario J / K）待执行

按 `README.md` 运行方式，新 Claude 会话里跑 run_J.md / run_K.md，回填判据。

## 结论

（结构核对通过或失败，填入结论）
```

实际运行 Step 1 后，用真实数字替换每个 `_`，并在"实际"列写当前 grep 返回值，"结果"列写 ✅ / ❌。

- [ ] **Step 3: 填入真实 skill 仓 commits**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git log --oneline -n 6
```

把最近 6 条 oneline 填到 structure_check.md "skill 仓 commits" 节。

- [ ] **Step 4: 填入真实 test 仓 commits**

Run:
```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && git log --oneline -n 5
```

把最近 5 条 oneline 填到 structure_check.md "test 仓 commits" 节（Task 10 本 commit 尚未建，所以这步先记前 4 条，Task 10 commit 后在 structure_check.md 里再补 1 条——但为避免额外 commit，可先 Write 时留 "（本提交）tests/18/structure_check.md" 占位）。

- [ ] **Step 5: Commit structure_check.md**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test && git add tests/18-assembly-contract-dryrun/structure_check.md && git commit -m "$(cat <<'EOF'
test(18): 新增 structure_check.md 汇总 8 项结构核对 + commit 清单

8 项结构核对全通过；Scenario J / K 行为验证待用户在新会话执行。

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: 双仓 push（需用户确认后执行）**

**本步不自动推送**，停下来让用户确认再执行。提示用户 review：

```
双仓本地 commits 清单：
- skill 仓（/Users/liyijiang/.agents/skills/build123d-cad）最近 6 条
- test 仓（/Users/liyijiang/work/build123d-cad-skill-test）最近 5 条

是否全部推送到 origin/main？
```

收到用户"push"或"ok push"后执行：

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad && git push origin main && cd /Users/liyijiang/work/build123d-cad-skill-test && git push origin main
```

Expected: 两条 push 都成功，输出类似 `... main -> main`。

---

## 总结

10 个任务全部完成后，交付物：

1. skill 仓：layer0-contract.md 加 Appendix B；multi-part-playbook.md 加 Step 2e / P3 前置 / Step 4.3 / FM-10~12
2. test 仓：tests/18-assembly-contract-dryrun/ 含 README + run_J + run_K + structure_check
3. 8 项结构核对全通过
4. 双仓 push 到 remote（用户确认后）

**行为验证（Scenario J / K）**不在本计划 Task 内，由用户在新 Claude 会话执行后回填 run_J.md / run_K.md 判据。
