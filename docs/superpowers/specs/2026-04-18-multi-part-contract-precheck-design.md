# 多部件 assembly_contract + bbox 预检设计

**日期**：2026-04-18
**范围**：`references/protocols/multi-part-playbook.md` 新增 Step 2e / P3 前置 / P4 Step 4.3；`references/verify/layer0-contract.md` 追加 Appendix B
**不改**：SKILL.md 路由段 / single-part-playbook.md / reference-product-playbook.md / Layer 1 Stage A/B/C 执行器代码 / assets/
**驱动问题**：多部件流程 P2 产出独立部件后直接进 P3 装配，缺少"整机真实来源"——装配关系散在 P1 拆解口头描述里，P3 Joint 靠记忆、P4 验证没有依据。同时 P2→P3 间缺快速"位置算错"检查，碰撞要拖到 P4 才发现。
**核心机制**：P2 末尾合同化 + bbox 预检 + 用户确认门；P3 引用 cross_refs 指导 Joint；P4 Stage C 对整机跑已声明约束

---

## 1. 架构

**新增/改动 3 处**：

1. **P2 末尾新增 Step 2e**：Layer 0 合同化 + bbox 预检 + 用户确认门 ✋
   - 产出 `tests/<test>/assembly_contract.yaml`（parts + cross_refs）
   - 产出 `tests/<test>/precheck_bbox.md`（两两 AABB 重叠检查）
   - 用户 review 后决定进 P3 / 回 P2 调

2. **P3 前置**从"STEP 齐全"改为"STEP + assembly_contract.yaml 已确认"
   - P3 装配设计 Joint 时，cross_refs 是目标清单
   - P3 末尾产出 `joint_to_crossref.md` 映射表

3. **P4 Layer 1 Stage C 验证**：新增 Step 4.3 对装配体跑 assembly_contract.cross_refs
   - 执行器零代码改动，复用现有 Stage C

**不动**：
- Layer 1 Stage C constraint 执行器（已支持 `inter_dist` / `ordering` / `colinear` / `same_face` / `symmetric_pair` / `concentric` 6 种跨特征类型）
- SKILL.md 路由段
- single-part-playbook.md（parts / cross_refs 字段缺省即可）
- reference-product-playbook.md

**核心价值**：
- bbox 预检在 P2 末尾 catch "位置算错"类错误，不拖到 P4 发现才回退
- cross_refs 在 P2 就落到合同里，P3 装配有目标、P4 验证有依据，三阶段共享同一真实来源

## 2. Step 2e 结构

Step 2e 在 P2 末尾插入，紧接 2d（三变体用户选定）之后、进 P3 之前。三子步：

### 2e.a — 汇总 `assembly_contract.yaml`

**输入**：
- 每个部件最终变体的 `<part>.py`（取 bbox + 关键参数）
- P1 需求拆解报告里的"部件间关系"段

**产出结构**（扩展现有 layer0-contract schema，所有新增字段顶层可选）：

```yaml
version: "1.0"
meta:
  name: servo_arm_assembly
  source: multi-part-playbook P2 Step 2e
  date: 2026-04-18

globals:
  unit: mm

parts:                               # 新增可选顶层
  - slug: arm
    file: arm.py
    bbox: {x: 80, y: 20, z: 8}       # 最终变体的 bbox（粗估 OK）
    placement:
      anchor: "底座 servo horn 中心"
      offset: [0, 0, 6]
  - slug: horn
    file: horn.py
    bbox: {x: 20, y: 20, z: 5}
    placement:
      anchor: "servo 轴"
      offset: [0, 0, 0]

cross_refs:                          # 新增可选顶层
  - id: arm_above_horn
    type: ordering
    parts: [arm, horn]
    axis: z
    direction: "arm > horn"
    tolerance: 0.5
  - id: axle_center_match
    type: concentric
    parts: [arm, horn]
    feature: "axle_hole"
    tolerance: 0.1

features: []                         # Single-Part 用的 per-part 特征这里留空或不写
param_map: {}
variants: []                          # 整机不做变体
```

**规则**：
- `parts` 节每条对应一个 `<part>.py`
- `cross_refs.type` 限定 Stage C 已支持的 6 种
- cross_refs 硬下限：**≥1 条**（零跨部件关系 = 不该走多部件流程）

### 2e.b — bbox 预检

**算法**：AABB 重叠，对 `parts` 节每对 (i, j) 算三轴重叠：

