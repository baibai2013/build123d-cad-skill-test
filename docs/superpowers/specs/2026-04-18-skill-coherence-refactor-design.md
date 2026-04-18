# build123d-cad skill 连贯性重构设计

**日期**：2026-04-18
**范围**：SKILL.md 路由层 + `references/protocols/` 目录 + `references/INDEX.md`
**不改**：references/verify/、reference-product/、parts/、process/、assembly/、simulation/ 等子文档内容；SKILL.md 的 description / name / 触发词
**驱动问题**：SKILL.md 把 R1~R5 产出物总表完整复述了一遍，AI 读完路由段就"以为自己懂了"，不再打开 Playbook 本体 → 凭记忆走 → 跳步 / 漏产出报告 / 伪造置信度
**核心机制**：SKILL.md 去内容化 + 三流程 Playbook 化 + Quote-back 强制证据 + INDEX 统一导航
**前置依赖**：`docs/superpowers/specs/2026-04-18-experience-cache-design.md` 已实施完成（经验缓存机制落地，Playbook 执行契约已含第 6 条）

---

## 1. 问题陈述

SKILL.md 当前 1419 行。根因三条：

1. **信息双写**：L63-L74 把 Playbook 里的"R1~R5 产出物总表"完整复述 8 行，AI 读这段就满足了
2. **视觉暗示诱导**：L49 路由表用 `👇 下方内容` 强化 "内容就在 SKILL.md 下方"
3. **缺硬证据**：AI 是否真打开 Playbook 无法验证，只能事后发现跳步

同样的问题也发生在单/多部件流程——Step 1~4 和 Phase 1~4 直接写在 SKILL.md 里 200 多行，AI 根本不需要 Read 任何文件。

## 2. 架构

```
/Users/liyijiang/.agents/skills/build123d-cad/
├── SKILL.md                                    1419 → ~200 行（纯路由 + 跨流程规则）
└── references/
    ├── INDEX.md                                 新增：场景路由 + 目录地图
    └── protocols/
        ├── README.md                            新增：三 Playbook 交叉索引 + 骨架模板
        ├── reference-product-playbook.md        已存在（experience-cache 修订后的状态）
        ├── single-part-playbook.md              新增：Step 1~4 单部件
        └── multi-part-playbook.md               新增：Phase 1~4 多部件
```

**分工**：
- SKILL.md = 入口路由。角色规则 + 准入序列 + 流程路由表，止于"Read 哪个 Playbook"。
- Playbook = AI 执行期单一真实来源。进入 Playbook 后 SKILL.md 其它内容不再影响决策。
- INDEX.md = 跨目录兜底导航（SKILL.md 路由表覆盖不到时用）。

## 3. SKILL.md 改动

### 3.1 删除

- L47-L51 流程路由表（去 emoji 和 `👇` 暗示）→ 重写，见 3.2
- L55-L78 参考物建模流程详细段（产出物总表）→ 只保留 4 行路由子段
- 当前 "单部件简化流程（Single-Part Protocol）" 全段 → 只保留 4 行路由子段
- 当前 "多部件 4 阶段流程（Multi-Part Protocol）" 全段 → 只保留 4 行路由子段
- 凡含 `### Step ` / `### Phase ` 的详细段落一律搬走

### 3.2 新增

**A. SKILL.md 头部新增"AI 执行准入序列"块**（插在"角色规则"之前）：

```markdown
## AI 执行准入序列（每次会话第一件事）

1. 读本 SKILL.md 的"流程路由"表
2. 匹配场景 → Read 对应 Playbook
3. Playbook 顶部契约生效后再开始答题
4. Playbook 引用的子文档按需 Read
5. 禁止跳过 Playbook 直接从 references/<子领域>/ 自拼流程
```

**B. 流程路由表重写**（替换现 L47-L51）：

