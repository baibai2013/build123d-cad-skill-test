# tests/18 — Assembly Contract + bbox 预检 Dry-run

**日期**：2026-04-18
**对应设计**：`docs/superpowers/specs/2026-04-18-multi-part-contract-precheck-design.md`
**对应计划**：`docs/superpowers/plans/2026-04-18-multi-part-contract-precheck-plan.md`

## 目的

验证 `references/protocols/multi-part-playbook.md` 新增的 **Step 2e + P3 前置 + P4 Step 4.3 + FM-10/11/12** 在真实 AI 对话里能被执行、catch 到已知陷阱。

本 test 是 **dry-run**：不生成代码、不跑 OCP，只看 AI 是否按 Playbook 流程产出 `assembly_contract.yaml` / `precheck_bbox.md` / `joint_to_crossref.md`，以及在故意制造漏翻译时是否触发 FM-12。

## Scenario 列表

| ID | 场景描述 | 预期路径 | 失败判据 |
|---|---|---|---|
| **J** | "做带 SG90 舵机的两关节机械臂"（≥2 部件） | P2 末尾产出 assembly_contract（parts≥2, cross_refs≥2）+ precheck_bbox；确认门等用户 → P3 Joint 对齐 cross_refs → P4 Stage C PASS | 跳 Step 2e / cross_refs 为空 / 确认门自动过 / P3 无 joint_to_crossref.md |
| **K** | 故意让 P1 拆解列 3 条装配关系但 AI 只翻译 2 条 | 触发 FM-12（cross_refs 覆盖不全）回补 | 漏条未被 catch / 强行进 P3 |

## 运行方式

在新 Claude 会话里（载入 build123d-cad skill），逐个 Scenario 喂入 prompt，完整 AI 回复粘贴到对应 `run_<ID>.md`。

**Scenario J prompt**：

```
帮我做一个带 SG90 舵机的两关节机械臂（base / arm / gripper 3 个部件），用 build123d-cad skill 的多部件流程。
```

**Scenario K prompt**：

```
做一个手机支架：底座（base）+ 支撑杆（rod）+ 夹持头（clamp），要求
1) base 和 rod 同轴
2) rod 和 clamp 成 ordering（rod 在下 clamp 在上）
3) clamp 的夹口中心线和 base 平行

走多部件流程。
```

Scenario K 的 prompt 故意列 3 条关系；在 AI 走到 Step 2e.a 时，如果 cross_refs 只翻译了前 2 条（漏掉 "clamp 夹口线 colinear base"），应触发 FM-12 回补。

## 判据 check（run_J.md / run_K.md 产出后）

见各自 run 文件末尾的 check list。

## 后续

- dry-run 不计入 Layer 1/2 验证
- 如 Scenario J/K 任一失败 → 回 Playbook 文档修订文案
- 全通过后 `structure_check.md` 填表
