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

## AI 完整回复

> 运行方式：Agent 子代理模拟新会话（2026-04-18）。包含阶段 1 首次产出（漏第 3 条）+ 用户触发话术 + 阶段 2 修复。

```text
════════════════════════════════════════════════════════
【阶段 1 — P1 需求拆解】
════════════════════════════════════════════════════════

## 需求拆解报告

### 部件清单
| 编号 | 名称  | 功能                     |
|------|-------|--------------------------|
| P1   | base  | 底座，提供重量与支撑     |
| P2   | rod   | 支撑杆                   |
| P3   | clamp | 夹持头                   |

### 装配关系（逐条来自用户 prompt）
1. base ↔ rod：concentric（同轴，沿 Z 轴）
2. rod ↔ clamp：ordering（Z 轴，rod 在下 clamp 在上）
3. clamp 夹口中心线 ∥ base（夹口方向与底座平面平行 → colinear 语义）

### 工艺确认
目标工艺：3D打印

### 仿真需求
[x] 无需仿真

Phase P1 产出报告
引自 multi-part-playbook.md §Phase P1 / 本步产出："需求拆解报告（部件清单 + 装配关系 + 工艺确认 + 仿真需求 + 可选专家意见）"
- [x] 需求拆解报告已输出（部件 3 项 / 装配关系 3 条 / 工艺=3D打印）
- [ask] 用户确认继续进 P2？

[用户：OK 进 P2]

════════════════════════════════════════════════════════
【阶段 1 — P2 每部件 3 变体（简化）】
════════════════════════════════════════════════════════

base V1/V2/V3 → 用户选 V2（Ø100×12 圆盘）
rod  V1/V2/V3 → 用户选 V2（Ø10×L150 杆）
clamp V1/V2/V3 → 用户选 V2（U 形夹口宽 75）

Phase P2 产出报告
引自 multi-part-playbook.md §Phase P2 / 本步产出："每部件 3 变体..."
- [x] base/rod/clamp × V1/V2/V3 断言全过，用户选 V2
- [ask] 进入 Step 2e 汇总？

[用户：进]

════════════════════════════════════════════════════════
【阶段 1 — Step 2e.a 首次产出（故意漏第 3 条）】
════════════════════════════════════════════════════════

### assembly_contract.yaml

```yaml
version: "1.0"
meta:
  name: phone_stand
  source: multi-part-playbook P2 Step 2e
  date: 2026-04-18

globals:
  unit: mm

parts:
  - slug: base
    file: base_v2.py
    bbox: {x: 100, y: 100, z: 12}
    placement: {anchor: "原点", offset: [0, 0, 0]}
  - slug: rod
    file: rod_v2.py
    bbox: {x: 10, y: 10, z: 150}
    placement: {anchor: "base 顶面中心", offset: [0, 0, 12]}
  - slug: clamp
    file: clamp_v2.py
    bbox: {x: 75, y: 30, z: 40}
    placement: {anchor: "rod 顶端", offset: [0, 0, 162]}

cross_refs:
  - id: base_rod_concentric
    type: concentric
    parts: [base, rod]
    feature: "center_axis_z"
    tolerance: 0.1
  - id: rod_below_clamp
    type: ordering
    parts: [rod, clamp]
    axis: z
    sequence: [rod, clamp]
    tolerance: 0.5

