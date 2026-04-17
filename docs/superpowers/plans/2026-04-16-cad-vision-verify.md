# CAD Vision Verify Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone `cad-vision-verify` skill at `/Users/liyijiang/.agents/skills/cad-vision-verify/` that compares CAD model screenshots against reference images, diagnoses root causes of visual deviations, and routes fixes.

**Architecture:** Five Python modules under `scripts/` (vision_probe, screenshot, compare, diagnose, verify_loop) orchestrated by verify_loop.py. Each module is independently testable. SKILL.md defines the workflow protocol for Claude Code integration. The skill reads contract YAML + reference images and outputs structured JSON reports.

**Tech Stack:** Python 3, PyYAML (required), Anthropic SDK (optional), OpenCV (optional), Pillow (optional), ocp_vscode (optional)

---

## File Structure

```
/Users/liyijiang/.agents/skills/cad-vision-verify/
├── SKILL.md                          — Skill definition + workflow protocol
├── scripts/
│   ├── vision_probe.py               — Vision API proxy probe with 24h cache
│   ├── screenshot.py                 — OCP 7-view screenshot generation
│   ├── compare.py                    — Three-mode comparison engine
│   ├── diagnose.py                   — Root cause diagnosis + fix routing
│   └── verify_loop.py                — Full verification-fix loop entry point + CLI
├── references/
│   ├── constraint-types.md           — Constraint type quick reference
│   └── examples/
│       └── k70-report.json           — Example verification report
└── tests/
    ├── test_vision_probe.py          — Unit tests for probe + cache
    ├── test_compare.py               — Unit tests for compare (opencv + report)
    ├── test_diagnose.py              — Unit tests for diagnosis engine
    └── fixtures/
        ├── sample_contract.yaml      — Minimal test contract
        ├── ref_BACK.png              — 50x50 test reference image
        └── model_BACK.png            — 50x50 test model image
```

**Files modified in build123d-cad:**
- `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md` — Update R4 to reference new skill
- `/Users/liyijiang/.agents/skills/build123d-cad/scripts/validate/visual_compare.py` — Add deprecation header

---

### Task 1: Create skill directory structure + SKILL.md

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/SKILL.md`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/` (directory)
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/references/` (directory)
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/references/examples/` (directory)
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/` (directory)
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/` (directory)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /Users/liyijiang/.agents/skills/cad-vision-verify/{scripts,references/examples,tests/fixtures}
```

- [ ] **Step 2: Write SKILL.md**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/SKILL.md` with:

```markdown
---
name: cad-vision-verify
description: |
  CAD 模型视觉验证与参数诊断。对比模型截图与参考图，输出偶合度评分 + 根因诊断 + 修复路由。
  三模式自动降级：Claude Vision -> OpenCV -> 人工并排。
  触发词：「视觉验证」「比对参考图」「检查模型」「Layer 2」
  「看起来对不对」「验证截图」「visual verify」「compare reference」
---

# CAD Vision Verify

CAD 模型视觉验证与参数诊断 skill。对比模型截图与参考图，输出偶合度评分、根因诊断和修复路由。

---

## When to Activate

- 用户说「视觉验证」「比对参考图」「检查模型」「看起来对不对」
- build123d-cad 的 Step R4 建模完成后自动调用
- 用户提供参考图 + 模型截图，要求比对
- 英文: "visual verify", "compare reference", "check model", "vision check"

---

## Dependencies

| Dependency | Required? | Purpose |
|---|:---:|---|
| PyYAML | Required | Parse contract.yaml |
| Anthropic SDK | Optional | ai_vision mode (highest accuracy) |
| OpenCV (cv2) | Optional | opencv mode (medium accuracy) |
| Pillow (PIL) | Optional | manual mode (side-by-side images) |
| OCP CAD Viewer | Optional | Auto-screenshot generation |

All optional deps missing -> degrades to skip mode.

---

## Workflow Protocol

```
Step 1: Input Check
  - contract.yaml exists? -> Full mode (L1+L2+diagnosis)
  - No contract but reference images? -> Visual-only mode (L2 only)
  - Nothing available? -> Prompt user to provide inputs

Step 2: Environment Probe + Mode Decision
  - Probe Vision API -> ai_vision (best)
  - Check OpenCV -> opencv (fallback)
  - Check PIL -> manual (fallback)
  - Nothing -> skip
  Output: "Current mode: ai_vision / opencv / manual / skip"

Step 3: Screenshot Capture
  - OCP running -> Auto-capture 7 standard views
  - OCP not running -> Ask user for screenshot paths

Step 4: Run Comparison -> Output scored report

Step 5: Verdict
  - PASS (avg >= 80) -> Report result, done
  - WARN (avg 60-79) -> List issues, user decides
  - FAIL (avg < 60) -> Enter Step 6

Step 6: Root Cause Diagnosis -> Output diagnosis report
  - Root cause C (code error) -> "Suggest: modify code variable xxx"
  - Root cause B (contract error) -> "Suggest: modify contract.yaml xxx"
  - Root cause A (data source error) -> "Needs manual: params.md value xxx may be inaccurate"
```

---

## Two Invocation Modes

### Mode 1: Called by build123d-cad (embedded in workflow)

build123d-cad Step R4 passes: solid object, contract.yaml, ref_dir.
Skill returns: verdict + diagnoses list.
build123d-cad routes fix based on root cause.

### Mode 2: User triggers directly (standalone)

User provides: model screenshots + reference images + contract.yaml (optional).
Skill runs comparison independently.
Without contract, degrades to visual-only (no root cause diagnosis).

---

## Comparison Modes

### ai_vision (Claude Vision API)
- Sends reference + model screenshot to Claude with structured prompt
- Claude outputs JSON with per-feature shape/position/size match scores
- Highest accuracy: understands semantics, detects missing features

### opencv (OpenCV contour matching)
- Weighted score: area_ratio(25%) + hu_moment(35%) + centroid(20%) + feature_count(20%)
- No API needed, fully local
- Limited: only compares outer contours

### manual (side-by-side images)
- Generates compare_{VIEW}.png with reference left, model right
- Returns MANUAL_REVIEW verdict for human inspection

---

## Root Cause Classification

| Root Cause | Meaning | Auto-fixable? | Fix Target |
|:---:|---|:---:|---|
| A | Data source error | No | params.md values |
| B | Contract error | Yes | contract.yaml constraints |
| C | Code error | Yes | Modeling code |

Key insight: Layer 2 FAIL but Layer 1 PASS -> likely root cause A or B.

---

## Fix Loop Limits

| Layer | Max Rounds |
|---|:---:|
| Layer 1 auto-fix | 3 |
| Layer 2 visual fix | 2 |
| Cross-layer feedback | 2 |
| **Total** | **<= 5** |

Exceeds limit -> output diagnosis report, hand to human.

---

## Scripts

| Script | Purpose | CLI Usage |
|---|---|---|
| `vision_probe.py` | Probe Vision API support | `python3 scripts/vision_probe.py` |
| `screenshot.py` | Generate 7-view screenshots | `python3 scripts/screenshot.py --output-dir out/` |
| `compare.py` | Run comparison (3 modes) | `python3 scripts/compare.py --contract c.yaml --ref-dir refs/ --output-dir out/` |
| `diagnose.py` | Diagnose failures | `python3 scripts/diagnose.py --l1-result l1.json --l2-result l2.json --contract c.yaml` |
| `verify_loop.py` | Full verification loop | `python3 scripts/verify_loop.py --contract c.yaml --ref-dir refs/ --output-dir out/` |

---

## Reference Documents

- Design spec: `docs/superpowers/specs/2026-04-16-cad-vision-verify-design.md`
- Layer 2 visual spec: `build123d-cad/references/verify/layer2-visual.md`
- Feedback diagnosis spec: `build123d-cad/references/verify/feedback-diagnosis.md`
- Constraint types: `references/constraint-types.md`
- Example report: `references/examples/k70-report.json`
```

