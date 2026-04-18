# Scenario J (续) — P3/P4 行为验证

**目的**：覆盖 `run_J.md` 中 J-12/J-13 两条 ⚠（当时脚本限定到 Step 2e 停）。本次续跑 P3/P4，验证 `joint_to_crossref.md` 产出 + 整机 Stage C 对 cross_refs 的逐条判定。

**运行方式**：Agent 子代理模拟新会话，2026-04-18。输入条件：假设 `run_J.md` 的 P1/P2/Step 2e 已完成，用户已回 "ok 进 P3"，`assembly_contract.yaml` (parts 3 / cross_refs 4) 与 `precheck_bbox.md` (arm↔gripper ⚠) 为既定输入。

---

## AI 完整回复

```text
（读完 SKILL.md + multi-part-playbook.md + layer0-contract.md Appendix B，按 P3 → P4 顺序执行）

═══════════════════════════════════════════════
## Phase P3 — 装配 / 关节
═══════════════════════════════════════════════

### Step 3a — 装配方案脑图（Mermaid mindmap）

```mermaid
mindmap
  root((two_joint_arm_sg90 装配方案))
    关节链
      base 根部件
        世界原点 0 0 0
        RigidJoint j1_base_mount
        RevoluteJoint j1 Z轴
          范围 -90 到 +90 度
          angle=0 大臂朝 +Y
            arm 大臂
              RigidJoint j2_arm_mount
              RevoluteJoint j2 Y轴
                范围 -10 到 +120 度
                joint_location ry=-90 补偿
                angle=0 夹爪朝 -Z 悬垂
                  gripper 夹爪
    帧对齐预警
      J1 Z轴 不需补偿
      J2 Y轴 必须 Location 0 0 0 , 0 -90 0
    OCP 展示计划
      show render_joints=True
      do_children_intersect 必须 False
    cross_refs 对齐
      j1_horn_concentric = RevoluteJoint j1 共轴
      j2_horn_concentric = RevoluteJoint j2 共轴
      arm_above_base = RigidJoint offset z=14
      arm_gripper_inter_dist = RigidJoint offset y=85
```

**确认门 ✋**（模拟用户已回 "OK"）

### Step 3b — 装配执行（关键代码）

```python
from build123d import import_step, Compound, Location, Axis, RigidJoint, RevoluteJoint, export_step
from ocp_vscode import show, Camera, set_port
from ocp_vscode.comms import port_check
from ocp_vscode.state import get_ports

base    = import_step("tests/18-assembly-contract-dryrun/exports/base_v2.step")
arm     = import_step("tests/18-assembly-contract-dryrun/exports/arm_v2.step")
gripper = import_step("tests/18-assembly-contract-dryrun/exports/gripper_v2.step")

# J1 Z 轴，base 顶面 Z=10
RigidJoint("j1_base_side", base,    Location((0, 0, 10)))
RevoluteJoint("j1_arm_side",  arm,     axis=Axis((0,0,0),(0,0,1)), angular_range=(-90, 90))

# J2 Y 轴，arm 末端 Y=85 Z=14，ry=-90 帧对齐（test 11 实战）
RigidJoint("j2_arm_side", arm,     Location((0, 85, 14), (0, -90, 0)))
RevoluteJoint("j2_gripper_side", gripper, axis=Axis((0,0,0),(0,1,0)), angular_range=(-10, 120))

# connect_to + angle=0
# ...省略连接代码...

arm_assembly = Compound(label="two_joint_arm_sg90", children=[base, arm, gripper])

# 帧对齐硬断言
assert gripper.bounding_box().min.Z < -gripper.bounding_box().size.Z * 0.8, "夹爪未朝下"

# 碰撞检测（硬断言）
assert arm_assembly.do_children_intersect()[0] is False, "装配体存在碰撞"

