"""行星齿轮组【可动画 URDF】测试
===================================
目标(用户三诉求):预览里**齿轮真转** + **参数可配** + **每齿轮不同色**。

机制(build123d-cad 原生,非自造):
  build123d 出各齿轮独立网格(分色)→ joints.yaml(continuous + mimic 耦合关节,
  齿比当 multiplier)→ export_urdf.py 出带色 URDF → viewer urdf 引擎「关节滑块 + play」
  按正确行星运动学驱动转动(比上游相机 orbit 更真:真齿轮啮合)。

运动学(内圈固定、太阳轮 j_sun 为驱动,其余 mimic 它):
  carrier 绝对角  θ_c = θ_s · z_s/(z_s+z_r) = θ_s·0.30        → j_carrier mimic ×0.30
  planet 相对架角 θ_p/c = -(z_s/z_p)(θ_s-θ_c) = -1.05·θ_s      → j_spin  mimic ×-1.05
  减速比 i = 1 + z_r/z_s = 3.33 : 1(太阳输入→行星架输出)

参数可配:改下面常量重跑即换几何;viewer 里拖 j_sun 滑块 / 按 play 即换转角与转速。
"""
import math
import os
import subprocess
import sys
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from planetary_lib import (make_spur_gear, make_ring_gear, make_carrier,
                           make_flange, make_bearing, make_shaft)
from build123d import export_stl, Location

# ===== 参数(改这里换几何)=====
MODULE, Z_SUN, Z_PLANET, N_PLANET, FACE_WIDTH = 2.0, 18, 12, 3, 10.0
# 对齿(clocking):行星绕自身轴预转,使齿落进太阳/内圈的齿槽(视觉啮合)。
# 太阳在每个行星方位(120°整数倍)恰为齿尖,行星需朝太阳留槽 → +15°(已渲染验证)。
CLOCK_DEG = 15.0
# 内齿圈对齿:转半个齿距,使内齿落在 0/120/240° 三个行星方位(均为齿距整数倍),
# 与行星外侧齿咬合(已渲染验证)。半齿距 = 360/z_r/2。
RING_CLOCK_DEG = 360.0 / (Z_SUN + 2 * Z_PLANET) / 2     # 42 齿 → 4.286°
Z_RING = Z_SUN + 2 * Z_PLANET                       # 42
A_CENTER_MM = (Z_SUN + Z_PLANET) * MODULE / 2       # 30 mm
A_CENTER_M = A_CENTER_MM / 1000.0                   # 关节 origin 用米

CARRIER_MULT = Z_SUN / (Z_SUN + Z_RING)             # 0.30
PLANET_MULT = -(Z_SUN / Z_PLANET) * (Z_RING / (Z_SUN + Z_RING))  # -1.05

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
URDF_OUT = os.path.join(OUT, "planetary_urdf")
os.makedirs(OUT, exist_ok=True)

print(f"行星组 m={MODULE} z_s={Z_SUN} z_p={Z_PLANET}×{N_PLANET} z_r={Z_RING}")
print(f"mimic: carrier×{CARRIER_MULT:.3f}  planet×{PLANET_MULT:.3f}  减速比 {1+Z_RING/Z_SUN:.2f}:1")

# ===== 1) 各齿轮建在原点(URDF 靠关节 origin 摆位)=====
sun = make_spur_gear(Z_SUN, MODULE, FACE_WIDTH, bore_r=5.0)        # 太阳 bore Φ10 坐输入轴
planet = make_spur_gear(Z_PLANET, MODULE, FACE_WIDTH, bore_r=4.0)  # 行星 bore Φ8 套行星轴承外圈
ring = make_ring_gear(Z_RING, MODULE, FACE_WIDTH)
carrier = make_carrier(A_CENTER_MM, N_PLANET, FACE_WIDTH)

# 行星轴承(单位 mm;URDF 靠关节 origin 摆位)
bp_in, bp_out = make_bearing(inner_bore_r=2, outer_r=4, width=6.0, race_t=0.8, n_ball=6)           # 行星轴承(套销Φ4↔行星bore Φ8)
bearing_planet = bp_in + bp_out                                    # 行星轴承整体随行星转,当单一 link

# 轴系(中空轴同轴布局,均在 +Z 侧):
#   输出轴空心(随架),太阳轴从中心穿过它+法兰盘伸出(随太阳),行星销随架撑行星轮。
shaft_in  = make_shaft(shaft_r=4.8, length=39.0)                   # 太阳轴 Φ9.6,穿空心输出轴+法兰中心,+Z 露芯
shaft_out = make_shaft(shaft_r=9.5, length=20.0, bore_r=6.0)       # 输出轴 Φ19 空心(内孔 Φ12 让太阳轴穿过)
pin       = make_shaft(shaft_r=1.9, length=15.0)                   # 行星销(略小于轴承内孔 r2,留隙)

