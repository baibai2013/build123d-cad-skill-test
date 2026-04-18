# skill-coherence-refactor 结构核对

运行日期：2026-04-18

对应设计文档 §7.1 与验收标准 §10。

## 检查结果

| # | 检查项 | 期望 | 实际 | 结果 |
|---|---|---|---|---|
| 1 | `wc -l SKILL.md` | ≤ 1200 | 1153 | ✅ |
| 2 | `grep -c "^### Step \|^### Phase " SKILL.md` | 0 | 0 | ✅ |
| 3 | SKILL.md 含 `## AI 执行准入序列` | 有 | L24 | ✅ |
| 4 | `ls references/protocols/` | README + 3 Playbook | README.md + reference-product + single-part + multi-part | ✅ |
| 5 | `references/INDEX.md` 存在 | 有 | 1250 bytes | ✅ |
| 6 | reference-product-playbook 契约 7 条 | 有 | 已确认（Task 5 追加第 7 条） | ✅ |
| 7 | single-part-playbook 契约 7 条 | 有 | 已确认（Task 9 成文） | ✅ |
| 8 | multi-part-playbook 契约 7 条 | 有 | 已确认（Task 11 成文） | ✅ |
| 9 | reference-product Quote-back 示范 | ≥ 8 | 8 | ✅ |
| 10 | single-part Quote-back 示范 | ≥ 4 | 5 | ✅ |
| 11 | multi-part Quote-back 示范 | ≥ 4 | 4 | ✅ |
| 12 | FM-9 Quote-back 伪造 | 有 | `### FM-9：Quote-back 伪造` (L611) | ✅ |

## commits（skill 仓）

- d095d37 AI 执行准入序列（Task 1）
- b719661 路由表去 emoji（Task 2）
- 4e0904f INDEX.md（Task 3）
- 4dde53f protocols/README.md（Task 4）
- 47dd09c 契约第 7 条 Quote-back（Task 5）
- 260a581 8 Step Quote-back 示范（Task 6）
- 04931a9 FM-9（Task 7）
- 904121b SKILL.md 删参考物段（Task 8）
- 4e1e5e7 single-part-playbook.md（Task 9）
- a79c3f8 SKILL.md 删单部件段（Task 10）
- f2903b3 multi-part-playbook.md（Task 11）
- 71063e5 SKILL.md 删多部件段（Task 12）
- 9d57e8f SKILL.md 消除残留 ### Step N（Task 12 补丁）

## commits（test 仓）

- e5ee8f7 tests/17-skill-optimization-dryrun 占位（Task 13）
- （本提交）tests/17/structure_check.md

## 行为验证（Scenario G / H / I）待执行

运行方式见 `README.md`。由用户在新 Claude 会话里跑，完整回复粘回 `run_G.md` / `run_H.md` / `run_I.md`。

## 回归验证待执行

- test 13（红米 K80 Pro 手机壳）重跑
- test 14（小米 K70 手机壳）重跑

## 结论

结构核对 12/12 全通过。行为验证 + 回归验证需用户在新会话中完成。
