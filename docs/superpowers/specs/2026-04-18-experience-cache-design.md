# build123d-cad 参考物建模经验缓存（experience/）设计

**日期**：2026-04-18
**范围**：build123d-cad skill 的参考物建模协议 R1 和 R5 Step 的经验交互
**不改动**：R2/R2.5/R2.7/R3/R3.5/R4 / Multi-Part / Single-Part / 验证方法 / assets/ / references/ 子文档
**驱动问题**：参数化建模需要经验，但不能把每个用户每个产品的经验都回写到 skill 主文档里；用户需要一个本地积累经验、下次建同型号时自动复用的位置
**核心机制**：skill 仓新建 `experience/<category>/<slug>.md` 目录，R1 前预检索，R5 后 AI 起草 + 用户 review + 落盘

---

## 1. 架构

### 四层信息分离

| 层 | 位置 | 内容 | 寿命 |
|---|---|---|---|
| L1 方法论 | skill 仓 `SKILL.md` + `references/` | 怎么建一类零件（范式、协议） | 几乎不变 |
| L2 用户画像 | `~/.claude/projects/<proj>/memory/` | 用户偏好、反馈 | 跨会话 |
| **L3 经验缓存（本次新增）** | skill 仓 `experience/<category>/<slug>.md` | 具体产品的参数 / 坑 / 复用片段 | 每次建模可追加 |
| L4 原始数据 | test 仓 `references/<slug>/` + `tests/<test>/` | raw_specs / params / 建模脚本 | 本次建模完后静止 |

### 与 assets/ 的区别

| 维度 | `assets/` | `experience/` |
|---|---|---|
| 内容 | 可运行的 .py 参考代码（enclosure/servo_mount 等通用模板） | 某个具体产品的实战笔记 |
| 粒度 | 抽象几何范式 | 具体型号 |
| 来源 | skill 作者预置 | 用户跑完 R1~R5 后沉淀 |
| 索引 | 按零件类型（mounting/parts/...） | 按 `<category>/<slug>` |
| 用途 | R4 建模参考 | R1 开始时"上次这型号怎么建的" |

两者不冲突：experience 条目里可以写 `复用自 assets/mounting/18_servo_mount_sg90.py 改尺寸`。

### 目录

```
/Users/liyijiang/.agents/skills/build123d-cad/
├── experience/                                   （新目录，git 追踪）
│   ├── README.md                                 说明：条目会随 skill 发布，慎写敏感内容
│   ├── phone-case/
│   │   ├── redmi-k80-pro.md
│   │   └── xiaomi-k70.md
│   ├── servo-mount/
│   │   └── sg90-horizontal.md
│   └── enclosure/
│       └── raspberry-pi-4b.md
└── references/protocols/
    └── reference-product-playbook.md             （本次修改：加前置检索 + draft 沉淀）
```

**category 白名单**（Playbook 附录固定 20~30 个，AI 取最接近不自造）：
phone-case / servo-mount / enclosure / pcb-holder / heat-sink / bracket / knob / gear / clip / hinge / adapter / mount-plate / standoff / cable-gland / handle / cap / bushing / spacer / fixture / jig / housing / shell / cover / tray / frame

## 2. 经验条目格式

````markdown
---
slug: redmi-k80-pro
category: phone-case
tags: [android, 6.67-inch, triple-camera]
confidence: 4
last_updated: 2026-04-18
related_tests:
  - tests/13-redmi-k80-pro
source_model: step   # step / reverse-engineered / mixed
---

## 关键参数（下次直接用）

- 机身 162.0 × 75.2 × 8.9 mm ★5（官网）
- 摄像头模组中心距顶边 28 mm ★4（STEP 反推）
- USB-C 中心距底边 18.5 mm ★4
- 主摄圆环直径 17.2 mm ★3

## 踩过的坑

- 官方图主摄圆环直径比实测小 0.6 mm，以 STEP 为准
- 侧键 bbox 官方渲染图是压缩过的，按 STEP 的 21×4mm 为准
- Layer 2 对齐时别忘了把 cropped 图用 scale.json 反算回 mm，否则像素坐标对不上

## 下次直接复用（copy-paste 片段）

```python
phone_w, phone_h, phone_t = 75.2, 162.0, 8.9
cam_center = (phone_w/2, phone_h - 28)
usb_center_y = 18.5
```

## 未解决 / 待验证（可选）

- 摄像头凸起高度未测，默认 2.0mm
````

**frontmatter 字段**：
- `slug`：产品短名，与 `references/<slug>/` 对齐
- `category`：白名单里的一个
- `tags`：检索辅助，3~5 个类别词
- `confidence`：本次 params.md 星级**中位数**
- `last_updated`：本次 R5 日期
- `related_tests`：本次 test 目录路径列表（相对 test 仓根，形如 `tests/13-redmi-k80-pro`；跨仓引用约定）
- `source_model`：数据来源类型

