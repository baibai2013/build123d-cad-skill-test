"""
行星齿轮组 / Planetary Gear Set
=================================
建模策略:复用 02-spur-gear 的渐开线齿廓(根圆柱 + 逐齿 Algebra 融合),
封装成 make_spur_gear() 后组装:
    太阳轮(外齿 z_s)+ N 行星轮(外齿 z_p)+ 内齿圈(z_r,环坯减外齿刀)+ 行星架

啮合约束(已满足,几何自洽):
    内齿圈齿数 z_r = z_s + 2·z_p
    行星中心距 a = (z_s + z_p)·m/2 = (z_r − z_p)·m/2     ← 太阳/内圈两侧都对得上
    N 行星等分装配:(z_s + z_r) 必须被 N 整除

预览:导出装配 STEP,交 build123d-cad 的 viewer 子技能 start.sh 起网页看。
"""
from build123d import *  # noqa: F403
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace  # type: ignore[import-untyped]
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir  # type: ignore[import-untyped]
import math

# 标件优先从 parts-lib 导入(项目工作规则);齿轮本体才参数化自建。
from build123d_parts_lib.parts.fasteners.pin_spring import make_spring_pin
from build123d_parts_lib.parts.fasteners.socket_head_screw import make_socket_head_screw
from build123d_parts_lib.parts.servos.sg90 import make_sg90

# ===== 参数(顶部集中,改一处全局生效)=====
MODULE      = 2.0      # 模数 m
Z_SUN       = 18       # 太阳轮齿数
Z_PLANET    = 12       # 行星轮齿数
N_PLANET    = 3        # 行星轮个数
FACE_WIDTH  = 10.0     # 齿宽 mm
PRESSURE_A  = 20.0     # 压力角 °
TOOTH_STEPS = 6        # 渐开线采样段数(越大越精,越慢)
SUN_BORE    = 5.0      # 太阳轮中心轴孔半径
PLANET_BORE = 2.0      # 行星轮销孔半径(对齐 parts-lib Ø4 弹性销)
CARRIER_T   = 4.0      # 行星架厚度

# ===== 派生 =====
Z_RING = Z_SUN + 2 * Z_PLANET          # = 42
A_CENTER = (Z_SUN + Z_PLANET) * MODULE / 2  # 行星中心距 = 30
RING_PITCH_R = MODULE * Z_RING / 2          # = 42
RING_OUTER_R = RING_PITCH_R + 2.5 * MODULE  # 环外缘

assert Z_RING == Z_SUN + 2 * Z_PLANET
assert abs((Z_RING - Z_PLANET) * MODULE / 2 - A_CENTER) < 1e-9, "内圈侧中心距不一致"
assert (Z_SUN + Z_RING) % N_PLANET == 0, f"(z_s+z_r) 不被 {N_PLANET} 整除,行星无法等分"

XY_PLANE = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _face_from_pts(pts_2d):
    wire = Wire.make_polygon([(x, y, 0) for x, y in pts_2d], close=True)
    return Face(BRepBuilderAPI_MakeFace(XY_PLANE, wire.wrapped, True).Face())


def _tooth_pts(tooth_idx, teeth, base_r, root_r, addendum_r, steps):
    """单齿渐开线两侧 + 齿根圆弧,返回闭合多边形点列(可能 None)。"""
    pitch_angle = 2 * math.pi / teeth
    half_t = math.pi / (2 * teeth)
    a_i = pitch_angle * tooth_idx
    inv_max = math.sqrt(max(0.0, (addendum_r / base_r) ** 2 - 1))

    left = []
    for s in range(steps + 1):
        ia = inv_max * (s / steps)
        r = base_r * math.sqrt(1 + ia ** 2)
        if r < root_r:
            continue
        r = min(r, addendum_r)
        th = a_i + half_t - ia + math.atan(ia)
        left.append((r * math.cos(th), r * math.sin(th)))

    right = []
    for s in range(steps, -1, -1):
        ia = inv_max * (s / steps)
        r = base_r * math.sqrt(1 + ia ** 2)
        if r < root_r:
            continue
        r = min(r, addendum_r)
        th = a_i - half_t + ia - math.atan(ia)
        right.append((r * math.cos(th), r * math.sin(th)))

    if not left or not right:
        return None

    th_r = math.atan2(right[-1][1], right[-1][0])
    th_l = math.atan2(left[0][1], left[0][0])
    if th_l < th_r:
        th_l += 2 * math.pi
    arc = [(root_r * math.cos(th_r + (th_l - th_r) * k / 4),
            root_r * math.sin(th_r + (th_l - th_r) * k / 4)) for k in range(1, 4)]
    return left + right + arc