```markdown
| 需求类型 | 判断 | 必读路径（Read 后才能开始回答） |
|---|---|---|
| 参考物建模 | 型号名出现 | references/protocols/reference-product-playbook.md |
| 单部件 | 1 个独立实体 | references/protocols/single-part-playbook.md |
| 多部件 | ≥2 个 / 仿真 / 装配 | references/protocols/multi-part-playbook.md |
```

**C. 三个流程路由子段**（统一 4 行模板，替换原有所有流程段落）：

```markdown
## 参考物建模流程

**触发**：需求含已存在产品型号（红米 K80、树莓派 4B、SG90 舵机…）。

**唯一执行路径**：立即 Read `references/protocols/reference-product-playbook.md`，按 Playbook 的 R1~R5 执行。

**SKILL.md 本文件不含 R1~R5 细节**——凭记忆走视为违规，必须回补 Read + Quote-back。

**Quote-back 强制**：每个 Step 产出报告第一行引用 Playbook 原文（格式见 Playbook §执行契约）。
```

单部件 / 多部件同构。

### 3.3 SKILL.md 目标体量

- 总行数 ≤ 300
- `grep "^### Step \|^### Phase " SKILL.md` = 0 条
- 保留：角色规则 12 条、准入序列、流程路由表、三个 4 行路由子段、OCP 预览标准模板、跨流程规则（角色规则 8~12 条里的验证/装配/工艺/仿真引导）

## 4. Quote-back 机制

### 4.1 格式

每个 Step 产出报告**第一行**必须是：

```
引自 <playbook-basename> §Step <Rn> / <小标题>：
  "<原文一行>"
```

完整示例：

```
Step R2.7 产出报告
引自 reference-product-playbook.md §Step R2.7 / 本步产出：
  "references/<slug>/clean/<stem>_cropped.png（每张要进 Layer 2 的参考图）"
- [x] references/k80/clean/back_cropped.png
- [x] references/k80/part_face_mapping.yaml
下一步：Step R3
```

### 4.2 锚点约定

- 锚点用"标题 + 小标题"（`§Step R2.7 / 本步产出`），不用裸行号
- 行号会漂，标题稳定
- 小标题取自 Playbook 每 Step 模块内的加粗段标题（`**本步产出**`、`**前置**`、`**AI 回报契约**`）

### 4.3 三种违规

- **缺 Quote-back** → 视为没读 Playbook，回补 Read + 重出产出报告
- **引错 Step**（R3 报告引 R2.7 原文）→ 回补正确引用
- **原文捏造**（与 Playbook 实际不符）→ 回补 + 警告

### 4.4 契约集成

**参考物 Playbook 执行契约段新增第 7 条**（experience-cache 已用第 6 条，本次顺延第 7 条）：

```
7. 每个 Step 产出报告第一行必须是 Quote-back。
   格式：引自 <file> §Step Rn / <小标题>："<原文>"
   缺 Quote-back、引错 Step、原文与文件不符 = 违规，必须回补。
```

**失败模式新增 FM-9**（接 experience-cache 的 FM-7/FM-8 之后）：

```
FM-9 Quote-back 伪造：AI 写了 Quote-back 但原文与 Playbook 实际不符
诊断：grep 本次引用的原文在 Playbook 里找不到
修复：AI 必须重新 Read 对应 Step 原文后重出产出报告
```

### 4.5 Playbook 内部同步改动

三个 Playbook 每个 Step 模块的"AI 回报契约"示例块首行加 Quote-back 示范，让 AI 有可复制模板。改动范围：
- reference-product-playbook.md：R1/R2/R2.5/R2.7/R3/R3.5/R4/R5 共 8 个回报示例
- single-part-playbook.md：S1/S2/S3/S4 共 4 个回报示例
- multi-part-playbook.md：P1/P2/P3/P4 共 4 个回报示例

## 5. 单 / 多部件 Playbook 化

### 5.1 统一骨架（三 Playbook 共用）

