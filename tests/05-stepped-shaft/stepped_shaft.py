"""
05-stepped-shaft — Stepped Shaft / 阶梯轴
Tests / 测试:
  BuildSketch(Plane.XZ) + revolve  — multi-step profile rotation / 多段阶梯轮廓旋转体
  Mode.SUBTRACT extrude            — keyway slot cut / 键槽切割
  chamfer                          — end chamfers / 两端倒角

Design intent (Dave Cowden style) / 设计意图:
  Draw half-profile on XZ plane -> revolve 360° -> cut keyway on top -> chamfer both ends
  在 XZ 平面画半截面轮廓 -> 旋转 360° -> 顶面切键槽 -> 两端倒角
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
# Shaft segments (from one end to other) / 轴段（从一端到另一端）
# Segment:   [radius, length]
segments = [
    (6,  15),   # end journal / 端轴颈  φ12 x 15mm
    (8,  25),   # mid journal / 中间轴颈  φ16 x 25mm
    (10, 40),   # main body   / 主轴段  φ20 x 40mm
    (8,  25),   # mid journal / 中间轴颈  φ16 x 25mm
    (6,  15),   # end journal / 端轴颈  φ12 x 15mm
]
total_length = sum(s[1] for s in segments)  # 120 mm

# Keyway on main body / 主轴段键槽
key_width  = 6    # keyway width mm / 键槽宽度 mm
key_depth  = 3    # keyway depth mm / 键槽深度 mm  (cut below top surface)
key_length = 30   # keyway length mm / 键槽长度 mm  (centered on main body)

chamfer_len = 0.5  # end chamfer length mm / 端面倒角长度 mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
step_path  = os.path.join(output_dir, "stepped_shaft.step")

# ===== Modeling / 建模 =====

# --- Step 1: build half-profile polyline on XZ plane, then revolve ---
# --- 步骤1：在 XZ 平面建半截面折线，然后旋转 ---
with BuildPart() as shaft:
    with BuildSketch(Plane.XZ):
        # Build profile points from left end to right end, then back along Z axis
        # 从左端到右端构建轮廓点，再沿 Z 轴返回
        pts = []
        z = -total_length / 2  # start at left end / 从左端开始
        pts.append((0, z))     # left end center / 左端中心点
        for r, l in segments:
            pts.append((r, z))
            z += l
            pts.append((r, z))
        pts.append((0, z))     # right end center / 右端中心点

        with BuildLine():
            Polyline(*pts)
        make_face()

    revolve(axis=Axis.Z)

    # --- Step 2: cut keyway slot on top of main body ---
    # --- 步骤2：在主轴段顶面切键槽 ---
    # Locate the top face of the main body (largest radius section)
    # 定位主轴段顶面（最大半径截面的顶面，即 +X 最远面）
    main_r = max(r for r, _ in segments)  # 10 mm

    # The keyway is cut from the top (+Y face at max radius)
    # Use a sketch on the XY plane at the top of the main body
    # 键槽从顶部（最大半径处的 +Y 面）向下切
    with BuildSketch(Plane.XY.offset(main_r)):
        Rectangle(key_length, key_width)
    extrude(amount=-key_depth, mode=Mode.SUBTRACT)

    # --- Step 3: chamfer both ends ---
    # --- 步骤3：两端倒角 ---
    # Select the circular edges at both Z extremes / 选择两端最外圆边
    end_edges = (
        shaft.edges().filter_by(GeomType.CIRCLE)
              .sort_by(Axis.Z)
    )
    # Take the outermost edge at each end / 取两端最外边（最小和最大 Z）
    chamfer(end_edges[0], length=chamfer_len)
    chamfer(end_edges[-1], length=chamfer_len)

# ===== Validation Layer 1 + 2 / 验证 =====
assert shaft.part is not None, "part is None / part 为空"
assert shaft.part.is_valid,    "BRep invalid / BRep 无效"

vol = shaft.part.volume
bb  = shaft.part.bounding_box()
print(f"Dimensions / 尺寸: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")

# Bounding box checks / 包围盒检查
max_r = max(r for r, _ in segments)
assert abs(bb.size.Z - total_length) < 1.0, \
    f"length deviation / 总长偏差: {bb.size.Z:.2f} vs {total_length}"
assert abs(bb.size.X - max_r * 2) < 1.0, \
    f"max diameter deviation / 最大径偏差: {bb.size.X:.2f} vs {max_r*2}"

# Volume: must be positive and less than full cylinder of max radius
# 体积：必须为正且小于最大半径全柱体积
full_vol = math.pi * max_r**2 * total_length
assert 0 < vol < full_vol, f"volume out of range / 体积超范围: {vol:.2f}"

# Exactly one solid / 只有一个 solid
assert len(shaft.part.solids()) == 1, "expected exactly one solid / 应只有一个 solid"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP export + re-import / STEP 导出 + 重导入 =====
export_step(shaft.part, step_path)
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

        views = [
            ("ISO",   Camera.ISO),
            ("TOP",   Camera.TOP),
            ("FRONT", Camera.FRONT),
        ]
        for label, cam in views:
            show(shaft.part, names=["stepped_shaft"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"stepped_shaft_{label}.png"))
            print(f"Screenshot saved / 截图已保存: stepped_shaft_{label}.png")

        print(f"OCP Viewer: preview opened on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 05-stepped-shaft all tests passed / 全部测试通过")
