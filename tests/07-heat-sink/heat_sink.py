"""
07-heat-sink — Heat Sink / 散热片
Tests / 测试:
  Box base + top face selector  — 80×60×5mm base plate / 底板顶面选择器
  GridLocations fin array       — 8 fins, 25mm tall, 1.5mm thick / 8 片鳍片阵列
  sort_by(Axis.Z) top face      — sketch plane from sorted face / 排序取顶面作草图平面

Design intent (Dave Cowden style) / 设计意图:
  Base plate -> select top face -> grid-locate fin sketches -> extrude fins upward
  底板 -> 选顶面 -> 网格定位鳍片草图 -> 向上拉伸鳍片
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
base_l  = 80     # base plate length mm / 底板长度 mm
base_w  = 60     # base plate width mm / 底板宽度 mm
base_h  = 5      # base plate height mm / 底板高度 mm

fin_count  = 8        # number of fins / 鳍片数量
fin_h      = 25       # fin height mm / 鳍片高度 mm
fin_t      = 1.5      # fin thickness mm / 鳍片厚度 mm
fin_len    = base_l - 10   # fin length mm (leave 5mm margin each end) / 鳍片长度（两端各留 5mm）
# Fins are spaced evenly across the width / 鳍片在宽度方向均匀分布
# GridLocations spacing: (fin_count-1) intervals across usable width / GridLocations 间距：可用宽度等分
fin_y_spacing = (base_w - 10) / (fin_count - 1)  # 7.14mm spacing / 间距

output_dir = os.path.join(os.path.dirname(__file__), "output")
step_path  = os.path.join(output_dir, "heat_sink.step")

# ===== Modeling / 建模 =====
with BuildPart() as sink:

    # Step 1: base plate / 步骤1：底板
    Box(base_l, base_w, base_h)

    # Step 2: select top face as fin sketch plane / 步骤2：选顶面作鳍片草图平面
    top_face = sink.faces().sort_by(Axis.Z)[-1]

    # Step 3: grid-locate fin sketches on top face, extrude upward
    # 步骤3：在顶面网格定位鳍片草图，向上拉伸
    with BuildSketch(top_face):
        with GridLocations(0, fin_y_spacing, 1, fin_count):
            Rectangle(fin_len, fin_t)
    extrude(amount=fin_h)

# ===== Validation Layer 1 + 2 / 验证 =====
assert sink.part is not None, "part is None / part 为空"
assert sink.part.is_valid,    "BRep invalid / BRep 无效"

vol = sink.part.volume
bb  = sink.part.bounding_box()
print(f"Bounding box / 包围盒: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"Volume / 体积: {vol:.2f} mm³")

# Bounding box checks / 包围盒检查
assert abs(bb.size.X - base_l) < 1.0, \
    f"length deviation / 长度偏差: {bb.size.X:.2f} vs {base_l}"
assert abs(bb.size.Y - base_w) < 1.0, \
    f"width deviation / 宽度偏差: {bb.size.Y:.2f} vs {base_w}"
assert abs(bb.size.Z - (base_h + fin_h)) < 1.0, \
    f"total height deviation / 总高偏差: {bb.size.Z:.2f} vs {base_h + fin_h}"

# Volume: base plate + fin array / 体积：底板 + 鳍片阵列
base_vol = base_l * base_w * base_h
fin_vol  = fin_count * fin_len * fin_t * fin_h
total_approx = base_vol + fin_vol
# Allow ±5% tolerance / 允许 ±5% 宽容度
assert total_approx * 0.95 < vol < total_approx * 1.05, \
    f"volume out of range / 体积超范围: {vol:.2f}, expected ~{total_approx:.2f}"

assert len(sink.part.solids()) == 1, "expected exactly one solid / 应只有一个 solid"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(sink.part, step_path)
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
            show(sink.part, names=["heat_sink"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"heat_sink_{label}.png"))
            print(f"Screenshot saved / 截图已保存: heat_sink_{label}.png")
        print(f"OCP Viewer: preview opened on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 07-heat-sink all tests passed / 全部测试通过")