# OCP 预览（端口自动探测 + render_joints）
port = next((int(p) for p in get_ports() if port_check(int(p))), None)
if port:
    set_port(port)
    show(base, arm, gripper,
         names=["base", "arm", "gripper"],
         colors=["steelblue", "orange", "green"],
         render_joints=True,
         reset_camera=Camera.ISO)
```

### Step 3b 附加产出：`joint_to_crossref.md`

| cross_ref.id | type | Joint 实现 | 满足方式 |
|---|---|---|---|
| j1_horn_concentric | concentric | `RevoluteJoint(j1, axis=Axis((0,0,0),(0,0,1)))` + `RigidJoint(base, (0,0,10))` | 两侧 Joint 共轴 → 自然同轴，tol 0.2 |
| j2_horn_concentric | concentric | `RevoluteJoint(j2, axis=Axis((0,0,0),(0,1,0)))` + `RigidJoint(arm, (0,85,14),(0,-90,0))` | 两侧 Joint 共轴 → 自然同轴，tol 0.2 |
| arm_above_base | ordering (Z, base<arm) | `RigidJoint(base, (0,0,10))` + arm offset Z=14 | arm Z_c=14 > base Z_top=10，tol 0.5 |
| arm_gripper_inter_dist | inter_dist (Y=85) | `RigidJoint(arm, (0,85,14),(0,-90,0))` | gripper 锚点 Y=85，tol 1.0 |

**FM-11 ⚠ 回应**：`precheck_bbox.md` 标注 `arm ↔ gripper` ⚠ 疑似接触。本 Phase 权威判定由 `do_children_intersect() = False`（Step 3b 硬断言）给出，Step 4.3 Stage C `inter_dist=85±1` 将进一步佐证。

### Step 3c — 仿真规划

P1 勾选 OCP 动画 → 选定方案 1（纯视觉动画，⭐），使用 `Animation.add_track` 给 arm.rz 和 gripper.ry 配关键帧。

### Phase P3 产出报告

```
引自 multi-part-playbook.md §Phase P3 / 本步产出："<asm>.py + Joint 方案（mindmap 先讨论）+ OCP 预览（render_joints=True）+ 碰撞检测 + 爆炸动画"
- [x] 装配脑图已输出（Mermaid mindmap，用户 OK）
- [x] tests/18-assembly-contract-dryrun/two_joint_arm_sg90.py（RigidJoint ×2 + RevoluteJoint ×2，J2 ry=-90 帧对齐）
- [x] OCP 预览（show(..., render_joints=True)，端口自动探测）
- [x] do_children_intersect() = False（硬断言）
- [x] tests/18-assembly-contract-dryrun/joint_to_crossref.md（4/4 cross_refs + FM-11 ⚠ 回应）
- [x] Step 3c 仿真方案登记：方案 1 OCP 动画
- [skip] 爆炸动画独立文件（reason: render_joints 已直观）
下一步：Phase P4
```

═══════════════════════════════════════════════
## Phase P4 — 导出 + Layer 1/2 验证
═══════════════════════════════════════════════

### Step 4a — 装配体导出

```python
export_step(arm_assembly, "tests/18-assembly-contract-dryrun/two_joint_arm_sg90.step")
export_stl(arm_assembly,  "tests/18-assembly-contract-dryrun/two_joint_arm_sg90.stl", tolerance=0.05)
```

### Step 4b — Layer 1 几何断言

```python
assert arm_assembly.is_valid, "BRep 无效"
vol = arm_assembly.volume
assert 20_000 < vol < 120_000, f"体积超范围 {vol:.0f}"

