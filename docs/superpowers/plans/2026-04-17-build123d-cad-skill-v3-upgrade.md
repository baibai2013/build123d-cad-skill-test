# build123d-cad Skill v3 升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 test 13/14 实战中的临时脚本和方法论升级为 build123d-cad skill 的复用资产（P0 视觉验证工具链 + 现实对齐预处理；P1 参考物反推方法论），保证下一个参考物建模 task 开箱可用。

**Architecture:** 全部新增在 skill repo `scripts/visual/` 和 `references/verify/`、`references/reference-product/` 三个目录。不改动现有 deprecated `scripts/validate/visual_compare.py`（已迁移到 cad-vision-verify 姊妹 skill）。新工具聚焦在"几何对齐 + 现实图预处理"这一块，和姊妹 skill 的 AI 视觉编排互补。

**Tech Stack:** Python 3.11+、build123d 0.10.0、ocp_vscode、Pillow (PIL)、numpy、opencv-python、matplotlib、PyYAML。所有依赖现有环境已具备（cad-vision-verify skill 已经引入）。

---

## Spec Source

所有任务基于 `docs/superpowers/specs/2026-04-17-build123d-cad-skill-v3-upgrade-design.md`。spec 章节映射：
- §3 → Phase 1~2（P0 工具链 5 个脚本）
- §4 → Phase 6（P1 反推方法论）
- §5 → Phase 1 Task 1 + Phase 3 Task 6/7（现实对齐预处理）
- §6 → 本计划**不包含**（P2 已明确延后）

## Skill Repo Path

所有新增文件都写到 **`/Users/liyijiang/.agents/skills/build123d-cad/`** 下，不是测试仓库。测试仓库 `/Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/` 仅用于 Phase 5 和 Phase 7 的验收跑批。

---

## File Structure

```
/Users/liyijiang/.agents/skills/build123d-cad/
├── SKILL.md                                              # 修改：Step R2.5 + R2.7 + Layer 2 桥接段
├── scripts/
│   └── visual/                                           # 🆕 新目录
│       ├── __init__.py                                   # 🆕 空文件（让 tests/ 能 import 上层脚本）
│       ├── multi_view_screenshot.py                      # 🆕 P0（Task 7）
│       ├── skybox_unfold.py                              # 🆕 P0（Task 8）
│       ├── visual_compare.py                             # 🆕 P0（Task 5）
│       ├── pixel_measure.py                              # 🆕 P0（Task 4）
│       ├── preprocess_reference.py                       # 🆕 P0（Task 3）
│       ├── annotate_reference.py                         # 🆕 P1（Task 14）
│       └── tests/
│           ├── __init__.py                               # 🆕
│           ├── test_preprocess_reference.py              # 🆕 P0（Task 3）
│           ├── test_pixel_measure.py                     # 🆕 P0（Task 4）
│           ├── test_visual_compare.py                    # 🆕 P0（Task 5）
│           ├── test_annotate_reference.py                # 🆕 P1（Task 14）
│           ├── run_all_tests.py                          # 🆕 P0（Task 2）
│           └── fixtures/                                 # 🆕 合成测试图
│               ├── synthetic_phone_front.png             # 在 Task 2 生成
│               ├── synthetic_phone_back.png              # 在 Task 2 生成
│               └── generate_fixtures.py                  # 🆕 P0（Task 2）
└── references/
    ├── verify/
    │   ├── multi-view-protocol.md                        # 🆕 P0（Task 9）
    │   ├── edge-comparison.md                            # 🆕 P0（Task 10）
    │   ├── reference-image-preprocessing.md              # 🆕 P0（Task 11）
    │   └── part-face-mapping-template.yaml               # 🆕 P0（Task 12）
    └── reference-product/                                # 🆕 新目录
        ├── reverse-engineering.md                        # 🆕 P1（Task 15）
        └── photo-annotation.md                           # 🆕 P1（Task 16）
```

**现有 skill 已存在的资产（不改动，仅在新文档中 cross-link）**：
- `scripts/validate/visual_compare.py` ← DEPRECATED，已迁到 cad-vision-verify
- `references/verify/layer2-visual.md` ← 仍权威，新 `multi-view-protocol.md` 链接过去
- `references/verify/feedback-diagnosis.md` ← 不动

---

## Design Decisions Locked

1. **测试框架**：skill 无 pytest，用标准 `unittest` + `python3 -m unittest` 运行。测试脚本放在 `scripts/visual/tests/`，单独可运行。
2. **OCP 依赖脚本的测试策略**：`multi_view_screenshot.py` / `skybox_unfold.py` / `annotate_reference.py` 依赖运行中的 OCP Viewer。这三个脚本 **不写自动化测试**，只写 smoke 说明（task 中 manual verification 步骤），由 Phase 5/7 集成验收。纯图像处理脚本（preprocess / pixel_measure / visual_compare）走 TDD。
3. **脚本末尾 OCP 预览块**：只有真正生成 build123d Part 的脚本才需要。本计划的 6 个脚本全部是工具脚本（不产 Part），所以**不加** OCP 预览块。spec §9 第 4 条验收标准对工具脚本不适用——task 11 会更新 spec 对应措辞。
4. **CLI 参数解析**：统一用 `argparse`。每个脚本 `--help` 必须能打印完整用法。
5. **错误处理原则**：图像文件不存在 / bbox 越界 / scale 非数字 → `sys.exit(2)` + stderr 明确原因。正常流程 bug 不做 try/except 吞错。

---

## Execution Phases Overview

| Phase | Tasks | 目的 | 验收方式 |
|---|---|---|---|
| 0 | Task 1 | 目录 + 空 `__init__` | `git status` 看到空目录骨架 |
| 1 | Task 2 | 合成 fixture + 测试 runner | `python3 run_all_tests.py` exit 0（空测试通过） |
| 2 | Task 3~5 | 纯图像处理三件套（TDD） | `run_all_tests.py` 每任务加测试后仍通过 |
| 3 | Task 6 | `part_face_mapping.yaml` template + loader | 在 Task 7 被消费 |
| 4 | Task 7~8 | OCP 依赖脚本 | 在 test 14 跑 smoke，生成 7 视图 + skybox |
| 5 | Task 9~12 | P0 references 文档 | 人工 review |
| 6 | Task 13 | SKILL.md P0 桥接段 | grep 确认插入点正确 |
| 7 | Task 14 | P0 端到端验收 | test 14 K70 目录下完整跑一遍 P0 链路 |
| 8 | Task 15~17 | P1 工具 + 文档 + SKILL.md R2.5 | 同上 |
| 9 | Task 18 | P1 端到端验收 | test 14 K70 做一次"无 STEP"反推实操 |

---

## Phase 0 — Scaffolding

### Task 1: 创建目录骨架

**Files:**
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/__init__.py`
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/__init__.py`
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/fixtures/.gitkeep`
- Create: `/Users/liyijiang/.agents/skills/build123d-cad/references/reference-product/.gitkeep`

- [ ] **Step 1: 创建空 `__init__` 和 `.gitkeep` 文件**

```bash
SKILL_ROOT=/Users/liyijiang/.agents/skills/build123d-cad
mkdir -p $SKILL_ROOT/scripts/visual/tests/fixtures
mkdir -p $SKILL_ROOT/references/reference-product
touch $SKILL_ROOT/scripts/visual/__init__.py
touch $SKILL_ROOT/scripts/visual/tests/__init__.py
touch $SKILL_ROOT/scripts/visual/tests/fixtures/.gitkeep
touch $SKILL_ROOT/references/reference-product/.gitkeep
```

- [ ] **Step 2: 验证目录结构**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
ls scripts/visual/
ls scripts/visual/tests/
ls references/reference-product/
```
Expected: 两个 `__init__.py` + `tests/fixtures/.gitkeep` + `reference-product/.gitkeep`

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/ references/reference-product/
git commit -m "chore: scaffold scripts/visual and references/reference-product dirs"
```

---

## Phase 1 — Fixture Generator + Test Runner

### Task 2: 合成测试图 + 单元测试 runner

**Files:**
- Create: `scripts/visual/tests/fixtures/generate_fixtures.py`
- Create: `scripts/visual/tests/run_all_tests.py`

**目的**：后续 Task 3~5 的 TDD 需要确定性的测试图。用 PIL 生成两张合成手机图（正面、背面），包含已知 bbox、已知特征位置、已知比例尺。这样测试断言有数值基准。

- [ ] **Step 1: 写 `generate_fixtures.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/fixtures/generate_fixtures.py`

```python
#!/usr/bin/env python3
"""Generate synthetic phone images for unit tests.
合成手机测试图（已知 bbox + 特征位置 + 比例尺）用于单元测试。
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent
PHONE_L_MM = 160.0  # phone physical length
PHONE_W_MM = 75.0   # phone physical width
PX_PER_MM = 5.0     # scale
BBOX_PAD = 40       # white margin around phone

def px(mm: float) -> int:
    return int(round(mm * PX_PER_MM))

def make_front() -> Image.Image:
    canvas_w = px(PHONE_W_MM) + BBOX_PAD * 2
    canvas_h = px(PHONE_L_MM) + BBOX_PAD * 2
    img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(img)
    x0, y0 = BBOX_PAD, BBOX_PAD
    x1, y1 = x0 + px(PHONE_W_MM), y0 + px(PHONE_L_MM)
    draw.rectangle([x0, y0, x1, y1], fill=(40, 40, 40), outline=(0, 0, 0), width=2)
    screen_pad = px(3.0)
    draw.rectangle(
        [x0 + screen_pad, y0 + screen_pad, x1 - screen_pad, y1 - screen_pad],
        fill=(20, 20, 80),
    )
    cam_cx = x0 + px(PHONE_W_MM / 2)
    cam_cy = y0 + px(8.0)
    draw.ellipse([cam_cx - 8, cam_cy - 8, cam_cx + 8, cam_cy + 8], fill=(0, 0, 0))
    return img

def make_back() -> Image.Image:
    canvas_w = px(PHONE_W_MM) + BBOX_PAD * 2
    canvas_h = px(PHONE_L_MM) + BBOX_PAD * 2
    img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(img)
    x0, y0 = BBOX_PAD, BBOX_PAD
    x1, y1 = x0 + px(PHONE_W_MM), y0 + px(PHONE_L_MM)
    draw.rectangle([x0, y0, x1, y1], fill=(180, 180, 180), outline=(0, 0, 0), width=2)
    cam_x = x0 + px(8.0)
    cam_y = y0 + px(8.0)
    cam_w = px(35.0)
    cam_h = px(35.0)
    draw.rectangle(
        [cam_x, cam_y, cam_x + cam_w, cam_y + cam_h],
        fill=(30, 30, 30),
        outline=(0, 0, 0),
        width=2,
    )
    return img

def main() -> None:
    front = make_front()
    back = make_back()
    front.save(OUT_DIR / "synthetic_phone_front.png")
    back.save(OUT_DIR / "synthetic_phone_back.png")
    meta = {
        "phone_length_mm": PHONE_L_MM,
        "phone_width_mm": PHONE_W_MM,
        "px_per_mm": PX_PER_MM,
        "bbox_pad_px": BBOX_PAD,
        "front_bbox_px": [BBOX_PAD, BBOX_PAD, px(PHONE_W_MM), px(PHONE_L_MM)],
        "back_bbox_px": [BBOX_PAD, BBOX_PAD, px(PHONE_W_MM), px(PHONE_L_MM)],
        "front_camera_center_px": [BBOX_PAD + px(PHONE_W_MM / 2), BBOX_PAD + px(8.0)],
        "back_camera_bbox_px": [BBOX_PAD + px(8.0), BBOX_PAD + px(8.0), px(35.0), px(35.0)],
    }
    import json
    (OUT_DIR / "fixtures_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote {OUT_DIR}/synthetic_phone_front.png")
    print(f"Wrote {OUT_DIR}/synthetic_phone_back.png")
    print(f"Wrote {OUT_DIR}/fixtures_meta.json")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行 generator，确认三个文件产出**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/fixtures/generate_fixtures.py
ls scripts/visual/tests/fixtures/
```
Expected:
```
fixtures_meta.json
generate_fixtures.py
synthetic_phone_back.png
synthetic_phone_front.png
```

- [ ] **Step 3: 写 `run_all_tests.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/run_all_tests.py`

```python
#!/usr/bin/env python3
"""Discover and run all tests under scripts/visual/tests/.
发现并运行 scripts/visual/tests/ 下所有 unittest。
"""
import unittest
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent

def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(THIS_DIR), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试 runner（当前应该没有测试文件，空套件通过）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
echo "exit_code=$?"
```
Expected: `OK` + `exit_code=0`（0 个测试通过也算成功）

- [ ] **Step 5: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/tests/fixtures/generate_fixtures.py scripts/visual/tests/fixtures/synthetic_phone_front.png scripts/visual/tests/fixtures/synthetic_phone_back.png scripts/visual/tests/fixtures/fixtures_meta.json scripts/visual/tests/run_all_tests.py
git commit -m "test: add synthetic phone fixtures and test runner"
```

---

## Phase 2 — Pure Image Processing Tools (TDD)

### Task 3: `preprocess_reference.py`（P0 核心 — 现实图预处理）

**Files:**
- Create: `scripts/visual/preprocess_reference.py`
- Test: `scripts/visual/tests/test_preprocess_reference.py`

**功能**：输入原始参考图 + bbox + 物理尺寸 → 输出裁剪图、bbox.json、scale.json（mm/px）。

**CLI**：
```
python3 preprocess_reference.py <photo.png> --bbox "x,y,w,h" --physical-length "160.0mm" --physical-axis height --output-dir refs/clean/
```

- [ ] **Step 1: 写失败测试**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/test_preprocess_reference.py`

```python
"""Unit tests for preprocess_reference.
preprocess_reference 的单元测试。
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.visual.preprocess_reference import preprocess