```
顶部：进入条件 + 执行契约 1~7 条
中部：Step / Phase 总表（本步产出 / 允许跳过 / 下一步）
下部：每个 Step / Phase 详细模块（前置 + 本步产出 + 命令模板 + AI 回报契约含 Quote-back 示范）
底部：常见失败模式（FM-xx，初版可空）
```

骨架模板写进 `references/protocols/README.md`。

### 5.2 `single-part-playbook.md`

**内容来源**：当前 SKILL.md 的"单部件简化流程（Single-Part Protocol）Step 1~4"。

**Step 结构**：
- S1 需求拆解（输出需求拆解报告）
- S2 三变体设计（3 个 .py 变体 + OCP 对比 + 用户选定）
- S3 最终建模（`<part>.py` + OCP 预览自动触发）
- S4 导出 + 工艺提示（`<part>.step` 或 `.stl` + 3D 打印 / CNC / 激光约束清单）

### 5.3 `multi-part-playbook.md`

**内容来源**：当前 SKILL.md 的"多部件 4 阶段流程（Multi-Part Protocol）Phase 1~4"。

**Phase 结构**：
- P1 需求拆解 + 专家咨询（需求拆解报告 + 确认门 ✋）
- P2 部件级建模（每部件 3 变体 + OCP 对比，含确认门）
- P3 装配 / 关节（`<asm>.py` + Joint 方案）
- P4 导出 + Layer 1/2 验证（对装配体做几何验证）

### 5.4 搬运规则

- 内容从 SKILL.md 搬到新 Playbook 后，SKILL.md 对应原文**整段删除**
- 不在 SKILL.md 留副本（防止信息双写）
- 每个 Step / Phase 加 "AI 回报契约 + Quote-back 示范"（§4.5）
- `## 常见失败模式` 节如果 SKILL.md 现文没归纳 → 保持空 + 注释 "等 test 沉淀"
- 不强行造失败模式

## 6. references/INDEX.md 设计

### 6.1 定位

跨目录场景路由 + 目录地图。不强制每次 Read——SKILL.md 路由表能覆盖的场景直接跳 Playbook；只有"三场景不符合"或"Playbook 内部引用的子文档找不到"时兜底用 INDEX。

### 6.2 内容

```markdown
# references/ 导航索引

## 场景路由（兜底表）

| 用户想做什么 | 先 Read | 后续可能用到 |
|---|---|---|
| 做某型号配件 | protocols/reference-product-playbook.md | verify/, reference-product/ |
| 单个零件 | protocols/single-part-playbook.md | parts/ |
| 多部件 / 装配 | protocols/multi-part-playbook.md | assembly/, simulation/ |
| 曲面建模 | parts/surface-modeling.md | parts/cheatsheet.md |
| 工艺约束 | process/{3d-printing,cnc,laser}.md | — |
| 仿真 / IK | simulation/ | peter-corke/simulation-philosophy.md |

## 目录职责（一行一目录）

- protocols/          三大流程 Playbook（AI 执行期 SSOT）
- verify/             Layer 0/1/2 + 反馈闭环
- reference-product/  参考物建模子方法论（反推 / 标注 / 摄影）
- parts/              API cheatsheet + 曲面建模
- process/            3D 打印 / CNC / 激光工艺
- assembly/           装配模式 + 爆炸动画
- simulation/         FK / IK / 步态 / URDF
- peter-corke/        仿真哲学

## 准入原则

- 进 Playbook 是唯一合法流程入口
- 禁止从 references/<子领域>/ 自拼流程（会跳步）
- Playbook 内部引用的子文档按需 Read
```

### 6.3 与 protocols/README.md 的边界

- `references/INDEX.md` = 跨目录总图
- `protocols/README.md` = protocols 内部三 Playbook 交叉索引 + 骨架模板

两者不重叠：INDEX 指向 `protocols/` 作为一个整体，README 负责 `protocols/` 内部导航。

## 7. 验证方法

### 7.1 结构核对（自动可查）