DENSITY = {"sun": 7850, "planet": 7850, "ring": 7850, "carrier": 2700,
           "flange": 700, "bearing": 700, "shaft": 700, "pin": 700}  # kg/m³(木件估)


def inertial_of(part, density):
    """按 mesh 体积×密度估质量 + bbox 粗算对角惯量(预览用,非动力学精度)。"""
    vol_m3 = part.volume * 1e-9          # mm³ → m³
    m = max(vol_m3 * density, 1e-3)
    bb = part.bounding_box()
    rx, ry, rz = bb.size.X / 2000, bb.size.Y / 2000, bb.size.Z / 2000  # mm→m 半尺寸
    return {
        "mass": round(m, 5),
        "origin": {"xyz": [0.0, 0.0, 0.0], "rpy": [0.0, 0.0, 0.0]},
        "inertia": {
            "ixx": round(max(m * (ry * ry + rz * rz) / 3, 1e-6), 8),
            "iyy": round(max(m * (rx * rx + rz * rz) / 3, 1e-6), 8),
            "izz": round(max(m * (rx * rx + ry * ry) / 3, 1e-6), 8),
            "ixy": 0.0, "ixz": 0.0, "iyz": 0.0,
        },
    }


# ===== 2) joints.yaml(分色材质 + continuous + mimic + 每 link inertial)=====
def origin(x=0.0, y=0.0, z=0.0):
    return {"xyz": [x, y, z], "rpy": [0.0, 0.0, 0.0]}

CARRIER_Z = 0.012    # 行星架移到 +Z 输出侧(z=+12mm);行星 j_spin origin z=-CARRIER_Z 回到 z=0 共面
                     # 输出端(+Z):架/输出轴/主轴承/法兰;输入端(-Z):输入轴从太阳伸出

# link 名 → (零件, 密度键, 材质=木种);export_urdf 的 mesh 文件名按 link 名取 meshes/<name>.stl
# 木种分组:固定组深色 walnut / 输出旋转组浅色 maple / 太阳 cherry / 行星 oak / 行星轴承 cherry
link_parts = {
    "ring":               (ring,         "ring",    "walnut"),
    "sun":                (sun,          "sun",     "cherry"),
    "carrier":            (carrier,      "carrier", "maple"),
    "shaft_in":           (shaft_in,     "shaft",   "cherry"),   # 输入轴,随太阳
    "shaft_out":          (shaft_out,    "shaft",   "maple"),    # 输出轴,随架
}
for k in range(N_PLANET):
    link_parts[f"planet_{k+1}"] = (planet, "planet", "oak")
for k in range(N_PLANET):
    link_parts[f"bearing_planet_{k+1}"] = (bearing_planet, "bearing", "cherry")
for k in range(N_PLANET):
    link_parts[f"pin_{k+1}"] = (pin, "pin", "maple")             # 行星销,随架

links = [{"name": n, "mesh": f"meshes/{n}.stl", "material": mat,
          "inertial": inertial_of(part, DENSITY[dk])}
         for n, (part, dk, mat) in link_parts.items()]

joints = [
    {"name": "j_sun", "type": "continuous", "parent": "ring", "child": "sun",
     "origin": origin(), "axis": [0, 0, 1]},                                # 驱动关节
    {"name": "j_carrier", "type": "continuous", "parent": "ring", "child": "carrier",
     "origin": origin(z=CARRIER_Z), "axis": [0, 0, 1],
     "mimic": {"joint": "j_sun", "multiplier": round(CARRIER_MULT, 4)}},
]
for k in range(N_PLANET):
    a = 2 * math.pi * k / N_PLANET
    joints.append({
        "name": f"j_spin_{k+1}", "type": "continuous", "parent": "carrier",
        "child": f"planet_{k+1}",
        "origin": origin(A_CENTER_M * math.cos(a), A_CENTER_M * math.sin(a), -CARRIER_Z),
        "axis": [0, 0, 1],
        "mimic": {"joint": "j_sun", "multiplier": round(PLANET_MULT, 4)},
    })

