# build123d-cad R1~R5 Playbook-ification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the build123d-cad skill's Reference-Product Protocol (Step R1~R5) into a standalone Playbook with Artifact Gates so the AI can no longer skip steps silently.

**Architecture:** SKILL.md L55~L278 collapses to a ~30-line thin router. All R1~R5 step details move into a new single file `references/protocols/reference-product-playbook.md` that enforces Artifact Gates (each Step defines required output files + an in-reply "产出报告" contract). No code changes — existing scripts (`preprocess_reference.py`, `pixel_measure.py`, `visual_compare.py`, `multi_view_screenshot.py`, `contract_verify.py`) are referenced from Playbook command templates.

**Tech Stack:** Markdown only. Two repos touched:
- Skill repo: `/Users/liyijiang/.agents/skills/build123d-cad/` — SKILL.md edit + new Playbook
- Test repo: `/Users/liyijiang/work/build123d-cad-skill-test/` — dry-run test dir `tests/15-playbook-dryrun/`

**Path convention:** Playbook uses `references/<slug>/` at the consumer project's root (matches `tests/13-redmi-k80-pro/` → `references/redmi-k80-pro/` convention). `<test>` = per-test directory (e.g. `tests/14-xiaomi-k70-case/`). The spec's `refs/<slug>/` shorthand is expanded to `references/<slug>/` in the Playbook text for clarity.

---

## File Structure

### Skill repo (`/Users/liyijiang/.agents/skills/build123d-cad/`)

| File | Role | Responsibility |
|---|---|---|
| `SKILL.md` | Modified (L55~L278) | Becomes thin router: trigger + artifact summary table + jump to Playbook |
| `references/protocols/reference-product-playbook.md` | New | Single source of truth for R1~R5 execution. 8 Step modules + global 执行契约 header + failure modes appendix |

### Test repo (`/Users/liyijiang/work/build123d-cad-skill-test/`)

| File | Role | Responsibility |
|---|---|---|
| `tests/15-playbook-dryrun/README.md` | New | How to run behavior verifications A/B/C |
| `tests/15-playbook-dryrun/run_A.md` | New (empty template) | Conversation transcript for scenario A |
| `tests/15-playbook-dryrun/run_B.md` | New (empty template) | Conversation transcript for scenario B |
| `tests/15-playbook-dryrun/run_C.md` | New (empty template) | Conversation transcript for scenario C |

**Responsibility boundaries:**
- `SKILL.md` knows *when* to enter the Playbook, nothing else about R1~R5.
- `reference-product-playbook.md` owns the full execution contract. One file, not split, because the AI needs to read it top-to-bottom during a single conversation.
- `tests/15-playbook-dryrun/` is an evidence folder for the human operator, not runtime artifacts.

---

## Phase 0 — Prep

### Task 0: Sanity checks before editing

**Files:**
- Read-only check of `SKILL.md` line boundaries

- [ ] **Step 1: Verify current R1~R5 block boundaries in SKILL.md**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "^## 参考物建模流程\|^## 多部件 4 阶段流程\|^### Step R" SKILL.md
```

Expected output (approx — verify matches before proceeding):
```
55:## 参考物建模流程（Reference-Product Protocol）
62:### Step R1 — 识别 + 生成搜索计划（先告知，不执行）
89:### Step R2 — 执行搜集（用户确认后）
114:### Step R2.5 — 没有 STEP 模型时的反推流程（v3 新增）
131:### Step R2.7 — 参考图现实对齐检查（v3 新增）
147:### Step R3 — 生成 params.md（建模直接输入）
177:### Step R3.5 — 生成 Layer 0 参数合同（contract.yaml）
211:### Step R4 — 进入标准建模流程
268:### Step R5 — 收尾提示
280:## 多部件 4 阶段流程（Multi-Part Protocol）
```

If line numbers differ, RECORD the actual `## 参考物建模流程` and `## 多部件 4 阶段流程` line numbers — these define the replacement block for Task 11.

- [ ] **Step 2: Confirm the protocols directory does not already exist**

Run:
```bash
ls /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/ 2>&1
```

Expected: `No such file or directory`. If it exists, inspect contents before proceeding.

- [ ] **Step 3: Verify skill repo has a clean working tree**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git status --short
```

Expected: empty output (clean). If not clean, STOP and let the user decide whether to stash or commit first.

---

## Phase 1 — Playbook scaffold

### Task 1: Create the Playbook file with header + global 执行契约 block

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`

- [ ] **Step 1: Create the directory**

Run:
```bash
mkdir -p /Users/liyijiang/.agents/skills/build123d-cad/references/protocols/
```

- [ ] **Step 2: Write the header + 执行契约 block**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`

```markdown
# 参考物建模协议 Playbook（Reference-Product Playbook）

> **何时进入此 Playbook**：用户需求中出现已存在的具体产品型号（手机/开发板/舵机/传感器…）。
> 入口由 `SKILL.md` 的"参考物建模流程"路由段触发。

---

## 执行契约（进入此 Playbook 后对本次对话强制生效）

1. 每个 Step 完成后，**必须在当次回复里输出"产出报告"块**——列出本步 artifact 的 `[x]`（已产出）或 `[skip] reason=...`（显式跳过）。
2. **没写产出报告的 Step 视为未完成**，禁止进入下一步。
3. **跳步必须声明理由**，格式 `[skip] <step-id> reason=<具体理由>`。静默略过视为违规。
4. **Artifact 是硬约束**——用户接管某步也不例外（例如用户直接给 contract，AI 仍必须把内容落盘到约定路径）。
5. 遇到本步 artifact 缺失：回到本步补产，禁止写 `[x]` 骗过。发现上游缺失：在回复里明写 "回补 Step Rx" 并执行，禁止下行。

