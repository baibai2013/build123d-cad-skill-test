"""
Test 21 — SG90 舵机安装座（servo mount）
SG90 servo bracket: body cavity + ear ledge + M2 holes + cable exit + frame holes
验证：extrude(Mode.SUBTRACT) 精确腔体 + 选择器定位 + 多层减材 + 阵列孔
设计理念：舵机竖直插入（输出轴朝上），耳片搁在顶面台阶上，M2 螺丝从上穿入
"""
from build123d import *
from ocp_vscode import show, set_port, Camera
from ocp_vscode.comms import port_check
from ocp_vscode.state import get_ports
import os

# ===== SG90 标准尺寸（来自 mounting-experience.md）=====
# SG90 standard dimensions
servo_l          = 22.8   # mm，本体长 (X) / body length
servo_w          = 12.2   # mm，本体宽 (Y) / body width
servo_h          = 22.7   # mm，本体高 (Z) / body height
ear_span         = 32.2   # mm，含双耳总宽 (Y) / total Y width with ears
ear_t            = 2.5    # mm，耳片厚度 / ear tab thickness
ear_from_bottom  = 15.5   # mm，耳底距舵机底面 / ear bottom from servo bottom

m2_r             = 1.1    # mm，M2 攻丝前钻孔半径 / M2 pre-tap drill radius
m2_hole_span     = 27.6   # mm，两耳 M2 孔中心沿 X 间距 / M2 hole X spacing

cable_w          = 9.0    # mm，线缆出口宽 / cable exit width
cable_h          = 6.0    # mm，线缆出口高 / cable exit height

# ===== 安装座设计参数 / Mount design parameters =====
gap      = 0.3    # mm，装配间隙 FDM / FDM clearance
wall     = 2.5    # mm，壁厚 / wall thickness
base_t   = 2.5    # mm，底板厚度 / base thickness
fr       = 1.5    # mm，外廓竖边圆角 / corner fillet

m3_r     = 1.6    # mm，底面固定 M3 孔半径 / bottom M3 mounting hole radius
m3_margin = 5.0   # mm，M3 孔距外壁距离 / M3 hole inset from edge

# ===== 推导尺寸 / Derived =====
cav_l   = servo_l + 2 * gap          # 内腔长 / cavity length (X)
cav_w   = servo_w + 2 * gap          # 内腔宽 / cavity width (Y)
ear_cav = ear_span + 2 * gap         # 含耳片总宽（Y）/ ear slot Y span

outer_l = cav_l   + 2 * wall         # 外形长 / outer length
outer_w = ear_cav + 2 * wall         # 外形宽（含耳壁）/ outer width
# 总高度：底板 + 耳片台阶 + 本体腔 = 底板 + 舵机全高
outer_h = base_t + servo_h           # 外形高 / outer height

# 耳片台阶位置（从底面算）：舵机耳朵离底面的距离 = ear_from_bottom
ear_ledge_z = base_t + ear_from_bottom  # 台阶 Z / ledge Z from bottom

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)