def make_spur_gear(teeth, *, module=MODULE, face_width=FACE_WIDTH,
                   pressure_a=PRESSURE_A, steps=TOOTH_STEPS, bore_r=0.0):
    """外齿渐开线直齿轮,中心在原点;bore_r>0 钻中心孔。返回 Part。"""
    pitch_r = module * teeth / 2
    addendum_r = pitch_r + module
    root_r = pitch_r - 1.25 * module
    base_r = pitch_r * math.cos(math.radians(pressure_a))

    gear = Cylinder(radius=root_r, height=face_width)
    for i in range(teeth):
        pts = _tooth_pts(i, teeth, base_r, root_r, addendum_r, steps)
        if pts is None:
            continue
        with BuildPart() as tooth:
            with BuildSketch(Plane.XY.offset(-face_width / 2)):
                add(_face_from_pts(pts))
            extrude(amount=face_width)
        gear = gear + tooth.part
    if bore_r > 0:
        gear = gear - Cylinder(radius=bore_r, height=face_width * 1.1)
    return gear


def make_ring_gear():
    """内齿圈:实心环坯(到外缘)减去 z_r 外齿刀,刀齿即圈的齿槽 → 留内齿。"""
    blank = Cylinder(radius=RING_OUTER_R, height=FACE_WIDTH)
    cutter = make_spur_gear(Z_RING, bore_r=0.0)          # 外齿刀(同模数同齿数)
    cutter = scale(cutter, by=(1, 1, 1.2))               # 刀略高于环,确保切穿
    return blank - cutter


def make_carrier():
    """行星架:薄盘 + 3 销孔 + 中心孔,放在齿轮组下方。"""
    plate = Cylinder(radius=A_CENTER + 6, height=CARRIER_T)
    plate = plate - Cylinder(radius=SUN_BORE + 1, height=CARRIER_T * 1.1)  # 中心让位
    for k in range(N_PLANET):
        ang = 2 * math.pi * k / N_PLANET
        pin = Cylinder(radius=PLANET_BORE, height=CARRIER_T * 1.1)
        pin = pin.moved(Location((A_CENTER * math.cos(ang), A_CENTER * math.sin(ang), 0)))
        plate = plate - pin
    return plate.moved(Location((0, 0, -(FACE_WIDTH / 2 + CARRIER_T / 2 + 1))))


# ===== 组装 =====
print(f"模数 m={MODULE}  太阳 z={Z_SUN}  行星 z={Z_PLANET}×{N_PLANET}  内圈 z={Z_RING}")
print(f"行星中心距 a={A_CENTER}mm  内圈外缘 R={RING_OUTER_R}mm")

sun = make_spur_gear(Z_SUN, bore_r=SUN_BORE)
print("  ✓ 太阳轮")

planets = []
for k in range(N_PLANET):
    ang = 2 * math.pi * k / N_PLANET
    p = make_spur_gear(Z_PLANET, bore_r=PLANET_BORE)
    # 视觉相位:行星绕中心放置(精确啮合相位非预览必需,做近似)
    p = p.moved(Location((A_CENTER * math.cos(ang), A_CENTER * math.sin(ang), 0)))
    planets.append(p)
    print(f"  ✓ 行星轮 {k + 1} @ {math.degrees(ang):.0f}°")