---

## R1~R5 Step 总表

| Step | 必须产出 | 允许跳过？ | 下一步分叉 |
|---|---|---|---|
| R1 识别 + 搜索计划 | `references/<slug>/search_plan.md` | 否 | → R2 |
| R2 执行搜集 | `references/<slug>/raw_specs.md` + `images/*` | 否 | 有 `model.step` → R3/R2.7；无 → R2.5 |
| R2.5 无 STEP 反推 | `references/<slug>/clean/*_scale.json` + `measurements.csv` | 仅 R2 已产出 `model.step` 时可 skip | → R2.7 |
| R2.7 参考图现实对齐 | `references/<slug>/clean/*_cropped.png` + `part_face_mapping.yaml` | 否（Layer 2 必做）；仅 "有 STEP + 不做视觉对比" 可 skip | → R3 |
| R3 生成 params.md | `references/<slug>/params.md`（含 ★ 置信度） | 否 | → R3.5 |
| R3.5 生成 contract.yaml | `tests/<test>/contract.yaml` | 否 | → R4 |
| R4 建模 | `tests/<test>/<part>.py` + OCP 自动预览 | 否 | → R5 |
| R5 收尾提示 | 回复中输出"完成汇总"块 | 否 | （终态） |

**术语**：
- `<slug>` = 产品短名（kebab-case），如 `redmi-k80-pro`
- `<test>` = 测试目录名，如 `14-xiaomi-k70-case`
- `<part>` = 部件脚本名，如 `xiaomi_k70_case`
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "feat(skill): scaffold reference-product-playbook with contract + totals table"
```

---

## Phase 2 — Step modules

### Task 2: Append Step R1 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R1 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R1 — 识别 + 生成搜索计划

**前置**：
- [x] 用户需求中明确提到一个具体产品型号

**本步产出（必须全部存在才允许进入下一步）**：
- `references/<slug>/search_plan.md`（列出 3~4 个待查来源 + 预期获取的资料类型）

**命令模板**：
```bash
SLUG=<kebab-case-product-name>
mkdir -p references/$SLUG
cat > references/$SLUG/search_plan.md <<'EOF'
# 搜索计划：<产品名>

## 目标
- 获取产品尺寸（长/宽/厚 + 关键特征位置）
- 获取官方产品图（至少正面 + 背面）
- 尝试获取 STEP 模型

## 搜索来源
1. 官网规格页 — <品牌官网 URL>
2. GSMArena / 电商规格 — <URL>
3. GrabCAD / Printables — STEP 模型搜索
4. iFixit / B 站拆解视频（兜底）
EOF
```

**AI 回报契约（完成后必须在回复里输出）**：
```
Step R1 产出报告
- [x] references/<slug>/search_plan.md  (4 来源，待用户确认)
下一步：等用户确认 → Step R2
```

**确认门 ✋** 用户确认后进入 R2。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R1 module"
```

---

### Task 3: Append Step R2 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R2 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R2 — 执行搜集

**前置**：
- [x] `references/<slug>/search_plan.md` 已写入并经用户确认

**本步产出（必须全部存在才允许进入下一步）**：
- `references/<slug>/raw_specs.md`（官网/电商文本规格，含尺寸关键数字）
- `references/<slug>/images/*.{jpg,png}`（至少 1 张产品图，建议正+背+侧各 1）
- （可选）`references/<slug>/model.step`（GrabCAD / 官网下载到的 3D 模型）

**命令模板**：
```bash
SLUG=<your-slug>
mkdir -p references/$SLUG/images

# 1) 抓取官网规格文本 → raw_specs.md（用 WebFetch 或 curl，精炼后写入）
# references/$SLUG/raw_specs.md 内容建议包含：
#   - 产品全名 + 发布年份
#   - 三围尺寸（长/宽/厚）
#   - 重量
#   - 摄像头/按键/接口位置（文字描述）

# 2) 下载官方图
curl -sL <img-url-1> -o references/$SLUG/images/official_01_front.jpg
curl -sL <img-url-2> -o references/$SLUG/images/official_02_back.jpg

# 3) 若 GrabCAD/官网有 STEP：
curl -sL <step-url> -o references/$SLUG/model.step
```

**AI 回报契约**（三种典型场景）：

场景 1：无 STEP
```
Step R2 产出报告
- [x] references/<slug>/raw_specs.md   (官网 + GSMArena 规格合并)
- [x] references/<slug>/images/        (3 张：正/背/侧)
- [skip] references/<slug>/model.step  (reason: GrabCAD 无收录)
下一步：Step R2.5（model.step 缺失 → 反推）
```

场景 2：有 STEP + 不做 Layer 2
```
Step R2 产出报告
- [x] references/<slug>/raw_specs.md
- [x] references/<slug>/images/
- [x] references/<slug>/model.step     (来源：GrabCAD)
下一步：Step R3（有 STEP + 不做视觉对比，[skip] R2.5 reason=已有 model.step，[skip] R2.7 reason=不做 Layer 2 视觉对比）
```

