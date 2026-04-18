# Scenario F — 同类命中（slug 不同但 category 相同）

## 前置准备

仅保留 `experience/phone-case/redmi-k80-pro.md`，不要有 `xiaomi-k70.md`：

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
ls $SKILL/experience/phone-case/
# Expected: redmi-k80-pro.md（可能还有 Scenario D 落盘的文件）
# 不能有 xiaomi-k70.md；如有则先移走
```

## 用户 prompt

```
做小米 K70 手机壳
```

（slug=xiaomi-k70，category=phone-case，与 redmi-k80-pro 不同 slug 但同类）

## 预期 AI 行为

### R1 产出报告必须形如

```
Step R1 产出报告
- [x] references/xiaomi-k70/search_plan.md   (待用户确认)
- [partial] experience/phone-case/*          (同类命中 1 条：redmi-k80-pro.md confidence=4，作为参考)
- [miss] experience/*/xiaomi-k70.md          (无精确命中)
下一步：等用户确认 → Step R2
```

**关键检查点**：
- ✅ `[partial]` 状态
- ✅ 列出 `redmi-k80-pro.md` 作为**参考**（不是当成事实）
- ✅ `search_plan.md` 的「已知参数」节**不包含** redmi-k80-pro 的精确参数（因为 slug 不同）
- ✅ `search_plan.md` 的「预期坑」节可**借鉴** redmi-k80-pro 的坑（类型层面共通：如"摄像头 Y 坐标正负"），并标注「来自同类 experience/phone-case/redmi-k80-pro.md，K70 需独立验证」

### R5 行为

AI 起草 Experience Draft 时 slug 不同 → 直接创建新条目 `experience/phone-case/xiaomi-k70.md`（无需 diff），用户确认后落盘。

## 失败判据

- R1 没出现 `[partial]`
- R1 把 redmi-k80-pro 的精确参数（如 160.26×74.95）当成 K70 的数填进 search_plan（**重大错误**——跨 slug 自动合并）
- `预期坑`节完全空（没借鉴同类）或完全复制（没标"需独立验证"）
- R5 误判为"已存在" → 拿 redmi-k80-pro.md diff（slug 不同就是新文件）

## 实跑结果（待操作员粘贴）

```
<完整 AI 回复>
```

## 审阅结论

- [ ] R1 出 `[partial]` 且正确识别参考对象
- [ ] 同类参考**仅用于坑的借鉴**，参数不自动迁移
- [ ] R5 创建新条目（不和 redmi-k80-pro.md 混淆）
- [ ] Appendix A 白名单遵守（category=phone-case，不是 `手机壳` 或 `case`）

**若有问题**：记录 + 回流到 Playbook Appendix A 或改动 3 修订。