# ===== 建模（全减材策略）/ Modeling — subtract-only =====
with BuildPart() as mount:
    # 1. 外壳主体 / Outer solid box
    Box(outer_l, outer_w, outer_h)

    # 2. 舵机本体腔（从顶面向下切 servo_h）
    #    Body cavity: cut from top face, cav_l × cav_w × servo_h
    top = mount.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top):
        Rectangle(cav_l, cav_w)
    extrude(amount=-servo_h, mode=Mode.SUBTRACT)

    # 3. 耳片台阶槽（从顶面向下切 ear_t，宽度扩展到 ear_cav）
    #    Ear ledge slot: cut from top, full ear_cav width × ear_t deep
    #    → 在 cav_w 两侧各挖出耳片空间，形成台阶
    top = mount.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top):
        # 耳片区域 = 全宽矩形 - 本体区域（仅切两侧）
        # ear region = full width rect minus body region (cut sides only)
        Rectangle(cav_l, ear_cav)
        Rectangle(cav_l, cav_w, mode=Mode.SUBTRACT)
    extrude(amount=-ear_t, mode=Mode.SUBTRACT)

    # 4. M2 螺丝孔（从顶面向下钻，穿过耳片台阶，深 ear_t + 2mm 攻丝段）
    #    M2 tap holes from top, through ear ledge + 2mm thread engagement
    m2_depth  = ear_t + 2.0
    ear_y_ctr = (cav_w / 2 + ear_cav / 2) / 2   # Y 中心线 / Y center of each ear area
    top = mount.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top):
        with Locations(
            ( m2_hole_span / 2,  ear_y_ctr),
            (-m2_hole_span / 2,  ear_y_ctr),
            ( m2_hole_span / 2, -ear_y_ctr),
            (-m2_hole_span / 2, -ear_y_ctr),
        ):
            Circle(m2_r)
    extrude(amount=-m2_depth, mode=Mode.SUBTRACT)

    # 5. 线缆出口（-X 侧面中心）
    #    Cable exit slot on back face (-X side)
    back = mount.faces().sort_by(Axis.X)[0]
    with BuildSketch(back):
        # 出口居中，高度对应线缆离地 5mm 处
        Rectangle(cable_h, cable_w)
    extrude(amount=wall, mode=Mode.SUBTRACT)

    # 6. 底面 M3 固定孔（4 角）安装座固定到机架用
    #    Bottom M3 mounting holes for attaching mount to frame
    bot = mount.faces().sort_by(Axis.Z)[0]
    bx  = outer_l / 2 - m3_margin
    by  = outer_w / 2 - m3_margin
    with BuildSketch(bot):
        with Locations((bx, by), (-bx, by), (bx, -by), (-bx, -by)):
            Circle(m3_r)
    extrude(amount=base_t, mode=Mode.SUBTRACT)

    # 7. 外廓竖边圆角 / Corner fillets
    fillet(mount.edges().filter_by(Axis.Z), radius=fr)

# ===== 验证 / Validation =====
print("=== Servo Mount 验证 ===")
solid = mount.part

assert solid.is_valid, "BRep 无效"

vol = solid.volume
bb  = solid.bounding_box()
print(f"尺寸: {bb.size.X:.2f} × {bb.size.Y:.2f} × {bb.size.Z:.2f} mm")
print(f"体积: {vol:.1f} mm³")
print(f"期望: {outer_l:.2f} × {outer_w:.2f} × {outer_h:.2f} mm")

assert abs(bb.size.X - outer_l) < 1.0, f"X 偏差: {bb.size.X:.2f} vs {outer_l:.2f}"
assert abs(bb.size.Y - outer_w) < 1.0, f"Y 偏差: {bb.size.Y:.2f} vs {outer_w:.2f}"
assert abs(bb.size.Z - outer_h) < 1.0, f"Z 偏差: {bb.size.Z:.2f} vs {outer_h:.2f}"
assert len(solid.solids()) == 1, "应只有一个 solid"

fill = vol / (bb.size.X * bb.size.Y * bb.size.Z)
print(f"填充率: {fill:.1%}  (有腔体，合理 20%~75%)")
assert 0.15 < fill < 0.75, f"填充率异常: {fill:.1%}"

# Layer 3：STEP 精度
step_path = os.path.join(output_dir, "servo_mount.step")
export_step(solid, step_path)
ri   = import_step(step_path)
diff = abs(ri.volume - vol) / vol
print("STEP: " + ("✅ 精度OK" if diff < 0.001 else f"❌ 精度损失 {diff:.3%}"))
print(f"已导出: {step_path}")

print("\n✅ 所有断言通过")

# ===== OCP 预览 / OCP Preview =====
try:
    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        show(mount, reset_camera=Camera.ISO)
        print("OCP Viewer 预览已打开 ✓")
    else:
        print("OCP Viewer 未检测到 — 请启动 OCP CAD Viewer 扩展")
except Exception as e:
    print(f"OCP 预览跳过: {e}")