场景 3：有 STEP + 要做 Layer 2
```
Step R2 产出报告
- [x] references/<slug>/raw_specs.md
- [x] references/<slug>/images/
- [x] references/<slug>/model.step
下一步：Step R2.7（[skip] R2.5 reason=已有 model.step，但 R2.7 必做以支持 Layer 2）
```

**分叉判定**：R2 结束时 AI 必须向用户确认"本次是否需要 Layer 2 视觉对比"。
- 需要 + 无 STEP → R2.5 → R2.7 → R3
- 需要 + 有 STEP → R2.7 → R3（skip R2.5）
- 不需要 + 有 STEP → R3（skip R2.5 + R2.7）
- 不需要 + 无 STEP → R2.5（仍需反推尺寸） → R3（skip R2.7）
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R2 module with branching decision"
```

---

### Task 4: Append Step R2.5 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R2.5 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R2.5 — 无 STEP 时反推尺寸

**前置**：
- [x] Step R2 已产出 `references/<slug>/images/`
- [x] `references/<slug>/model.step` 不存在

**本步产出（必须全部存在才允许进入下一步）**：
- `references/<slug>/clean/<stem>_scale.json`（每张要测量的图 × 1）
- `references/<slug>/clean/<stem>_cropped.png`（同上）
- `references/<slug>/measurements.csv`（≥ 1 条关键特征测量值）

**命令模板**：
```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
SLUG=<your-slug>
STEM=official_01_back   # 对每张要测量的图都跑一次

# 1) 获取 bbox（首次：用 matplotlib ginput 手动标定左上+右下）
python3 -c "
from PIL import Image; import matplotlib.pyplot as plt
img = Image.open('references/$SLUG/images/$STEM.jpg')
plt.imshow(img); pts = plt.ginput(2)
x0,y0 = map(int, pts[0]); x1,y1 = map(int, pts[1])
print(f'--bbox {x0},{y0},{x1-x0},{y1-y0}')
"

# 2) 预处理：裁边 + 建 scale
python3 $SKILL/scripts/visual/preprocess_reference.py \
  references/$SLUG/images/$STEM.jpg \
  --bbox "<paste-from-step-1>" \
  --physical-length "<真实物理长度，如 162.2mm>" \
  --physical-axis <height 或 width> \
  --output-dir references/$SLUG/clean/

# 3) 像素测量关键点（原点 = 部件中心）
python3 $SKILL/scripts/visual/pixel_measure.py \
  references/$SLUG/clean/${STEM}_cropped.png \
  --scale references/$SLUG/clean/${STEM}_scale.json \
  --points "<x1,y1;x2,y2;x3,y3>" \
  --origin center \
  --output references/$SLUG/measurements.csv
```

**AI 回报契约**：
```
Step R2.5 产出报告
- [x] references/<slug>/clean/official_01_back_scale.json   (mm_per_px=0.26)
- [x] references/<slug>/clean/official_01_back_cropped.png
- [x] references/<slug>/measurements.csv                     (3 条：摄像头中心/主相机/电源键)
下一步：Step R2.7
```

**参考**：`references/reference-product/reverse-engineering.md`（5 种手段 A~E 的应用边界）
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R2.5 reverse-engineering module"
```

---

### Task 5: Append Step R2.7 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R2.7 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R2.7 — 参考图现实对齐检查

**前置**：
- [x] Step R2 已产出 `references/<slug>/images/`
- [x] 本次要做 Layer 2 视觉对比（若不做视觉对比 + 有 STEP，可 skip）

**本步产出（必须全部存在才允许进入下一步）**：
- `references/<slug>/clean/<stem>_cropped.png`（每张要进 Layer 2 的参考图，若 R2.5 已跑过可复用）
- `references/<slug>/clean/<stem>_scale.json`（同上）
- `references/<slug>/part_face_mapping.yaml`（语义面 → OCP Camera 枚举映射）

**命令模板**：
```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
SLUG=<your-slug>

# 1) 预处理每张要进 Layer 2 的参考图（若 R2.5 已跑过同图可跳过）
python3 $SKILL/scripts/visual/preprocess_reference.py \
  references/$SLUG/images/official_02_front.jpg \
  --bbox "<x,y,w,h>" --physical-length "<162.2mm>" --physical-axis height \
  --output-dir references/$SLUG/clean/

# 2) 基于模板写 part_face_mapping.yaml
cp $SKILL/references/verify/part-face-mapping-template.yaml \
   references/$SLUG/part_face_mapping.yaml
# 编辑内容：
#   - part: <产品 slug>
#   - coordinate_system.screen_normal: -Y (屏幕朝下) / +Y / ...
#   - face_mapping: FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM 各映射到 Camera 枚举
#   - face_labels: 每面一句中文描述
# 实战参考：tests/14-xiaomi-k70-case/part_face_mapping.yaml
```

**AI 回报契约**：
```
Step R2.7 产出报告
- [x] references/<slug>/clean/official_02_front_cropped.png
- [x] references/<slug>/clean/official_02_front_scale.json
- [x] references/<slug>/part_face_mapping.yaml            (6 face mappings，coord: screen -Y)
下一步：Step R3
```

**参考**：
- `references/verify/reference-image-preprocessing.md`（预处理 6 节规范）
- `references/verify/part-face-mapping-template.yaml`（模板）
- `references/verify/edge-comparison.md`（下游 Layer 2 阈值）