- [ ] **Step 3: Verify SKILL.md is valid YAML frontmatter**

```bash
python3 -c "
import yaml
with open('/Users/liyijiang/.agents/skills/cad-vision-verify/SKILL.md') as f:
    content = f.read()
# Extract frontmatter between --- markers
parts = content.split('---', 2)
meta = yaml.safe_load(parts[1])
assert meta['name'] == 'cad-vision-verify', f'Expected cad-vision-verify, got {meta[\"name\"]}'
print(f'SKILL.md valid: name={meta[\"name\"]}')
"
```

Expected: `SKILL.md valid: name=cad-vision-verify`

- [ ] **Step 4: Commit**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
git init  # if not already a repo — skip if parent is a repo
git add SKILL.md
git commit -m "feat(cad-vision-verify): add skill skeleton + SKILL.md"
```

---

### Task 2: vision_probe.py — Vision API proxy probe with caching

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/vision_probe.py`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_vision_probe.py`

- [ ] **Step 1: Write the failing test**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_vision_probe.py`:

```python
"""Tests for vision_probe.py — Vision API proxy probe with caching."""
import os
import sys
import json
import time
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_probe_returns_dict_when_no_sdk():
    """probe_vision_support returns unsupported when anthropic SDK missing."""
    # This test works even without anthropic installed
    from vision_probe import probe_vision_support
    result = probe_vision_support()
    assert isinstance(result, dict)
    assert "supported" in result


def test_cache_write_and_read():
    """Cache stores probe result and reads it back within TTL."""
    from vision_probe import write_cache, read_cache
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "vision_probe_cache.json")
        data = {"supported": True, "model": "test"}
        write_cache(cache_path, data)
        result = read_cache(cache_path, ttl_seconds=3600)
        assert result is not None
        assert result["supported"] is True


def test_cache_expired():
    """Cache returns None when TTL expired."""
    from vision_probe import write_cache, read_cache
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "vision_probe_cache.json")
        data = {"supported": True, "model": "test", "timestamp": time.time() - 100000}
        with open(cache_path, "w") as f:
            json.dump(data, f)
        result = read_cache(cache_path, ttl_seconds=3600)
        assert result is None


def test_cache_missing_file():
    """Cache returns None when file doesn't exist."""
    from vision_probe import read_cache
    result = read_cache("/nonexistent/path/cache.json", ttl_seconds=3600)
    assert result is None


def test_check_opencv():
    """check_opencv returns bool."""
    from vision_probe import check_opencv
    result = check_opencv()
    assert isinstance(result, bool)


def test_check_ocp():
    """check_ocp returns bool (likely False in test env)."""
    from vision_probe import check_ocp
    result = check_ocp()
    assert isinstance(result, bool)


def test_decide_mode_no_refs():
    """decide_mode returns skip when no reference images."""
    from vision_probe import decide_mode
    result = decide_mode(contract={}, ref_dir="/nonexistent/dir")
    assert result == "skip"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 -m pytest tests/test_vision_probe.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'vision_probe'`

- [ ] **Step 3: Write vision_probe.py**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/vision_probe.py`:

```python
#!/usr/bin/env python3
"""
Vision API Probe + Environment Detection
Vision API 代理探测 + 环境检测

Probes whether the current Anthropic API proxy supports multimodal (image) input.
Caches result for 24 hours to avoid repeated probe calls.
Also provides environment checks for OpenCV, OCP Viewer, and Pillow.
"""

import os
import sys
import json
import time

# ── Cache ──

CACHE_TTL = 86400  # 24 hours / 24 小时
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")


def write_cache(cache_path, data):
    """Write probe result to cache file with timestamp."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    data["timestamp"] = time.time()
    with open(cache_path, "w") as f:
        json.dump(data, f)


def read_cache(cache_path, ttl_seconds=CACHE_TTL):
    """Read cached probe result. Returns None if expired or missing."""
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        ts = data.get("timestamp", 0)
        if time.time() - ts < ttl_seconds:
            return data
        return None
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


# ── Vision API Probe ──

TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="
)


def probe_vision_support(cache_dir=None):
    """
    Probe whether the current API proxy supports image input.
    Sends a minimal 1x1 PNG (~68 bytes base64), consuming negligible tokens.
    Results are cached for 24 hours.
    探测当前 API 代理是否支持图片输入。结果缓存 24 小时。
    """
    # Check cache first / 先检查缓存
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    cache_path = os.path.join(cache_dir, "vision_probe_cache.json")
    cached = read_cache(cache_path)
    if cached is not None:
        return cached

    try:
        import anthropic
    except ImportError:
        result = {"supported": False, "reason": "anthropic SDK not installed"}
        write_cache(cache_path, result)
        return result

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": TINY_PNG_B64
                    }},
                    {"type": "text", "text": "Reply with the single word OK"}
                ]
            }]
        )
        result = {"supported": True, "model": "claude-sonnet-4-20250514"}
    except Exception as e:
        result = {"supported": False, "reason": str(e)}

    write_cache(cache_path, result)
    return result


# ── Environment Checks ──

def check_opencv():
    """Check if OpenCV is available."""
    try:
        import cv2
        return True
    except ImportError:
        return False


def check_ocp():
    """Check if OCP CAD Viewer is running."""
    try:
        from ocp_vscode.state import get_ports
        from ocp_vscode.comms import port_check
        active = next((int(p) for p in get_ports() if port_check(int(p))), None)
        return active is not None
    except (ImportError, StopIteration):
        return False


def check_pillow():
    """Check if Pillow (PIL) is available."""
    try:
        from PIL import Image
        return True
    except ImportError:
        return False


# ── Reference Image Matching ──

VIEW_KEYWORDS = {
    "BACK":   ["back", "rear", "behind", "\u80cc\u9762", "\u6444\u50cf\u5934"],
    "FRONT":  ["front", "screen", "\u6b63\u9762", "\u5c4f\u5e55"],
    "RIGHT":  ["right", "side", "\u53f3\u4fa7", "\u6309\u952e"],
    "LEFT":   ["left", "\u5de6\u4fa7"],
    "BOTTOM": ["bottom", "port", "\u5e95\u90e8", "usb", "\u5145\u7535"],
    "TOP":    ["top", "\u9876\u90e8"],
    "ISO":    ["iso", "angle", "3d", "\u5168\u666f", "\u7acb\u4f53"],
}


def match_ref_to_views(ref_dir, contract=None):
    """
    Match reference images to standard views by filename keywords.
    按文件名关键词将参考图匹配到标准视角。
    """
    if not ref_dir or not os.path.isdir(ref_dir):
        return {}

    matches = {}
    for img_file in os.listdir(ref_dir):
        if not img_file.lower().endswith((".jpg", ".png", ".jpeg", ".webp")):
            continue
        name_lower = img_file.lower()
        for view, kws in VIEW_KEYWORDS.items():
            if any(kw in name_lower for kw in kws):
                matches[view] = os.path.join(ref_dir, img_file)
                break

    return matches


# ── Mode Decision ──

def decide_mode(contract, ref_dir, cache_dir=None):
    """
    Auto-decide comparison mode based on available tools.
    根据可用工具自动决定比对模式。

    Priority: ai_vision > opencv > manual > skip
    """
    refs = match_ref_to_views(ref_dir, contract)
    if not refs:
        return "skip"

    if not check_ocp():
        if check_pillow():
            return "manual"
        return "skip"

    probe = probe_vision_support(cache_dir=cache_dir)
    if probe.get("supported"):
        return "ai_vision"

    if check_opencv():
        return "opencv"

    if check_pillow():
        return "manual"

    return "skip"


# ── CLI ──

if __name__ == "__main__":
    print("=== Vision Probe ===")
    result = probe_vision_support()
    print(f"Vision API: {json.dumps(result, indent=2)}")
    print(f"OpenCV: {check_opencv()}")
    print(f"OCP Viewer: {check_ocp()}")
    print(f"Pillow: {check_pillow()}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 -m pytest tests/test_vision_probe.py -v
```

Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/vision_probe.py tests/test_vision_probe.py
git commit -m "feat(cad-vision-verify): add vision_probe.py with cache + env detection"
```

---

### Task 3: screenshot.py — OCP 7-view screenshot generation

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/screenshot.py`

- [ ] **Step 1: Write screenshot.py**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/screenshot.py`:

```python
#!/usr/bin/env python3
"""
OCP CAD Viewer Screenshot Generator
OCP CAD Viewer 多角度截图生成

