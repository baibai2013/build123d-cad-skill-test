# 结构核对报告（experience/ + Playbook 修改）

执行日期：2026-04-18
执行命令：见 docs/superpowers/plans/2026-04-18-experience-cache.md Task 13

## 7 项核对

| # | 项 | 命令 | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| 1 | experience/ 目录存在 | `ls $SKILL/experience/` | README.md + phone-case/ | README.md + phone-case | ✅ |
| 2 | README 含发布风险声明 | `grep -c "发布风险说明" ...README.md` | 1 | 1 | ✅ |
| 3 | Playbook 契约第 6 条 | `grep -c "R1 开始前必须查" ...playbook.md` | 1 | 1 | ✅ |
| 4 | R1 前置检索子段 | `grep -c "前置检索" ...playbook.md` | ≥1 | 2 | ✅ |
| 5 | R5 Experience Draft | `grep -c "Experience Draft" ...playbook.md` | ≥4 | 6 | ✅ |
| 6 | FM-7 + FM-8 | `grep -cE "^### FM-[78]" ...playbook.md` | 2 | 2 | ✅ |
| 7 | Appendix A | `grep -c "^## Appendix A" ...playbook.md` | 1 | 1 | ✅ |

## Git 追踪核对

```
$ cd $SKILL && git ls-files experience/
experience/README.md
experience/phone-case/redmi-k80-pro.md
```

✅ experience/ 已进 git。

## 行为验证（Scenario D/E/F）

见 run_D.md / run_E.md / run_F.md。本 structure_check 只覆盖静态结构，行为验证由操作员后续手动跑。

## 结论

- [x] 所有 7 项静态核对 pass
- [x] experience/ 进 git 追踪
- [ ] 行为验证 D/E/F 完成（由操作员填 run_*.md 后勾）