**特别提示**：
- 只要本次要做 Layer 2 视觉对比，R2.7 就必做——哪怕 R2 有 STEP。
- `part_face_mapping.yaml` 是 `multi_view_screenshot.py --face-mapping` 的强制输入。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R2.7 reality-alignment module"
```

---

### Task 6: Append Step R3 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R3 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R3 — 生成 params.md（建模直接输入）

**前置**：
- [x] Step R2（raw_specs.md 提供官方尺寸）
- [x] Step R2.7 已产出（若做 Layer 2）或 Step R2 已产出 `model.step`

**本步产出（必须全部存在才允许进入下一步）**：
- `references/<slug>/params.md`，结构必须包含：
  - `## 数据来源` 段（列出每个来源 + 置信度 ★）
  - `## 产品尺寸（建模直接使用）` 表（参数/数值/来源/置信度四列）
  - `## 配件建模参数建议` 表（壁厚/配合间隙/开孔余量 等工艺参数）

**模板**：
```markdown
# 参数表：<产品名> 配件建模参考

## 数据来源
- 官网：<url>  ★★★★★
- GSMArena：<url>  ★★★★
- STEP 模型：GrabCAD <url>  ★★★★★（如有）
- 反推测量：references/<slug>/measurements.csv  ★★★★

## 产品尺寸（建模直接使用）
| 参数 | 数值 | 来源 | 置信度 |
|------|------|------|--------|
| 长度 | 162.2mm | 官网 | ★★★★★ |
| 宽度 | 74.9mm | 官网 | ★★★★★ |
| 厚度 | 8.9mm | GSMArena | ★★★★ |
| 摄像头模组 | 38×38mm | 反推（手段 B） | ★★★★ |
| 摄像头凸起高度 | ~2mm | 特征比例推断（手段 D） | ★★ |

## 配件建模参数建议
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 壁厚 | 1.2mm | FDM 打印最小可靠壁厚 |
| 配合间隙（单侧） | +0.3mm | 确保装入顺畅 |
| 开孔余量（单侧） | +0.5mm | 防止遮挡关键接口 |
```

**置信度约定**（与 `references/reference-product/photo-annotation.md` 同步）：
- ★★★★★ 官网参数 / 规格书 / STEP 实测
- ★★★★ 三视图反推（手段 B）/ 已知基准测量（手段 C）
- ★★★ 拆机视频截帧反推（手段 E）
- ★★ 特征比例推断（手段 D）— 下游必须标记"待验证"
- ★ 未确认 / 待用户实测

**AI 回报契约**：
```
Step R3 产出报告
- [x] references/<slug>/params.md  (8 行尺寸表：5 项 ★★★★★ / 2 项 ★★★★ / 1 项 ★★)
下一步：等用户确认 → Step R3.5
```

**确认门 ✋** 用户确认后进入 R3.5。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R3 params.md module with confidence convention"
```

---

### Task 7: Append Step R3.5 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R3.5 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R3.5 — 生成 Layer 0 参数合同（contract.yaml）

**前置**：
- [x] Step R3 `params.md` 已用户确认

**本步产出（必须全部存在才允许进入下一步）**：
- `tests/<test>/contract.yaml`，结构必须包含：`meta` / `features` / `param_map`

**模板**：
```yaml
meta:
  product: "<产品名>"
  body_ref: {L: 162.2, W: 74.9, T: 8.9}

features:
  - name: camera_module
    type: rounded_rect
    face: back
    dims: {w: 38.0, h: 38.0, r: 8.0}
    pos: {cx: -13.0, cy: 55.0}
    constraints:
      - {type: on_face, value: back, locks: [Z]}
      - {type: edge_dist, ref: top, value: 26.4, tol: 2.0, locks: [Y]}
      - {type: edge_dist, ref: left, value: 24.9, tol: 2.0, locks: [X]}

param_map:
  camera_module.pos.cx: CAMERA_CX
  camera_module.pos.cy: CAMERA_CY
```

**要求**：
- 每个 feature 至少 3 条 constraints（覆盖 X / Y / Z 三轴）
- `_ratios` 归一化比例字段可选，但一旦填写须与绝对值一致

**静态检查**：
```bash
python3 /Users/liyijiang/.agents/skills/build123d-cad/scripts/validate/contract_verify.py \
  --contract tests/<test>/contract.yaml --check-only
```
期望：exit code 0 + "contract complete and consistent"。

**AI 回报契约**：
```
Step R3.5 产出报告
- [x] tests/<test>/contract.yaml           (3 features, 9 constraints, 静态检查通过)
下一步：等用户确认 → Step R4
```

**参考**：`references/verify/layer0-contract.md`

**确认门 ✋** 用户确认合同无误后进入 R4。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R3.5 contract.yaml module"
```

---

### Task 8: Append Step R4 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R4 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R4 — 进入标准建模流程

**前置**：
- [x] Step R3.5 `contract.yaml` 已用户确认

**本步产出（必须全部存在才允许进入下一步）**：
- `tests/<test>/<part>.py`（建模脚本，末尾带 OCP 自动预览块）
- OCP Viewer 实际打开并显示模型（可用截图或 `get_ports()` 的输出作为证据）

**路由**：
- 单个配件 → 走 `SKILL.md` "单部件简化流程（Single-Part Protocol）" Step 1~4（含 3 变体 OCP 对比）
- 多部件 → 走 `SKILL.md` "多部件 4 阶段流程（Multi-Part Protocol）" Phase 1~4

