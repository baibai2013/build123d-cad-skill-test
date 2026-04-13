"""
09-organic-shell — 5-Section Organic Loft Shell / 五截面有机曲面外壳
Tests / 测试:
  5-section Ellipse Loft    — varying semi-axes, streamlined form / 变截面椭圆放样，流线型轮廓
  shell() hollow            — uniform inward wall thickness / 均匀向内抽壳
  Ellipse parametric        — a/b semi-axes vary with height / 长短轴随高度参数化变化

Design intent (Dave Cowden style) / 设计意图:
  Five elliptical cross-sections at increasing heights, semi-axes vary smoothly:
    bottom (z=0):  a=15mm, b=10mm  — narrow base / 底部窄
    lower  (z=15): a=20mm, b=14mm  — widening / 加宽
    middle (z=30): a=18mm, b=16mm  — near-circular midsection / 中间近圆
    upper  (z=45): a=14mm, b=12mm  — tapering / 收窄
    top    (z=60): a=10mm, b= 8mm  — narrow apex / 顶部最窄
  Loft blends smoothly → organic solid → shell(bottom, -2mm) → hollow shell
  五截面椭圆放样得到有机实体，从底面抽壳得到均匀壁厚空腔外壳
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
z_heights = [0, 15, 30, 45, 60]          # section heights mm / 截面高度 mm

# (a = X semi-axis, b = Y semi-axis) at each height / 各高度 (X半轴, Y半轴)
ellipse_params = [
    (15, 10),   # z=0  narrow base / 底部窄
    (20, 14),   # z=15 widening   / 加宽
    (18, 16),   # z=30 midsection / 中间近圆
    (14, 12),   # z=45 tapering   / 收窄
    (10,  8),   # z=60 apex       / 顶部最窄
]

wall_t  = 2.0                                       # shell wall thickness mm / 抽壳壁厚 mm
z_top   = z_heights[-1]                             # total height mm / 总高 mm
max_a   = max(a for a, b in ellipse_params)         # widest X semi-axis / 最大X半轴
max_b   = max(b for a, b in ellipse_params)         # widest Y semi-axis / 最大Y半轴

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "organic_shell.step")

# ===== Modeling / 建模 =====
with BuildPart() as organic:

    # Step 1: build ellipse sketch at each height / 步骤1：各高度建椭圆草图
    for z, (a, b) in zip(z_heights, ellipse_params):
        with BuildSketch(Plane.XY.offset(z)):
            Ellipse(a, b)

    # Step 2: loft through all 5 sections / 步骤2：五截面放样
    loft()

    # Step 3: shell — open bottom face, hollow inward / 步骤3：抽壳——开放底面，向内挖空
    bottom_face = organic.faces().sort_by(Axis.Z)[0]
    offset(amount=-wall_t, openings=bottom_face)

# ===== Validation Layer 1 + 2 / 验证 =====
assert organic.part is not None, "part is None / part 为空"
assert organic.part.is_valid,    "BRep invalid / BRep 无效"

vol = organic.part.volume
bb  = organic.part.bounding_box()
print(f"Bounding box / 包围盒: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")

# Height check / 高度检查
assert abs(bb.size.Z - z_top) < 1.0, \
    f"height deviation / 高度偏差: {bb.size.Z:.2f} vs {z_top}"

# XY span: must cover the widest section / XY 跨度：须覆盖最宽截面
assert bb.size.X > max_a * 2 * 0.9, \
    f"X span too small / X 跨度过小: {bb.size.X:.2f} vs {max_a * 2 * 0.9:.2f}"
assert bb.size.Y > max_b * 2 * 0.9, \
    f"Y span too small / Y 跨度过小: {bb.size.Y:.2f} vs {max_b * 2 * 0.9:.2f}"

# Volume: shell < full elliptic cylinder at widest section / 体积：抽壳后 < 最大截面椭圆柱
vol_max_solid = math.pi * max_a * max_b * z_top   # π * 20 * 16 * 60 ≈ 60319 mm³
assert 0 < vol < vol_max_solid, \
    f"volume out of range / 体积超范围: {vol:.2f}, should be (0, {vol_max_solid:.0f}]"

assert len(organic.part.solids()) == 1, "expected exactly one solid / 应只有一个 solid"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(organic.part, step_path)
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
            show(organic.part, names=["organic_shell"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"organic_shell_{label}.png"))
            print(f"Screenshot saved / 截图已保存: organic_shell_{label}.png")
        print(f"OCP Viewer: preview opened on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 09-organic-shell all tests passed / 全部测试通过")
