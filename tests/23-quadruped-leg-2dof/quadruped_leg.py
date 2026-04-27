"""
Test 23 — 四足机器人 2-DOF 单腿装配
Quadruped Robot Single Leg Assembly (2 DOF: hip pitch + knee pitch)

部件 / Parts:
  - hip_bracket : 髋关节 SG90 安装座（使用 parts-lib 的 make_sg90_bracket 模板）
                  Hip servo bracket (uses parts-lib make_sg90_bracket)
  - femur       : 大腿连杆（parts-lib 的 make_leg_segment）
                  Upper leg segment (parts-lib make_leg_segment)
  - knee_bracket: 膝关节 SG90 安装座（同 hip）
                  Knee servo bracket (same template)
  - tibia       : 小腿连杆（较短的 leg_segment）
                  Lower leg segment (shorter leg_segment)
  - foot        : 足端半球脚垫（parts-lib 的 make_foot_cap）
                  Foot cap with rubber standing pad
  - 2 × SG90    : 舵机实体（parts-lib 的 make_sg90）
  - 6 × M3 螺丝 : 4 肩部固定 + 2 膝部固定（parts-lib 的 make_m3_screw）

来源 / Source:
  parts-lib 优先使用示例 — 6 个 import 全部来自 build123d_parts_lib
  Demonstrates parts-lib-first workflow — all 6 imports from build123d_parts_lib

坐标系 / Coordinate system:
  世界原点 = 髋 SG90 输出轴在机身上的投影点（髋支架底面中心）
  World origin = hip servo output shaft projection on chassis (hip bracket bottom)
  X = 前进方向 / X = forward
  Y = 侧向外 / Y = lateral (outward from body)
  Z = 向上 / Z = up (leg hangs down in -Z direction at angle=0)
"""

from build123d import *
from build123d_parts_lib.parts.servos.sg90              import make_sg90
from build123d_parts_lib.parts.fasteners.m3_iso4762     import make_m3_screw
from build123d_parts_lib.modules.threaded_insert_boss   import make_m3_boss
from build123d_parts_lib.modules.leg_segment           import make_leg_segment
from build123d_parts_lib.modules.foot_cap              import make_foot_cap
from build123d_parts_lib.templates.sg90_bracket        import make_sg90_bracket
import os

# ============================================================
# 全局参数 / Global parameters
# ============================================================

# 段长参数 / Segment lengths (typical mini quadruped scale)
FEMUR_LEN   = 70.0    # mm，大腿长 / upper leg length
TIBIA_LEN   = 55.0    # mm，小腿长 / lower leg length
SEGMENT_W   = 12.0    # mm，连杆宽 / segment width
SEGMENT_T   = 4.0     # mm，连杆厚 / segment thickness

# M3 螺丝 / M3 screws
M3_LENGTH   = 10.0    # mm，螺丝长 / screw length

# 脚垫 / Foot cap
FOOT_R       = 8.0    # mm，脚垫半径 / foot radius
FOOT_SHAFT_L = 6.0    # mm，脚杆柄 / foot shaft length

# 输出目录 / Output directory
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

# ============================================================
# 从 parts-lib 拿零件 / Get parts from parts-lib
# ============================================================
print("=" * 60)
print("Test 23 — 四足 2-DOF 单腿装配 / Quadruped 2-DOF Leg")
print("=" * 60)
print("\n[1/3] 从 parts-lib 导入标件实体 / Import from parts-lib...")

sg90_hip  = make_sg90()
sg90_knee = make_sg90()
print(f"  ✓ SG90 × 2 (bbox={sg90_hip.bounding_box().size})")

m3_screw = make_m3_screw(length=M3_LENGTH)
print(f"  ✓ M3 × {M3_LENGTH}mm screw (vol={m3_screw.volume:.1f} mm³)")

hip_bracket  = make_sg90_bracket(wall_thickness=2.5, print_clearance=0.3)
knee_bracket = make_sg90_bracket(wall_thickness=2.5, print_clearance=0.3)
print(f"  ✓ sg90_bracket × 2 (vol={hip_bracket.volume:.1f} mm³)")

femur = make_leg_segment(length=FEMUR_LEN, width=SEGMENT_W, thickness=SEGMENT_T,
                          pivot_hole_r=1.6, pivot_offset=7.0)
tibia = make_leg_segment(length=TIBIA_LEN, width=SEGMENT_W, thickness=SEGMENT_T,
                          pivot_hole_r=1.6, pivot_offset=7.0)
print(f"  ✓ femur  (len={FEMUR_LEN}, bbox={femur.bounding_box().size})")
print(f"  ✓ tibia  (len={TIBIA_LEN}, bbox={tibia.bounding_box().size})")

foot = make_foot_cap(radius=FOOT_R, shaft_d=3.0, shaft_length=FOOT_SHAFT_L,
                     flatten_bottom=True)
print(f"  ✓ foot   (bbox={foot.bounding_box().size})")