**建模完成后自动触发 Layer 1/2 验证链**：

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad

# Layer 1 合同运行时验证
python3 $SKILL/scripts/validate/contract_verify.py \
  --contract tests/<test>/contract.yaml \
  --params tests/<test>/params.json

# Layer 2 视觉对比（需要 R2.7 产出的 part_face_mapping.yaml）
python3 $SKILL/scripts/visual/multi_view_screenshot.py \
  tests/<test>/<part>.step \
  --mode ortho \
  --face-mapping references/<slug>/part_face_mapping.yaml

python3 $SKILL/scripts/visual/visual_compare.py \
  output/<part>_FRONT.png references/<slug>/clean/official_front_cropped.png \
  --reference-scale references/<slug>/clean/official_front_scale.json \
  --rendered-scale auto \
  --mode edge_overlay \
  --output output/compare_front.png
```

**AI 回报契约**：
```
Step R4 产出报告
- [x] tests/<test>/<part>.py              (Layer 1 pass)
- [x] OCP Viewer 预览已打开               (端口 3939)
- [x] Layer 2 edge_overlay: IoU=0.87     (≥0.85 阈值，pass)
下一步：Step R5
```

**Layer 2 失败反馈**：若 IoU < 0.85，按 `references/verify/feedback-diagnosis.md` 分根因回退：
- 根因 A（数据源错）→ 回补 R2/R3
- 根因 B（合同错）→ 回 R3.5 改 contract.yaml
- 根因 C（代码错）→ 修改建模代码
- 修复上限：L1×3 + L2×2 + 跨层×2 = 总计 ≤ 5 轮

**参考**：
- Layer 1：`references/verify/layer1-verification.md`
- Layer 2：`references/verify/layer2-visual.md` + `references/verify/edge-comparison.md`
- 反馈闭环：`references/verify/feedback-diagnosis.md`
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R4 modeling + verification module"
```

---

### Task 9: Append Step R5 module

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append R5 module**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## Step R5 — 收尾提示

**前置**：
- [x] Step R4 建模完成且 Layer 1 / Layer 2 通过（或已按反馈闭环修复完成）

**本步产出**（注意：R5 的产出是**当次回复里的一段文字**，不落盘）：
- 在回复末尾输出"完成汇总"块

**完成汇总块模板**：

```markdown
## 完成汇总

### 验证状态
- Layer 0（合同静态检查）：✅
- Layer 1（合同运行时验证）：✅
- Layer 2（视觉对比）：✅ IoU=0.87

### 置信度分布
- 尺寸 ★★★★★：5 项
- 尺寸 ★★★★：2 项
- 尺寸 ★★：1 项（摄像头凸起高度，建议用户实测后回填）

### 参考资料归档
- `references/<slug>/` 已完成使命，是否保留？
  - [ 保留 ]（作为设计依据，后续回改参数时复用）
  - [ 删除 ]（本次已落入 `params.md` + `contract.yaml`，原始资料可清）

### 下一步建议
- <Layer 2 IoU 偏低 → 建议回 R2.7 检查 face_mapping>
- <某特征置信度 ≤ ★★ → 建议用户实测后更新 params.md>
- <未出现异常 → 可进入 3D 打印 / CNC 流程>
```

**AI 回报契约**：
```
Step R5 产出报告
- [x] 完成汇总块已输出（上方）
- [ask] references/<slug>/ 保留 or 删除？
参考物建模协议 R1~R5 完成。
```
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add Step R5 wrap-up module"
```

---

### Task 10: Append 常见失败模式 appendix

**Files:**
- Modify: `references/protocols/reference-product-playbook.md` (append)

- [ ] **Step 1: Append failure modes section**

Append to `/Users/liyijiang/.agents/skills/build123d-cad/references/protocols/reference-product-playbook.md`:

````markdown

---

## 常见失败模式（test 13 / 14 沉淀）

### FM-1：bbox 越界
**现象**：`preprocess_reference.py` 报 `bbox out of image range`
**根因**：误以为图是竖版（height 主轴），实际是横版（width 主轴）；或直接复用他图的 bbox 数字
**诊断**：
```bash
python3 -c "from PIL import Image; print(Image.open('<img>').size)"
```
**修复**：根据实际 size 切换 `--physical-axis width` 或 `height` + 重新标 bbox

### FM-2：mm/px 反算
**现象**：测量值数量级异常（单位看起来像 µm 或 km）
**根因**：`--physical-length` 填成了图上像素数，而非真实物理长度
**诊断**：检查 `*_scale.json` 里 `mm_per_px`，合理区间通常是 0.05 ~ 1.0
**修复**：用真实物理长度（如 `162.2mm`）重跑 preprocess

### FM-3：face_mapping 写反
**现象**：Layer 2 每个面都 IoU < 0.3，整体对不上
**根因**：`part_face_mapping.yaml` 的 FRONT/BACK 与 OCP `Camera.FRONT/BACK` 的法线方向搞反
**诊断**：检查 `coordinate_system.screen_normal`，再逐条核对 `face_mapping` 条目
**修复**：参考实战样本 `tests/14-xiaomi-k70-case/part_face_mapping.yaml`，明确"屏幕朝 -Y → FRONT→BACK"的等价关系

### FM-4：R2.7 偷懒跳过
**现象**：AI 有 STEP 模型就直接跳 R3，后续 Layer 2 失败时才发现缺 `part_face_mapping.yaml`
**根因**：错误等同"有 STEP = R2.7 可跳"，忽略"做 Layer 2 就必做 R2.7"
**诊断**：在 R2 产出报告里必须显式答复"本次是否做 Layer 2"
**修复**：是 → R2.7 必做（只跳 R2.5）；否 → skip R2.7 + reason

### FM-5：置信度伪造
**现象**：params.md 里反推尺寸被标 ★★★★★
**根因**：AI 为了让验证通过，把低置信度尺寸标高
**诊断**：交叉检查 params.md "数据来源"段：若来自"反推/拆机/推断"，置信度不得 ≥ ★★★★
**修复**：如实填写置信度。允许 ★★ 尺寸进入下游建模，但 R5 完成汇总里要提醒用户实测

### FM-6：产出报告漏写
**现象**：AI 直接开始做下一步，没有先输出产出报告
**根因**：遗忘"执行契约"第 1 条
**诊断**：用户注意到回复里没有 `Step Rn 产出报告` 块
**修复**：立刻补一条产出报告，回补漏的 artifact，再继续
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): add failure modes appendix from test 13/14 lessons"
```