Generates 7 standard-view screenshots of a CAD solid via OCP CAD Viewer.
通过 OCP CAD Viewer 自动截取 7 个标准视角截图。
"""

import os
import time


STANDARD_VIEWS = ["ISO", "FRONT", "BACK", "TOP", "BOTTOM", "RIGHT", "LEFT"]


def generate_screenshots(solid, output_dir, prefix="model", views=None, delay=0.8):
    """
    Generate standard-view screenshots via OCP CAD Viewer.
    用 OCP CAD Viewer 自动截标准视角截图。

    Args:
        solid: build123d solid object
        output_dir: directory to save screenshots
        prefix: filename prefix (default "model")
        views: list of view names to capture (default: all 7)
        delay: seconds to wait after show() for render (default 0.8)

    Returns:
        dict with "status" ("OK" or "SKIP") and "screenshots" {view: path}
    """
    try:
        from ocp_vscode import show, set_port, Camera, save_screenshot
        from ocp_vscode.comms import port_check
        from ocp_vscode.state import get_ports
    except ImportError:
        return {"status": "SKIP", "reason": "ocp_vscode not available"}

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if not active_port:
        return {"status": "SKIP", "reason": "OCP Viewer not running"}

    set_port(active_port)
    os.makedirs(output_dir, exist_ok=True)

    cam_map = {
        "ISO": Camera.ISO,
        "FRONT": Camera.FRONT,
        "BACK": Camera.BACK,
        "TOP": Camera.TOP,
        "BOTTOM": Camera.BOTTOM,
        "RIGHT": Camera.RIGHT,
        "LEFT": Camera.LEFT,
    }

    if views is None:
        views = STANDARD_VIEWS

    screenshots = {}
    for view_name in views:
        cam = cam_map.get(view_name)
        if cam is None:
            continue
        show(solid, names=[prefix], reset_camera=cam)
        time.sleep(delay)
        path = os.path.join(output_dir, f"{prefix}_{view_name}.png")
        save_screenshot(path)
        screenshots[view_name] = path

    return {"status": "OK", "screenshots": screenshots}
```

Note: No unit test for screenshot.py — it requires a running OCP Viewer + build123d solid, which is an integration test. The function is straightforward (thin wrapper around ocp_vscode) and will be tested via the full verify_loop integration test with a real model.

- [ ] **Step 2: Commit**

```bash
git add scripts/screenshot.py
git commit -m "feat(cad-vision-verify): add screenshot.py for OCP 7-view capture"
```

---

### Task 4: compare.py — Three-mode comparison engine

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/compare.py`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_compare.py`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/sample_contract.yaml`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/ref_BACK.png`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/model_BACK.png`

- [ ] **Step 1: Create test fixtures**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/sample_contract.yaml`:

```yaml
version: "0.1"
meta:
  product: "Test Product"
  body_ref:
    L: 100.0
    W: 50.0
    T: 10.0
features:
  - name: test_hole
    type: circle
    face: back
    dims:
      d: 10.0
    constraints:
      - {type: on_face, value: back, locks: [Z]}
      - {type: centered, plane: XZ, locks: [X]}
      - {type: offset, axis: Z, value: side_center, locks: [Z]}
```

Generate two small test PNG images (50x50, one white with black circle, one white with black square):

```bash
python3 -c "
from PIL import Image, ImageDraw
# Reference: white bg with black circle / 参考图：白底黑圆
img = Image.new('RGB', (50, 50), 'white')
draw = ImageDraw.Draw(img)
draw.ellipse([15, 15, 35, 35], fill='black')
img.save('/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/ref_BACK.png')
# Model: white bg with slightly smaller circle / 模型：白底稍小黑圆
img2 = Image.new('RGB', (50, 50), 'white')
draw2 = ImageDraw.Draw(img2)
draw2.ellipse([17, 17, 33, 33], fill='black')
img2.save('/Users/liyijiang/.agents/skills/cad-vision-verify/tests/fixtures/model_BACK.png')
print('Test fixtures created')
"
```

- [ ] **Step 2: Write failing tests**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_compare.py`:

```python
"""Tests for compare.py — three-mode comparison engine."""
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
REF_IMG = os.path.join(FIXTURES, "ref_BACK.png")
MODEL_IMG = os.path.join(FIXTURES, "model_BACK.png")
CONTRACT_PATH = os.path.join(FIXTURES, "sample_contract.yaml")


def _load_contract():
    import yaml
    with open(CONTRACT_PATH) as f:
        return yaml.safe_load(f)


def test_opencv_returns_score():
    """OpenCV comparison returns a dict with overall_score 0-100."""
    from compare import compare_opencv
    result = compare_opencv(REF_IMG, MODEL_IMG, "BACK")
    assert isinstance(result, dict)
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert result["view"] == "BACK"
    assert result["overall_match"] in ("good", "fair", "poor")


def test_opencv_identical_images():
    """OpenCV returns high score for identical images."""
    from compare import compare_opencv
    result = compare_opencv(REF_IMG, REF_IMG, "BACK")
    assert result["overall_score"] >= 90


def test_opencv_bad_path():
    """OpenCV returns score 0 for non-existent image."""
    from compare import compare_opencv
    result = compare_opencv("/nonexistent.png", MODEL_IMG, "BACK")
    assert result["overall_score"] == 0


def test_manual_generates_image():
    """Manual mode generates a side-by-side comparison image."""
    from compare import compare_manual
    with tempfile.TemporaryDirectory() as tmpdir:
        path = compare_manual(REF_IMG, MODEL_IMG, "BACK", tmpdir)
        assert os.path.exists(path)
        assert "compare_BACK" in path


def test_generate_report_pass():
    """Report with high scores returns PASS verdict."""
    from compare import generate_report
    comparisons = [
        {"view": "BACK", "overall_score": 90, "overall_match": "good",
         "checks": [], "missing_features": [], "suggestions": []},
        {"view": "RIGHT", "overall_score": 85, "overall_match": "good",
         "checks": [], "missing_features": [], "suggestions": []},
    ]
    report = generate_report(comparisons, {})
    assert report["verdict"] == "PASS"
    assert report["avg_score"] >= 80


def test_generate_report_fail():
    """Report with low scores returns FAIL verdict."""
    from compare import generate_report
    comparisons = [
        {"view": "BACK", "overall_score": 40, "overall_match": "poor",
         "checks": [], "missing_features": ["camera"], "suggestions": ["fix it"]},
    ]
    report = generate_report(comparisons, {})
    assert report["verdict"] == "FAIL"
    assert report["n_issues"] > 0


def test_generate_report_warn():
    """Report with medium scores returns WARN verdict."""
    from compare import generate_report
    comparisons = [
        {"view": "BACK", "overall_score": 70, "overall_match": "fair",
         "checks": [], "missing_features": [], "suggestions": []},
    ]
    report = generate_report(comparisons, {})
    assert report["verdict"] == "WARN"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 -m pytest tests/test_compare.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'compare'`

- [ ] **Step 4: Write compare.py**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/compare.py`:

```python
#!/usr/bin/env python3
"""
Three-Mode Comparison Engine
三模式比对引擎