# 法兰 / 轴承 / 轴 / 销:fixed 关节,运动由父 link 携带(无需 mimic)。
# 挂 carrier 的件用 (z_abs - CARRIER_Z) 换算相对原点;CARRIER_Z=+0.012(架在 +Z 输出侧)。
joints += [
    {"name": "j_shaft_in", "type": "fixed", "parent": "sun", "child": "shaft_in",
     "origin": origin(z=0.0145)},                                   # 随太阳,+Z 穿空心输出轴+法兰,露芯至 z≈+34
    {"name": "j_shaft_out", "type": "fixed", "parent": "carrier", "child": "shaft_out",
     "origin": origin(z=0.020 - CARRIER_Z)},                        # 随架,空心,z≈+10~+30
]
for k in range(N_PLANET):
    joints.append({                                                 # 行星轴承随各行星转(同心同面)
        "name": f"j_bearing_planet_{k+1}", "type": "fixed",
        "parent": f"planet_{k+1}", "child": f"bearing_planet_{k+1}",
        "origin": origin(),
    })
for k in range(N_PLANET):
    a = 2 * math.pi * k / N_PLANET
    joints.append({                                                 # 行星销随架,在 A_CENTER 撑行星
        "name": f"j_pin_{k+1}", "type": "fixed",
        "parent": "carrier", "child": f"pin_{k+1}",
        "origin": origin(A_CENTER_M * math.cos(a), A_CENTER_M * math.sin(a), 0.0025 - CARRIER_Z),
    })

spec = {
    "schema_version": 1,
    "robot": "planetary_gear",
    "units": {"length": "m", "angle": "rad"},
    "mesh_units": "mm",
    "mesh_uri_style": "relative",
    "naming_convention": "custom",
    "materials_library": {   # 木种(color_rgba 仅无纹理预览用;木纹流程最终覆盖)
        "oak":    {"density_kg_m3": 700, "color_rgba": [0.80, 0.62, 0.38, 1.0]},   # 行星轮
        "cherry": {"density_kg_m3": 700, "color_rgba": [0.65, 0.34, 0.24, 1.0]},   # 太阳轮 / 行星轴承
        "maple":  {"density_kg_m3": 700, "color_rgba": [0.88, 0.76, 0.55, 1.0]},   # 输出旋转组
        "walnut": {"density_kg_m3": 700, "color_rgba": [0.40, 0.26, 0.16, 1.0]},   # 固定组
    },
    "links": links,
    "joints": joints,
}
joints_yaml = os.path.join(OUT, "planetary_joints.yaml")
with open(joints_yaml, "w", encoding="utf-8") as f:
    yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
print(f"  ✓ joints.yaml({len(links)} links / {len(joints)} joints)")

# ===== 3) export_urdf.py 出 URDF =====
EXPORT_URDF = os.path.expanduser(
    "~/.agents/skills/build123d-cad/skills/urdf/scripts/export_urdf.py")
rc = subprocess.run([sys.executable, EXPORT_URDF, joints_yaml, "-o", URDF_OUT, "--no-l1"],
                    cwd=OUT).returncode
if rc != 0:
    sys.exit(f"export_urdf 失败 rc={rc}")

# ===== 4) 按 link 名导出网格到 URDF 的 meshes/(export_urdf 不拷 STL,只引用)=====
mdir = os.path.join(URDF_OUT, "meshes")
os.makedirs(mdir, exist_ok=True)
for name, (part, _dk, _mat) in link_parts.items():
    p = part
    if name.startswith("planet_"):     # 行星 clocking:齿落进太阳齿槽
        p = part.moved(Location((0, 0, 0), (0, 0, 1), CLOCK_DEG))
    elif name == "ring":               # 内齿圈 clocking:内齿落在行星方位,与行星外齿咬合
        p = part.moved(Location((0, 0, 0), (0, 0, 1), RING_CLOCK_DEG))
    export_stl(p, os.path.join(mdir, f"{name}.stl"))
print(f"  ✓ meshes → {mdir}(行星 clock {CLOCK_DEG:g}° / 内圈 clock {RING_CLOCK_DEG:.3f}°)")

# 颜色由 export_urdf.py 原生输出(顶层 <material> 定义 + visual 内联 <color>),无需后处理。
urdf_path = os.path.join(URDF_OUT, "robot.urdf")   # export_urdf 固定输出 robot.urdf
print(f"Done URDF: {urdf_path}")
print("预览: bash ~/.agents/skills/build123d-cad/skills/viewer/scripts/start.sh "
      f"{urdf_path} $(git rev-parse --show-toplevel)")
print("  → viewer urdf 引擎:拖 j_sun 滑块 / 按 play 看行星啮合转动")