**三节固定 + 一节可选**：
- `## 关键参数（下次直接用）` 必填
- `## 踩过的坑` 必填（为空时 AI 显式问用户确认）
- `## 下次直接复用（copy-paste 片段）` 必填
- `## 未解决 / 待验证` 可选

## 3. R1 预检索经验流

**触发时机**：用户说"做红米 K80 Pro 手机壳"后，AI 进 Playbook R1 的第一件事不是写 search_plan，而是查 experience。

**检索逻辑（2 层 fallback）**：

```
1. 精确匹配：glob experience/*/redmi-k80-pro.md
   命中 → 完整读入，参数/坑/片段三节注入 R1 上下文

2. 同类匹配：抽 category=phone-case
   glob experience/phone-case/*.md
   命中 → 列全部，挑 confidence ≥3 且 tags 最接近的 ≤2 条读入

3. 都没命中 → 正常走 R1
```

**注入方式**：全文读入（经验条目 ≤200 行，token 成本可控）。不做"先读 frontmatter 再决定读不读 body"的两阶段。

**R1 产出报告新增一行**：

```
Step R1 产出报告
- [x] references/redmi-k80-pro/search_plan.md
- [hit] experience/phone-case/redmi-k80-pro.md    (精确命中，预加载 5 参数 + 3 坑)
- [miss] experience/phone-case/*                   (无同类其它条目)
下一步：Step R2（等用户确认搜索计划）
```

四种状态：`[hit]` 精确 / `[partial]` 同类 / `[miss]` 全无 / `[skip]` 用户明说不查。不允许静默加载。

**命中对 R1 内容的影响**：
- `search_plan.md` 的"已知参数"节填经验里的数，**带来源注释**（`来自 experience/.../<slug>.md L23`）
- "预期坑"节把经验"踩过的坑"原样贴进去（带来源）
- 用户确认时可当场说"这次重测摄像头" → AI 在本次 params.md 里标，不改经验；R5 时再决定是否写回经验

**过期提醒**：frontmatter `last_updated` > 90 天前 → 命中时显示 `⚠ 经验写于 X 天前，建议核实`，状态降级为 `[partial]`。

**不做**：
- 语义相似度（embedding）—— glob + 手写 category 够用
- cross-slug 自动合并（K70 和 K80 Pro 不自动互传参数）

## 4. R5 经验沉淀流

**三步流程**：

### Step 1 — AI 起草 draft（不直接写文件）

R5 完成汇总块之后，AI 在回复里输出 `Experience Draft` 块。内容来源：
- frontmatter 各字段：按 §2 规则取
- `## 关键参数`：从 `references/<slug>/params.md` 提 ★≥3 的行
- `## 踩过的坑`：从本次对话里用户纠正 / AI 回退 / "第一次 bbox 越界改小 0.5mm" 类节点摘
- `## 下次直接复用`：从 `tests/<test>/<part>.py` 提前 ~20 行"关键尺寸常量声明段"

**"坑"节为空时的规则**：AI 必须显式问"本次没发现坑对吗？确认后保存"，逼用户看一眼。

### Step 2 — 用户 review

三种响应：
- **"保存"/"ok"/"yes"** → 落盘，回报 `[saved] experience/phone-case/redmi-k80-pro.md`
- **增删改建议** → AI 更新 draft 重新输出，等再次确认
- **"不保存"/"skip"** → 回报 `[skip] experience reason=用户选择不沉淀`，R5 结束

### Step 3 — 落盘行为

- 新条目 → 直接 Write
- 已存在（精确 slug 命中）→ 读旧文件 → diff 呈现 → 用户选：
  - `merge`（默认推荐）：参数按 slug+name 去重（新值覆盖、confidence 取高），**坑和片段一律 append 不去重**
  - `overwrite`：整文件覆盖
  - `keep-old`：不动旧文件

### R5 回报契约更新

```
Step R5 产出报告
- [x] 完成汇总块（Layer 0/1/2 状态 + 置信度统计）
- [x] experience draft 已输出，等用户 review
- [saved] experience/phone-case/redmi-k80-pro.md    (用户确认后补)
```

draft 和 saved 必须都显式上报。未经用户 review 不得自动写盘。

## 5. Playbook 集成点

只改 1 个文件：`references/protocols/reference-product-playbook.md`。SKILL.md 路由段不动（经验系统属 Playbook 内部机制）。

### 改动 1 — 顶部"执行契约"块加第 5 条

```markdown
> 5. R1 开始前必须查 experience/，R5 结束前必须输出 experience draft
>    （状态用 [hit]/[partial]/[miss]/[skip]/[saved]，见各 Step 定义）
```

### 改动 2 — R1~R5 总表新增"经验交互"列

| Step | 经验交互 |
|---|---|
| R1 | **读** experience/（hit/partial/miss 必报） |
| R2 ~ R2.7 | — |
| R3 | 参考命中经验的参数星级，可上调本次置信度 |
| R3.5 | — |
| R4 | 若命中经验有"复用片段"，优先引用 |
| R5 | **写** experience draft → 用户 review → 落盘 |