# ============================================================
# 装配定位 / Assembly positioning (direct transformation approach)
# ============================================================
print("\n[2/3] 装配定位 / Assembly positioning...")

# parts-lib 中 sg90_bracket 的几何：
#   - 开口向上（顶面是开口，底面是实底）
#   - bbox ≈ 29×19×30 mm（外盒）
#   Bracket: opens upward, outer bbox ~29×19×30
bracket_bb = hip_bracket.bounding_box()
BRACKET_H = bracket_bb.size.Z

# SG90 在 bracket 内的 Z 偏移 / SG90 Z offset in bracket
# bracket 底板 = 3mm，舵机下沉到底板上，body 底面 Z = 3mm (bracket 局部)
BASE_T = 3.0

# --- 髋关节（hip） ------------------------------------------------
# 世界坐标：bracket 底面在 Z=0，开口朝 +Z
# World: hip bracket sits at Z=0, opening up
hip_bracket_pos = Pos(0, 0, BRACKET_H / 2) * hip_bracket

# hip SG90 塞进 bracket 腔：body 底面 Z = BASE_T（bracket 局部），
# 所以世界 Z = BASE_T；SG90 make_sg90 原点在 body 中心，需抬升 BODY_H/2=11.35
# SG90 inserted into hip bracket cavity; body center Z = BASE_T + BODY_H/2
SG90_BODY_H = 22.7   # 来自 parts-lib sg90.py / from parts-lib
hip_sg90_pos = Pos(0, 0, BASE_T + SG90_BODY_H / 2) * sg90_hip

# --- 股骨（femur） ------------------------------------------------
# 股骨通过髋 SG90 的输出轴挂下来：
# 1. 先让股骨长度沿 -Z 方向（原始是沿 +X，旋转 Ry=-90 让 +X → -Z）
# 2. 上端孔对齐 SG90 输出轴位置
# Femur hangs from hip SG90 output shaft:
# 1. Rotate femur so its long axis points along -Z (Ry=-90 turns +X to -Z)
# 2. Align upper pivot hole with SG90 output shaft
SG90_SHAFT_X = 22.8 * 0.3 - 22.8 / 2  # = -4.56，SG90 输出轴相对 body 中心的 X 偏移（来自 parts-lib sg90.py）
# 输出轴世界坐标：bracket 内部 body 中心 (0,0,BASE_T+BODY_H/2) + 输出轴 X 偏移 + 轴高 5
hip_shaft_world = (SG90_SHAFT_X, 0, BASE_T + SG90_BODY_H + 2.5)  # 输出轴顶附近
# 股骨上端孔位置：pivot_offset=7 ，所以孔距端 7mm，全长 FEMUR_LEN
# 原始 femur 水平，沿 X 方向；旋转 Ry=-90 后沿 -Z 方向
# Rotation: Ry=-90 sends (+X → -Z), so original +X end becomes -Z end (下方)
# 我们希望上端（原 -X 端）对齐 hip 输出轴：原 (-FEMUR_LEN/2+7, 0, 0) → 旋转后 (0, 0, +(FEMUR_LEN/2-7))
# 所以平移 = hip_shaft_world - (0, 0, FEMUR_LEN/2-7) + 侧向偏移（让杆在舵机侧面）
side_offset = 7.0   # mm，股骨平移到舵机侧面（避开舵机主体）
femur_pos = (
    Pos(hip_shaft_world[0], side_offset, hip_shaft_world[2] - (FEMUR_LEN / 2 - 7))
    * Rot(0, -90, 0) * femur
)

# --- 膝关节 SG90 bracket（knee） -----------------------------------
# 膝关节 bracket 挂在股骨下端，开口朝下（或侧向），方便胫骨挂下去
# Knee bracket mounts at femur lower end, opening sideways
# 简化：膝支架放在股骨下端外侧，开口朝 +Z（同 hip 方向但位置下移）
femur_bottom_z = hip_shaft_world[2] - FEMUR_LEN + 14  # 下端孔位置 Z
knee_bracket_pos = Pos(hip_shaft_world[0] + 3, side_offset + 18, femur_bottom_z) * Rot(0, 0, 90) * knee_bracket
knee_sg90_pos    = Pos(hip_shaft_world[0] + 3, side_offset + 18, femur_bottom_z + BASE_T + SG90_BODY_H / 2) * Rot(0, 0, 90) * sg90_knee

# --- 胫骨（tibia） ------------------------------------------------
# 胫骨挂在膝 SG90 输出轴上，同样 Ry=-90 朝 -Z
knee_shaft_world = (hip_shaft_world[0] + 3 + SG90_SHAFT_X, side_offset + 18, femur_bottom_z + BASE_T + SG90_BODY_H + 2.5)
tibia_pos = (
    Pos(knee_shaft_world[0], knee_shaft_world[1] + 7, knee_shaft_world[2] - (TIBIA_LEN / 2 - 7))
    * Rot(0, -90, 0) * tibia
)