FIXTURES = Path(__file__).parent / "fixtures"


class TestPreprocess(unittest.TestCase):
    def test_crop_matches_bbox(self) -> None:
        meta = json.loads((FIXTURES / "fixtures_meta.json").read_text())
        bbox = meta["front_bbox_px"]
        with tempfile.TemporaryDirectory() as tmp:
            out = preprocess(
                image_path=FIXTURES / "synthetic_phone_front.png",
                bbox=tuple(bbox),
                physical_length_mm=meta["phone_length_mm"],
                physical_axis="height",
                output_dir=Path(tmp),
            )
            cropped = out["cropped_path"]
            self.assertTrue(cropped.exists(), "cropped image must be written")
            from PIL import Image
            img = Image.open(cropped)
            self.assertEqual(img.size, (bbox[2], bbox[3]))

    def test_scale_json_mm_per_px(self) -> None:
        meta = json.loads((FIXTURES / "fixtures_meta.json").read_text())
        bbox = meta["front_bbox_px"]
        expected_mm_per_px = 1.0 / meta["px_per_mm"]
        with tempfile.TemporaryDirectory() as tmp:
            out = preprocess(
                image_path=FIXTURES / "synthetic_phone_front.png",
                bbox=tuple(bbox),
                physical_length_mm=meta["phone_length_mm"],
                physical_axis="height",
                output_dir=Path(tmp),
            )
            scale = json.loads(out["scale_path"].read_text())
            self.assertAlmostEqual(scale["mm_per_px"], expected_mm_per_px, places=4)
            self.assertEqual(scale["physical_axis"], "height")

    def test_bbox_json_round_trip(self) -> None:
        meta = json.loads((FIXTURES / "fixtures_meta.json").read_text())
        bbox = meta["front_bbox_px"]
        with tempfile.TemporaryDirectory() as tmp:
            out = preprocess(
                image_path=FIXTURES / "synthetic_phone_front.png",
                bbox=tuple(bbox),
                physical_length_mm=meta["phone_length_mm"],
                physical_axis="height",
                output_dir=Path(tmp),
            )
            bj = json.loads(out["bbox_path"].read_text())
            self.assertEqual(bj["bbox_xywh"], list(bbox))

    def test_invalid_bbox_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                preprocess(
                    image_path=FIXTURES / "synthetic_phone_front.png",
                    bbox=(10, 10, 10000, 10000),
                    physical_length_mm=160.0,
                    physical_axis="height",
                    output_dir=Path(tmp),
                )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: `ImportError: No module named 'scripts.visual.preprocess_reference'` 或 4 个测试全部 FAIL

- [ ] **Step 3: 实现 `preprocess_reference.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/preprocess_reference.py`

```python
#!/usr/bin/env python3
"""Preprocess a real-world reference photo into comparable form.
参考图预处理：裁剪 + 比例尺 + 输出干净图 / 元数据。

CLI:
    python3 preprocess_reference.py <photo.png> \\
        --bbox "x,y,w,h" \\
        --physical-length "160.0mm" \\
        --physical-axis height \\
        --output-dir refs/clean/

产出：
    {stem}_cropped.png   裁剪后的部件图
    {stem}_bbox.json     {"bbox_xywh": [x, y, w, h], "source_image": "..."}
    {stem}_scale.json    {"mm_per_px": <float>, "physical_axis": "height"|"width", "physical_length_mm": <float>}
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Tuple

from PIL import Image


def _parse_length(text: str) -> float:
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*mm\s*$", text, re.IGNORECASE)
    if not m:
        raise ValueError(f"physical-length must look like '160.0mm', got {text!r}")
    return float(m.group(1))


def preprocess(
    image_path: Path,
    bbox: Tuple[int, int, int, int],
    physical_length_mm: float,
    physical_axis: str,
    output_dir: Path,
) -> dict:
    if physical_axis not in ("height", "width"):
        raise ValueError(f"physical-axis must be 'height' or 'width', got {physical_axis!r}")
    x, y, w, h = bbox
    if w <= 0 or h <= 0:
        raise ValueError(f"bbox w/h must be positive, got {bbox}")
    img = Image.open(image_path).convert("RGB")
    iw, ih = img.size
    if x < 0 or y < 0 or x + w > iw or y + h > ih:
        raise ValueError(f"bbox {bbox} out of image bounds {(iw, ih)}")

    cropped = img.crop((x, y, x + w, y + h))
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem
    cropped_path = output_dir / f"{stem}_cropped.png"
    bbox_path = output_dir / f"{stem}_bbox.json"
    scale_path = output_dir / f"{stem}_scale.json"

    cropped.save(cropped_path)
    axis_len_px = h if physical_axis == "height" else w
    mm_per_px = physical_length_mm / axis_len_px

    bbox_path.write_text(json.dumps({
        "bbox_xywh": [x, y, w, h],
        "source_image": str(image_path),
    }, indent=2))
    scale_path.write_text(json.dumps({
        "mm_per_px": mm_per_px,
        "physical_axis": physical_axis,
        "physical_length_mm": physical_length_mm,
        "reference_image": str(cropped_path),
    }, indent=2))
    return {
        "cropped_path": cropped_path,
        "bbox_path": bbox_path,
        "scale_path": scale_path,
        "mm_per_px": mm_per_px,
    }


def _parse_bbox(text: str) -> Tuple[int, int, int, int]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 4:
        raise ValueError(f"bbox must be 'x,y,w,h' with 4 comma-separated ints, got {text!r}")
    return tuple(int(p) for p in parts)  # type: ignore[return-value]


def main() -> int:
    p = argparse.ArgumentParser(description="Preprocess reference photo for Layer 2 visual compare.")
    p.add_argument("photo", type=Path)
    p.add_argument("--bbox", required=True, help="'x,y,w,h' pixel coordinates of the part.")
    p.add_argument("--physical-length", required=True, help="e.g. '160.26mm'")
    p.add_argument("--physical-axis", choices=["height", "width"], default="height")
    p.add_argument("--output-dir", type=Path, default=Path("refs/clean"))
    args = p.parse_args()

    try:
        bbox = _parse_bbox(args.bbox)
        length_mm = _parse_length(args.physical_length)
        out = preprocess(
            image_path=args.photo,
            bbox=bbox,
            physical_length_mm=length_mm,
            physical_axis=args.physical_axis,
            output_dir=args.output_dir,
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"cropped: {out['cropped_path']}")
    print(f"bbox:    {out['bbox_path']}")
    print(f"scale:   {out['scale_path']} (mm_per_px={out['mm_per_px']:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: 4 tests OK

- [ ] **Step 5: CLI smoke test**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/preprocess_reference.py \
  scripts/visual/tests/fixtures/synthetic_phone_front.png \
  --bbox "40,40,375,800" \
  --physical-length "160.0mm" \
  --physical-axis height \
  --output-dir /tmp/v3_preprocess_smoke
cat /tmp/v3_preprocess_smoke/synthetic_phone_front_scale.json
```
Expected: `mm_per_px ≈ 0.2`（800px / 160.0mm ≈ 5px/mm → 0.2mm/px）

- [ ] **Step 6: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/preprocess_reference.py scripts/visual/tests/test_preprocess_reference.py
git commit -m "feat(visual): add preprocess_reference.py with bbox + scale metadata"
```

---

### Task 4: `pixel_measure.py`（P0 — 像素测量反推尺寸）

**Files:**
- Create: `scripts/visual/pixel_measure.py`
- Test: `scripts/visual/tests/test_pixel_measure.py`

**功能**：给定图像 + 比例尺（从 scale.json 或 CLI 传入） + 像素坐标列表 → 输出每个点在"以 bbox 中心为原点"的毫米坐标。默认 batch 模式（CSV 输入/输出），`--interactive` 启用 matplotlib 点击收集模式（本任务**只实现 batch 模式**，interactive 模式作为 docstring 里的 TODO）。

**CLI（batch）**：
```
python3 pixel_measure.py <image.png> --scale scripts.json --points "x1,y1;x2,y2" [--origin "cx,cy"] [--output csv_path]
```

- [ ] **Step 1: 写失败测试**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/test_pixel_measure.py`