---

## Phase 3 — SKILL.md router swap

### Task 11: Replace SKILL.md L55~L278 with thin router

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`

- [ ] **Step 1: Re-verify replacement block boundaries**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "^## 参考物建模流程\|^## 多部件 4 阶段流程" SKILL.md
```
Record the two line numbers. The block to replace spans from the `## 参考物建模流程` line through the line immediately before `## 多部件 4 阶段流程` (inclusive of any `---` separator).

- [ ] **Step 2: Use Edit tool to replace the block**

Replace the entire span from `## 参考物建模流程（Reference-Product Protocol）` through (and including) the `---` line just before `## 多部件 4 阶段流程`.

New content:

````markdown
## 参考物建模流程（Reference-Product Protocol）

**触发条件**：需求中包含已存在的具体产品型号，例如：
「做红米 K80 的手机壳」「给树莓派 4B 做散热壳」「SG90 舵机安装座」

**执行方式**：进入 `references/protocols/reference-product-playbook.md` 按 checklist 走完 R1~R5。
Playbook 里的"执行契约"对本次对话强制生效——**每步必须在回复中输出产出报告，禁止静默跳步**。

**R1~R5 产出物总表**（详细契约见 Playbook）：

| Step | 必须产出 | 允许跳过？ |
|---|---|---|
| R1 识别 + 搜索计划 | `references/<slug>/search_plan.md` | 否 |
| R2 执行搜集 | `references/<slug>/raw_specs.md` + `images/*` | 否 |
| R2.5 无 STEP 反推 | `references/<slug>/clean/*_scale.json` + `measurements.csv` | 仅 R2 已产出 `model.step` 时可 skip |
| R2.7 参考图现实对齐 | `references/<slug>/clean/*_cropped.png` + `part_face_mapping.yaml` | 否（Layer 2 必做） |
| R3 params.md | `references/<slug>/params.md`（带置信度） | 否 |
| R3.5 contract.yaml | `tests/<test>/contract.yaml` | 否 |
| R4 建模 | `tests/<test>/<part>.py` + 自动预览 | 否 |
| R5 收尾 | 回复中输出完成汇总块 | 否 |

**分叉规则**：R2 完成后，有 `model.step` → R3（或 R2.7 若做 Layer 2）；无 `model.step` → R2.5 → R2.7 → R3。

---
````

Use the Edit tool with the old_string being the full block starting with `## 参考物建模流程（Reference-Product Protocol）` and ending with the `---` immediately before `## 多部件 4 阶段流程`. If the block is too large for a single Edit, split into an Edit that changes the first line's header line + multiple smaller edits — but the simplest path is a single exact-match Edit using the full block content captured in Step 1.

**Suggested procedure** (safer for large blocks):
1. Read the current SKILL.md with the Read tool, capturing lines from `## 参考物建模流程` through the `---` before `## 多部件`.
2. Use that exact captured text as `old_string` in Edit, and the new thin-router content above as `new_string`.

- [ ] **Step 3: Verify replacement**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "^### Step R" SKILL.md
wc -l SKILL.md
grep -n "^## 参考物建模流程\|^## 多部件 4 阶段流程" SKILL.md
grep -n "reference-product-playbook.md" SKILL.md
```

Expected:
- `grep -n "^### Step R" SKILL.md` → **0 lines** (all R steps are now in Playbook)
- `wc -l SKILL.md` → **≤ 1420 lines** (down from 1619)
- `^## 参考物建模流程` and `^## 多部件 4 阶段流程` both present, separated by ≤ 25 lines
- Playbook reference path present in SKILL.md

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "refactor(skill): slim SKILL.md R1~R5 section into Playbook router (~195 line reduction)"
```

---

## Phase 4 — Structure validation

### Task 12: Automated structure checks

**Files:**
- Read-only validation; no commits unless a fix is needed

- [ ] **Step 1: Check Playbook module count**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -c "^## Step R" references/protocols/reference-product-playbook.md
grep -c "^## 常见失败模式" references/protocols/reference-product-playbook.md
grep -c "^## 执行契约" references/protocols/reference-product-playbook.md
grep -c "^## R1~R5 Step 总表" references/protocols/reference-product-playbook.md
```

Expected:
- `^## Step R` → **8** (R1, R2, R2.5, R2.7, R3, R3.5, R4, R5)
- `^## 常见失败模式` → **1**
- `^## 执行契约` → **1**
- `^## R1~R5 Step 总表` → **1**