features: []
param_map: {}
variants: []
```

### precheck_bbox.md
（3 对 AABB，全部 ✅ 无碰撞；省略）

Step 2e 产出报告
引自 multi-part-playbook.md §Phase P2 / Step 2e：
  "Step 2e 末尾必须等用户确认 assembly_contract.yaml 和 precheck_bbox.md"
- [x] assembly_contract.yaml（parts: 3，cross_refs: **2**）
- [x] precheck_bbox.md
请 review，回 "ok 进 P3" 或 "改 <具体>"

────────────────────────────────────────────────────────
[用户提示]：你的 cross_refs 数量对得上 P1 拆解里的 3 条装配关系吗？
────────────────────────────────────────────────────────

════════════════════════════════════════════════════════
【阶段 2 — 自检并修复（FM-12）】
════════════════════════════════════════════════════════

你说得对。按 multi-part-playbook.md §常见失败模式 §FM-12「cross_refs 覆盖不全」：
  "P1 需求拆解报告列的装配关系条数 > assembly_contract.cross_refs 条数，存在漏翻译"

自检：
- P1 拆解 3 条：① base↔rod concentric  ② rod↔clamp ordering  ③ clamp 夹口线 ∥ base（colinear 语义）
- assembly_contract.cross_refs 只 2 条 → **漏第 3 条**
- 根因：colinear 类型在多部件跨部件约束里不常用，翻译时把"夹口中心线 ∥ base 平面"忽略了。按 FM-12 修复指令：回 Step 2e.a 对齐 P1 拆解报告逐条补齐。

### 修订后的 assembly_contract.yaml（cross_refs 节）

```yaml
cross_refs:
  - id: base_rod_concentric
    type: concentric
    parts: [base, rod]
    feature: "center_axis_z"
    tolerance: 0.1

  - id: rod_below_clamp
    type: ordering
    parts: [rod, clamp]
    axis: z
    sequence: [rod, clamp]
    tolerance: 0.5

  - id: clamp_aperture_parallel_base
    type: colinear
    parts: [clamp, base]
    feature_a: "clamp.aperture_centerline"   # 夹口开口方向中心 edge
    feature_b: "base.top_face_axis_x"        # base 顶面参考方向 edge
    axis: x
    tolerance: 0.5
```

### precheck_bbox.md 更新备注
- bbox 不受 colinear 约束影响，3 对碰撞结论不变
- clamp_aperture_parallel_base 为姿态约束，AABB 预检不覆盖，将在 P3 Joint 设计阶段通过 clamp 的 Location 姿态对齐实现，Step 4.3 整机 Stage C (colinear) 做权威判定

Step 2e 产出报告（修订后）
引自 multi-part-playbook.md §Phase P2 / Step 2e：
  "Step 2e 末尾必须等用户确认 assembly_contract.yaml 和 precheck_bbox.md"
修复动作：依据 §FM-12「cross_refs 覆盖不全」，回 Step 2e.a 补第 3 条 colinear。
- [x] assembly_contract.yaml（parts: 3，cross_refs: 3 ✓ 与 P1 装配关系 3 条齐）
  · base_rod_concentric          (type=concentric)
  · rod_below_clamp              (type=ordering)
  · clamp_aperture_parallel_base (type=colinear) ← NEW
- [x] precheck_bbox.md（3 对 AABB 结论不变；新增姿态约束备注）
- [x] 静态自检：cross_refs 条数 (3) ≥ P1 装配关系数 (3) ✓
请 review 两份产物，回 "ok 进 P3" 或 "改 <具体>"
下一步：等用户回执（未收到前不进 P3）
```

**(可选) 触发话术**（本次已使用）：

```
你的 cross_refs 数量对得上 P1 拆解里的 3 条装配关系吗？
```

---

## 判据 check

- [x] **K-1**：P1 拆解报告列了 3 条装配关系（条目数与 prompt 对齐）
- [x] **K-2**：Step 2e.a 首次产出的 `cross_refs` 条数 = **2**（漏 1 条，如设计预期）
- [x] **K-3**：用户提示后 AI 明确引用 **FM-12**（"cross_refs 覆盖不全"）并定位漏条
- [x] **K-4**：修复后 `cross_refs` 条数 = 3 ≥ P1 拆解装配关系数 3
- [x] **K-5**：修复后第 3 条 type=`colinear`（语义合理，匹配"夹口中心线 ∥ base"）
- [x] **K-6**：修复过程未强行进 P3，Step 2e.c 确认门仍在等用户回执
- [x] **K-7**：修复后 Quote-back 格式正确（`引自 multi-part-playbook.md §Phase P2 / Step 2e：...`）

## 结论

- **通过**：7/7 ✅。K-3 走"用户提示触发"路径（AI 未主动自察觉），判据注释允许（"AI 自察觉更佳，用户提示亦可"）
- 硬下限 K-3 / K-4 / K-6 全 ✅，未强行进 P3、未跳过 Step 2e 确认门

## Review 记录

- 运行人：Claude Code Opus 4.7（子代理模拟新会话）
- 运行日期：2026-04-18
- FM-12 是否主动触发：**需用户提示**（AI 自察觉未触发 → 可作为后续 Playbook 改进点：考虑加 "Step 2e.c 自检清单：cross_refs 数量 ≥ P1 拆解装配关系数"）
- 总体结论：**通过**。FM-12 修复路径走通，AI 正确回到 Step 2e.a 补 colinear，未越过确认门。