- `wc -l SKILL.md` ≤ 300
- `grep -n "^### Step \|^### Phase " SKILL.md` = 0
- SKILL.md 头部含 `## AI 执行准入序列`
- `ls references/protocols/` 含 README.md + 3 个 Playbook
- `references/INDEX.md` 存在
- 三个 Playbook 顶部执行契约各 7 条
- 每个 Playbook 每个 Step / Phase 回报示例首行含 `引自 ` 前缀
- 参考物 Playbook 失败模式含 FM-9

### 7.2 行为验证（真对话，落在 `tests/17-skill-optimization-dryrun/`）

- **Scenario G — 参考物**：新对话"做某型号手机壳"
  - 预期：AI Read 参考物 Playbook → 每 Step 产出报告含 Quote-back → R1~R5 完整走完
  - 失败判据：没 Read / 缺 Quote-back / 原文捏造 / 跳 Step

- **Scenario H — 单部件**：新对话"做一个齿轮"
  - 预期：AI Read single-part-playbook → S1~S4 含 Quote-back
  - 失败判据：照当前 SKILL.md 记忆走 / 直接给代码不走 Step

- **Scenario I — 多部件**：新对话"做带舵机的机械臂"
  - 预期：AI Read multi-part-playbook → P1~P4 含 Quote-back + 确认门
  - 失败判据：跳 Phase / 缺确认门 / 缺 Quote-back

每个 Scenario 保存完整 AI 回复为 `run_G.md` / `run_H.md` / `run_I.md` 人工审阅。

### 7.3 回归验证

- test 13（红米 K80 Pro 手机壳）重跑：R1~R5 能走完，不因路由段瘦身而跳步
- test 14（小米 K70 手机壳）重跑：R2.7 仍必做、face_mapping.yaml 仍生成

### 7.4 不做

- Playbook 格式 linter
- Quote-back 原文自动校验脚本
- SKILL.md 自动瘦身工具

## 8. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| Quote-back 增加 token 消耗（每 Step 多 1~2 行） | 低 | 可接受；对比一次跳步导致的回补成本更低 |
| 单/多部件内容搬运破坏已跑通的 test 行为 | 中 | Scenario H/I 行为验证 + test 13/14 回归 |
| 三 Playbook 共享骨架但 Step 前缀不一致（R/S/P） | 低 | 接受差异，骨架只统一契约 + 总表 + 回报模板 |
| SKILL.md 太瘦 AI 找不到角色规则 | 低 | 准入序列 + 角色规则 12 条保留 |
| 准入序列 / 路由段被 AI 扫读跳过 | 中 | Quote-back 是事后补救；准入序列 + 路由段本身无强证据机制，靠规则叠加 |
| 跟 experience-cache 契约条号冲突 | 低 | 严格声明 experience-cache 先实施，本次顺延第 7 条 |

## 9. Out of Scope

- 不改 `references/verify/`、`reference-product/`、`parts/`、`process/`、`assembly/`、`simulation/`、`peter-corke/` 子文档内容
- 不加 linter / 自动校验脚本 / precheck 子 Agent
- 不改 experience-cache 设计本身（仅 Playbook 契约条号顺延）
- 不改 SKILL.md 的 description / name / 触发词（skill 发现机制不动）
- 不新造失败模式（除 Quote-back 违规的 FM-9）
- 不做 SKILL.md 其它段落的重写（OCP 预览标准模板、Layer 验证引导段原样保留）
- 不动 `assets/` 目录

## 10. 验收标准

- SKILL.md ≤ 300 行，grep 7 项结构核对全通过
- `references/protocols/` 含 README + 3 个 Playbook，每个 Playbook 顶部契约 7 条
- `references/INDEX.md` 存在且含 3 节
- 每个 Playbook 每个 Step / Phase 回报示例首行含 Quote-back 示范
- 参考物 Playbook 失败模式含 FM-9
- Scenario G / H / I 三个行为验证 pass（AI 真 Read + 真 Quote-back + 不跳步）
- test 13 / test 14 回归跑通，无行为回退