```
三轴重叠 = (bbox_i.x + bbox_j.x)/2 > |placement_i.offset.x - placement_j.offset.x|
         AND 同理 y AND 同理 z
```

任一轴不重叠 → 安全。三轴都重叠 → 标 ⚠ "疑似碰撞"。

**产出** `precheck_bbox.md`：

```markdown
# P2 bbox 预检（简化 AABB）

配对数：3
疑似碰撞：1

## arm ↔ horn
- placement 距离：(0, 0, 6)
- 三轴重叠：x ✓  y ✓  z ✗
- 结论：✅ 无碰撞风险

## arm ↔ base
- placement 距离：(0, 0, 14)
- 三轴重叠：x ✓  y ✓  z ✗
- 结论：✅

## horn ↔ base
- placement 距离：(0, 0, 8)
- 三轴重叠：x ✓  y ✓  z ✓
- 结论：⚠ 疑似碰撞，P3 装配时检查是否 horn 应埋进 base
```

**疑似碰撞不阻断**——标注即可。P3 装配后由 `do_children_intersect()` 做权威判定。

### 2e.c — 用户确认门 ✋

AI 汇报格式：

```
Step 2e 产出报告
引自 multi-part-playbook.md §Phase P2 / Step 2e：
  "Step 2e 末尾必须等用户确认 assembly_contract.yaml 和 precheck_bbox.md"
- [x] tests/<test>/assembly_contract.yaml（parts: N，cross_refs: M）
- [x] tests/<test>/precheck_bbox.md（疑似碰撞 K 处）
请 review 两份产物，回：
  - "ok 进 P3"：继续装配
  - "改 <具体>"：回 P2 对应 Step 调整
下一步：等用户回执
```

## 3. P3 / P4 集成点

### 3.1 P3 前置变更

**当前**："所有部件 STEP 齐全"
**改为**："所有部件 STEP 齐全 + `assembly_contract.yaml` 已通过 Step 2e 用户确认"

**P3 内部新增一句**：
> P3 装配设计 Joint 时，先 Read `assembly_contract.yaml` 的 cross_refs 节。每条 cross_ref 对应一个装配约束目标，Joint 方案需对齐（例：`concentric` 对应 `RigidJoint` 沿同轴、`inter_dist(d=10)` 对应 `LinearJoint` 行程包含该距离）。

**P3 末尾产出报告**新增：
```
- [x] Joint 方案覆盖 cross_refs 全部 N 条（映射表见 tests/<test>/joint_to_crossref.md）
```

`joint_to_crossref.md` 简单映射表（非严格 schema）：

```markdown
| cross_ref.id | Joint 实现 |
|---|---|
| arm_above_horn | RigidJoint(arm, offset=Location((0,0,6))) |
| axle_center_match | RigidJoint.concentric(arm.hole, horn.axle) |
```

### 3.2 P4 新增 Step 4.3 整机 Stage C 验证

```
Step 4.3 整机 Stage C 验证
引自 multi-part-playbook.md §Phase P4 / Step 4.3：
  "对装配体运行 assembly_contract.cross_refs，Stage C 执行器已支持全部 6 种类型"
- 输入：装配体（Compound）+ assembly_contract.yaml
- 执行：对每条 cross_ref 提取对应 part 的 face/edge/point，按 type 跑 Stage C
- 输出：tests/<test>/output/stage_c_assembly.md（PASS/FAIL per cross_ref）
```

**硬规则**：
- cross_refs 任一 FAIL → P4 不通过
- `do_children_intersect()` 仍保留（几何侵入是 Stage A/B 层，cross_refs 是语义约束层，互补不替代）

### 3.3 Layer 1 Stage C 执行器变更

**约束类型代码零改动**，仅新增一个顶层入口。Stage C 现状：遍历 `contract.features[].constraints[]`。
**集成方式**：Stage C 执行器新增一个入口，接受 `cross_refs` 作为顶层 constraint 列表（scope = parts 而非 features），6 种类型的判定逻辑直接复用 per-feature 分支，不新增类型、不改已有判定代码。

## 4. schema 扩展（`references/verify/layer0-contract.md`）

在现有 schema 文档末尾追加 Appendix B，不改现有字段：