```python
"""Unit tests for pixel_measure batch mode.
pixel_measure batch 模式的单元测试。
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.visual.pixel_measure import measure_points


FIXTURES = Path(__file__).parent / "fixtures"


class TestPixelMeasure(unittest.TestCase):
    def setUp(self) -> None:
        self.meta = json.loads((FIXTURES / "fixtures_meta.json").read_text())
        self.mm_per_px = 1.0 / self.meta["px_per_mm"]

    def test_origin_at_bbox_center_gives_zero(self) -> None:
        bbox = self.meta["front_bbox_px"]
        cx = bbox[0] + bbox[2] // 2
        cy = bbox[1] + bbox[3] // 2
        results = measure_points(
            points_px=[(cx, cy)],
            mm_per_px=self.mm_per_px,
            origin_px=(cx, cy),
        )
        self.assertAlmostEqual(results[0]["x_mm"], 0.0, places=4)
        self.assertAlmostEqual(results[0]["y_mm"], 0.0, places=4)

    def test_camera_position_in_mm(self) -> None:
        bbox = self.meta["front_bbox_px"]
        origin = (bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2)
        cam_px = tuple(self.meta["front_camera_center_px"])
        results = measure_points(
            points_px=[cam_px],
            mm_per_px=self.mm_per_px,
            origin_px=origin,
        )
        self.assertAlmostEqual(results[0]["x_mm"], 0.0, places=2)
        # Camera is near top edge (y small), origin at center. In image coords y grows downward.
        # Physical y of camera relative to origin is negative.
        self.assertLess(results[0]["y_mm"], 0)

    def test_y_axis_sign_convention_flag(self) -> None:
        results_image = measure_points(
            points_px=[(100, 200)],
            mm_per_px=0.5,
            origin_px=(50, 50),
            y_axis_up=False,
        )
        results_math = measure_points(
            points_px=[(100, 200)],
            mm_per_px=0.5,
            origin_px=(50, 50),
            y_axis_up=True,
        )
        self.assertAlmostEqual(results_image[0]["y_mm"], 75.0, places=4)
        self.assertAlmostEqual(results_math[0]["y_mm"], -75.0, places=4)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行确认失败**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: import error on pixel_measure

- [ ] **Step 3: 实现 `pixel_measure.py` (batch 模式)**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/pixel_measure.py`

```python
#!/usr/bin/env python3
"""Convert pixel coordinates to millimeters using a known scale.
基于已知比例尺把像素坐标换算为部件本地坐标系下的毫米值。

CLI (batch):
    python3 pixel_measure.py <image.png> \\
        --scale refs/clean/xxx_scale.json \\
        --points "120,340;560,210" \\
        --origin "center"  # or "x_px,y_px"
        [--y-axis up|down]  # default down (image convention)
        [--output csv_path]

Interactive mode (matplotlib click collection) is TODO — see
ISSUE: interactive mode not yet implemented; use CLI points for now.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image


def measure_points(
    points_px: Iterable[Tuple[int, int]],
    mm_per_px: float,
    origin_px: Tuple[int, int],
    y_axis_up: bool = False,
) -> List[dict]:
    ox, oy = origin_px
    out = []
    for px, py in points_px:
        dx_px = px - ox
        dy_px = py - oy
        x_mm = dx_px * mm_per_px
        y_mm = (-dy_px if y_axis_up else dy_px) * mm_per_px
        out.append({
            "x_px": px, "y_px": py,
            "x_mm": round(x_mm, 3), "y_mm": round(y_mm, 3),
        })
    return out


def _parse_points(text: str) -> List[Tuple[int, int]]:
    pts = []
    for pair in text.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        xs, ys = pair.split(",")
        pts.append((int(xs), int(ys)))
    return pts


def _resolve_origin(spec: str, image_path: Path) -> Tuple[int, int]:
    if spec == "center":
        w, h = Image.open(image_path).size
        return (w // 2, h // 2)
    xs, ys = spec.split(",")
    return (int(xs), int(ys))


def main() -> int:
    p = argparse.ArgumentParser(description="Convert pixel coords to millimeters.")
    p.add_argument("image", type=Path)
    p.add_argument("--scale", required=True, type=Path, help="scale.json from preprocess_reference")
    p.add_argument("--points", required=True, help="'x1,y1;x2,y2;...'")
    p.add_argument("--origin", default="center", help="'center' or 'x,y'")
    p.add_argument("--y-axis", choices=["up", "down"], default="down")
    p.add_argument("--output", type=Path, default=None, help="write CSV (stdout if omitted)")
    args = p.parse_args()

    try:
        scale = json.loads(args.scale.read_text())
        mm_per_px = float(scale["mm_per_px"])
        origin = _resolve_origin(args.origin, args.image)
        points = _parse_points(args.points)
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    results = measure_points(
        points_px=points,
        mm_per_px=mm_per_px,
        origin_px=origin,
        y_axis_up=(args.y_axis == "up"),
    )

    fieldnames = ["x_px", "y_px", "x_mm", "y_mm"]
    if args.output:
        with args.output.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(results)
        print(f"wrote {args.output} ({len(results)} rows)")
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: 7 tests OK（4 preprocess + 3 pixel_measure）

- [ ] **Step 5: CLI smoke test（连上 Task 3 的 scale.json）**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/pixel_measure.py \
  scripts/visual/tests/fixtures/synthetic_phone_front.png \
  --scale /tmp/v3_preprocess_smoke/synthetic_phone_front_scale.json \
  --points "227,80;227,470" \
  --origin "227,470"
```
Expected: 两行 CSV，第一点 `y_mm ≈ 78mm`（top 边距中心），第二点 `y_mm ≈ 0`

- [ ] **Step 6: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/pixel_measure.py scripts/visual/tests/test_pixel_measure.py
git commit -m "feat(visual): add pixel_measure.py batch mode"
```

---

### Task 5: `visual_compare.py`（P0 — 边缘对比 + 差异热图）

**Files:**
- Create: `scripts/visual/visual_compare.py`
- Test: `scripts/visual/tests/test_visual_compare.py`

**功能**：输入 rendered.png + reference_cropped.png + 两个 scale.json（或 `--rendered-scale auto`）→ 按 mm/px 归一化到同一尺度 → 输出 side_by_side / edge_overlay / diff_heatmap 三种对比图。

**和现有 `scripts/validate/visual_compare.py` 的关系**：
- 现有那个已 DEPRECATED，且专注 AI Vision / OpenCV 多模式编排
- 本任务的新脚本**只做几何对齐视角下的边缘对比**，是 cad-vision-verify 姊妹 skill 的补充工具
- 两个脚本路径不同（`validate/` vs `visual/`），不冲突

- [ ] **Step 1: 写失败测试**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/test_visual_compare.py`

```python
"""Unit tests for visual_compare.
visual_compare 的单元测试。
"""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from scripts.visual.visual_compare import (
    canny_edges, compose_side_by_side, compose_edge_overlay, compose_diff_heatmap,
    normalize_to_scale,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _identical_pair() -> tuple[Image.Image, Image.Image]:
    img = Image.open(FIXTURES / "synthetic_phone_front.png").convert("RGB")
    return img, img.copy()


class TestVisualCompare(unittest.TestCase):
    def test_canny_returns_binary_mask(self) -> None:
        img, _ = _identical_pair()
        edges = canny_edges(np.array(img.convert("L")))
        self.assertEqual(edges.dtype, np.uint8)
        unique = set(np.unique(edges).tolist())
        self.assertTrue(unique.issubset({0, 255}))

    def test_side_by_side_shape(self) -> None:
        a, b = _identical_pair()
        out = compose_side_by_side(a, b)
        self.assertEqual(out.height, max(a.height, b.height))
        self.assertEqual(out.width, a.width + b.width)

    def test_edge_overlay_identical_has_no_blue_only_pixels(self) -> None:
        a, b = _identical_pair()
        overlay = compose_edge_overlay(a, b)
        arr = np.array(overlay)
        # For identical images, red (reference) and blue (rendered) edges
        # should be at same pixels -> appear purple, not pure blue-only.
        blue_only = (arr[..., 2] > 0) & (arr[..., 0] == 0)
        self.assertEqual(int(blue_only.sum()), 0)

    def test_diff_heatmap_identical_is_zero(self) -> None:
        a, b = _identical_pair()
        heat = compose_diff_heatmap(a, b)
        arr = np.array(heat.convert("L"))
        self.assertLess(float(arr.mean()), 5.0)

    def test_normalize_to_scale_resizes_to_common_mm_per_px(self) -> None:
        a, _ = _identical_pair()
        a_small = a.resize((a.width // 2, a.height // 2))
        na, nb = normalize_to_scale(
            a_small, mm_per_px_a=2.0,
            b=a, mm_per_px_b=1.0,
        )
        self.assertEqual(na.size, nb.size)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 确认失败**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```

- [ ] **Step 3: 实现 `visual_compare.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/visual_compare.py`