Modes:
  ai_vision — Claude Vision API (highest accuracy)
  opencv    — OpenCV contour matching (no API)
  manual    — Side-by-side images for human review

Spec: build123d-cad/references/verify/layer2-visual.md
"""

import os
import json


# ── Mode A: Claude Vision ──

def compare_ai_vision(ref_path, model_path, view_name, contract):
    """
    Compare reference vs model using Claude Vision API.
    用 Claude Vision 比对参考图和模型截图。
    """
    import anthropic
    import base64

    def encode_image(path):
        with open(path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    feature_list = "\n".join(
        f"- {f['name']}: {f['type']} on {f['face']} face"
        for f in contract.get("features", [])
    )
    product = contract.get("meta", {}).get("product", "unknown")

    prompt = f"""You are a CAD model quality inspector. Compare two images:
- Image 1: Reference (real product photo, {view_name} view)
- Image 2: CAD model screenshot (same view)

Product: {product}
Feature list:
{feature_list}

Output JSON:
{{
  "view": "{view_name}",
  "overall_match": "good|fair|poor",
  "overall_score": 0-100,
  "checks": [
    {{
      "feature": "name",
      "visible": true/false,
      "shape_match": "good|fair|poor",
      "position_match": "good|fair|poor",
      "size_match": "good|fair|poor",
      "issue": "specific issue or null"
    }}
  ],
  "missing_features": ["features in reference but not in model"],
  "extra_features": ["features in model but not in reference"],
  "proportion_issues": ["overall proportion issues"],
  "suggestions": ["fix suggestions"]
}}

