"""
安装板 / Mounting Plate
建模序列：取平板毛坯 → 四角打 M5 通孔 → 顶面圆角
参数化重点：修改 margin 一个参数，孔位自动跟随
"""
from build123d import *

# ===== 参数 =====
l        = 100    # 板长 mm
w        = 80     # 板宽 mm
h        = 10     # 板厚 mm
hole_r   = 2.5    # M5 孔半径 mm（M5 = Φ5mm，R=2.5mm）
margin   = 12     # 孔中心到板边距离 mm（改这一个参数，孔位全局跟随）
fillet_r = 3      # 顶面圆角半径 mm

# ===== 派生尺寸 =====
hole_x_spacing = l - 2 * margin   # 两孔列间距（X 方向）
hole_y_spacing = w - 2 * margin   # 两孔行间距（Y 方向）

# ===== 建模 =====
# 操作序列：取毛坯 → 四角打孔 → 顶面圆角
with BuildPart() as plate:
    # Step 1: 平板毛坯
    Box(l, w, h)

    # Step 2: 四角 M5 通孔（2×2 GridLocations 阵列）
    with GridLocations(hole_x_spacing, hole_y_spacing, 2, 2):
        Hole(radius=hole_r)

    # Step 3: 顶面所有边倒 R3 圆角（选择器取顶面，无硬编码 Z 坐标）
    fillet(plate.faces().sort_by(Axis.Z)[-1].edges(), radius=fillet_r)

# ===== 验证 =====
bb = plate.part.bounding_box()
print(f"尺寸: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")
print(f"体积: {plate.part.volume:.1f} mm³")
print(f"孔间距: {hole_x_spacing} x {hole_y_spacing} mm（孔中心 GridLocations 跨度）")
print(f"孔半径: {hole_r} mm  M5 标准通孔")
print(f"※ 修改 margin={margin} → 孔位自动跟随（±孔间距同步变化）")

# ===== 参数化演示：验证 margin 联动 =====
print(f"\n参数化联动验证：")
for m_test in [8, 12, 16]:
    xs = l - 2 * m_test
    ys = w - 2 * m_test
    print(f"  margin={m_test:2d}mm → 孔间距 {xs}×{ys}mm")

# ===== 导出 =====
export_step(plate.part, "output/mounting_plate.step")
print("\n导出完成: output/mounting_plate.step")

# ===== OCP 预览 =====
try:
    from ocp_vscode import show
    show(plate.part, names=["mounting_plate"], colors=["steelblue"])
    print("OCP Viewer: 预览已加载")
except Exception:
    print("提示: 在 VS Code + OCP CAD Viewer 扩展中运行可看 3D 预览")