```markdown
## Appendix B: 整机扩展字段（多部件专用）

以下两节为 Multi-Part Playbook P2 Step 2e 使用，Single-Part / 参考物流程可缺省。

### parts（顶层，可选数组）
每条装配部件一项：
- slug（必填）：短名，与 `<part>.py` 文件 stem 对齐
- file（必填）：`.py` 相对路径
- bbox（必填）：{x, y, z}，最终变体的包围盒（粗估 OK，单位 mm）
- placement（必填）：{anchor: str, offset: [x,y,z]}，P1 拆解里的大致装配位

### cross_refs（顶层，可选数组）
跨部件约束，类型限定为 Layer 1 Stage C 已支持的 6 种：
inter_dist / ordering / colinear / same_face / symmetric_pair / concentric
每条字段参考 `references/verify/layer1-verification.md §Stage C` constraint 定义，
多一个必填字段 `parts: [slug, slug]` 指明参与约束的部件。
```

## 5. 失败模式（追加至 multi-part-playbook.md）

```
FM-10 缺 assembly_contract
  诊断：P2 末尾没产出 assembly_contract.yaml 就进 P3
  修复：回 P2 Step 2e 补齐，重走确认门

FM-11 bbox 预检疑似碰撞未记录
  诊断：precheck_bbox.md 标了 ⚠ 但 P3 joint_to_crossref.md 没回应该碰撞位
  修复：P3 装配后针对该对跑 do_children_intersect()，或在 cross_refs 里加对应 inter_dist 约束下限

FM-12 cross_refs 覆盖不全
  诊断：P1 拆解报告列的装配关系数 > assembly_contract.cross_refs 条数
  修复：回 Step 2e.a 补全翻译；cross_refs 硬下限 ≥1 条
```

## 6. 验证方法

### 6.1 结构核对（自动可查）

- `grep "Step 2e" multi-part-playbook.md` = 3 处（总表 + 详细模块 + 回报示范）
- `grep "Appendix B" references/verify/layer0-contract.md` = 1 处
- `grep "^FM-1[012]" multi-part-playbook.md` = 3 行
- P3 前置条目含 "assembly_contract.yaml"
- P4 含 "Step 4.3 整机 Stage C 验证"

### 6.2 行为验证（落在 `tests/18-assembly-contract-dryrun/`）

- **Scenario J**：新对话"做带 SG90 舵机的两关节机械臂"（≥2 部件）
  - 预期：P2 末尾产出 assembly_contract（parts≥2, cross_refs≥2）+ precheck_bbox；确认门等用户 → P3 Joint 对齐 cross_refs → P4 Stage C PASS
  - 失败判据：跳 Step 2e / cross_refs 为空 / 确认门自动过

- **Scenario K**：故意让 P1 拆解列 3 条装配关系但 AI 只翻译 2 条 → 验 FM-12 触发

每 Scenario 保存完整 AI 回复为 `run_J.md` / `run_K.md` 人工审阅。

### 6.3 回归验证

- 无（现有 test 13/14 是 single-part，不涉及 multi-part 流程）

### 6.4 不做

- cross_refs 自动翻译脚本
- bbox 预检精度提升（OBB / 实体 bool）
- schema linter
- Joint 自动生成

## 7. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| AI 把 bbox 预检的 ⚠ 当 PASS 放行 | 中 | FM-11 + P3 joint_to_crossref.md 映射要求 |
| cross_refs 翻译漏条 | 中 | FM-12 + P1 拆解 → P2 cross_refs 条数对比 |
| 用户嫌 Step 2e 确认门啰嗦 | 低 | 确认门只出 2 个产物摘要，秒过即可 |
| parts.placement.anchor 写法自由引歧义 | 低 | 只作 bbox 粗检参考，P3 Joint 才是权威 |
| Stage C 执行器接 cross_refs 时 scope 理解错 | 中 | Scenario J 的 Stage C 跑一遍兜底 |

## 8. Out of Scope

- Single-Part Playbook 加 parts / cross_refs（留空即可）
- reference-product-playbook.md 任何改动
- SKILL.md 路由段任何改动
- Layer 1 Stage A/B 改动
- 新增 constraint type（用现有 6 种够）
- bbox 之外的预检（侵入 / 干涉 / 运动学）
- Joint 自动生成
- precheck_bbox.md 严格 schema（Markdown 够用）

## 9. 验收标准

- multi-part-playbook.md 含 Step 2e 三子步 + P3 前置更新 + P4 Step 4.3 + FM-10/11/12
- layer0-contract.md 含 Appendix B（parts + cross_refs 描述）
- Scenario J 跑通：AI 真产 assembly_contract + precheck_bbox，用户 review 后进 P3，P4 Stage C PASS
- Scenario K 跑通：cross_refs 遗漏触发 FM-12 回补
