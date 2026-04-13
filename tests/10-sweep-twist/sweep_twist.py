"""
10-sweep-twist — Twist Sweep / 扭转扫掠
Tests / 测试:
  helix path (quarter turn)   — 3D curved path with torsion / 有扭矩的三维螺旋路径
  ribbon cross-section sweep  — thin rectangle follows Frenet frame / 薄矩形截面跟随 Frenet 框架
  is_frenet=True              — natural twist from path curvature / 路径曲率驱动的自然扭转

Design intent (Dave Cowden style) / 设计意图:
  Helix path: radius=40mm, height=60mm, quarter turn (90°) — gently curving in 3D.
  Cross-section: 30×5mm ribbon, placed perpendicular to path tangent at start.
  sweep(is_frenet=True) lets OCC Frenet frame drive the section twist as path curves.
  The ribbon naturally rolls/twists following the helix — organic twisted-band solid.
  螺旋路径：半径40mm，高60mm，四分之一圈（90°）。
  截面：30×5mm 薄矩形，垂直于起点切线放置。
  is_frenet=True 让 OCC Frenet 框架随路径曲率自然扭转截面，得到有机扭转缎带实体。
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
helix_r    = 40     # helix radius mm / 螺旋半径 mm
helix_h    = 60     # helix height mm (quarter turn) / 螺旋高度 mm（四分之一圈）
helix_p    = helix_h / 0.25    # pitch mm/rev to get exactly 90° turn / 一圈节距，恰好走 90°

section_w  = 30     # ribbon width mm / 缎带宽度 mm
section_h  = 5      # ribbon thickness mm / 缎带厚度 mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "sweep_twist.step")

# ===== Modeling / 建模 =====
# Path: quarter-turn helix (90° arc lifted by helix_h) / 路径：四分之一圈螺旋线
path = Edge.make_helix(pitch=helix_p, height=helix_h, radius=helix_r)

# Start plane: origin at path start, normal = path tangent at t=0
# 起始平面：原点在路径起点，法向 = 路径 t=0 处切线
start_plane = Plane(origin=path @ 0, z_dir=path % 0)

with BuildPart() as twisted:

    # Cross-section: thin ribbon at path start / 截面：路径起点处的薄矩形缎带
    with BuildSketch(start_plane):
        Rectangle(section_w, section_h)

    # Sweep along helix path; is_frenet=True rotates section with Frenet frame
    # 沿螺旋路径扫掠；is_frenet=True 让截面跟随 Frenet 框架旋转
    sweep(path=path, is_frenet=True)

# ===== Validation Layer 1 + 2 / 验证 =====
assert twisted.part is not None, "part is None / part 为空"
assert twisted.part.is_valid,    "BRep invalid / BRep 无效"

vol = twisted.part.volume
bb  = twisted.part.bounding_box()
print(f"Bounding box / 包围盒: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")
print(f"Path length / 路径长度: {path.length:.2f} mm")

# Height: Z span should cover helix_h / 高度：Z 跨度应覆盖螺旋高度
assert bb.size.Z >= helix_h * 0.9, \
    f"Z span too small / Z 跨度过小: {bb.size.Z:.2f}"

# Volume: section_area × path_length (±20% tolerance for Frenet twist geometry)
# 体积：截面面积 × 路径长度（Frenet 扭转几何允许 ±20% 宽容度）
approx_vol = section_w * section_h * path.length
assert approx_vol * 0.80 < vol < approx_vol * 1.20, \
    f"volume out of range / 体积超范围: {vol:.2f}, expected ~{approx_vol:.0f}"

assert len(twisted.part.solids()) == 1, "expected exactly one solid / 应只有一个 solid"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(twisted.part, step_path)
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
            show(twisted.part, names=["sweep_twist"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"sweep_twist_{label}.png"))
            print(f"Screenshot saved / 截图已保存: sweep_twist_{label}.png")
        print(f"OCP Viewer: preview opened on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 10-sweep-twist all tests passed / 全部测试通过")