If any count is wrong, fix the corresponding Task 2~10 module before proceeding.

- [ ] **Step 2: Check every Step module has the required 3 blocks**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
for k in "前置" "本步产出" "AI 回报契约"; do
  n=$(grep -c "^\*\*$k" references/protocols/reference-product-playbook.md)
  echo "$k: $n (expected 8)"
done
```

Expected: each count = 8 (one per Step). If not, audit the missing module.

- [ ] **Step 3: Check SKILL.md size and router integrity**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
wc -l SKILL.md
grep -n "reference-product-playbook.md" SKILL.md
grep -c "^### Step R" SKILL.md
```

Expected:
- `wc -l SKILL.md` ≤ **1420**
- Playbook path appears ≥ 1 time in SKILL.md
- `^### Step R` count = **0**

- [ ] **Step 4: Smoke-verify Playbook references are all resolvable**

Run:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
for p in \
  references/verify/reference-image-preprocessing.md \
  references/verify/part-face-mapping-template.yaml \
  references/verify/edge-comparison.md \
  references/verify/layer0-contract.md \
  references/verify/layer1-verification.md \
  references/verify/layer2-visual.md \
  references/verify/feedback-diagnosis.md \
  references/reference-product/reverse-engineering.md \
  references/reference-product/photo-annotation.md \
  scripts/visual/preprocess_reference.py \
  scripts/visual/pixel_measure.py \
  scripts/visual/visual_compare.py \
  scripts/visual/multi_view_screenshot.py \
  scripts/validate/contract_verify.py; do
  test -e "$p" && echo "OK  $p" || echo "MISS $p"
done
```

Expected: every line prints `OK`. If any `MISS`, update the Playbook to remove/replace the broken reference.

- [ ] **Step 5: Commit only if any Playbook edit was needed to fix Step 1/2/4 failures**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git status --short
# If changes are present:
git add references/protocols/reference-product-playbook.md
git commit -m "docs(playbook): fix structure validation findings"
```

If `git status` is clean after Step 1~4, no commit needed.

---

## Phase 5 — Dry-run test scaffolding

### Task 13: Create dry-run evidence folder in test repo

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/README.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_A.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_B.md`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_C.md`

- [ ] **Step 1: Create the directory**

Run:
```bash
mkdir -p /Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun
```

- [ ] **Step 2: Write README.md with the 3 scenarios**

File: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/README.md`

```markdown
# Playbook Dry-Run 验证（R1~R5 行为回归）

本目录不跑代码——这里是"让 AI 按 Playbook 走一遍"的人工评估证据。

## 如何使用
1. 在一个全新对话里输入对应 scenario 的需求
2. AI 应该按 Playbook 输出 `Step Rn 产出报告` 块
3. 把 AI 完整回复（所有步骤的报告 + 中间产出）贴到对应 `run_*.md`
4. 对照"预期"核对，记录偏差

## Scenario A：复现 test 14 K70 壳（全量走完 R1~R5）
**Prompt**：「帮我做一个小米 K70 的手机壳，要跟官方图片做视觉对比」
**预期产出报告数**：8 次（R1 / R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5）
**失败判据**：
- 任一 Step 没有 `Step Rn 产出报告` 块 → 回改 Playbook 执行契约强度
- R2.7 被遗漏（最常见的 v3 问题）→ 加强 Playbook 的"FM-4"提示
- AI 直接写代码、跳过 R1/R2/R2.5/R2.7 → Playbook 入口指引不够明确

## Scenario B：有 STEP + 不做 Layer 2（走 R1/R2/R3/R3.5/R4/R5）
**Prompt**：「帮我做红米 K80 Pro 的手机壳。GrabCAD 上有 STEP，我只要模型能打印就行，不用做视觉对比」
**预期产出报告数**：**6 次**（R1 / R2 / R3 / R3.5 / R4 / R5，R2.5 + R2.7 显式 skip）
**关键检查**：
- R2 产出报告末尾必须显式声明 `[skip] R2.5 reason=已有 model.step` + `[skip] R2.7 reason=不做 Layer 2`
- R3~R5 以 STEP 为主要尺寸来源，params.md 置信度应 ≥ ★★★★
**失败判据**：
- AI 硬跑 R2.5 反推 → Playbook 分叉规则表述不清
- AI 静默 skip 不写 reason → 回改执行契约第 3 条为更严

## Scenario C：有 STEP + 要做 Layer 2（陷阱场景）
**Prompt**：「帮我做红米 K80 Pro 的手机壳。GrabCAD 上有 STEP，但我还想跟官方照片做视觉对比」
**预期产出报告数**：**7 次**（R1 / R2 / R2.7 / R3 / R3.5 / R4 / R5，只 skip R2.5）
**关键检查**：
- R2 产出报告末尾显式 `[skip] R2.5 reason=已有 model.step`，但 R2.7 必须跑
- R2.7 产出 `part_face_mapping.yaml` + 参考图 cropped/scale
- Layer 2 对比结果在 R4 报告里出现 IoU 数字
**失败判据**：
- AI 把"有 STEP"等同于"跳 R2.7" → Playbook R2.7 段"特别提示"需要加粗/重写
- Layer 2 执行失败但没按 feedback-diagnosis 回退 → 回 Playbook R4 加强