```python
#!/usr/bin/env python3
"""Geometric visual comparison: rendered vs preprocessed reference.
几何视角的视觉对比：渲染图 vs 预处理后的参考图。

Produces one of three outputs per invocation:
  side_by_side   两图并排
  edge_overlay   Canny 边缘叠加（红=参考，蓝=渲染，紫=吻合）
  diff_heatmap   灰度差热图

Prerequisite: reference image MUST have passed through preprocess_reference.py
            参考图必须先经过 preprocess_reference.py 得到 *_scale.json
            否则 IoU/差值无物理意义，脚本会拒绝执行。

CLI:
    python3 visual_compare.py <rendered.png> <reference_cropped.png> \\
        --reference-scale refs/clean/front_scale.json \\
        --rendered-scale auto \\
        --mode edge_overlay \\
        --output out/compare_front.png
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore


CANNY_LOW = 50
CANNY_HIGH = 150


def canny_edges(gray: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    if cv2 is None:
        raise RuntimeError("opencv-python not installed; required for Canny.")
    blurred = cv2.GaussianBlur(gray, ksize=(0, 0), sigmaX=sigma)
    return cv2.Canny(blurred, CANNY_LOW, CANNY_HIGH)


def normalize_to_scale(
    a: Image.Image, mm_per_px_a: float,
    b: Image.Image, mm_per_px_b: float,
) -> Tuple[Image.Image, Image.Image]:
    """Resize both images to the coarser of the two mm/px scales."""
    target_mm_per_px = max(mm_per_px_a, mm_per_px_b)
    def _rescale(img: Image.Image, from_mm_per_px: float) -> Image.Image:
        factor = from_mm_per_px / target_mm_per_px
        new_w = max(1, int(round(img.width * factor)))
        new_h = max(1, int(round(img.height * factor)))
        return img.resize((new_w, new_h), Image.LANCZOS)
    return _rescale(a, mm_per_px_a), _rescale(b, mm_per_px_b)


def _align_shapes(a: Image.Image, b: Image.Image) -> Tuple[Image.Image, Image.Image]:
    w = max(a.width, b.width)
    h = max(a.height, b.height)
    pad_a = Image.new("RGB", (w, h), "white"); pad_a.paste(a, (0, 0))
    pad_b = Image.new("RGB", (w, h), "white"); pad_b.paste(b, (0, 0))
    return pad_a, pad_b


def compose_side_by_side(a: Image.Image, b: Image.Image) -> Image.Image:
    h = max(a.height, b.height)
    canvas = Image.new("RGB", (a.width + b.width, h), "white")
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width, 0))
    return canvas


def compose_edge_overlay(rendered: Image.Image, reference: Image.Image) -> Image.Image:
    r, f = _align_shapes(rendered, reference)
    er = canny_edges(np.array(r.convert("L")))
    ef = canny_edges(np.array(f.convert("L")))
    rgb = np.zeros((*er.shape, 3), dtype=np.uint8)
    rgb[..., 0] = ef      # reference → red
    rgb[..., 2] = er      # rendered → blue
    rgb[(ef > 0) & (er > 0)] = [255, 0, 255]  # agreement → purple
    return Image.fromarray(rgb)


def compose_diff_heatmap(rendered: Image.Image, reference: Image.Image) -> Image.Image:
    r, f = _align_shapes(rendered, reference)
    ar = np.array(r.convert("L")).astype(np.int16)
    af = np.array(f.convert("L")).astype(np.int16)
    diff = np.abs(ar - af).astype(np.uint8)
    if cv2 is not None:
        heat = cv2.applyColorMap(diff, cv2.COLORMAP_HOT)
        heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    else:
        heat = np.stack([diff, np.zeros_like(diff), np.zeros_like(diff)], axis=-1)
    return Image.fromarray(heat)


def _load_scale(path: Path) -> float:
    data = json.loads(path.read_text())
    return float(data["mm_per_px"])


def _load_rendered_scale(spec: str, rendered: Path) -> float:
    if spec == "auto":
        # Assume rendered image was saved at 1px = 1mm. Can be overridden.
        return 1.0
    if spec.endswith(".json"):
        return _load_scale(Path(spec))
    return float(spec)


def main() -> int:
    p = argparse.ArgumentParser(description="Geometric visual compare.")
    p.add_argument("rendered", type=Path)
    p.add_argument("reference", type=Path)
    p.add_argument("--reference-scale", required=True, type=Path)
    p.add_argument("--rendered-scale", default="auto", help="'auto' | float | scale.json path")
    p.add_argument("--mode", choices=["side_by_side", "edge_overlay", "diff_heatmap"], default="edge_overlay")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    try:
        ref_scale = _load_scale(args.reference_scale)
        ren_scale = _load_rendered_scale(args.rendered_scale, args.rendered)
        a = Image.open(args.rendered).convert("RGB")
        b = Image.open(args.reference).convert("RGB")
        a_n, b_n = normalize_to_scale(a, ren_scale, b, ref_scale)
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.mode == "side_by_side":
        out = compose_side_by_side(a_n, b_n)
    elif args.mode == "edge_overlay":
        out = compose_edge_overlay(a_n, b_n)
    else:
        out = compose_diff_heatmap(a_n, b_n)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)
    print(f"wrote {args.output} (mode={args.mode}, ref_mm_per_px={ref_scale}, ren_mm_per_px={ren_scale})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: 12 tests OK（4+3+5）

- [ ] **Step 5: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/visual_compare.py scripts/visual/tests/test_visual_compare.py
git commit -m "feat(visual): add edge-overlay / diff-heatmap visual_compare with scale contract"
```

---

---

## Phase 3 — Part Face Mapping (前置于 OCP 脚本)

### Task 6: `part-face-mapping-template.yaml` + loader

**Files:**
- Create: `references/verify/part-face-mapping-template.yaml`
- Create: `scripts/visual/face_mapping.py`
- Test: `scripts/visual/tests/test_face_mapping.py`

**目的**：部件的 FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM 要按"部件语义面"而非坐标轴。脚本 `multi_view_screenshot.py` / `skybox_unfold.py` 都依赖这个 loader。

- [ ] **Step 1: 写 template**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/verify/part-face-mapping-template.yaml`

```yaml
# part_face_mapping.yaml — declare how a part's semantic faces map to
# world-axis camera views. Each part directory should ship one of these
# alongside params.md / contract.yaml.
#
# 一份范本：声明部件语义面到世界坐标相机视角的映射。
# 部件目录应当把这个文件和 params.md / contract.yaml 放在一起。

part: <part-name>              # e.g. phone_case
description: <one-line>

coordinate_system:
  up:             "+Z"         # world axis for part's "up" direction
  right:          "+X"         # world axis for part's "right"
  screen_normal:  "-Y"         # face-normal pointing at the viewer

# Map semantic view name → OCP Camera direction
# (ocp_vscode.Camera enum: FRONT, BACK, LEFT, RIGHT, TOP, BOTTOM, ISO)
face_mapping:
  FRONT:  BACK        # semantic FRONT (screen/正面) — ocp camera direction
  BACK:   FRONT       # semantic BACK (后盖)
  LEFT:   LEFT
  RIGHT:  RIGHT
  TOP:    TOP
  BOTTOM: BOTTOM

# Optional: describe what each face means in the product so viewers
# reading comparison reports can understand each view semantically.
face_labels:
  FRONT:  "屏幕面 / screen side"
  BACK:   "后盖 / back cover"
  LEFT:   "左侧边 / left edge"
  RIGHT:  "右侧边 / right edge"
  TOP:    "顶部 / top edge (听筒一侧)"
  BOTTOM: "底部 / bottom edge (充电口一侧)"
```

- [ ] **Step 2: 写失败测试**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/test_face_mapping.py`

```python
"""Unit tests for face_mapping loader.
face_mapping loader 的单元测试。
"""
import tempfile
import unittest
from pathlib import Path

from scripts.visual.face_mapping import load_face_mapping, DEFAULT_MAPPING


YAML_OK = """
part: test_phone
coordinate_system:
  up: "+Z"
  right: "+X"
  screen_normal: "-Y"
face_mapping:
  FRONT: BACK
  BACK: FRONT
  LEFT: LEFT
  RIGHT: RIGHT
  TOP: TOP
  BOTTOM: BOTTOM
"""


class TestFaceMapping(unittest.TestCase):
    def test_load_valid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mapping.yaml"
            p.write_text(YAML_OK)
            mapping = load_face_mapping(p)
            self.assertEqual(mapping.semantic_to_camera("FRONT"), "BACK")
            self.assertEqual(mapping.semantic_to_camera("BACK"), "FRONT")

    def test_default_when_missing(self) -> None:
        mapping = load_face_mapping(None)
        self.assertEqual(mapping.semantic_to_camera("FRONT"), "FRONT")
        self.assertTrue(mapping.is_default)

    def test_unknown_view_raises(self) -> None:
        mapping = load_face_mapping(None)
        with self.assertRaises(KeyError):
            mapping.semantic_to_camera("DIAGONAL")

    def test_invalid_target_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.yaml"
            p.write_text("part: x\nface_mapping:\n  FRONT: WAT\n")
            with self.assertRaises(ValueError):
                load_face_mapping(p)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: 确认失败**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```

- [ ] **Step 4: 实现 `face_mapping.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/face_mapping.py`

```python
#!/usr/bin/env python3
"""Load and validate part_face_mapping.yaml.
加载并校验 part_face_mapping.yaml。
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


VALID_CAMERAS = {"FRONT", "BACK", "LEFT", "RIGHT", "TOP", "BOTTOM", "ISO"}
VALID_SEMANTICS = {"FRONT", "BACK", "LEFT", "RIGHT", "TOP", "BOTTOM"}

DEFAULT_MAPPING: Dict[str, str] = {v: v for v in VALID_SEMANTICS}


@dataclass
class FaceMapping:
    mapping: Dict[str, str]
    is_default: bool
    source_path: Optional[Path]

    def semantic_to_camera(self, semantic_view: str) -> str:
        if semantic_view not in self.mapping:
            raise KeyError(f"unknown semantic view {semantic_view!r}; valid: {sorted(VALID_SEMANTICS)}")
        return self.mapping[semantic_view]


def load_face_mapping(path: Optional[Path]) -> FaceMapping:
    if path is None:
        return FaceMapping(mapping=dict(DEFAULT_MAPPING), is_default=True, source_path=None)
    data = yaml.safe_load(path.read_text()) or {}
    raw = data.get("face_mapping", {}) or {}
    mapping = dict(DEFAULT_MAPPING)
    for sem, cam in raw.items():
        if sem not in VALID_SEMANTICS:
            raise ValueError(f"unknown semantic view {sem!r} in {path}")
        if cam not in VALID_CAMERAS:
            raise ValueError(f"invalid camera target {cam!r} for {sem} in {path}")
        mapping[sem] = cam
    return FaceMapping(mapping=mapping, is_default=False, source_path=path)
```

- [ ] **Step 5: 运行测试确认通过**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
```
Expected: 16 tests OK（12+4）

- [ ] **Step 6: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/verify/part-face-mapping-template.yaml scripts/visual/face_mapping.py scripts/visual/tests/test_face_mapping.py
git commit -m "feat(visual): add part_face_mapping template + loader"
```

---

## Phase 4 — OCP-Integrated Tools (Manual / Integration Verification)

> **Note**：以下两个脚本依赖运行中的 OCP Viewer（端口 3939/4567），不写自动化测试。每个任务包含 smoke 验证步骤，由 Phase 5 端到端验收兜底。

### Task 7: `multi_view_screenshot.py`（P0）

**Files:**
- Create: `scripts/visual/multi_view_screenshot.py`

**功能**：
- 输入：`.step` 路径（用 `import_step`）或 `.py` 路径（subprocess 执行后通过 OCP Viewer）
- 读取可选的 `part_face_mapping.yaml`
- `--mode {ortho, iso, both}`：
  - `ortho`：7 张 = FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM + 1 张 ISO
  - `iso`：4 张 ISO 变体（前上、前下、后上、后下）
  - `both`：10 张全套
- 文件命名：`{name}_{VIEW}.png`

- [ ] **Step 1: 实现脚本**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/multi_view_screenshot.py`

```python
#!/usr/bin/env python3
"""Generate 7 orthographic + 4 ISO screenshots via OCP Viewer.
通过 OCP Viewer 生成 7 正交视图 + 4 ISO 变体截图。

Prerequisite: OCP Viewer must be running (port 3939 or 4567).
前置：OCP Viewer 必须处于运行状态（端口 3939 或 4567）。

CLI:
    python3 multi_view_screenshot.py <input.step|input.py> \\
        [--output-dir PATH] \\
        [--name NAME] \\
        [--mode ortho|iso|both] \\
        [--face-mapping PATH] \\
        [--views FRONT,BACK,...]
"""
from __future__ import annotations
import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

