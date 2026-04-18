# tests/18 结构核对

运行日期：2026-04-18

对应设计文档 `docs/superpowers/specs/2026-04-18-multi-part-contract-precheck-design.md` §6.1 与验收标准 §9。

## 检查结果

| # | 检查项 | 期望 | 实际 | 结果 |
|---|---|---|---|---|
| 1 | `grep -c "Step 2e" references/protocols/multi-part-playbook.md` | ≥ 3（总表 + 详细 + 回报）| 多处引用，含总表 / 详细段 / Step 2e.a~c 全节 | ✅ |
| 2 | `grep "Appendix B" references/verify/layer0-contract.md` | 1 处 | L269 `## Appendix B: 整机扩展字段（多部件专用）` | ✅ |
| 3 | Appendix B 含 parts / cross_refs 两节 | 两节 | L273 `### parts` + L296 `### cross_refs` | ✅ |
| 4 | `grep "^### FM-1[012]" multi-part-playbook.md` | 3 行 | L533 FM-10 / L539 FM-11 / L545 FM-12 | ✅ |
| 5 | P3 前置条目含 `assembly_contract.yaml` | 有 | Phase P3 前置列 `tests/<test>/assembly_contract.yaml 已通过 Step 2e 用户确认门（内含 cross_refs）` | ✅ |
| 6 | P4 含 Step 4.3 整机 Stage C | 有 | L470 `### Step 4.3 — 整机 Stage C 验证（对装配体跑 cross_refs）` | ✅ |
| 7 | Phase 总表 P2/P3/P4 更新 | 三行各自加新产出 | P2 行加 Step 2e / P3 行加 joint_to_crossref.md / P4 行加 Step 4.3 | ✅ |
| 8 | Step 2e.a cross_refs.type 限定 6 种 | 限定 | 段落明确列 `inter_dist / ordering / colinear / same_face / symmetric_pair / concentric` | ✅ |
| 9 | `cross_refs` 硬下限 ≥ 1 条写入 | 有 | 2e.a "硬下限：**≥1 条**" + Appendix B 尾部 "硬规则" | ✅ |
| 10 | P3 cross_refs↔Joint 6 类型映射表 | 有 | P3 段有 6 行 `cross_ref.type → Joint 实现方向` 表 | ✅ |
| 11 | `joint_to_crossref.md` 模板 | 有 | P3 段尾示例 markdown 表 2 行 | ✅ |
| 12 | tests/18/ 含 README + run_J + run_K | 3 文件 | README.md / run_J.md / run_K.md 齐 | ✅ |

## 文件改动清单

### skill 仓 `/Users/liyijiang/.agents/skills/build123d-cad/`

- `references/verify/layer0-contract.md`：+46 行 Appendix B
- `references/protocols/multi-part-playbook.md`：+172 行 / -6 行（Step 2e + P3 前置 + P4 Step 4.3 + FM-10/11/12）

commits：

- c197710 docs(layer0-contract): 追加 Appendix B 整机扩展字段 parts / cross_refs
- 6ad5e91 docs(multi-part): Step 2e 整机合同 + bbox 预检 + P4 整机 Stage C

### test 仓 `/Users/liyijiang/work/build123d-cad-skill-test/`

- `tests/18-assembly-contract-dryrun/README.md`（新建）
- `tests/18-assembly-contract-dryrun/run_J.md`（新建，13 判据）
- `tests/18-assembly-contract-dryrun/run_K.md`（新建，7 判据）
- `tests/18-assembly-contract-dryrun/structure_check.md`（本文件）

commit 待本次提交。

## 行为验证 Scenario J / K 待执行

运行方式见 `README.md`。由用户在新 Claude 会话里跑，完整回复粘回 `run_J.md` / `run_K.md`，按各自判据清单人工打勾。

## 回归验证待执行

- test 13（红米 K80 Pro 手机壳，single-part）— 不触碰 parts / cross_refs，应无回退
- test 14（小米 K70 手机壳，single-part）— 同上

## 结论

结构核对 12/12 全通过。行为验证（Scenario J/K）+ 回归验证（test 13/14）需用户在新会话中完成。
