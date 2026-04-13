"""
11-revolute-hinge — Animal Skeleton Knee Joint + Animation / 动物骨骼膝关节 + 旋转动画
Tests / 测试:
  Bone shape (Algebra Mode)    — Cylinder shaft + Sphere joint heads / 圆柱骨干 + 球形关节头
  RigidJoint on thigh          — fixed knee connection point / 大腿骨固定膝关节点
  RevoluteJoint on shin        — 1 DOF knee, angular_range=(-10,120) / 小腿单自由度膝关节
  connect_to auto-position     — j_thigh.connect_to(j_shin, angle=0) → straight / 小腿自动定位直腿
  OCP Animation GIF            — knee flex/extend 60° cycle / 屈伸 60° 循环动画

Design intent (Dave Cowden style) / 设计意图:
  Thigh bone: cylinder shaft (r=5, h=50mm) with sphere joint heads at hip and knee.
  Shin bone: cylinder shaft (r=4, h=45mm) with sphere heads, LOCAL origin = knee pivot.
  Knee joint: RevoluteJoint, Y-axis rotation.
    joint_location rotation (ry=-90°) corrects alignment so angle=0 = straight leg.
    angular_range=(-10°, 120°): -10° slight hyperextension, 120° full flex.
  Animation: straight(0°) → bent(60°) → straight(0°), simple open-close cycle → GIF.
  大腿骨：r=5mm 圆柱 + 两端球形关节头。小腿骨：r=4mm 圆柱，本地原点=膝关节轴心。
  关节frame修正（ry=-90°）保证 angle=0 = 直腿（小腿朝下）。
  动画：直腿(0°) → 屈膝(60°) → 直腿(0°)，循环 GIF。
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
thigh_r   = 5       # thigh shaft radius mm / 大腿骨干半径 mm
thigh_h   = 50      # thigh length mm / 大腿长度 mm
shin_r    = 4       # shin shaft radius mm / 小腿骨干半径 mm
shin_h    = 45      # shin length mm / 小腿长度 mm
joint_r   = 9       # knee joint sphere radius mm / 膝关节球半径 mm
hip_r     = 8       # hip joint sphere radius mm / 髋关节球半径 mm
ankle_r   = 6       # ankle joint sphere radius mm / 踝关节球半径 mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "revolute_hinge.step")

# ===== Bone Models (Algebra Mode) / 骨骼模型（代数模式）=====

# Thigh bone: shaft from z=0 (knee) upward to z=thigh_h (hip)
# 大腿骨：骨干从 z=0（膝）向上到 z=thigh_h（髋）
thigh_shaft = Cylinder(radius=thigh_r, height=thigh_h,
                       align=(Align.CENTER, Align.CENTER, Align.MIN))  # z=0 to z=thigh_h
thigh_knee  = Sphere(radius=joint_r)                                   # knee joint head at z=0
thigh_hip   = Sphere(radius=hip_r).translate((0, 0, thigh_h))         # hip joint head at top
thigh = thigh_shaft + thigh_knee + thigh_hip
thigh.label = "thigh"

# Shin bone: LOCAL origin = knee pivot (z=0), shaft goes DOWN to z=-shin_h
# 小腿骨：本地原点 = 膝关节轴心 (z=0)，骨干向下延伸至 z=-shin_h
shin_shaft  = Cylinder(radius=shin_r, height=shin_h,
                       align=(Align.CENTER, Align.CENTER, Align.MAX))  # z=-shin_h to z=0
shin_knee   = Sphere(radius=joint_r)                                   # knee head at z=0 (pivot)
shin_ankle  = Sphere(radius=ankle_r).translate((0, 0, -shin_h))       # ankle at bottom
shin = shin_shaft + shin_knee + shin_ankle
shin.label = "shin"

# ===== Joints / 关节 =====
# RigidJoint on thigh at z=0 (the knee attachment point)
# ry=-90° rotation corrects the joint frame so angle=0 = straight leg (shin pointing down)
# 大腿骨膝关节固定点；ry=-90° 修正关节 frame 使 angle=0 对应直腿（小腿朝下）
j_thigh = RigidJoint(
    label="knee_upper",
    to_part=thigh,
    joint_location=Location((0, 0, 0), (0, -90, 0))   # ry=-90° → angle=0 = straight
)

# RevoluteJoint on shin: Y-axis rotation, range (-10°, 120°)
# angle=0 → shin straight down; angle=60 → 60° knee flex
# 小腿骨旋转关节：Y 轴旋转；angle=0=直腿，angle=60=屈膝 60°
j_shin = RevoluteJoint(
    label="knee_lower",
    to_part=shin,
    axis=Axis((0, 0, 0), (0, 1, 0)),     # Y-axis rotation / Y 轴旋转
    angular_range=(-10, 120)             # -10° hyperext to 120° full flex / -10°过伸 到 120°全屈
)

# ===== Connect at 0° (straight leg) / 连接为 0°（直腿） =====
j_thigh.connect_to(j_shin, angle=0)

# ===== Assembly / 装配体 =====
assembly = Compound([thigh, shin], label="leg_joint")

# ===== Validation Layer 1 + 2 / 验证 =====
assert thigh.is_valid,    "thigh BRep invalid / 大腿骨 BRep 无效"
assert shin.is_valid,     "shin BRep invalid / 小腿骨 BRep 无效"
assert assembly.is_valid, "assembly BRep invalid / 装配体 BRep 无效"

thigh_vol = thigh.volume
shin_vol  = shin.volume
asm_vol   = assembly.volume

print(f"Thigh volume / 大腿骨体积: {thigh_vol:.2f} mm³")
print(f"Shin  volume / 小腿骨体积: {shin_vol:.2f} mm³")
print(f"Assembly solids / 实体数:  {len(assembly.solids())}")

# Volume rough checks / 体积粗检
thigh_approx = math.pi*thigh_r**2*thigh_h + (4/3)*math.pi*joint_r**3 + (4/3)*math.pi*hip_r**3
shin_approx  = math.pi*shin_r**2*shin_h  + (4/3)*math.pi*joint_r**3 + (4/3)*math.pi*ankle_r**3
assert thigh_vol > thigh_approx * 0.5,  f"thigh volume too small / 大腿骨体积过小: {thigh_vol:.0f}"
assert shin_vol  > shin_approx  * 0.5,  f"shin volume too small / 小腿骨体积过小: {shin_vol:.0f}"
assert len(assembly.solids()) == 2, "expected 2 solids / 应有 2 个实体"

# Verify shin is pointing downward at angle=0 (straight leg)
# 验证 angle=0 时小腿朝下（直腿）：ankle bbox 应主要在 -Z 方向
bb_shin = shin.bounding_box()
assert bb_shin.min.Z < -shin_h * 0.8, \
    f"shin not pointing down at angle=0 / 小腿未朝下: Z_min={bb_shin.min.Z:.1f}"

print(f"Shin ankle direction check (Z_min should be ≈ -{shin_h+ankle_r}): {bb_shin.min.Z:.1f}")
print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(assembly, step_path)
reimported = import_step(step_path)
vol_diff = abs(reimported.volume - asm_vol) / asm_vol
print(f"STEP re-import volume deviation / 重导入体积偏差: {vol_diff:.6%}")
assert vol_diff < 0.001, f"STEP precision loss / 精度损失: {vol_diff:.4%}"
print("✅ Layer 3 passed / 通过")

# ===== OCP Animation / OCP 旋转动画 =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot, Animation
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if not active_port:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
    else:
        set_port(active_port)

        # --- Static screenshots: straight / half-bend / full-bend / 三姿态截图 ---
        for angle, label in [(0, "straight"), (30, "bent30"), (60, "bent60")]:
            j_thigh.connect_to(j_shin, angle=angle)
            asm_pose = Compound([thigh, shin], label="leg_joint")
            show(asm_pose, names=["leg_joint"], render_joints=True,
                 reset_camera=Camera.ISO)
            time.sleep(0.6)
            save_screenshot(os.path.join(output_dir, f"pose_{label}.png"))
            print(f"Screenshot saved / 截图已保存: pose_{label}.png")

        # Reset to straight / 复位直腿
        j_thigh.connect_to(j_shin, angle=0)
        assembly = Compound([thigh, shin], label="leg_joint")

        # --- Animation GIF: 0° → 60° → 0° (open and close) / 动画 GIF：屈伸 60° 循环 ---
        # Step 5° per frame, 13 steps out + 13 steps back = 26 frames total
        # 每帧 5°，去程 13 步 + 回程 13 步 = 共 26 帧
        angles_fw = list(range(0, 61, 5))    # 0 → 60°, step 5° (13 steps)
        angles_bk = list(range(60, -1, -5))  # 60° → 0, step -5° (13 steps)
        anim_angles = angles_fw + angles_bk  # 26 frames total

        frame_paths = []
        show(assembly, names=["leg_joint"], render_joints=False, reset_camera=Camera.ISO)
        time.sleep(0.5)

        for idx, ang in enumerate(anim_angles):
            j_thigh.connect_to(j_shin, angle=ang)
            asm_frame = Compound([thigh, shin], label="leg_joint")
            show(asm_frame, names=["leg_joint"], render_joints=False, reset_camera=None)
            time.sleep(0.25)
            fpath = os.path.join(output_dir, f"anim_{idx:03d}.png")
            save_screenshot(fpath)
            frame_paths.append(fpath)

        print(f"Animation frames saved / 动画帧已保存: {len(frame_paths)} frames")

        # --- Compile GIF with Pillow / 用 Pillow 合成 GIF ---
        try:
            from PIL import Image
            imgs = [Image.open(p) for p in frame_paths]
            gif_path = os.path.join(output_dir, "leg_joint_rotation.gif")
            imgs[0].save(
                gif_path,
                save_all=True,
                append_images=imgs[1:],
                loop=0,
                duration=100     # 100ms per frame = 10fps / 每帧 100ms
            )
            for p in frame_paths:
                os.remove(p)
            print(f"GIF saved / GIF 已保存: leg_joint_rotation.gif ({len(imgs)} frames)")
        except ImportError:
            print("Pillow not installed, GIF skipped / Pillow 未安装，跳过 GIF")

        # --- Final ISO screenshot / 最终 ISO 截图 ---
        j_thigh.connect_to(j_shin, angle=0)
        # Show thigh and shin as separate named objects so OCP can address them individually
        # 分开 show 大腿和小腿，使 OCP 能独立寻址做动画
        show(thigh, shin, names=["thigh", "shin"], render_joints=True, reset_camera=Camera.ISO)
        time.sleep(0.5)
        save_screenshot(os.path.join(output_dir, "revolute_hinge_ISO.png"))

        # --- OCP Animation track / OCP Animation 轨道 ---
        try:
            anim = Animation()
            # Flex/extend cycle: straight(0°) → bent(60°, 2s) → hold 1s → straight(0°, 4s) → hold 1s
            # 屈伸循环：直腿(0°) → 屈膝(60°,2s) → 保持1s → 直腿(0°,4s) → 保持1s
            anim.add_track("/Group/shin", "ry",
                           times =[0,   2,   3,   5,   6],
                           values=[0,  60,  60,   0,   0])
            anim.animate(speed=1)
            print("OCP Animation playing / OCP 动画播放中 ✓")
        except Exception as e:
            print(f"OCP Animation skipped / OCP 动画跳过: {e}")

        print(f"OCP Viewer: port {active_port} ✓")

except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 11-revolute-hinge all tests passed / 全部测试通过")
