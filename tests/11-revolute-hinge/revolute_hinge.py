"""
11-revolute-hinge — Revolute Joint Hinge / 旋转铰链关节
Tests / 测试:
  RigidJoint on base         — fixed connection point on base plate / 底座固定连接点
  RevoluteJoint on arm       — 1 DOF rotating joint, angular_range=(0,120) / 单自由度旋转
  connect_to auto-position   — arm auto-positioned at given angle / 臂自动定位到指定角度
  Compound assembly export   — two-body assembly in one STEP / 双体装配体导出

Design intent (Dave Cowden style) / 设计意图:
  Base plate (80×30×8mm): fixed. Hinge pin at right end top face.
  Arm (60×14×6mm): rotates around pin axis (+Z). angular_range=(0,120).
  connect_to(angle=60) positions arm 60° from closed position.
  底座平板固定，铰链销轴在右端顶面。臂绕销轴（+Z）旋转，范围 0~120°。
  connect_to(angle=60) 将臂定位到半开状态（60°）。
"""

from build123d import *
import os, math

# ===== Parameters / 参数 =====
base_l, base_w, base_h = 80, 30, 8    # base plate dimensions mm / 底座尺寸 mm
arm_l,  arm_w,  arm_h  = 60, 14, 6    # arm dimensions mm / 臂尺寸 mm
hinge_angle = 60                        # arm angle at demo pose degrees / 演示姿态角度

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path  = os.path.join(output_dir, "revolute_hinge.step")

# ===== Parts / 零件 =====
# Base plate: centered at origin / 底座平板：原点居中
with BuildPart() as base_bp:
    Box(base_l, base_w, base_h)

base = base_bp.part

# Arm: centered at origin initially / 臂：初始居中
with BuildPart() as arm_bp:
    Box(arm_l, arm_w, arm_h)

arm = arm_bp.part

# ===== Joints / 关节 =====
# RigidJoint on base: at right end, top face center / 底座刚性关节：右端顶面中心
j_base = RigidJoint(
    label="hinge_base",
    to_part=base,
    joint_location=Location((base_l / 2, 0, base_h))   # right end, top / 右端顶面
)

# RevoluteJoint on arm: pivot at left end of arm, axis = +Z / 臂旋转关节：左端，轴向+Z
j_arm = RevoluteJoint(
    label="hinge_arm",
    to_part=arm,
    axis=Axis((-arm_l / 2, 0, 0), (0, 0, 1)),          # pivot at left end / 左端轴
    angular_range=(0, 120)                               # 0~120° range / 限位范围
)

# Position arm at hinge_angle degrees
# 将臂定位到指定角度：j_base.connect_to(j_arm) 通过刚性关节调用，arm 移动而 base 不动
j_base.connect_to(j_arm, angle=hinge_angle)

# ===== Assembly / 装配体 =====
assembly = Compound([base, arm], label="hinge_assembly")

# ===== Validation Layer 1 + 2 / 验证 =====
assert base.is_valid, "base BRep invalid / 底座 BRep 无效"
assert arm.is_valid,  "arm BRep invalid / 臂 BRep 无效"
assert assembly.is_valid, "assembly BRep invalid / 装配体 BRep 无效"

base_vol = base.volume
arm_vol  = arm.volume
asm_vol  = assembly.volume

print(f"Base volume / 底座体积: {base_vol:.2f} mm³  (expected {base_l*base_w*base_h:.0f})")
print(f"Arm  volume / 臂体积:   {arm_vol:.2f} mm³  (expected {arm_l*arm_w*arm_h:.0f})")
print(f"Assembly solids / 装配体实体数: {len(assembly.solids())}")

assert abs(base_vol - base_l * base_w * base_h) < 1.0, "base volume error / 底座体积误差"
assert abs(arm_vol  - arm_l  * arm_w  * arm_h)  < 1.0, "arm volume error / 臂体积误差"
assert len(assembly.solids()) == 2, "expected 2 solids / 应有 2 个实体"

# Verify arm was repositioned by connect_to / 验证臂已被 connect_to 重新定位
arm_loc = arm.location
loc_t   = arm_loc.position     # translation / 平移
loc_r   = arm_loc.orientation  # rotation / 旋转
print(f"Arm location / 臂位置: pos={loc_t}, orient={loc_r}")
# After connecting to base right end (x=40, z=8), arm should have moved from origin
# 连接到底座右端后，臂的 X 和 Z 应非零
assert abs(loc_t.X) > 1.0 or abs(loc_t.Z) > 1.0, \
    f"arm not repositioned / 臂未被重新定位: pos={loc_t}"

print("✅ Layer 1+2 passed / 通过")

# ===== Validation Layer 3: STEP re-import / STEP 重导入 =====
export_step(assembly, step_path)
reimported = import_step(step_path)
vol_diff = abs(reimported.volume - asm_vol) / asm_vol
print(f"STEP re-import volume deviation / 重导入体积偏差: {vol_diff:.6%}")
assert vol_diff < 0.001, f"STEP precision loss / 精度损失: {vol_diff:.4%}"
print("✅ Layer 3 passed / 通过")

# ===== OCP preview with render_joints / OCP 关节可视化预览 =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        for label, cam in [("ISO", Camera.ISO), ("TOP", Camera.TOP), ("FRONT", Camera.FRONT)]:
            show(assembly, names=["hinge_assembly"], render_joints=True, reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"revolute_hinge_{label}.png"))
            print(f"Screenshot saved / 截图已保存: revolute_hinge_{label}.png")
        print(f"OCP Viewer: preview on port {active_port} / 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: no running Viewer detected / 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP preview skipped / 预览跳过: {e}")

print("\n✅ 11-revolute-hinge all tests passed / 全部测试通过")
