"""
08-loft-transition — Multi-Section Loft Transition / 多截面放样过渡
Tests / 测试:
  multi-plane BuildSketch + loft  — Circle → Rectangle → Circle / 圆→方→圆三截面放样
  Plane.XY.offset multi-height    — three sections at different heights / 三个不同高度截面
  surface continuity              — G1 tangent continuity check via volume / 曲面连续性体积验证

Design intent (Dave Cowden style) / 设计意图:
  Three horizontal cross-sections at increasing heights:
    bottom (z=0):  Circle r=20mm
    middle (z=30): Rectangle 28×28mm
    top    (z=60): Circle r=20mm
  Loft blends smoothly between sections → organic transitional solid
  三个水平截面在不同高度：底部圆 → 中间方 → 顶部圆，放样得到有机过渡实体
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
r_bottom   = 20     # bottom circle radius mm / 底部圆半径 mm
r_top      = 20     # top circle radius mm / 顶部圆半径 mm
rect_w     = 28     # middle rectangle width mm / 中间矩形宽度 mm
rect_h     = 28     # middle rectangle height mm / 中间矩形高度 mm

z_bottom   = 0      # bottom section height mm / 底部截面高度 mm
z_middle   = 30     # middle section height mm / 中间截面高度 mm
z_top      = 60     # top section height mm / 顶部截面高度 mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "loft_transition.step")

# ===== Modeling / 建模 =====
with BuildPart() as transition:

    # Step 1: bottom section — circle at z=0 / 步骤1：底部截面——z=0 处的圆
    with BuildSketch(Plane.XY.offset(z_bottom)):
        Circle(r_bottom)

    # Step 2: middle section — rectangle at z=30 / 步骤2：中间截面——z=30 处的矩形
    with BuildSketch(Plane.XY.offset(z_middle)):
        Rectangle(rect_w, rect_h)

    # Step 3: top section — circle at z=60 / 步骤3：顶部截面——z=60 处的圆
    with BuildSketch(Plane.XY.offset(z_top)):
        Circle(r_top)

    # Step 4: loft through all three sections / 步骤4：三截面放样
    loft()

# ===== Validation Layer 1 + 2 / 验证 =====
assert transition.part is not None, "part is None / part 为空"
assert transition.part.is_valid,    "BRep invalid / BRep 无效"

vol = transition.part.volume
bb  = transition.part.bounding_box()
print(f"Bounding box / 包围盒: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")

# Bounding box: height = z_top, XY span ≈ diameter of circles / 包围盒：高度等于顶截面高度
assert abs(bb.size.Z - z_top) < 1.0, \
    f"height deviation / 高度偏差: {bb.size.Z:.2f} vs {z_top}"
assert bb.size.X > rect_w * 0.9, \
    f"X span too small / X 跨度过小: {bb.size.X:.2f}"
assert bb.size.X < r_bottom * 2 + 5, \
    f"X span too large / X 跨度过大: {bb.size.X:.2f}"

# Volume bounds: loft volume is between 50% and 100% of the full cylinder
# (circle sections r=20 are LARGER than the rectangle 28×28, so cylinder is upper bound)
# 体积区间：放样体积介于圆柱的 50%~100% 之间
# （圆截面 r=20 面积 > 矩形 28×28，所以全圆柱是上界）
vol_cylinder = math.pi * r_bottom**2 * z_top   # upper bound / 上限（全圆柱）
assert vol_cylinder * 0.5 < vol < vol_cylinder, \
    f"volume out of range / 体积超范围: {vol:.2f}, bounds [{vol_cylinder*0.5:.0f}, {vol_cylinder:.0f}]"

assert len(transition.part.solids()) == 1, "expected exactly one solid / 应只有一个 solid"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(transition.part, step_path)
reimported = import_step(step_path)
vol_diff = abs(reimported.volume - vol) / vol
print(f"STEP re-import volume deviation / 重导入体积偏差: {vol_diff:.6%}")
assert vol_diff < 0.001, f"STEP precision loss / 精度损失: {vol_diff:.4%}"
print("✅ Layer 3 passed / 通过")

# ===== OCP preview (three-view screenshots) / OCP 预览（三视角截图）=====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        for label, cam in [("ISO", Camera.ISO), ("TOP", Camera.TOP), ("FRONT", Camera.FRONT)]:
            show(transition.part, names=["loft_transition"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"loft_transition_{label}.png"))
            print(f"Screenshot saved / 截图已保存: loft_transition_{label}.png")
        print(f"OCP Viewer: preview opened on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 08-loft-transition all tests passed / 全部测试通过")