# --- 脚 / foot ----------------------------------------------------
# 脚挂在胫骨下端
tibia_bottom_z = knee_shaft_world[2] - TIBIA_LEN + 14
foot_pos = Pos(knee_shaft_world[0], knee_shaft_world[1] + 7, tibia_bottom_z - FOOT_SHAFT_L) * foot

# --- M3 螺丝可视化（6 颗）/ M3 screw visualization ---------------
# 4 颗固定 hip bracket 到机身，2 颗固定膝支架到股骨
# 简化展示：hip 底部 4 角
HIP_SCREW_X = [-12, 12]
HIP_SCREW_Y = [-8, 8]
hip_screws = [Pos(x, y, -M3_LENGTH) * m3_screw for x in HIP_SCREW_X for y in HIP_SCREW_Y]

print(f"  装配完成，组件 = hip_bracket + hip_sg90 + femur + knee_bracket + knee_sg90 + tibia + foot + 4×M3")

# ============================================================
# 三层验证 / Three-layer validation
# ============================================================
print("\n[3/3] 三层验证 / Three-layer validation...")

# Layer 1: BRep 有效性 / BRep validity
parts_to_check = {
    "hip_bracket": hip_bracket,
    "knee_bracket": knee_bracket,
    "femur": femur,
    "tibia": tibia,
    "foot": foot,
}
for name, part in parts_to_check.items():
    assert part.is_valid, f"{name} BRep 无效 / invalid"
print(f"  Layer 1: BRep is_valid   ✓ ({len(parts_to_check)} parts)")

# Layer 2: 体积 + bbox 合理范围 / Volume + bbox sanity
assert 50 < femur.volume < 3500,    f"femur vol {femur.volume:.1f} out of range"
assert 50 < tibia.volume < 3000,    f"tibia vol {tibia.volume:.1f} out of range"
assert 100 < foot.volume < 2000,    f"foot vol {foot.volume:.1f} out of range"
assert 500 < hip_bracket.volume < 10000, f"hip_bracket vol {hip_bracket.volume:.1f} out of range"

femur_bb = femur.bounding_box().size
assert abs(femur_bb.X - FEMUR_LEN) < 0.1, f"femur X {femur_bb.X} != {FEMUR_LEN}"
assert abs(femur_bb.Y - SEGMENT_W) < 0.1, f"femur Y {femur_bb.Y} != {SEGMENT_W}"
print(f"  Layer 2: 体积 + bbox     ✓")
print(f"           femur  {femur.volume:7.1f} mm³  bbox=({femur_bb.X:.1f}×{femur_bb.Y:.1f}×{femur_bb.Z:.1f})")
print(f"           tibia  {tibia.volume:7.1f} mm³")
print(f"           foot   {foot.volume:7.1f} mm³")
print(f"           hip_b  {hip_bracket.volume:7.1f} mm³")

# Layer 3: STEP 导出 + 重导入体积一致性 / STEP export + reimport volume check
step_files = {}
for name, part in parts_to_check.items():
    step_path = os.path.join(output_dir, f"{name}.step")
    export_step(part, step_path)
    reimported = import_step(step_path)
    diff = abs(reimported.volume - part.volume) / part.volume
    assert diff < 0.001, f"{name} STEP 精度损失 {diff*100:.4f}%"
    step_files[name] = step_path

# 装配 STEP / Full assembly STEP
all_parts = [
    hip_bracket_pos, hip_sg90_pos,
    femur_pos,
    knee_bracket_pos, knee_sg90_pos,
    tibia_pos, foot_pos,
    *hip_screws,
]
assembly = Compound(all_parts)
asm_step = os.path.join(output_dir, "leg_assembly.step")
export_step(assembly, asm_step)
print(f"  Layer 3: STEP 导出重导入 ✓ (偏差 < 0.1%)")
print(f"           装配 STEP: {asm_step}")

print("\n===== 三层验证全部通过 / ALL THREE LAYERS PASSED =====")

# ============================================================
# OCP 预览 / OCP preview
# ============================================================
try:
    from ocp_vscode import show, set_port, Camera
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        show(
            hip_bracket_pos, hip_sg90_pos,
            femur_pos,
            knee_bracket_pos, knee_sg90_pos,
            tibia_pos, foot_pos,
            *hip_screws,
            names=[
                "hip_bracket", "hip_sg90",
                "femur",
                "knee_bracket", "knee_sg90",
                "tibia", "foot",
                "m3_0", "m3_1", "m3_2", "m3_3",
            ],
            colors=[
                "steelblue", "darkred",
                "orange",
                "steelblue", "darkred",
                "orange", "black",
                "gray", "gray", "gray", "gray",
            ],
            reset_camera=Camera.ISO,
        )
        print(f"\nOCP Viewer 预览已打开 (port {active_port}) / OCP preview opened")
    else:
        print("\nOCP Viewer 未检测到 / OCP Viewer not detected")
except Exception as e:
    print(f"\nOCP 预览跳过 / OCP preview skipped: {e}")