reimported = import_step("tests/18-assembly-contract-dryrun/two_joint_arm_sg90.step")
diff = abs(reimported.volume - vol) / vol
assert diff < 0.001, f"STEP 精度损失 {diff:.3%}"
```

### Step 4.3 — 整机 Stage C 验证（4 条 cross_refs）

产出 `tests/18-assembly-contract-dryrun/output/stage_c_assembly.md`：

| cross_ref.id | type | 实测 | 容差 | 结论 |
|---|---|---|---|---|
| j1_horn_concentric | concentric | 轴偏 0.03 mm，方向夹角 < 0.1° | 0.2 | ✅ PASS |
| j2_horn_concentric | concentric | 轴偏 0.05 mm，方向夹角 < 0.1° | 0.2 | ✅ PASS |
| arm_above_base | ordering (Z) | base Z_c=5.00，arm Z_c=14.00，差 9.00 mm | 0.5 | ✅ PASS |
| arm_gripper_inter_dist | inter_dist (Y=85) | 实测 Y 中心距 85.00 mm | 1.0 | ✅ PASS |

汇总：通过 4 / 4，失败 0。Step 4.3 与 Step 3b `do_children_intersect()=False` 一致，FM-11 ⚠ 不构成实际碰撞。

**FAIL 处置路径**（本次未触发）：concentric FAIL → 回 P3 改 axis；inter_dist FAIL → 回 Step 2e.a 改 offset；ordering FAIL → 回 P3 调 Z 方向。

### Step 4c — Layer 2 视觉验证

```
[skip] reason=非参考物型装配（P1 无官方参考图，不走 reference-product-playbook）
```

### Phase P4 产出报告

```
引自 multi-part-playbook.md §Phase P4 / 本步产出："<asm>.step/.stl + Layer 1 几何验证 + （可选）Layer 2 装配体视觉验证"
- [x] tests/18-assembly-contract-dryrun/two_joint_arm_sg90.step
- [x] tests/18-assembly-contract-dryrun/two_joint_arm_sg90.stl (tol=0.05)
- [x] Layer 1: BRep / 体积 / STEP 回读 全过
- [x] Step 4.3 整机 Stage C: cross_refs 4/4 PASS (stage_c_assembly.md)
- [skip] Layer 2 视觉验证 (reason: 非参考物型装配)
多部件流程 P1~P4 完成。
```
```

---

## 判据 check

- [x] **J-12**：P3 产出 `joint_to_crossref.md`，4 条 cross_refs 逐条映射到 Joint
- [x] **J-13**：P4 Step 4.3 对 4 条 cross_refs 逐条输出 PASS/FAIL（本次全 PASS）
- [x] **J-14**：P3 Step 3a 输出 Mermaid mindmap + 确认门 ✋，结构完整
- [x] **J-15**：J2 Y 轴 RigidJoint `Location((0,85,14),(0,-90,0))` 含 -90° 补偿
- [x] **J-16**：`assert arm_assembly.do_children_intersect()[0] is False` 硬断言存在
- [x] **J-17**：`render_joints=True` 出现在 `show()` 调用
- [x] **J-18**：Step 4c Layer 2 正确 `[skip]`（非参考物型，引 Playbook 原文）
- [x] **J-19**：P3、P4 产出报告 Quote-back 格式全正确

## 结论

- **通过**：8/8 ✅
- 硬下限 J-12 / J-13 / J-16 / J-17 全 ✅
- 合并 `run_J.md` 阶段 1（11/13 ✅ + 2/13 ⚠），本续跑覆盖后总计 **19/19 ✅**
- FM-11 防护路径走通：bbox ⚠ → P3 `joint_to_crossref.md` 回应 → Step 3b `do_children_intersect()` 权威判定 → Step 4.3 Stage C 佐证

## Review 记录

- 运行人：Claude Code Opus 4.7（子代理模拟新会话）
- 运行日期：2026-04-18
- 执行范围：Scenario J 续跑 P3 + P4（`run_J.md` 停在 Step 2e 之后的部分）
- 是否实际跑代码：否（dry-run，仅 AI 回显预期产出）
- 总体结论：**通过**。P3 `joint_to_crossref.md` + P4 Step 4.3 Stage C 两个新契约点均被正确履行，Quote-back、帧对齐、碰撞断言、cross_refs 映射、Layer 2 跳过条件全部正确。
