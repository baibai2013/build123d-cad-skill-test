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
from planetary_lib import make_spur_gear, make_ring_gear, make_carrier
from build123d import export_stl, Location

# ===== 参数(改这里换几何)=====
MODULE, Z_SUN, Z_PLANET, N_PLANET, FACE_WIDTH = 2.0, 18, 12, 3, 10.0
# 对齿(clocking):行星绕自身轴预转,使齿落进太阳/内圈的齿槽(视觉啮合)。
# 太阳在每个行星方位(120°整数倍)恰为齿尖,行星需朝太阳留槽 → +15°(已渲染验证)。
CLOCK_DEG = 15.0
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
sun = make_spur_gear(Z_SUN, MODULE, FACE_WIDTH, bore_r=5.0)
planet = make_spur_gear(Z_PLANET, MODULE, FACE_WIDTH, bore_r=2.0)
ring = make_ring_gear(Z_RING, MODULE, FACE_WIDTH)
carrier = make_carrier(A_CENTER_MM, N_PLANET, FACE_WIDTH)

DENSITY = {"sun": 7850, "planet": 7850, "ring": 7850, "carrier": 2700}  # kg/m³


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

CARRIER_Z = -0.012   # 行星架下沉 12mm,行星再抬回 z=0 与太阳/内圈共面啮合

# link 名 → (零件, 密度, 材质);export_urdf 的 mesh 文件名按 link 名取 meshes/<name>.stl
link_parts = {"ring": (ring, "ring", "blue"), "sun": (sun, "sun", "red"),
              "carrier": (carrier, "carrier", "gray")}
for k in range(N_PLANET):
    link_parts[f"planet_{k+1}"] = (planet, "planet", "green")

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

spec = {
    "schema_version": 1,
    "robot": "planetary_gear",
    "units": {"length": "m", "angle": "rad"},
    "mesh_units": "mm",
    "mesh_uri_style": "relative",
    "naming_convention": "custom",
    "materials_library": {
        "red":   {"density_kg_m3": 7850, "color_rgba": [0.85, 0.20, 0.20, 1.0]},   # 太阳轮
        "green": {"density_kg_m3": 7850, "color_rgba": [0.25, 0.70, 0.30, 1.0]},   # 行星轮
        "blue":  {"density_kg_m3": 7850, "color_rgba": [0.25, 0.45, 0.85, 1.0]},   # 内齿圈
        "gray":  {"density_kg_m3": 2700, "color_rgba": [0.55, 0.55, 0.58, 1.0]},   # 行星架
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
    if name.startswith("planet_"):     # 烤入 clocking,使行星齿落进太阳/内圈齿槽
        p = part.moved(Location((0, 0, 0), (0, 0, 1), CLOCK_DEG))
    export_stl(p, os.path.join(mdir, f"{name}.stl"))
print(f"  ✓ meshes → {mdir}(clocking {CLOCK_DEG:g}°,{len(link_parts)} 个)")

# 颜色由 export_urdf.py 原生输出(顶层 <material> 定义 + visual 内联 <color>),无需后处理。
urdf_path = os.path.join(URDF_OUT, "robot.urdf")   # export_urdf 固定输出 robot.urdf
print(f"Done URDF: {urdf_path}")
print("预览: bash ~/.agents/skills/build123d-cad/skills/viewer/scripts/start.sh "
      f"{urdf_path} $(git rev-parse --show-toplevel)")
print("  → viewer urdf 引擎:拖 j_sun 滑块 / 按 play 看行星啮合转动")
