"""
10-sweep-twist — Twist Sweep / 扭转扫掠
Tests / 测试:
  straight line path + section twist  — Rectangle section rotates 90° / 矩形截面扭转 90°
  sweep multisection                   — two oriented sections along path / 两个方向不同的截面
  Transition.ROUND                     — smooth corner transition / 圆滑过渡

Design intent (Dave Cowden style) / 设计意图:
  Straight vertical path (60mm), rectangular cross-section (20×10mm).
  Start section: width along X. End section: same rect rotated 90° (width along Y).
  sweep(multisection=True) interpolates between orientations → twisted prism.
  直线路径（60mm），矩形截面（20×10mm）。
  起始截面宽边朝 X，末端截面旋转 90° 后宽边朝 Y，放样扫掠得到扭转棱柱。
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
path_height = 60     # sweep path length mm (along Z) / 扫掠路径长度 mm（沿Z轴）
section_w   = 20     # cross-section width mm / 截面宽度 mm
section_h   = 10     # cross-section height mm / 截面高度 mm
twist_deg   = 90     # total twist angle degrees / 总扭转角度

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "sweep_twist.step")

# ===== Modeling / 建模 =====
# Path: straight line along +Z axis / 路径：沿+Z轴的直线
path = Edge.make_line((0, 0, 0), (0, 0, path_height))

# Rotated end plane: x_dir rotated twist_deg around Z / 末端平面：x_dir 绕Z轴旋转 twist_deg
rad = math.radians(twist_deg)
end_plane = Plane(
    origin=(0, 0, path_height),
    x_dir=(math.cos(rad), math.sin(rad), 0),   # 90°: (0, 1, 0)
    z_dir=(0, 0, 1)                             # normal stays +Z / 法向保持+Z
)

with BuildPart() as twisted:

    # Section 1 at z=0: rectangle, width along +X / 截面1 z=0：矩形，宽边朝+X
    with BuildSketch(Plane.XY):
        Rectangle(section_w, section_h)

    # Section 2 at z=path_height: same rect, rotated twist_deg / 截面2 末端：同矩形旋转 twist_deg
    with BuildSketch(end_plane):
        Rectangle(section_w, section_h)

    # Sweep: interpolate between sections along straight path / 扫掠：沿直线路径在截面间插值
    sweep(path=path, multisection=True, transition=Transition.ROUND)

# ===== Validation Layer 1 + 2 / 验证 =====
assert twisted.part is not None, "part is None / part 为空"
assert twisted.part.is_valid,    "BRep invalid / BRep 无效"

vol = twisted.part.volume
bb  = twisted.part.bounding_box()
print(f"Bounding box / 包围盒: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")

# Height check / 高度检查
assert abs(bb.size.Z - path_height) < 1.0, \
    f"height deviation / 高度偏差: {bb.size.Z:.2f} vs {path_height}"

# XY span: at 45° mid-twist the section projects to ≈ (section_w+section_h)*sin45°
# 中途 45° 时截面投影宽度约为 (section_w+section_h)*sin(45°) ≈ 21mm
min_xy_span = section_h                            # at least the narrower side / 至少窄边
max_xy_span = section_w + section_h               # loose upper bound / 宽松上界
assert bb.size.X >= min_xy_span * 0.9, \
    f"X span too small / X 跨度过小: {bb.size.X:.2f}"
assert bb.size.X <= max_xy_span * 1.05, \
    f"X span too large / X 跨度过大: {bb.size.X:.2f}"

# Volume: constant cross-section area × height (twist doesn't change area)
# 体积：截面面积（不随旋转变化）× 路径长度
approx_vol = section_w * section_h * path_height  # 20*10*60 = 12000 mm³
assert approx_vol * 0.90 < vol < approx_vol * 1.10, \
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