ring = make_ring_gear()
print("  ✓ 内齿圈")
carrier = make_carrier()
print("  ✓ 行星架")

# ===== 标件:全部从 parts-lib 导入(项目工作规则)=====
CARRIER_BOTTOM = -(FACE_WIDTH / 2 + CARRIER_T + 1)  # 行星架底面 z

# 行星销轴:弹性销穿过每个行星轮 + 行星架(nominal_d 对齐行星销孔 Ø)
pin_len = FACE_WIDTH + CARRIER_T + 8
pins = []
for k in range(N_PLANET):
    ang = 2 * math.pi * k / N_PLANET
    pin = make_spring_pin(nominal_d=2 * PLANET_BORE, length=pin_len)
    # 销默认沿 +Z;下移到穿过齿轮+架的位置
    pin = pin.moved(Location((A_CENTER * math.cos(ang), A_CENTER * math.sin(ang),
                              CARRIER_BOTTOM)))
    pins.append(pin)
print(f"  ✓ parts-lib 弹性销 ×{N_PLANET}(Ø{2*PLANET_BORE} × {pin_len:.0f})")

# 行星架紧固螺钉:M3 内六角,3 颗在行星之间(错 60°)
screws = []
for k in range(N_PLANET):
    ang = 2 * math.pi * k / N_PLANET + math.pi / N_PLANET  # 错开行星
    r = A_CENTER + 5
    sc = make_socket_head_screw(size="M3", length=10)
    sc = sc.moved(Location((r * math.cos(ang), r * math.sin(ang), CARRIER_BOTTOM)))
    screws.append(sc)
print(f"  ✓ parts-lib M3 内六角螺钉 ×{N_PLANET}")

# 驱动:SG90 舵机,输出轴对准太阳轮中心,机身位于行星架下方
servo = make_sg90()
sbb = servo.bounding_box()
servo = servo.moved(Location((0, 0, CARRIER_BOTTOM - sbb.size.Z / 2 - 1)))
print(f"  ✓ parts-lib SG90 舵机驱动(机身 {sbb.size.X:.0f}×{sbb.size.Y:.0f}×{sbb.size.Z:.0f})")

assembly = Compound(children=[
    Part(sun.wrapped, label="sun"),
    *[Part(p.wrapped, label=f"planet_{i+1}") for i, p in enumerate(planets)],
    Part(ring.wrapped, label="ring"),
    Part(carrier.wrapped, label="carrier"),
    *[Part(p.wrapped, label=f"pin_{i+1}") for i, p in enumerate(pins)],
    *[Part(s.wrapped, label=f"screw_{i+1}") for i, s in enumerate(screws)],
    Part(servo.wrapped, label="sg90_servo"),
])

# ===== 验证 =====
bb = assembly.bounding_box()
print(f"装配尺寸: {bb.size.X:.1f} × {bb.size.Y:.1f} × {bb.size.Z:.1f} mm")
print(f"零件数: {len(assembly.children)}  总 volume: {assembly.volume:.0f} mm3")

# ===== 导出(STEP 优先,装配件)=====
import os
os.makedirs("output", exist_ok=True)
export_step(assembly, "output/planetary_gear.step")
print("Done: output/planetary_gear.step")

# ===== 预览用 GLB sidecar =====
# build123d-cad 的 viewer cad 引擎按需读取隐藏 sidecar `.<name>.step.glb`(正常由
# cadpy.step_artifact 生成,本项目 venv 未装 cadpy)。这里用 build123d 自带
# export_gltf 直接出同名 sidecar,viewer 即可直接渲染,无需 cadpy 转换链。
export_gltf(assembly, "output/.planetary_gear.step.glb", binary=True)
print("Preview sidecar: output/.planetary_gear.step.glb")
print("预览: bash ~/.agents/skills/build123d-cad/skills/viewer/scripts/start.sh "
      "$PWD/output/planetary_gear.step $(git rev-parse --show-toplevel)")