## 审阅流程
1. 跑 A/B/C 三个对话，分别粘贴到 `run_A.md` / `run_B.md` / `run_C.md`
2. 每个 run_*.md 末尾加一段"评估"：
   - 产出报告计数是否匹配预期
   - 哪一步被跳/漏
   - 需要回改 Playbook 的具体位置（行号 + 建议）
3. 所有偏差汇总到 skill 仓的 Playbook 修订 PR 里
```

- [ ] **Step 3: Write empty run_A/B/C templates**

File: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_A.md`

```markdown
# Scenario A — 复现 test 14 K70 壳

**日期**：（待填）
**对话模型**：（待填）
**Playbook 版本**：（对应 skill 仓 commit hash）

## 用户 prompt
（粘贴）

## AI 完整回复
（粘贴，完整保留所有 `Step Rn 产出报告` 块）

## 评估
- 产出报告数：__ / 8
- 缺失 Step：（列出）
- 违约点：（列出）
- Playbook 修订建议：（列出行号 + 建议）
```

File: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_B.md`

```markdown
# Scenario B — 有 STEP + 不做 Layer 2

**日期**：（待填）
**对话模型**：（待填）
**Playbook 版本**：（对应 skill 仓 commit hash）

## 用户 prompt
（粘贴）

## AI 完整回复
（粘贴）

## 评估
- 产出报告数：__ / 6
- R2.5 + R2.7 是否正确 skip 且带 reason：__
- 违约点：（列出）
- Playbook 修订建议：（列出行号 + 建议）
```

File: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_C.md`

```markdown
# Scenario C — 有 STEP + 要做 Layer 2（陷阱）

**日期**：（待填）
**对话模型**：（待填）
**Playbook 版本**：（对应 skill 仓 commit hash）

## 用户 prompt
（粘贴）

## AI 完整回复
（粘贴）

## 评估
- 产出报告数：__ / 7
- R2.5 skip + R2.7 必做 + 带 reason：__
- Layer 2 IoU：__
- 违约点：（列出）
- Playbook 修订建议：（列出行号 + 建议）
```

- [ ] **Step 4: Commit in test repo**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/15-playbook-dryrun/
git commit -m "test: add Playbook dry-run evidence folder with 3 scenarios (A/B/C)"
```

---

## Phase 6 — End-to-end acceptance

### Task 14: Run Scenario A as first smoke test (optional but recommended)

**Files:**
- Modify: `/Users/liyijiang/work/build123d-cad-skill-test/tests/15-playbook-dryrun/run_A.md`

> Only the human operator can execute this task because it requires launching a fresh Claude Code conversation and observing output.

- [ ] **Step 1: Start a fresh conversation in the test repo**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
claude  # or however the user typically starts a fresh conversation
```

- [ ] **Step 2: Paste the Scenario A prompt**

Prompt: `帮我做一个小米 K70 的手机壳，要跟官方图片做视觉对比`

- [ ] **Step 3: Record the conversation**

Copy the AI's entire multi-turn response (through to Step R5 完成汇总块) and paste into `tests/15-playbook-dryrun/run_A.md`.

- [ ] **Step 4: Fill in the 评估 section**

Check:
- Are there 8 distinct `Step Rn 产出报告` blocks?
- Is R2.7 present?
- Are any Steps skipped with reason vs silent?

If Scenario A passes, Scenarios B and C can be scheduled separately.

- [ ] **Step 5: Commit the recorded run**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/15-playbook-dryrun/run_A.md
git commit -m "test(playbook): record Scenario A dry-run (K70 full flow)"
```

---

## Acceptance Criteria (spec §9)

- ✅ SKILL.md R1~R5 段压缩到 ≤ 30 行的路由；`grep -n "^### Step R" SKILL.md` 输出 0 行
- ✅ SKILL.md 总行数 ≤ 1420
- ✅ `references/protocols/reference-product-playbook.md` 存在，含：
  - 顶部"执行契约"块
  - "R1~R5 Step 总表"
  - 8 个 Step 模块（R1 / R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5），每个含前置 / 本步产出 / 命令模板 / AI 回报契约 四段
  - 末尾"常见失败模式" 6 条
- ✅ Playbook 引用的外部文件（scripts + references/verify/*）全部存在
- ✅ `tests/15-playbook-dryrun/` 有 README + run_A/B/C 模板
- ⚠️ Scenario A/B/C 的行为验证由操作者人工跑，不在本 plan 范围的自动化内

## Out of Scope (spec §8)

- ❌ Multi-Part / Single-Part Protocol 的 Playbook 化（下一轮）
- ❌ `references/` 目录整体重排
- ❌ 新增 precheck 脚本 / YAML linter
- ❌ AI 自检 sub-agent

---

## Summary Task Count

| Phase | Tasks | Produces |
|---|---|---|
| 0 Prep | 1 | Sanity checks |
| 1 Playbook scaffold | 1 | File created |
| 2 Step modules | 9 | 8 Steps + 常见失败模式 appendix |
| 3 SKILL.md swap | 1 | Thin router in place |
| 4 Structure validation | 1 | Automated checks pass |
| 5 Dry-run folder | 1 | README + run_A/B/C templates |
| 6 Smoke run | 1 (optional) | Scenario A evidence |
| **Total** | **14 tasks** | 1 new file + 1 modified file in skill repo + 4 new files in test repo |

**Estimated effort**: 2~3 hours. Most time is careful drafting + committing; no code tests.
