"""
Test 20 — BallJoint 球铰万向节
Ball-and-socket joint with 3 DOF (RigidJoint + BallJoint connect_to)
三种姿态并排展示：直立 / 单轴倾斜 30° / 双轴倾斜 30°+45°
"""
from build123d import *
from ocp_vscode import show, set_port, Camera
from ocp_vscode.comms import port_check
from ocp_vscode.state import get_ports
import os

# ===== 参数 / Parameters =====
# 底座 / Socket base
base_w      = 40        # mm，底座宽度 / base width
base_d      = 40        # mm，底座深度 / base depth
base_h      = 15        # mm，底座高度 / base height

# 球碗 / Socket cup
cup_r       = 10        # mm，球碗半径（略大于球半径）/ cup radius (slightly > ball)
cup_depth   = 7         # mm，球碗嵌入深度 / cup embed depth

# 球铰头 / Ball head
ball_r      = 9         # mm，球半径 / ball radius
arm_r       = 4         # mm，连杆半径 / arm radius
arm_len     = 45        # mm，连杆长度 / arm length

# 输出路径 / Output path
output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)

# ===== 底座（含球碗凹穴）/ Socket base with cup =====
with BuildPart() as socket_part:
    Box(base_w, base_d, base_h)
    # 顶面中心打球碗凹穴（半球形）/ hemispherical cup at top center
    top_face = socket_part.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top_face):
        Circle(radius=cup_r)
    extrude(amount=-cup_depth, mode=Mode.SUBTRACT)
    # 底板四角 R3 圆角 / R3 fillets on base corners
    base_vert_edges = socket_part.edges().filter_by(Axis.Z)
    fillet(base_vert_edges, radius=3)

    # RigidJoint：底座顶面球碗圆心位置 / at cup center on top face
    RigidJoint(
        label="socket",
        joint_location=Location((0, 0, base_h))    # 顶面中心 / top face center
    )

socket_solid = socket_part.part

# ===== 球铰臂（球 + 杆）/ Ball-arm (sphere + rod) =====
# Algebra Mode：球体 + 向上延伸的圆柱杆
# Ball center at origin, arm extends +Z
ball_body = Sphere(radius=ball_r)
arm_body  = Cylinder(radius=arm_r, height=arm_len,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
# 杆从球心上方 4mm 处起始（与球有 5mm 重叠，确保布尔融合）
# Rod starts 4mm above sphere center (5mm overlap ensures boolean union)
arm_shifted = arm_body.move(Location((0, 0, ball_r - 5)))
ball_arm_solid = ball_body + arm_shifted

# 添加 BallJoint：附着于球铰臂，中心在球心（原点）
# Add BallJoint on ball-arm at sphere center (origin)
BallJoint(
    label="ball",
    to_part=ball_arm_solid,
    joint_location=Location((0, 0, 0)),
    angular_range=((-45, 45), (-45, 45), (0, 360)),
)

# ===== 三姿态装配 / Three-pose assembly =====
def make_pose(angles: tuple[float, float, float]) -> Compound:
    """
    Clone socket+ball_arm, connect ball joint at given angles.
    返回已定位的 Compound。
    """
    import copy
    s = copy.copy(socket_solid)
    ba = copy.copy(ball_arm_solid)

    # 重新附加关节（copy 不携带 joints dict）
    # Re-attach joints (copy doesn't carry joints dict)
    RigidJoint(label="socket", to_part=s,
               joint_location=Location((0, 0, base_h)))
    BallJoint(label="ball", to_part=ba,
              joint_location=Location((0, 0, 0)),
              angular_range=((-45, 45), (-45, 45), (0, 360)))

    s.joints["socket"].connect_to(ba.joints["ball"],
                                   angles=Rotation(*angles))
    return Compound(children=[s, ba], label="pose")

pose_upright  = make_pose((0,   0,   0))    # 直立 / upright
pose_tilt_x   = make_pose((30,  0,   0))    # 绕 X 倾斜 30° / tilt X 30°
pose_tilt_xz  = make_pose((30,  0,  45))    # X 倾斜 30° + Z 旋转 45° / tilt + rotate

# 并排偏移：X 方向 / side-by-side along X
spacing = base_w * 1.8
pose_tilt_x_off  = pose_tilt_x.move(Location((spacing,      0, 0)))
pose_tilt_xz_off = pose_tilt_xz.move(Location((spacing * 2, 0, 0)))

# ===== 验证 / Validation =====
print("=== Ball-Joint 验证 ===")

# Layer 1：BRep 有效性 + 几何断言
for name, solid in [("socket", socket_solid), ("ball_arm", ball_arm_solid)]:
    assert solid.is_valid, f"{name} BRep 无效"
    vol = solid.volume
    bb  = solid.bounding_box()
    print(f"{name}: 体积={vol:.1f}mm³  bbox={bb.size.X:.1f}×{bb.size.Y:.1f}×{bb.size.Z:.1f}mm")

# 体积范围断言
socket_vol   = socket_solid.volume
ball_arm_vol = ball_arm_solid.volume
assert 5000 < socket_vol   < 30000, f"底座体积超范围: {socket_vol:.0f}"
assert 3000 < ball_arm_vol < 20000, f"球铰臂体积超范围: {ball_arm_vol:.0f}"
assert len(socket_solid.solids())   == 1, "底座应只有 1 个 solid"
assert len(ball_arm_solid.solids()) == 1, "球铰臂应只有 1 个 solid"

# Layer 3：STEP 导出 + 回读验证
step_socket = os.path.join(output_dir, "socket.step")
step_arm    = os.path.join(output_dir, "ball_arm.step")
export_step(socket_solid,   step_socket)
export_step(ball_arm_solid, step_arm)

ri_socket  = import_step(step_socket)
ri_arm     = import_step(step_arm)
for name, orig_vol, ri in [
    ("socket",   socket_vol,   ri_socket),
    ("ball_arm", ball_arm_vol, ri_arm),
]:
    diff = abs(ri.volume - orig_vol) / orig_vol
    status = "✅ STEP精度" if diff < 0.001 else f"❌ STEP精度损失({diff:.3%})"
    print(f"{name}: {status}")

# 装配体导出（直立姿态）
step_assy = os.path.join(output_dir, "ball_joint_assembly.step")
export_step(pose_upright, step_assy)
print(f"装配体已导出: {step_assy}")

print("\n✅ 所有断言通过")

# ===== OCP 预览（三姿态并排）/ OCP Preview (3 poses side-by-side) =====
try:
    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        show(
            pose_upright, pose_tilt_x_off, pose_tilt_xz_off,
            names=["pose_upright", "pose_tilt_x30", "pose_tilt_x30_z45"],
            colors=["steelblue", "orange", "green"],
            reset_camera=Camera.ISO,
            render_joints=True,
        )
        print("OCP Viewer 预览已打开：3 姿态并排 ✓")
    else:
        print("OCP Viewer 未检测到 — 请启动 OCP CAD Viewer 扩展")
except Exception as e:
    print(f"OCP 预览跳过: {e}")