Focus only on geometry and proportion, ignore color/material/lighting."""

    ref_b64 = encode_image(ref_path)
    model_b64 = encode_image(model_path)

    ext_ref = os.path.splitext(ref_path)[1].lstrip(".").lower()
    ext_model = os.path.splitext(model_path)[1].lstrip(".").lower()
    media_ref = "image/jpeg" if ext_ref in ("jpg", "jpeg") else f"image/{ext_ref}"
    media_model = "image/jpeg" if ext_model in ("jpg", "jpeg") else f"image/{ext_model}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_ref, "data": ref_b64}},
                {"type": "image", "source": {"type": "base64", "media_type": media_model, "data": model_b64}},
                {"type": "text", "text": prompt}
            ]
        }]
    )

    text = response.content[0].text
    start, end = text.find("{"), text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"view": view_name, "overall_match": "poor", "overall_score": 0,
            "suggestions": ["Failed to parse Vision API response"]}


# ── Mode B: OpenCV ──

def compare_opencv(ref_path, model_path, view_name):
    """
    OpenCV contour comparison. No API needed.
    Weighted: area(25%) + hu_moment(35%) + centroid(20%) + feature_count(20%).
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return {"view": view_name, "overall_score": 0, "overall_match": "poor",
                "suggestions": ["OpenCV not installed"]}

    ref = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
    model = cv2.imread(model_path, cv2.IMREAD_GRAYSCALE)

    if ref is None or model is None:
        return {"view": view_name, "overall_score": 0, "overall_match": "poor",
                "suggestions": ["Failed to read image file(s)"]}

    h = max(ref.shape[0], model.shape[0])
    w = max(ref.shape[1], model.shape[1])
    ref = cv2.resize(ref, (w, h))
    model = cv2.resize(model, (w, h))

    ref_edges = cv2.Canny(ref, 50, 150)
    model_edges = cv2.Canny(model, 50, 150)

    ref_contours, _ = cv2.findContours(ref_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    model_contours, _ = cv2.findContours(model_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ref_sorted = sorted(ref_contours, key=cv2.contourArea, reverse=True)[:10]
    model_sorted = sorted(model_contours, key=cv2.contourArea, reverse=True)[:10]

    # Area ratio (25%)
    ref_area = cv2.contourArea(ref_sorted[0]) if ref_sorted else 0
    model_area = cv2.contourArea(model_sorted[0]) if model_sorted else 0
    area_ratio = min(ref_area, model_area) / max(ref_area, model_area) if max(ref_area, model_area) > 0 else 0

    # Hu moment shape (35%)
    shape_score = 0
    if ref_sorted and model_sorted:
        match_val = cv2.matchShapes(ref_sorted[0], model_sorted[0], cv2.CONTOURS_MATCH_I2, 0)
        shape_score = max(0, 1.0 - match_val)

    # Centroid offset (20%)
    def centroid(contour):
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return (0, 0)
        return (M["m10"] / M["m00"], M["m01"] / M["m00"])

    ref_c = centroid(ref_sorted[0]) if ref_sorted else (w / 2, h / 2)
    model_c = centroid(model_sorted[0]) if model_sorted else (w / 2, h / 2)
    center_ratio = np.sqrt((ref_c[0] - model_c[0])**2 + (ref_c[1] - model_c[1])**2) / np.sqrt(w**2 + h**2)

    # Feature count (20%)
    min_area = w * h * 0.01
    ref_n = len([c for c in ref_sorted if cv2.contourArea(c) > min_area])
    model_n = len([c for c in model_sorted if cv2.contourArea(c) > min_area])
    feat_match = min(ref_n, model_n) / max(ref_n, model_n) if max(ref_n, model_n) > 0 else 1

    score = area_ratio * 25 + shape_score * 35 + (1 - center_ratio) * 20 + feat_match * 20

    suggestions = []
    if area_ratio < 0.7:
        suggestions.append("Main contour area differs significantly — check overall dimensions")
    if shape_score < 0.6:
        suggestions.append("Main contour shape differs — check fillet/proportion params")
    if center_ratio > 0.1:
        suggestions.append("Main contour centroid offset — check feature positions")
    if feat_match < 0.7:
        suggestions.append("Feature count mismatch — possible missing or extra features")

    return {
        "view": view_name,
        "overall_score": round(score, 1),
        "overall_match": "good" if score >= 80 else "fair" if score >= 60 else "poor",
        "metrics": {
            "area_ratio": round(area_ratio, 3),
            "shape_score": round(shape_score, 3),
            "center_offset_ratio": round(center_ratio, 4),
            "feature_count": {"ref": ref_n, "model": model_n},
        },
        "suggestions": suggestions
    }


# ── Mode C: Manual Side-by-Side ──

def compare_manual(ref_path, model_path, view_name, output_dir):
    """
    Generate side-by-side comparison image for human review.
    生成并排对比图供人工目视检查。
    """
    from PIL import Image, ImageDraw

    ref = Image.open(ref_path)
    model = Image.open(model_path)

    target_h = max(ref.height, model.height)
    ref = ref.resize((int(ref.width * target_h / ref.height), target_h))
    model = model.resize((int(model.width * target_h / model.height), target_h))

    gap = 40
    canvas = Image.new("RGB", (ref.width + gap + model.width, target_h + 60), "white")
    canvas.paste(ref, (0, 60))
    canvas.paste(model, (ref.width + gap, 60))

    draw = ImageDraw.Draw(canvas)
    draw.text((ref.width // 2 - 30, 10), "Reference", fill="blue")
    draw.text((ref.width + gap + model.width // 2 - 20, 10), "Model", fill="red")
    draw.text((canvas.width // 2 - 40, 30), f"View: {view_name}", fill="black")

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"compare_{view_name}.png")
    canvas.save(path)
    return path


# ── Report Generation ──

def generate_report(comparisons, contract):
    """
    Aggregate multi-view comparison results into a verdict.
    汇总多视角比对结果，生成判定报告。
    """
    scores = [c.get("overall_score", 100) for c in comparisons]
    avg_score = sum(scores) / len(scores) if scores else 0

    all_issues = []
    for comp in comparisons:
        for check in comp.get("checks", []):
            if check.get("issue"):
                all_issues.append({
                    "view": comp["view"],
                    "feature": check["feature"],
                    "issue": check["issue"],
                })
        for mf in comp.get("missing_features", []):
            all_issues.append({
                "view": comp["view"],
                "feature": mf,
                "issue": "Missing in model",
                "severity": "HIGH"
            })
        for s in comp.get("suggestions", []):
            all_issues.append({
                "view": comp.get("view", "?"),
                "feature": "-",
                "issue": s,
            })

    return {
        "avg_score": round(avg_score, 1),
        "verdict": "PASS" if avg_score >= 80 else "WARN" if avg_score >= 60 else "FAIL",
        "n_views": len(comparisons),
        "n_issues": len(all_issues),
        "issues": all_issues,
        "per_view": [
            {"view": c.get("view"), "score": c.get("overall_score", 0),
             "match": c.get("overall_match", "?")}
            for c in comparisons
        ],
        "suggestions": list({s for c in comparisons for s in c.get("suggestions", [])})
    }
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 -m pytest tests/test_compare.py -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/compare.py tests/test_compare.py tests/fixtures/
git commit -m "feat(cad-vision-verify): add compare.py with opencv/manual/report + tests"
```

---

### Task 5: diagnose.py — Root cause diagnosis engine

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/diagnose.py`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_diagnose.py`

- [ ] **Step 1: Write failing tests**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/tests/test_diagnose.py`:

```python
"""Tests for diagnose.py — root cause diagnosis engine."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_layer1_stage_a_failure():
    """Stage A (BRep) failure -> root cause C (code)."""
    from diagnose import diagnose_failure
    l1 = {"verdict": "FAIL", "stage": "A"}
    result = diagnose_failure(l1, None, {}, {})
    assert len(result) == 1
    assert result[0]["root_cause"] == "C"
    assert result[0]["severity"] == "HIGH"


def test_layer1_stage_b_mapping_error():
    """Stage B with wrong param_map -> root cause B (contract)."""
    from diagnose import diagnose_failure
    l1 = {
        "verdict": "FAIL", "stage": "B",
        "failures": [{
            "feature": "camera",
            "dims": [{"param": "w", "status": "FAIL", "expected": 38.0, "actual": 30.0}]
        }]
    }
    contract = {"param_map": {}}  # missing mapping
    result = diagnose_failure(l1, None, contract, {})
    assert any(d["root_cause"] == "B" for d in result)


def test_layer1_stage_c_ordering():
    """Stage C ordering failure -> root cause C."""
    from diagnose import diagnose_failure
    l1 = {
        "verdict": "FAIL", "stage": "C",
        "failures": [{
            "feature": "volume_btn",
            "constraints": [{"type": "ordering", "status": "FAIL", "detail": "wrong order"}]
        }]
    }
    result = diagnose_failure(l1, None, {}, {})
    assert any(d["root_cause"] == "C" for d in result)


def test_layer2_missing_feature():
    """Layer 2 missing feature -> root cause A+B."""
    from diagnose import diagnose_failure
    l2 = {
        "verdict": "FAIL",
        "issues": [{"feature": "ir_blaster", "issue": "Missing in model"}]
    }
    result = diagnose_failure(None, l2, {}, {})
    assert any(d["root_cause"] == "A+B" for d in result)


def test_layer2_proportion_issue():
    """Layer 2 proportion issue -> root cause A."""
    from diagnose import diagnose_failure
    l2 = {
        "verdict": "FAIL",
        "issues": [{"feature": "body", "issue": "proportion too wide"}]
    }
    result = diagnose_failure(None, l2, {}, {})
    assert any(d["root_cause"] == "A" for d in result)


def test_layer2_position_poor():
    """Layer 2 position poor -> root cause B (tolerance too wide)."""
    from diagnose import diagnose_failure
    l2 = {
        "verdict": "FAIL",
        "issues": [{"feature": "usb_c", "issue": "offset", "position_match": "poor"}]
    }
    result = diagnose_failure(None, l2, {}, {})
    assert any(d["root_cause"] == "B" for d in result)


def test_dedup_and_sort():
    """Diagnoses are deduplicated and sorted by severity."""
    from diagnose import diagnose_failure
    l1 = {
        "verdict": "FAIL", "stage": "C",
        "failures": [
            {"feature": "f1", "constraints": [
                {"type": "ordering", "status": "FAIL", "detail": "x"},
                {"type": "ordering", "status": "FAIL", "detail": "y"},  # dup
            ]},
        ]
    }
    result = diagnose_failure(l1, None, {}, {})
    # Should be deduplicated: same root_cause + target
    targets = [(d["root_cause"], d["target"]) for d in result]
    assert len(targets) == len(set(targets))


def test_can_auto_fix():
    """Root cause C is auto-fixable, root cause A is not."""
    from diagnose import can_auto_fix
    assert can_auto_fix([{"root_cause": "C"}]) is True
    assert can_auto_fix([{"root_cause": "B"}]) is True
    assert can_auto_fix([{"root_cause": "A"}]) is False
    assert can_auto_fix([{"root_cause": "A+B"}]) is False


def test_format_report():
    """format_report returns a non-empty string."""
    from diagnose import format_report
    diagnoses = [
        {"root_cause": "C", "target": "code:f1", "detail": "wrong", "fix_action": "fix_code", "severity": "HIGH"}
    ]
    text = format_report(diagnoses, product="Test Product", variant="V1")
    assert "HIGH" in text
    assert "Test Product" in text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_diagnose.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'diagnose'`

- [ ] **Step 3: Write diagnose.py**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/diagnose.py`:

```python
#!/usr/bin/env python3
"""
Root Cause Diagnosis Engine
根因诊断引擎

Classifies verification failures into three root causes:
  A — Data source error (params.md values wrong)
  B — Contract error (constraints wrong/missing/loose)
  C — Code error (implementation doesn't match contract)

Spec: build123d-cad/references/verify/feedback-diagnosis.md
"""

import json


# ── Fix Loop Limits ──

MAX_FIX_ROUNDS = {
    "layer1": 3,
    "layer2": 2,
    "cross_layer": 2,
    "total": 5,
}


# ── Diagnosis ──

def diagnose_failure(layer1_result, layer2_result, contract, code_params):
    """
    Diagnose root cause from Layer 1/2 failure symptoms.
    根据 Layer 1/2 失败症状，判断根因。

    Returns: [{root_cause, target, detail, fix_action, severity}]
    """
    diagnoses = []

    # ── Layer 1 failure analysis ──
    if layer1_result and layer1_result.get("verdict") == "FAIL":
        stage = layer1_result.get("stage", "")

        if stage == "A":
            diagnoses.append({
                "root_cause": "C",
                "target": "modeling code",
                "detail": "BRep build failed — check boolean ops and geometry",
                "fix_action": "fix_code",
                "severity": "HIGH"
            })

        elif stage == "B":
            for f in layer1_result.get("failures", []):
                for d in f.get("dims", []):
                    if d.get("status") == "FAIL":
                        param_key = f"{f['feature']}.{d['param']}"
                        mapped_var = contract.get("param_map", {}).get(param_key)

                        if mapped_var and code_params.get(mapped_var) == d.get("actual"):
                            diagnoses.append({
                                "root_cause": "A",
                                "target": f"params.md -> {param_key}",
                                "detail": f"expected {d['expected']}, code {mapped_var}={d['actual']}",
                                "fix_action": "update_params_md",
                                "severity": "MEDIUM"
                            })
                        else:
                            diagnoses.append({
                                "root_cause": "B",
                                "target": f"contract.param_map.{param_key}",
                                "detail": "param_map mapping incorrect or missing",
                                "fix_action": "fix_contract_mapping",
                                "severity": "MEDIUM"
                            })

        elif stage == "C":
            for f in layer1_result.get("failures", []):
                for c in f.get("constraints", []):
                    if c.get("status") == "FAIL":
                        ctype = c.get("type", "")
                        if ctype == "on_face":
                            diagnoses.append({
                                "root_cause": "C",
                                "target": f"code:{f['feature']}",
                                "detail": f"Feature on wrong face: {c.get('detail', '')}",
                                "fix_action": "fix_code_face",
                                "severity": "HIGH"
                            })
                        elif ctype in ("edge_dist", "offset"):
                            diagnoses.append({
                                "root_cause": "A_or_C",
                                "target": f"{f['feature']} position",
                                "detail": c.get("detail", ""),
                                "fix_action": "check_params_then_code",
                                "severity": "MEDIUM"
                            })
                        elif ctype == "ordering":
                            diagnoses.append({
                                "root_cause": "C",
                                "target": f"code:{f['feature']}",
                                "detail": "Wrong ordering — check coordinate sign",
                                "fix_action": "fix_code_coordinates",
                                "severity": "HIGH"
                            })

    # ── Layer 2 failure analysis ──
    if layer2_result and layer2_result.get("verdict") == "FAIL":
        for issue in layer2_result.get("issues", []):
            issue_text = issue.get("issue", "")
            feature = issue.get("feature", "")

            if "missing" in issue_text.lower():
                diagnoses.append({
                    "root_cause": "A+B",
                    "target": f"params.md + contract: {feature}",
                    "detail": f"Feature {feature} in reference but missing in model",
                    "fix_action": "add_to_params_and_contract",
                    "severity": "HIGH"
                })
            elif "proportion" in issue_text.lower():
                diagnoses.append({
                    "root_cause": "A",
                    "target": "params.md -> body_ref",
                    "detail": "Overall proportion mismatch — check base dimensions",
                    "fix_action": "verify_body_dimensions",
                    "severity": "HIGH"
                })
            elif issue.get("position_match") == "poor" or issue.get("position") == "poor":
                diagnoses.append({
                    "root_cause": "B",
                    "target": f"contract: {feature}.constraints.tol",
                    "detail": "L1 passed but visual position offset — tolerance too wide",
                    "fix_action": "tighten_constraint_tolerance",
                    "severity": "MEDIUM"
                })
            elif issue.get("shape_match") == "poor" or issue.get("shape") == "poor":
                diagnoses.append({
                    "root_cause": "A",
                    "target": f"params.md -> {feature} type/dims",
                    "detail": "Feature shape mismatch (e.g. rect vs circle)",
                    "fix_action": "update_feature_type_in_params",
                    "severity": "HIGH"
                })

    # Dedup + sort by severity / 去重 + 按严重度排序
    seen = set()
    unique = []
    for d in diagnoses:
        key = (d["root_cause"], d["target"])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    unique.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x.get("severity", "LOW"), 2))

    return unique


def can_auto_fix(diagnoses):
    """
    Check if all diagnoses are auto-fixable.
    Root cause C and B can be auto-fixed. A and A+B need human.
    """
    for d in diagnoses:
        if d["root_cause"] in ("A", "A+B"):
            return False
    return True


# ── Report Formatting ──

def format_report(diagnoses, product="", variant=""):
    """Format diagnoses into a human-readable report string."""
    lines = []
    lines.append("=" * 52)
    lines.append(f"  CAD Vision Verify — Diagnosis Report")
    if product or variant:
        lines.append(f"  {product} — {variant}".strip(" —"))
    lines.append("=" * 52)

    for i, d in enumerate(diagnoses, 1):
        lines.append(f"")
        lines.append(f"  Diagnosis #{i} [{d['severity']}] Root cause {d['root_cause']}")
        lines.append(f"  Target: {d['target']}")
        lines.append(f"  Symptom: {d['detail']}")
        lines.append(f"  Fix: {d['fix_action']}")

    lines.append("")
    lines.append("-" * 52)
    auto = [d for d in diagnoses if d["root_cause"] not in ("A", "A+B")]
    manual = [d for d in diagnoses if d["root_cause"] in ("A", "A+B")]
    lines.append(f"  Auto-fixable: {len(auto)}")
    lines.append(f"  Needs human: {len(manual)}")
    if diagnoses:
        lines.append(f"  Fix order: {' -> '.join(f'#{i+1}' for i in range(len(diagnoses)))}")
    lines.append("=" * 52)

    return "\n".join(lines)


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Root cause diagnosis engine")
    parser.add_argument("--l1-result", help="Path to Layer 1 result JSON")
    parser.add_argument("--l2-result", help="Path to Layer 2 result JSON")
    parser.add_argument("--contract", help="Path to contract YAML")
    args = parser.parse_args()

    l1 = json.load(open(args.l1_result)) if args.l1_result else None
    l2 = json.load(open(args.l2_result)) if args.l2_result else None
    contract = {}
    if args.contract:
        import yaml
        contract = yaml.safe_load(open(args.contract))

    diagnoses = diagnose_failure(l1, l2, contract, {})
    print(format_report(diagnoses))
    print(json.dumps(diagnoses, indent=2, ensure_ascii=False))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_diagnose.py -v
```

Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/diagnose.py tests/test_diagnose.py
git commit -m "feat(cad-vision-verify): add diagnose.py with root cause classification + tests"
```

---

### Task 6: verify_loop.py — Full verification-fix loop entry point

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/verify_loop.py`

- [ ] **Step 1: Write verify_loop.py**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/scripts/verify_loop.py`:

```python
#!/usr/bin/env python3
"""
Full Verification-Fix Loop
完整验证-修复闭环

Entry point that orchestrates: probe -> screenshot -> compare -> diagnose.
串联: 环境探测 -> 截图 -> 比对 -> 诊断 的完整流程。

Can be called programmatically (by build123d-cad) or via CLI.
"""

import os
import sys
import json
import argparse

from vision_probe import decide_mode, match_ref_to_views, probe_vision_support
from screenshot import generate_screenshots
from compare import compare_ai_vision, compare_opencv, compare_manual, generate_report
from diagnose import diagnose_failure, can_auto_fix, format_report, MAX_FIX_ROUNDS


def verify(solid, contract, ref_dir, output_dir, mode="auto", code_params=None,
           layer1_result=None):
    """
    Full Layer 2 visual verification with optional diagnosis.
    完整的 Layer 2 视觉验证 + 可选诊断。

    Args:
        solid: build123d solid object (None for file-based mode)
        contract: parsed contract dict (from YAML)
        ref_dir: directory containing reference images
        output_dir: output directory for screenshots + comparisons
        mode: "auto", "ai_vision", "opencv", "manual", "skip"
        code_params: dict of code variable values (for diagnosis)
        layer1_result: Layer 1 result dict (for cross-layer diagnosis)

    Returns:
        dict with verdict, report, diagnoses
    """
    os.makedirs(output_dir, exist_ok=True)

    # Phase 1: Mode decision / 模式决策
    if mode == "auto":
        mode = decide_mode(contract, ref_dir)

    if mode == "skip":
        return {
            "verdict": "SKIP",
            "mode": "skip",
            "reason": "No reference images or no comparison tools available",
            "report": None,
            "diagnoses": []
        }

    # Phase 2: Screenshot capture / 截图采集
    screenshots = {"status": "SKIP", "screenshots": {}}
    if solid is not None:
        screenshots = generate_screenshots(solid, output_dir)
        if screenshots["status"] == "SKIP" and mode in ("ai_vision", "opencv"):
            mode = "manual"

    # Phase 3: Comparison / 比对
    ref_images = match_ref_to_views(ref_dir, contract)
    comparisons = []

    if mode == "ai_vision":
        for view, ref_path in ref_images.items():
            model_path = screenshots.get("screenshots", {}).get(view)
            if not model_path:
                model_path = os.path.join(output_dir, f"model_{view}.png")
            if model_path and os.path.exists(model_path):
                r = compare_ai_vision(ref_path, model_path, view, contract)
                comparisons.append(r)

    elif mode == "opencv":
        for view, ref_path in ref_images.items():
            model_path = screenshots.get("screenshots", {}).get(view)
            if not model_path:
                model_path = os.path.join(output_dir, f"model_{view}.png")
            if model_path and os.path.exists(model_path):
                r = compare_opencv(ref_path, model_path, view)
                comparisons.append(r)

    elif mode == "manual":
        compare_images = []
        for view, ref_path in ref_images.items():
            model_path = screenshots.get("screenshots", {}).get(view)
            if not model_path:
                model_path = os.path.join(output_dir, f"model_{view}.png")
            if model_path and os.path.exists(model_path):
                path = compare_manual(ref_path, model_path, view, output_dir)
                compare_images.append(path)
        return {
            "verdict": "MANUAL_REVIEW",
            "mode": "manual",
            "compare_images": compare_images,
            "report": None,
            "diagnoses": []
        }

    if not comparisons:
        return {
            "verdict": "SKIP",
            "mode": mode,
            "reason": "No matching view pairs found",
            "report": None,
            "diagnoses": []
        }

    # Phase 4: Report / 评分报告
    report = generate_report(comparisons, contract)

    # Phase 5: Diagnosis (only on FAIL) / 诊断（仅失败时）
    diagnoses = []
    if report["verdict"] == "FAIL":
        diagnoses = diagnose_failure(
            layer1_result, report, contract, code_params or {}
        )

    return {
        "verdict": report["verdict"],
        "mode": mode,
        "report": report,
        "diagnoses": diagnoses,
        "auto_fixable": can_auto_fix(diagnoses) if diagnoses else None
    }


# ── Pretty Print ──

def print_result(result):
    """Print verification result to terminal."""
    v = result["verdict"]
    icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL",
            "SKIP": "SKIP", "MANUAL_REVIEW": "MANUAL_REVIEW"}.get(v, v)

    print()
    print("=" * 52)
    print(f"  CAD Vision Verify Result")
    print(f"  Mode: {result.get('mode', '?')}")
    print(f"  Verdict: {icon}")
    print("=" * 52)

    report = result.get("report")
    if report:
        print(f"  Avg score: {report.get('avg_score', 0):.1f}")
        print(f"  Views: {report.get('n_views', 0)}")
        for pv in report.get("per_view", []):
            print(f"    {pv['view']:8s} {pv['score']:5.1f}/100")
        if report.get("issues"):
            print(f"  Issues ({report['n_issues']}):")
            for i, iss in enumerate(report["issues"][:5], 1):
                print(f"    {i}. [{iss.get('view')}] {iss.get('feature')}: {iss.get('issue')}")

    if result.get("diagnoses"):
        product = result.get("report", {}).get("product", "")
        print()
        print(format_report(result["diagnoses"], product=product))

    if result.get("compare_images"):
        print(f"  Comparison images:")
        for p in result["compare_images"]:
            print(f"    {p}")


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="CAD Vision Verify — full loop")
    parser.add_argument("--contract", required=True, help="Path to contract.yaml")
    parser.add_argument("--ref-dir", required=True, help="Reference images directory")
    parser.add_argument("--output-dir", default="output/verify", help="Output directory")
    parser.add_argument("--mode", choices=["auto", "ai_vision", "opencv", "manual", "skip"],
                        default="auto")
    parser.add_argument("--l1-result", help="Layer 1 result JSON (for cross-layer diagnosis)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    import yaml
    with open(args.contract) as f:
        contract = yaml.safe_load(f)

    l1 = None
    if args.l1_result:
        with open(args.l1_result) as f:
            l1 = json.load(f)

    result = verify(
        solid=None,
        contract=contract,
        ref_dir=args.ref_dir,
        output_dir=args.output_dir,
        mode=args.mode,
        layer1_result=l1
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result)

    v = result["verdict"]
    sys.exit(0 if v in ("PASS", "SKIP", "MANUAL_REVIEW") else 1 if v == "WARN" else 2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/verify_loop.py
git commit -m "feat(cad-vision-verify): add verify_loop.py — full verification pipeline + CLI"
```

---

### Task 7: Reference docs + example report

**Files:**
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/references/constraint-types.md`
- Create: `/Users/liyijiang/.agents/skills/cad-vision-verify/references/examples/k70-report.json`

- [ ] **Step 1: Write constraint-types.md**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/references/constraint-types.md`:

```markdown
# Constraint Types Quick Reference

| Category | Type | Purpose | Locks |
|----------|------|---------|-------|
| Position | on_face | Feature is on specified face | Z (or face normal axis) |
| Position | offset | Feature offset from reference | specified axis |
| Position | edge_dist | Distance from body edge | specified axis |
| Position | centered | Centered on plane | specified axis |
| Orientation | normal | Face normal direction | rotation |
| Orientation | parallel | Parallel to reference | rotation |
| Inter-feature | ordering | Sequence along axis | relative position |
| Inter-feature | colinear | Aligned on axis | perpendicular axis |
| Inter-feature | inter_dist | Distance between features | along axis |
| Inter-feature | same_face | On same face as target | face |
| Inter-feature | symmetric_pair | Symmetric about plane | mirror axis |
| Ratio | ratio | Dimension ratio check | proportional |
| Ratio | size_range | Dimension within range | absolute |

Each feature needs >= 3 constraints covering X, Y, Z axes (CAD 3-2-1 principle).
```

- [ ] **Step 2: Write k70-report.json**

Create `/Users/liyijiang/.agents/skills/cad-vision-verify/references/examples/k70-report.json`:

```json
{
  "verdict": "PASS",
  "mode": "ai_vision",
  "report": {
    "avg_score": 88.8,
    "verdict": "PASS",
    "n_views": 4,
    "n_issues": 0,
    "per_view": [
      {"view": "BACK", "score": 92, "match": "good"},
      {"view": "RIGHT", "score": 88, "match": "good"},
      {"view": "BOTTOM", "score": 85, "match": "good"},
      {"view": "ISO", "score": 90, "match": "good"}
    ],
    "issues": [],
    "suggestions": []
  },
  "diagnoses": [],
  "auto_fixable": null
}
```

- [ ] **Step 3: Commit**

```bash
git add references/
git commit -m "docs(cad-vision-verify): add constraint-types reference + K70 example report"
```

---

### Task 8: Update build123d-cad SKILL.md integration + deprecate old script

**Files:**
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md:192-197` (update Layer 2 reference)
- Modify: `/Users/liyijiang/.agents/skills/build123d-cad/scripts/validate/visual_compare.py:1-5` (add deprecation)

- [ ] **Step 1: Add deprecation notice to visual_compare.py**

Add to the top of `/Users/liyijiang/.agents/skills/build123d-cad/scripts/validate/visual_compare.py`, replacing the existing docstring opening:

```python
#!/usr/bin/env python3
"""
DEPRECATED: This module is superseded by the cad-vision-verify skill.
Use: /Users/liyijiang/.agents/skills/cad-vision-verify/scripts/compare.py
This file is kept for backward compatibility.

Layer 2 Visual Comparison Tool
Layer 2 视觉比对验证工具
...
```

Only change the first 3 lines of the docstring — leave everything else intact.

- [ ] **Step 2: Update build123d-cad SKILL.md**

In `/Users/liyijiang/.agents/skills/build123d-cad/SKILL.md`, find the Layer 2 section (around line 192) and update the script path reference:

Change:
```bash
# Layer 2 视觉比对
python3 scripts/validate/visual_compare.py --contract contract.yaml --ref-dir references/<product>/images --output-dir output/visual
```

To:
```bash
# Layer 2 视觉比对 (via cad-vision-verify skill)
python3 /Users/liyijiang/.agents/skills/cad-vision-verify/scripts/verify_loop.py --contract contract.yaml --ref-dir references/<product>/images --output-dir output/visual
# Legacy (deprecated): python3 scripts/validate/visual_compare.py ...
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liyijiang/.agents/skills/build123d-cad
git add scripts/validate/visual_compare.py SKILL.md
git commit -m "refactor(build123d-cad): point Layer 2 to cad-vision-verify skill, deprecate visual_compare.py"
```

---

### Task 9: Run full test suite + smoke test

- [ ] **Step 1: Run all unit tests**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 -m pytest tests/ -v
```

Expected: All tests pass (vision_probe: 7, compare: 7, diagnose: 9 = 23 total)

- [ ] **Step 2: Smoke test CLI — verify_loop with skip mode**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 scripts/verify_loop.py \
  --contract tests/fixtures/sample_contract.yaml \
  --ref-dir /nonexistent \
  --output-dir /tmp/verify_test \
  --json
```

Expected output:
```json
{
  "verdict": "SKIP",
  "mode": "skip",
  "reason": "No reference images or no comparison tools available",
  ...
}
```

- [ ] **Step 3: Smoke test CLI — diagnose.py standalone**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
echo '{"verdict":"FAIL","stage":"A"}' > /tmp/l1_test.json
python3 scripts/diagnose.py --l1-result /tmp/l1_test.json
rm /tmp/l1_test.json
```

Expected: Diagnosis report showing root cause C (BRep failure).

- [ ] **Step 4: Smoke test CLI — vision_probe standalone**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
python3 scripts/vision_probe.py
```

Expected: Prints Vision API / OpenCV / OCP / Pillow availability status.

- [ ] **Step 5: Commit test fixtures if any changed**

```bash
cd /Users/liyijiang/.agents/skills/cad-vision-verify
git status
# If clean, skip. If fixtures changed:
git add -A
git commit -m "test(cad-vision-verify): finalize test suite — 23 tests passing"
```

---

## Self-Review Checklist

1. **Spec coverage**: All 9 spec sections mapped to tasks:
   - Sec 1 (Problem) -> Task 1 SKILL.md
   - Sec 2 (Architecture) -> Tasks 1-7 file structure
   - Sec 3 (Pipeline) -> Tasks 2-6 scripts
   - Sec 4 (Workflow) -> Task 1 SKILL.md protocol
   - Sec 5 (Report) -> Task 5 diagnose.py format_report
   - Sec 6 (Reuse) -> Task 8 deprecation
   - Sec 7 (Integration) -> Task 8 SKILL.md update
   - Sec 8 (Triggers) -> Task 1 SKILL.md frontmatter
   - Sec 9 (Scope) -> Enforced by module boundaries

2. **Placeholder scan**: No TBD/TODO found. All code blocks complete.

3. **Type consistency**: Function names consistent across tasks:
   - `probe_vision_support()` — Task 2 definition, Task 6 import via `vision_probe`
   - `decide_mode()` — Task 2 definition, Task 6 import
   - `compare_opencv()` / `compare_ai_vision()` / `compare_manual()` — Task 4 definition, Task 6 import
   - `generate_report()` — Task 4 definition, Task 6 import
   - `diagnose_failure()` / `can_auto_fix()` / `format_report()` — Task 5 definition, Task 6 import
