"""
04-flange — 法兰盘
测试：Cylinder + 中心孔 + PolarLocations 螺栓孔阵列 + CounterBoreHole 沉头孔

设计意图（Dave Cowden 风格）：
  毛坯圆盘 → 中心通孔 → 极坐标均布沉头螺栓孔
  每一步都能向机械师描述清楚
"""

from build123d import *
import os

# ===== 参数 =====
outer_r      = 40        # 外径半径 mm（外径 80mm）
flange_h     = 8         # 法兰高度 mm
center_r     = 15        # 中心通孔半径 mm

bolt_pcd_r   = 30        # 螺栓孔 PCD 半径 mm（PCD 60mm）
bolt_count   = 6         # 螺栓孔数量
bolt_r       = 4         # 螺栓通孔半径 mm（M8 通孔）
cbore_r      = 6.5       # 沉头半径 mm（M8 内六角螺栓头半径）
cbore_depth  = 4         # 沉头深度 mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
step_path  = os.path.join(output_dir, "flange.step")

# ===== 建模 =====
with BuildPart() as flange:
    # 步骤1：毛坯圆柱（法兰盘基体）
    Cylinder(radius=outer_r, height=flange_h)

    # 步骤2：中心通孔（主轴孔）
    Hole(radius=center_r)

    # 步骤3：PCD 均布 6 个沉头螺栓孔
    with PolarLocations(radius=bolt_pcd_r, count=bolt_count):
        CounterBoreHole(
            radius=bolt_r,
            counter_bore_radius=cbore_r,
            counter_bore_depth=cbore_depth,
        )

# ===== 验证 Layer 1 + 2 =====
assert flange.part is not None, "part 为空"
assert flange.part.is_valid,    "BRep 无效"

vol = flange.part.volume
bb  = flange.part.bounding_box()
print(f"尺寸: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
print(f"体积: {vol:.2f} mm³")

assert bb.size.Z > 0,                           "高度为 0"
assert abs(bb.size.Z - flange_h) < 0.5,        f"高度偏差: {bb.size.Z:.2f}"
assert abs(bb.size.X - outer_r * 2) < 0.5,     f"外径偏差: {bb.size.X:.2f}"
assert abs(bb.size.Y - outer_r * 2) < 0.5,     f"外径偏差: {bb.size.Y:.2f}"

# 体积下限：完整圆盘扣掉中心孔 + 6个沉头孔的估算
import math
raw_vol    = math.pi * outer_r**2 * flange_h                    # 完整圆柱
center_vol = math.pi * center_r**2 * flange_h                   # 中心孔
bolt_vol   = bolt_count * (math.pi * bolt_r**2 * flange_h       # 通孔
              + math.pi * (cbore_r**2 - bolt_r**2) * cbore_depth)  # 沉头额外部分
min_vol    = (raw_vol - center_vol - bolt_vol) * 0.9             # 10% 宽容度
assert vol > min_vol, f"体积异常: {vol:.2f} < {min_vol:.2f}"

# 确认有且仅有一个 solid
assert len(flange.part.solids()) == 1, "应只有一个 solid"

print("✅ Layer 1+2 通过")

# ===== 验证 Layer 3：STEP 导出 + 重导入精度 =====
export_step(flange.part, step_path)
reimported = import_step(step_path)
vol_diff = abs(reimported.volume - vol) / vol
print(f"STEP 重导入体积偏差: {vol_diff:.6%}")
assert vol_diff < 0.001, f"STEP 精度损失: {vol_diff:.4%}"
print("✅ Layer 3 通过")

# ===== OCP 预览（三视角截图）=====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)

        views = [
            ("ISO",   Camera.ISO),
            ("TOP",   Camera.TOP),
            ("FRONT", Camera.FRONT),
        ]
        for label, cam in views:
            show(flange.part, names=["flange"], reset_camera=cam)
            import time; time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"flange_{label}.png"))
            print(f"截图已保存: flange_{label}.png")

        print(f"OCP Viewer: 已在端口 {active_port} 打开预览 ✓")
    else:
        print("OCP Viewer: 未检测到运行中的 Viewer")
except Exception as e:
    print(f"OCP 预览跳过: {e}")

print("\n✅ 04-flange 全部测试通过")