from scripts.visual.face_mapping import load_face_mapping, FaceMapping

from ocp_vscode import show, save_screenshot, Camera, get_ports, port_check  # type: ignore

ORTHO_SEMANTIC = ["FRONT", "BACK", "LEFT", "RIGHT", "TOP", "BOTTOM"]
ISO_VARIANTS = [
    ("ISO_FRONT_TOP",    Camera.ISO,  (30,   0,  30)),
    ("ISO_FRONT_BOTTOM", Camera.ISO,  (-30,  0,  30)),
    ("ISO_BACK_TOP",     Camera.ISO,  (30,   0, 210)),
    ("ISO_BACK_BOTTOM",  Camera.ISO,  (-30,  0, 210)),
]


def _ensure_viewer() -> None:
    ports = get_ports()
    if not ports:
        print("ERROR: no OCP Viewer port detected. Start OCP Viewer first.", file=sys.stderr)
        sys.exit(2)
    for port in ports:
        if port_check(port):
            return
    print(f"ERROR: none of ports {ports} are responsive.", file=sys.stderr)
    sys.exit(2)


def _load_model(path: Path):
    if path.suffix.lower() in {".step", ".stp"}:
        from build123d import import_step
        return import_step(str(path))
    if path.suffix.lower() == ".py":
        # Run the .py file; it should `show(...)` the model itself.
        result = subprocess.run([sys.executable, str(path)], check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            sys.exit(2)
        return None  # assume the .py handled show()
    raise ValueError(f"unsupported input: {path.suffix}")


def _camera_for(name: str):
    return getattr(Camera, name)


def capture_orthographic(model, name_stem: str, output_dir: Path, mapping: FaceMapping, views: List[str]) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    produced = []
    for sem in views:
        cam_name = mapping.semantic_to_camera(sem)
        if model is not None:
            show(model, reset_camera=_camera_for(cam_name))
        else:
            # model already shown by .py subprocess; just set camera via show on last.
            # For .py inputs, caller is responsible for keeping the model on stage.
            pass
        time.sleep(0.9)
        path = output_dir / f"{name_stem}_{sem}.png"
        save_screenshot(str(path))
        produced.append(path)
    # Always include one default ISO
    if model is not None:
        show(model, reset_camera=Camera.ISO)
        time.sleep(0.9)
    iso_path = output_dir / f"{name_stem}_ISO.png"
    save_screenshot(str(iso_path))
    produced.append(iso_path)
    return produced


def capture_iso_variants(model, name_stem: str, output_dir: Path) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    produced = []
    for label, cam, _hint in ISO_VARIANTS:
        if model is not None:
            show(model, reset_camera=cam)
        time.sleep(0.9)
        path = output_dir / f"{name_stem}_{label}.png"
        save_screenshot(str(path))
        produced.append(path)
    return produced


def main() -> int:
    p = argparse.ArgumentParser(description="Multi-view screenshot via OCP Viewer.")
    p.add_argument("source", type=Path, help="input.step or input.py")
    p.add_argument("--output-dir", type=Path, default=Path("output"))
    p.add_argument("--name", default=None)
    p.add_argument("--mode", choices=["ortho", "iso", "both"], default="ortho")
    p.add_argument("--face-mapping", type=Path, default=None)
    p.add_argument("--views", default=",".join(ORTHO_SEMANTIC))
    args = p.parse_args()

    _ensure_viewer()
    name_stem = args.name or args.source.stem
    mapping = load_face_mapping(args.face_mapping)
    if mapping.is_default:
        print("WARNING: no --face-mapping supplied; view names = coord axes (may not match part semantics).", file=sys.stderr)

    model = _load_model(args.source)
    views = [v.strip() for v in args.views.split(",") if v.strip()]

    produced: List[Path] = []
    if args.mode in ("ortho", "both"):
        produced += capture_orthographic(model, name_stem, args.output_dir, mapping, views)
    if args.mode in ("iso", "both"):
        produced += capture_iso_variants(model, name_stem, args.output_dir)

    for p_ in produced:
        print(p_)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke — 用 test 14 或 test 13 现有 STEP 跑**

Requires OCP Viewer running. Ask user to start it, or check with:
```bash
python3 -c "from ocp_vscode import get_ports, port_check; ports=get_ports(); print('running' if any(port_check(p) for p in ports) else 'NOT running')"
```
Then:
```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/multi_view_screenshot.py \
  /Users/liyijiang/work/build123d-cad-skill-test/tests/13-redmi-k80-pro/output/redmi_k80_pro.step \
  --output-dir /tmp/v3_mvs_smoke \
  --name k80pro \
  --mode ortho
ls /tmp/v3_mvs_smoke/
```
Expected: 7 PNG files (`k80pro_FRONT.png` … `k80pro_BOTTOM.png` + `k80pro_ISO.png`)

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/multi_view_screenshot.py
git commit -m "feat(visual): add multi_view_screenshot with mode=ortho|iso|both + face mapping"
```

---

### Task 8: `skybox_unfold.py`（P0 — 核心新增）

**Files:**
- Create: `scripts/visual/skybox_unfold.py`

**功能**：相机固定 Camera.FRONT + 旋转模型 6 次，生成 6 面图；PIL 裁白边 + 十字布局拼接成 `skybox_unfolded.png`。

- [ ] **Step 1: 实现脚本**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/skybox_unfold.py`

```python
#!/usr/bin/env python3
"""Render skybox-style 6-face unfold of a part via OCP Viewer.
通过"相机固定 + 旋转模型"生成 6 面贴图并拼成十字展开。

Face layout (cross):
            TOP
    LEFT  FRONT  RIGHT  BACK
            BOTTOM

Prerequisite: OCP Viewer must be running.
前置：OCP Viewer 必须处于运行状态。

CLI:
    python3 skybox_unfold.py <input.step> \\
        [--output-dir PATH] [--name NAME] [--center FRONT]
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

from ocp_vscode import show, save_screenshot, Camera, get_ports, port_check  # type: ignore
from build123d import Axis, import_step  # type: ignore

FACE_ROTATIONS: Dict[str, List[Tuple[Axis, float]]] = {
    "FRONT": [(Axis.X, 90)],
    "BACK":  [(Axis.X, 90), (Axis.Z, 180)],  # extra Z flip to avoid mirror
    "UP":    [(Axis.X, 180)],
    "DOWN":  [],
    "LEFT":  [(Axis.Z, 90)],
    "RIGHT": [(Axis.Z, -90)],
}

MAX_CELL_W, MAX_CELL_H = 700, 500
CANVAS_W, CANVAS_H = MAX_CELL_W * 4, MAX_CELL_H * 3


def _ensure_viewer() -> None:
    ports = get_ports()
    for p in ports:
        if port_check(p):
            return
    print("ERROR: OCP Viewer not running on any known port.", file=sys.stderr)
    sys.exit(2)


def _capture_face(model, face: str, out_dir: Path, name_stem: str) -> Path:
    m = model
    for axis, deg in FACE_ROTATIONS[face]:
        m = m.rotate(axis, deg)
    show(m, names=[f"skybox_{face}"], reset_camera=Camera.FRONT)
    time.sleep(0.9)
    path = out_dir / f"{name_stem}_skybox_{face}.png"
    save_screenshot(str(path))
    return path


def _trim_white(img: Image.Image, pad: int = 20, threshold: int = 250) -> Image.Image:
    gray = np.array(img.convert("L"))
    mask = gray < threshold
    if not mask.any():
        return img
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    y0, y1 = np.argmax(rows), len(rows) - 1 - np.argmax(rows[::-1])
    x0, x1 = np.argmax(cols), len(cols) - 1 - np.argmax(cols[::-1])
    y0 = max(0, y0 - pad); y1 = min(img.height - 1, y1 + pad)
    x0 = max(0, x0 - pad); x1 = min(img.width - 1, x1 + pad)
    return img.crop((x0, y0, x1 + 1, y1 + 1))


def _fit_cell(img: Image.Image, cell_w: int, cell_h: int) -> Image.Image:
    scale = min(cell_w / img.width, cell_h / img.height)
    nw = max(1, int(img.width * scale))
    nh = max(1, int(img.height * scale))
    resized = img.resize((nw, nh), Image.LANCZOS)
    cell = Image.new("RGB", (cell_w, cell_h), "white")
    cell.paste(resized, ((cell_w - nw) // 2, (cell_h - nh) // 2))
    return cell


def compose_cross(faces: Dict[str, Image.Image]) -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
    positions = {
        "UP":    (1, 0),
        "LEFT":  (0, 1),
        "FRONT": (1, 1),
        "RIGHT": (2, 1),
        "BACK":  (3, 1),
        "DOWN":  (1, 2),
    }
    for name, (col, row) in positions.items():
        cell = _fit_cell(_trim_white(faces[name]), MAX_CELL_W, MAX_CELL_H)
        canvas.paste(cell, (col * MAX_CELL_W, row * MAX_CELL_H))
    return canvas


def main() -> int:
    p = argparse.ArgumentParser(description="Skybox 6-face unfold.")
    p.add_argument("source", type=Path)
    p.add_argument("--output-dir", type=Path, default=Path("output"))
    p.add_argument("--name", default=None)
    args = p.parse_args()

    _ensure_viewer()
    name_stem = args.name or args.source.stem
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.source.suffix.lower() not in {".step", ".stp"}:
        print("ERROR: skybox_unfold currently supports only .step input.", file=sys.stderr)
        return 2
    model = import_step(str(args.source))

    face_paths: Dict[str, Path] = {}
    for face in FACE_ROTATIONS:
        face_paths[face] = _capture_face(model, face, args.output_dir, name_stem)

    faces = {face: Image.open(path).convert("RGB") for face, path in face_paths.items()}
    cross = compose_cross(faces)
    cross_path = args.output_dir / f"{name_stem}_skybox_unfolded.png"
    cross.save(cross_path)
    print(f"wrote {cross_path}")
    for f, path in face_paths.items():
        print(f"  {f}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke (requires OCP Viewer running)**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/skybox_unfold.py \
  /Users/liyijiang/work/build123d-cad-skill-test/tests/13-redmi-k80-pro/output/redmi_k80_pro.step \
  --output-dir /tmp/v3_skybox_smoke \
  --name k80pro
ls /tmp/v3_skybox_smoke/
```
Expected: 6 face PNGs + `k80pro_skybox_unfolded.png` (cross layout)

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/visual/skybox_unfold.py
git commit -m "feat(visual): add skybox_unfold via fixed-camera + model rotation"
```

---

## Phase 5 — P0 References Documentation

### Task 9: `multi-view-protocol.md`

**Files:**
- Create: `references/verify/multi-view-protocol.md`

- [ ] **Step 1: 写文档**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/verify/multi-view-protocol.md`

````markdown
# 多视图截图规范 / Multi-View Screenshot Protocol

> 跟 `layer2-visual.md` 的关系：layer2-visual.md 负责"拍照后和参考图做 AI/OpenCV 比对"；本文档负责"拍出来的照片本身要符合规范"。

## 1. 视图命名

**7 个正交视图 + 1 个 ISO**：FRONT / BACK / LEFT / RIGHT / TOP / BOTTOM / ISO

视图名 **等于** 部件语义面，**不等于**世界坐标轴。部件目录必须提供 `part_face_mapping.yaml`（template 在 `references/verify/part-face-mapping-template.yaml`），否则 `multi_view_screenshot.py` 会打印 WARNING 并按坐标轴兜底。

## 2. 何时用什么

| 场景 | 推荐 | 原因 |
|---|---|---|
| 单部件快速预览 | ISO 单张 | 省时，能一眼看出轮廓对不对 |
| 多特征全面审查 | 7 视图 + skybox | 每个面单独可看 |
| 多部件装配审查 | 7 视图 + 多个 ISO 变体 | 需要从多角度看咬合 |
| 和实拍参考图比 | 7 视图 + `--mode iso` 4 变体 | 匹配营销 3/4 角度 |

## 3. 分辨率 / 背景 / 光照

- 默认 **800×800**（OCP Viewer 默认）
- 背景 **纯白**（OCP Viewer 默认）
- **不在对比前改光照参数**——保持默认，避免两次截图差异来自光照

## 4. 模型旋转 vs 相机移动

- **7 视图**：移动相机（`Camera.FRONT` etc.），**不旋转模型**
- **skybox 6 面**：固定 `Camera.FRONT`，**旋转模型**（`FACE_ROTATIONS` 查 `skybox_unfold.py`）

为什么 skybox 用旋转模型？保证 6 张图的光照/透视完全一致。移动相机会因为相机参数差异产生偏差。

## 5. 工具入口

```bash
# 7 视图正交
python3 scripts/visual/multi_view_screenshot.py <step> --mode ortho --face-mapping part_face_mapping.yaml

# 4 个 ISO 变体
python3 scripts/visual/multi_view_screenshot.py <step> --mode iso

# 全部 10 张
python3 scripts/visual/multi_view_screenshot.py <step> --mode both

# 6 面十字展开
python3 scripts/visual/skybox_unfold.py <step>
```

## 6. 产出文件命名约定

- `{name}_{VIEW}.png` — 7 正交视图（VIEW ∈ 第 1 节命名）
- `{name}_ISO_FRONT_TOP.png` / `..._FRONT_BOTTOM` / `..._BACK_TOP` / `..._BACK_BOTTOM`
- `{name}_skybox_{FACE}.png` + `{name}_skybox_unfolded.png`

## 7. 判定阈值

见 `edge-comparison.md`。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/verify/multi-view-protocol.md
git commit -m "docs: add multi-view-protocol.md covering 7+4 views naming and CLI"
```

---

### Task 10: `edge-comparison.md`

**Files:**
- Create: `references/verify/edge-comparison.md`

- [ ] **Step 1: 写文档**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/verify/edge-comparison.md`

````markdown
# 边缘对比判定阈值 / Edge Comparison Thresholds

> 这些是 **几何对齐视角** 的阈值（配合 `scripts/visual/visual_compare.py`）。
> AI Vision 模式的阈值见 cad-vision-verify skill 文档。

## 1. 判定表（第一版，test 13 N=1 样本）

| 指标 | 通过 ✅ | 警告 ⚠️ | 失败 ❌ |
|---|---|---|---|
| 边缘 IoU（二值化 Canny 后） | ≥ 0.85 | 0.70 ~ 0.85 | < 0.70 |
| Bounding box 尺寸偏差 | ≤ 2 % | 2 % ~ 5 % | > 5 % |
| 关键特征位置偏差 | ≤ 2 mm | 2 ~ 5 mm | > 5 mm |
| 灰度差 heatmap 平均值 | ≤ 15 | 15 ~ 30 | > 30 |

注：阈值为建议值，test 14/15 积累更多案例后应复核。

## 2. Canny 参数

- `low=50, high=150`，高斯模糊 `sigma=1.0`（实测可行于 test 13）
- **不调** Canny 参数去"抢救"失败的对比——如果 IoU 低，回源头修模型

## 3. 失败诊断路径

| 症状 | 回到哪一步 |
|---|---|
| 尺寸整体错 | Step R3 参数合同（params.md） |
| 特征位置错 | Step R3.5 合同校验（contract.yaml） |
| 比例错 | Step R2 资料来源（三视图尺寸核对） |
| 视图名对不上 | `part_face_mapping.yaml` |
| 参考图歪/畸变 | Step R2.7 参考图预处理 |

## 4. 不适用场景

- 透视强烈的 3/4 角度实拍 → 走 AI Vision（cad-vision-verify skill）
- 参考图有遮挡、阴影、反光 → IoU 会虚低，以人眼判断为准
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/verify/edge-comparison.md
git commit -m "docs: add edge-comparison thresholds and failure routing"
```

---

### Task 11: `reference-image-preprocessing.md`

**Files:**
- Create: `references/verify/reference-image-preprocessing.md`

- [ ] **Step 1: 写文档**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/verify/reference-image-preprocessing.md`

````markdown
# 参考图预处理规范 / Reference Image Preprocessing

> 核心原则：参考图是实拍/营销图，不是干净的正交视图。未经预处理的图不得进入 Layer 2 对比。

## 1. 为什么必做

- GSMArena / 官网营销图带背景、透视、阴影
- 拆机视频截帧有运动模糊
- 不裁掉背景直接对比 → Canny 会把背景边缘当部件边缘 → IoU 虚低

## 2. 最小预处理流程

```
原始参考图 ──► preprocess_reference.py
                │
                ├── 输入：图 + bbox + 物理尺寸 + 尺寸轴
                │
                ├── 输出：
                │    {stem}_cropped.png   去背景
                │    {stem}_bbox.json     原图坐标
                │    {stem}_scale.json    mm/px
                │
                └── 记录到：refs/clean/  或  references/{part}/clean/
```

## 3. bbox 怎么来

### 手动标注（推荐）
打开参考图，用 Preview 或 matplotlib ginput 点选 4 个角点：
```python
from PIL import Image
import matplotlib.pyplot as plt
img = Image.open("reference.png")
plt.imshow(img); pts = plt.ginput(2)  # 左上 + 右下
x0, y0 = map(int, pts[0]); x1, y1 = map(int, pts[1])
print(f"--bbox {x0},{y0},{x1-x0},{y1-y0}")
```

### 自动前景分割（兜底）
图像简单 + 背景纯色时可用 `rembg`（需单独安装）。否则走手动。

## 4. 物理尺寸从哪来

- **首选**：官方参数（已知手机长度 160.26 mm）
- **次选**：电商详情页标的"实拍"尺寸（置信度 ★★）
- **兜底**：特征比例推断（比如摄像头岛已知 = ? mm，反推长度，置信度 ★★）

## 5. 典型案例

### 案例 A：test 13 官方侧视图
```bash
python3 scripts/visual/preprocess_reference.py \
  references/redmi-k80-pro/images/official_03_side.jpg \
  --bbox "72,50,385,1063" \
  --physical-length "160.26mm" \
  --physical-axis height \
  --output-dir references/redmi-k80-pro/clean/
```

### 案例 B：GSMArena 背面图
```bash
python3 scripts/visual/preprocess_reference.py \
  references/redmi-k80-pro/images/gsmarena_3.jpg \
  --bbox "420,180,680,1480" \
  --physical-length "160.26mm" \
  --physical-axis height \
  --output-dir references/redmi-k80-pro/clean/
```

## 6. 产出命名

一组参考图建议都放在同一个 `clean/` 目录：
```
references/{product}/
├── images/                     # 原始图（保留）
│   ├── gsmarena_1.jpg
│   ├── official_03_side.jpg
│   └── ...
└── clean/                      # 预处理产出（入 Layer 2 比较）
    ├── official_03_side_cropped.png
    ├── official_03_side_bbox.json
    ├── official_03_side_scale.json
    └── ...
```
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/verify/reference-image-preprocessing.md
git commit -m "docs: add reference-image-preprocessing workflow and bbox capture"
```

---

## Phase 6 — SKILL.md P0 Bridge Updates

### Task 12: SKILL.md Layer 2 段落插入工具链桥接

**Files:**
- Modify: `SKILL.md`（在 Layer 2 对应段落后插入新小节）

- [ ] **Step 1: 定位插入点**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "Layer 2" SKILL.md | head -20
```
找到 "Layer 2 视觉" 开头的那个 section（约 L8xx-9xx），把新内容插到该 section 末尾 "---" 之前。

- [ ] **Step 2: 插入桥接段**

用 Edit 工具在 Layer 2 段末尾插入以下内容（保留 `old_string` 独特上下文，找到该 section 最后几行再插）：

```markdown
### Layer 2 视觉验证标准工具链（v3 / test 13 沉淀）

Layer 2 比对前，**参考图必须预处理过**（见 `references/verify/reference-image-preprocessing.md`）。

标准三步：

```bash
# 1) 7 视图 + skybox（需要 part_face_mapping.yaml）
python3 scripts/visual/multi_view_screenshot.py <step> --mode ortho --face-mapping <yaml>
python3 scripts/visual/skybox_unfold.py <step>

# 2) 参考图预处理
python3 scripts/visual/preprocess_reference.py <photo> \
    --bbox "x,y,w,h" --physical-length "160mm" --physical-axis height \
    --output-dir refs/clean/

# 3) 边缘对比
python3 scripts/visual/visual_compare.py \
    output/{part}_FRONT.png refs/clean/{photo}_cropped.png \
    --reference-scale refs/clean/{photo}_scale.json \
    --rendered-scale auto \
    --mode edge_overlay \
    --output output/compare_{view}.png
```

判定阈值见 `references/verify/edge-comparison.md`。
```

- [ ] **Step 3: 验证**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "Layer 2 视觉验证标准工具链" SKILL.md
wc -l SKILL.md
```
Expected: 找到该 heading；SKILL.md 行数 +约 28 行

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "docs(skill): bridge Layer 2 to v3 visual toolchain scripts"
```

---

### Task 13: SKILL.md 新增 Step R2.7 参考图预处理桥接段

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: 定位插入点**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "Step R2" SKILL.md
grep -n "Step R3" SKILL.md | head -5
```
插入点：Step R2（或 R2.x）之后、Step R3 之前。

- [ ] **Step 2: 插入 Step R2.7**

```markdown
### Step R2.7 — 参考图现实对齐检查（v3 新增）

任何要用于 Layer 2 视觉对比的参考图都是**实拍或营销图**，不是干净的正交视图。
进入 Layer 2 前必须走：

1. 判断图源类型：官方三视图 / 营销图 / 电商实拍 / 拆机视频截帧（不同置信度）
2. 跑 `preprocess_reference.py` 得到 `{stem}_cropped.png` + `{stem}_scale.json`
3. 为本部件写 `part_face_mapping.yaml`（template: `references/verify/part-face-mapping-template.yaml`）
4. 确定 visual_compare 的使用档位（ortho 正交 / iso 3/4 角度 / 手动匹配实拍）

**未经预处理的图不得进入 Layer 2** — 否则 IoU / 边缘对比毫无物理意义。

详见 `references/verify/reference-image-preprocessing.md` 和 `references/verify/multi-view-protocol.md`。
```

- [ ] **Step 3: 验证 + Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "Step R2.7" SKILL.md
git add SKILL.md
git commit -m "docs(skill): add Step R2.7 reference-image preprocessing gate"
```

---

## Phase 7 — P0 End-to-End Validation

### Task 14: 在 test 14（K70）目录下完整跑 P0 链路

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/part_face_mapping.yaml`
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/output/v3_validation/`（空目录，脚本填充）

> **目的**：用全新脚本跑现有 test 14，确认 P0 工具链"开箱即用"。如果任何脚本 fails，回补前 13 个任务。

- [ ] **Step 1: 检查 test 14 目录现状**

```bash
ls /Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/
ls /Users/liyijiang/work/build123d-cad-skill-test/references/redmi-k80-pro/images/ 2>/dev/null || echo "(no test 14 refs yet — use test 13 for smoke)"
```

- [ ] **Step 2: 写 part_face_mapping.yaml**

选择 test 14 已有 STEP / py 所在目录，创建 `part_face_mapping.yaml`：
```yaml
part: xiaomi_k70_case
coordinate_system:
  up: "+Z"
  right: "+X"
  screen_normal: "-Y"
face_mapping:
  FRONT: BACK       # 屏幕朝相机 -Y，所以取 Camera.BACK
  BACK:  FRONT
  LEFT:  LEFT
  RIGHT: RIGHT
  TOP:   TOP
  BOTTOM: BOTTOM
```

**注**：如 test 14 还没有成型的 STEP / 模型代码，这一步回落到用 test 13 的 K80 Pro STEP 做 smoke。

- [ ] **Step 3: 跑 P0 全链路**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/
TEST_STEP=<path/to/test14/output/xxx.step>   # or 用 test13 K80 Pro 兜底
SKILL=/Users/liyijiang/.agents/skills/build123d-cad
mkdir -p output/v3_validation

# 1. multi_view_screenshot
python3 $SKILL/scripts/visual/multi_view_screenshot.py $TEST_STEP \
  --output-dir output/v3_validation/ \
  --name k70case \
  --mode ortho \
  --face-mapping part_face_mapping.yaml

# 2. skybox_unfold
python3 $SKILL/scripts/visual/skybox_unfold.py $TEST_STEP \
  --output-dir output/v3_validation/ \
  --name k70case

# 3. preprocess a real reference (use test 13's official_03_side.jpg as stand-in)
python3 $SKILL/scripts/visual/preprocess_reference.py \
  /Users/liyijiang/work/build123d-cad-skill-test/references/redmi-k80-pro/images/official_03_side.jpg \
  --bbox "72,50,385,1063" \
  --physical-length "160.26mm" \
  --physical-axis height \
  --output-dir output/v3_validation/clean/

# 4. visual_compare
python3 $SKILL/scripts/visual/visual_compare.py \
  output/v3_validation/k70case_RIGHT.png \
  output/v3_validation/clean/official_03_side_cropped.png \
  --reference-scale output/v3_validation/clean/official_03_side_scale.json \
  --rendered-scale auto \
  --mode edge_overlay \
  --output output/v3_validation/compare_right.png

# 5. pixel_measure
python3 $SKILL/scripts/visual/pixel_measure.py \
  output/v3_validation/clean/official_03_side_cropped.png \
  --scale output/v3_validation/clean/official_03_side_scale.json \
  --points "100,100;200,500" \
  --origin "center"
```

- [ ] **Step 4: 肉眼验收**

打开 `output/v3_validation/`：
- 7 张 `k70case_{VIEW}.png` 各自对应正确语义面
- `k70case_skybox_unfolded.png` 十字布局无裂缝
- `compare_right.png` 红蓝边缘叠加清晰
- `pixel_measure` 的 CSV 输出数值合理（毫米范围）

**Acceptance gate**：任何一步失败 → 修脚本、回跑，直到全部通过。**不 commit 测试产出**（output/ 在 gitignore 里）。

- [ ] **Step 5: 总结 commit（只 commit test 14 的 yaml）**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/14-xiaomi-k70-case/part_face_mapping.yaml
git commit -m "test(14): add part_face_mapping.yaml for P0 v3 toolchain validation"
```

---

---

## Phase 8 — P1 Reverse-Engineering Methodology + Tool

### Task 15: `annotate_reference.py`（P1）

**Files:**
- Create: `scripts/visual/annotate_reference.py`
- Test: `scripts/visual/tests/test_annotate_reference.py`

**功能**：输入原始图 + annotations.json → 输出标注叠加图（尺寸线、特征框、置信度颜色）。

- [ ] **Step 1: 写失败测试**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/tests/test_annotate_reference.py`

```python
"""Unit tests for annotate_reference.
annotate_reference 的单元测试。
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.visual.annotate_reference import annotate


FIXTURES = Path(__file__).parent / "fixtures"


SAMPLE_ANNOTATIONS = {
    "scale": {"pixels": 800, "mm": 160.0},
    "origin": [227, 470],
    "features": [
        {"name": "camera", "center_px": [227, 80], "size_mm": [20, 20], "confidence": 5, "color": "blue"},
        {"name": "button", "center_px": [415, 300], "size_mm": [6, 20], "confidence": 3, "color": "red"},
    ],
}


class TestAnnotate(unittest.TestCase):
    def test_produces_output_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ann_path = Path(tmp) / "ann.json"
            ann_path.write_text(json.dumps(SAMPLE_ANNOTATIONS))
            out = annotate(
                image_path=FIXTURES / "synthetic_phone_front.png",
                annotations_path=ann_path,
                output_path=Path(tmp) / "annotated.png",
            )
            self.assertTrue(out.exists())

    def test_rejects_invalid_confidence(self) -> None:
        bad = dict(SAMPLE_ANNOTATIONS)
        bad = {**SAMPLE_ANNOTATIONS, "features": [
            {"name": "x", "center_px": [10, 10], "size_mm": [1, 1], "confidence": 99, "color": "red"}
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            ann_path = Path(tmp) / "ann.json"
            ann_path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                annotate(
                    image_path=FIXTURES / "synthetic_phone_front.png",
                    annotations_path=ann_path,
                    output_path=Path(tmp) / "annotated.png",
                )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 实现 `annotate_reference.py`**

File: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/visual/annotate_reference.py`

```python
#!/usr/bin/env python3
"""Draw dimension lines + feature boxes + confidence colors on a reference photo.
在参考图上叠加尺寸线 + 特征框 + 置信度颜色。

CLI:
    python3 annotate_reference.py <photo.png> --annotations FILE.json --output PATH

annotations.json:
    {
      "scale": {"pixels": 1080, "mm": 162.2},
      "origin": [540, 820],
      "features": [
        {"name": "camera_module", "center_px": [320, 150], "size_mm": [38, 38],
         "confidence": 4, "color": "red"},
        ...
      ]
    }
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


CONFIDENCE_COLORS = {
    5: (  0,   0, 200),  # blue  = 官方参数
    4: (200,   0,   0),  # red   = 反推
    3: (200, 140,   0),  # orange
    2: (200, 200,   0),  # yellow = 低置信
    1: (128, 128, 128),  # grey
}


def _pick_color(spec: str | None, confidence: int) -> tuple:
    if spec == "blue":   return (0, 0, 200)
    if spec == "red":    return (200, 0, 0)
    if spec == "yellow": return (200, 200, 0)
    if spec in ("orange", "amber"): return (200, 140, 0)
    return CONFIDENCE_COLORS.get(confidence, (0, 0, 0))


def annotate(image_path: Path, annotations_path: Path, output_path: Path) -> Path:
    data: dict[str, Any] = json.loads(annotations_path.read_text())
    img = Image.open(image_path).convert("RGB").copy()
    draw = ImageDraw.Draw(img)

    scale = data.get("scale", {})
    mm_per_px = scale["mm"] / scale["pixels"] if scale else None
    origin = data.get("origin")

    if origin:
        ox, oy = origin
        draw.line([(ox - 20, oy), (ox + 20, oy)], fill=(0, 0, 0), width=2)
        draw.line([(ox, oy - 20), (ox, oy + 20)], fill=(0, 0, 0), width=2)
        draw.text((ox + 8, oy + 8), "O", fill=(0, 0, 0))

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for feat in data.get("features", []):
        conf = int(feat.get("confidence", 3))
        if conf < 1 or conf > 5:
            raise ValueError(f"confidence must be 1..5, got {conf}")
        color = _pick_color(feat.get("color"), conf)
        cx, cy = feat["center_px"]
        sw_mm, sh_mm = feat["size_mm"]
        if mm_per_px is None:
            raise ValueError("annotations.scale required to convert size_mm → px")
        sw_px = sw_mm / mm_per_px
        sh_px = sh_mm / mm_per_px
        draw.rectangle(
            [cx - sw_px / 2, cy - sh_px / 2, cx + sw_px / 2, cy + sh_px / 2],
            outline=color, width=2,
        )
        label = f"{feat['name']} [{ '★' * conf }]"
        draw.text((cx + sw_px / 2 + 4, cy - sh_px / 2), label, fill=color, font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path


def main() -> int:
    p = argparse.ArgumentParser(description="Annotate a reference photo with dims + features.")
    p.add_argument("photo", type=Path)
    p.add_argument("--annotations", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    try:
        out = annotate(args.photo, args.annotations, args.output)
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: 运行测试 + Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
python3 scripts/visual/tests/run_all_tests.py
git add scripts/visual/annotate_reference.py scripts/visual/tests/test_annotate_reference.py
git commit -m "feat(visual): add annotate_reference.py with confidence-colored markers"
```

---

### Task 16: `reverse-engineering.md`（P1）

**Files:**
- Create: `references/reference-product/reverse-engineering.md`

- [ ] **Step 1: 写文档**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/reference-product/reverse-engineering.md`

````markdown
# 参考物尺寸反推方法论（5 种手段）

> 适用场景：官网未提供 STEP，GrabCAD 未收录，需要从公开资料反推尺寸。

## 1. 按置信度排序的 5 种手段

| 手段 | 输入 | 精度 | 适用场景 | 对应工具 |
|---|---|---|---|---|
| A. STEP 导入 | model.step | ★★★★★ | GrabCAD / 官网 | `import_step()` |
| B. 三视图比例反推 | 官方三视图 PNG | ★★★★ | 官网有高清产品图 | `pixel_measure.py` |
| C. 已知基准测量 | 实拍 + 已知尺寸 | ★★★ | 电商详情页实拍 | `pixel_measure.py` |
| D. 特征比例推断 | 单张正面图 | ★★ | 只有一张图 | 手动估算 |
| E. 拆解视频截帧 | 拆机视频帧 | ★★★ | iFixit / B 站 | `pixel_measure.py` |

## 2. 手段 B — 三视图比例反推（最常用）

1. 找到官方三视图 PNG（背景纯色，无透视畸变）
2. 用 `preprocess_reference.py` 裁部件 + 建 scale.json
3. 用 `pixel_measure.py` 批量测关键点
4. 换算成部件本地坐标（以中心为原点）
5. 填 `params.md` 的"摄像头模组位置"等行，**标 ★★★★ 置信度**

完整命令例：
```bash
# 1) crop
python3 scripts/visual/preprocess_reference.py official_back.jpg \
  --bbox "340,220,700,1520" --physical-length "162.0mm" --physical-axis height \
  --output-dir refs/k70/clean/

# 2) measure
python3 scripts/visual/pixel_measure.py refs/k70/clean/official_back_cropped.png \
  --scale refs/k70/clean/official_back_scale.json \
  --points "360,180;340,520;200,760" \
  --origin "center" --output refs/k70/measurements.csv
```

## 3. 手段 C — 已知基准测量

用途：官网没三视图，但电商详情页有一张"带尺子"的图。
步骤：
1. 在图上标"尺子两端"的像素坐标 → 得 mm/px
2. 用同一 mm/px 量其他特征

## 4. 手段 D — 特征比例推断（低置信度）

兜底手段。假设某一已知特征大小（如"iPhone 15 Pro 摄像头模组 ≈ 38mm × 38mm"）→ 反推整机尺寸。
**必须在 `params.md` 标 ★★ 置信度**，下游建模时要把这些尺寸标为"待验证"。

## 5. 手段 E — 拆解视频截帧

视频截帧通常有运动模糊和光照不均：
- 优先取特写帧（镜头静止 > 1 秒）
- 拿游标卡尺或已知螺丝尺寸做基准
- 结果置信度 ★★★（低于官方三视图）

## 6. 失败兜底

5 种手段全部不可用时：
- 让用户手动测量实物
- 提供测量位置清单（长/宽/厚/摄像头位置/按键位置）
- 在 `params.md` 标记"用户实测"来源
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/reference-product/reverse-engineering.md
git commit -m "docs: add 5-method reverse-engineering methodology for reference products"
```

---

### Task 17: `photo-annotation.md`（P1）

**Files:**
- Create: `references/reference-product/photo-annotation.md`

- [ ] **Step 1: 写文档**

File: `/Users/liyijiang/.agents/skills/build123d-cad/references/reference-product/photo-annotation.md`

````markdown
# 参考图标注规范 / Photo Annotation Convention

> 工具：`scripts/visual/annotate_reference.py`

## 1. 颜色约定

| 颜色 | 含义 | 典型 confidence |
|---|---|---|
| 🔵 蓝 | 官方参数（官网 / 规格书） | 5 |
| 🔴 红 | 反推尺寸（手段 B/C/E） | 4 |
| 🟠 橙 | 拆解/视频截帧反推 | 3 |
| 🟡 黄 | 特征比例推断（手段 D） | 2 |
| ⚫ 灰 | 未确认 / 待用户测量 | 1 |

`annotate_reference.py` 的 `confidence` 字段是 1~5，脚本按这个自动上色；`color` 字段可以手动覆盖。

## 2. annotations.json 格式

```json
{
  "scale": {"pixels": 1080, "mm": 162.0},
  "origin": [540, 820],
  "features": [
    {
      "name": "camera_module",
      "center_px": [320, 150],
      "size_mm": [38, 38],
      "confidence": 4,
      "color": "red"
    },
    {
      "name": "power_button",
      "center_px": [1000, 500],
      "size_mm": [6, 20],
      "confidence": 5
    }
  ]
}
```

## 3. 产出文件命名

- `{face}_annotated.png`（face ∈ front/back/side/top/bottom）
- 放到 `references/{product}/annotated/` 目录
- 原图保留在 `references/{product}/images/`

## 4. 标注流程

1. 跑 `preprocess_reference.py` 拿到 cropped 图 + scale.json
2. 用 Preview / matplotlib ginput 在原图或 cropped 图上点关键特征，记录像素坐标
3. 写 annotations.json（scale/origin/features）
4. 跑 `annotate_reference.py`
5. 肉眼检查输出，置信度低的特征加入 `params.md` 的"待确认"列表

## 5. 案例

见 `/Users/liyijiang/work/build123d-cad-skill-test/tests/13-redmi-k80-pro/output/photo_annotated.png` 和 `side_annotated.png`（test 13 实战产出）。
````

- [ ] **Step 2: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add references/reference-product/photo-annotation.md
git commit -m "docs: add photo-annotation color convention and annotations.json format"
```

---

### Task 18: SKILL.md 新增 Step R2.5 反推流程桥接

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: 定位插入点**

插入点：Step R2 兜底段之后、Step R2.7 之前。

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
grep -n "Step R2" SKILL.md
```

- [ ] **Step 2: 插入 Step R2.5**

```markdown
### Step R2.5 — 没有 STEP 模型时的反推流程（v3 新增）

官网未提供 STEP 且 GrabCAD 未收录时，按以下置信度顺序尝试：

1. **手段 B**（三视图比例反推）— 成本最低，官方三视图存在时首选
2. **手段 C**（已知基准测量）— 用电商实拍图补关键特征
3. **手段 E**（拆解视频截帧）— iFixit / B 站有拆机时
4. **手段 D**（特征比例推断）— 兜底，置信度 ★★，务必标注
5. **用户实测**——上面全部不可用时

反推完成后，`params.md` 的置信度列必须**如实填写**。禁止伪造 ★★★★★。

完整流程与 CLI 命令见 `references/reference-product/reverse-engineering.md`。
标注规范见 `references/reference-product/photo-annotation.md`。
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add SKILL.md
git commit -m "docs(skill): add Step R2.5 reverse-engineering routing for no-STEP cases"
```

---

## Phase 9 — P1 End-to-End Validation

### Task 19: 在 test 14 K70 做一次"无 STEP"反推实操

**Files:**
- Create: `/Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/refs/` 目录
- Create: `.../refs/annotations_back.json`（人工填）

> 目的：跑通"官方三视图 → preprocess → pixel_measure → annotate → params.md 填充"完整链路。

- [ ] **Step 1: 准备一张 K70 官方后盖图**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test/tests/14-xiaomi-k70-case/
mkdir -p refs/images refs/clean refs/annotated
# 放一张 K70 官方后盖图到 refs/images/
```
（如 test 14 还没下载，用 test 13 的 K80 Pro back 图做 smoke）

- [ ] **Step 2: 走完整链路**

```bash
SKILL=/Users/liyijiang/.agents/skills/build123d-cad

# 0) 先用 matplotlib ginput 取部件 bbox（手动，一次性）
python3 -c "
from PIL import Image; import matplotlib.pyplot as plt
img = Image.open('refs/images/k70_back.jpg'); plt.imshow(img); pts = plt.ginput(2)
x0, y0 = map(int, pts[0]); x1, y1 = map(int, pts[1])
print(f'--bbox {x0},{y0},{x1-x0},{y1-y0}')
"
# 假设输出：--bbox 340,220,700,1520

# 1) 预处理（用上一步输出的 bbox）
python3 $SKILL/scripts/visual/preprocess_reference.py \
  refs/images/k70_back.jpg \
  --bbox "340,220,700,1520" --physical-length "162.0mm" --physical-axis height \
  --output-dir refs/clean/

# 2) 标几个关键点（用 ginput 同法取 3 个特征中心）
python3 $SKILL/scripts/visual/pixel_measure.py \
  refs/clean/k70_back_cropped.png \
  --scale refs/clean/k70_back_scale.json \
  --points "360,180;340,520;200,760" --origin "center"

# 3) 写 annotations_back.json（人工 — 摄像头中心、主相机尺寸、电源键位置）
# (write file by hand based on step 2 output)

# 4) 渲染标注图
python3 $SKILL/scripts/visual/annotate_reference.py \
  refs/clean/k70_back_cropped.png \
  --annotations refs/annotations_back.json \
  --output refs/annotated/k70_back_annotated.png

# 5) 检查 annotations_back 置信度 → 填 params.md
```

- [ ] **Step 3: 肉眼验收**

- `k70_back_annotated.png` 上：原点 + 摄像头框 + 电源键框 + 星级标签
- `params.md` 新增反推特征都带置信度星级

- [ ] **Step 4: Commit 测试 artifacts**

```bash
cd /Users/liyijiang/work/build123d-cad-skill-test
git add tests/14-xiaomi-k70-case/refs/
git commit -m "test(14): validate P1 reverse-engineering + annotation toolchain"
```

---

## Acceptance Criteria（对齐 spec §10）

- ✅ P0 工具链（6 个脚本）在 test 14 目录下开箱可用，无需再写一次性脚本
- ✅ 参考图来自实拍 / 营销图时，必须先跑 `preprocess_reference.py`；`visual_compare.py` 以 scale.json 作为强制输入
- ✅ SKILL.md Step R2.5 / R2.7 / Layer 2 桥接段被插入，grep 可查
- ✅ P1 references 文档能直接指导"只有照片没有 STEP"场景的下一个参考物建模
- ✅ 所有纯图像脚本有 unittest，`run_all_tests.py` 通过（≥ 14 tests）
- ⚠️ **spec §9 第 4 条修订**：工具脚本（非 Part 生成脚本）不要求 OCP 自动预览块。Part 生成脚本（test 14 最终的 `xiaomi_k70_case.py`）仍需遵循原规则。

## Out of Scope

- ❌ **P2 SKILL.md 瘦身**：已明确延后至 P0+P1 稳定后再评估
- ❌ **`pixel_measure.py` 的 interactive matplotlib 模式**：本计划只实现 batch 模式；interactive 作为后续单独 task
- ❌ **AI Vision 比对**：属于 cad-vision-verify 姊妹 skill 职责
- ❌ **档 3（匹配实拍 3/4 角度）**：`multi_view_screenshot.py` 只做 ortho + iso 变体，不做相机参数匹配实拍

---

## Summary Task Count

| Phase | Tasks | 代码行数 | 文档行数 |
|---|---|---|---|
| 0 | 1 | 0 | 0 |
| 1 | 1 | ~80 | 0 |
| 2 | 3 | ~550 | 0 |
| 3 | 1 | ~80 | ~40 |
| 4 | 2 | ~300 | 0 |
| 5 | 3 | 0 | ~300 |
| 6 | 2 | 0 | ~60 |
| 7 | 1 | 0 | ~20 |
| 8 | 4 | ~180 | ~250 |
| 9 | 1 | 0 | ~30 |
| **Total** | **19 tasks** | **~1190 行** | **~700 行** |

预计总工作量：**1.5~2 个工作日**（P0 约 1 天，P1 约 0.5 天，端到端验收 0.5 天）。