### 改动 3 — Step R1 模块加"前置检索"子段

插入到 R1 现有"本步产出"之前：

````markdown
**前置检索（进 R1 第一件事）**：
1. 从需求抽 `<slug>` 和 `<category>`
2. glob `experience/*/<slug>.md` → 精确命中则完整读入
3. 未精确命中则 glob `experience/<category>/*.md` → 读 ≤2 条 confidence≥3 的
4. R1 产出报告里用 `[hit]`/`[partial]`/`[miss]` 明报
5. 命中内容融进 search_plan.md 的"已知参数" + "预期坑"两节（标来源）
````

### 改动 4 — Step R5 模块重写"本步产出"

从原来的 1 项（完成汇总块）扩到 4 项：完成汇总 + draft 输出 + 用户 review + 落盘（或 skip）。完整模板见 §2 + §4。

### 改动 5 — "常见失败模式"追加 2 条

- **FM7 静默加载经验**：R1 检索命中但不在产出报告里报 `[hit]`，用户不知道哪些参数来自历史 → 诊断：任何写进 search_plan 的经验参数必须带来源注释
- **FM8 经验污染 R2.7**：经验里的"预期坑"被当事实直接信，跳 R2.7 视觉对齐 → 诊断：经验是先验，R2.7 的 Layer 2 验证仍必做

### 附录 — category 白名单

Playbook 末尾新增 `## Appendix A: category 白名单` 节，列 §1 的 25 个词。AI 分类时从白名单取最接近的，不自造。

## 6. 验证方法

### 结构核对（自动可查）

- `experience/` 目录存在且被 git 追踪
- `experience/README.md` 存在，含发布风险声明
- Playbook 顶部契约块第 5 条存在
- R1 模块含"前置检索"子段（grep `前置检索`）
- R5 模块含 "Experience Draft 模板"（grep `Experience Draft`）
- 失败模式清单含 FM7 / FM8
- Playbook 附录含 category 白名单

### 行为验证（真对话跑，落在 `tests/16-experience-dryrun/`）

- **Scenario D — 冷启动**：新对话"做红米 K80 Pro 手机壳"，`experience/` 空
  - 预期：R1 报 `[miss]`；R5 出 draft，用户说"保存"，落盘 `experience/phone-case/redmi-k80-pro.md`
  - 失败判据：R1 不报 miss / R5 不出 draft / 未 review 就写盘

- **Scenario E — 精确命中**：D 之后再跑一次"做红米 K80 Pro 手机壳"
  - 预期：R1 报 `[hit]` + 内容注入；R5 draft 与旧文件 diff，用户选 merge
  - 失败判据：重复建模没用经验 / 覆盖写丢历史坑

- **Scenario F — 同类命中**：跑"做小米 K70 手机壳"
  - 预期：R1 报 `[partial]` + 列出 redmi-k80-pro 作参考；**不直接复用参数**，但"预期坑"可借鉴
  - 失败判据：把 K80 Pro 的精确参数当 K70 的用

每个 Scenario 保存完整 AI 回复为 `run_D.md` / `run_E.md` / `run_F.md` 人工审阅。

### 不做

- experience 条目 linter / schema 自动校验
- 经验缓存自动迁移脚本

## 7. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| 私密数据泄漏（skill 仓公开时经验里可能有客户信息） | 高 | `experience/README.md` 明写发布风险，用户自律；长期可加 `experience/.private/` 放 `.gitignore` |
| 经验过期（产品改版） | 中 | `last_updated > 90 天` 自动降级为 `[partial]` 提醒核实 |
| draft 质量差用户懒得 review 直接 ok | 中 | "踩过的坑"节为空时 AI 显式问用户确认 |
| category 分类漂移（phone-case vs case vs 手机壳） | 低 | Playbook 附录固定白名单，AI 取最接近不自造 |
| merge 逻辑吃掉历史坑 | 中 | 硬写规则：参数去重，坑和片段一律 append 不去重 |

## 8. Out of Scope

- 经验条目版本管理（git log 就够）
- 跨用户经验共享（每个 skill 仓是单用户的）
- embedding 语义检索
- experience 自动集成进 Claude memory 系统（层次不同）
- Multi-Part / Single-Part Protocol 的经验缓存（留到参考物协议跑通后再推广）
- 新增 precheck 脚本 / 校验子 Agent

## 9. 验收标准

- `experience/` 目录存在且进 git，含 README.md
- Playbook 经改动 1~5，grep 验证 5 项标记存在
- Scenario D/E/F 三个行为验证都跑通：R1 产出报告里 `[hit]/[partial]/[miss]` 状态正确，R5 draft 按预期生成，落盘行为符合用户选择
- 历史 test 13 的 params.md 手工转成 `experience/phone-case/redmi-k80-pro.md` 作为首个 seed 条目，验证格式可用
