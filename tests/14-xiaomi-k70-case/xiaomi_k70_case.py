"""
14-xiaomi-k70-case — Redmi K70 手机壳（3D打印 FDM）
Redmi K70 phone case for FDM 3D printing

参数来源：references/xiaomi-k70/params.md
Features:
  ① 壳体主体（外壳 = 手机尺寸 + 间隙 + 壁厚）/ Shell body
  ② 正面开口 + 屏幕保护唇边 / Front opening + screen lip
  ③ 背面摄像头模组开孔（圆角矩形）/ Rear camera cutout
  ④ 右侧音量键 + 电源键开孔 / Right-side button cutouts
  ⑤ 底部 USB-C + 扬声器 + SIM 开孔 / Bottom port cutouts
  ⑥ 顶部红外开孔 / Top IR blaster cutout
"""

from build123d import *
import os

# ===== 手机机身尺寸（建模基准）/ Phone body dimensions =====
PHONE_L = 162.78      # 长度 Y轴 / length Y-axis
PHONE_W = 75.74       # 宽度 X轴 / width X-axis
PHONE_T = 8.59        # 厚度 Z轴 / thickness Z-axis
PHONE_R = 8.5         # 竖边圆角 / corner radius

# ===== 手机壳通用参数 / Case common parameters =====
GAP       = 0.3       # 配合间隙（单侧）/ fitting clearance per side
HOLE_MRG  = 0.5       # 开孔余量（单侧）/ hole margin per side

# ===== 摄像头模组开孔（2×2网格，近正方形，左上角）=====
# Camera module cutout (2×2 grid, near-square, upper-left)
# 修正依据：GSMArena 官方产品图对比 / corrected per GSMArena product photos
CAM_W     = 38.0      # 开孔宽度（2×2网格需更宽）/ cutout width for 2×2 grid
CAM_H     = 38.0      # 开孔高度（近正方形）/ cutout height (near-square)
CAM_R     = 8.0       # 开孔圆角（实物更圆润）/ cutout corner radius (rounder)
CAM_CX    = -13.0     # 中心X偏移（偏左）/ center X offset (left)
CAM_CY    = 55.0      # 中心Y偏移（偏上）/ center Y offset (from center, upward)
CAM_BUMP  = 2.0       # 摄像头凸起高度 / camera bump height

# ===== 右侧按键开孔 / Right-side button cutouts =====
VOL_LEN   = 24.0      # 音量键开孔长度 / volume button cutout length
VOL_DY    = 40.0      # 音量键距顶边 / volume button from top
PWR_LEN   = 12.0      # 电源键开孔长度 / power button cutout length
PWR_DY    = 68.0      # 电源键距顶边 / power button from top
BTN_H     = 4.0       # 按键开孔高度（Z方向）/ button cutout height (Z)

# ===== 底部开孔 / Bottom cutouts =====
USBC_W    = 12.0      # USB-C 开孔宽度 / USB-C cutout width
USBC_H    = 5.0       # USB-C 开孔高度 / USB-C cutout height
SPK_W     = 16.0      # 扬声器开孔宽度 / speaker cutout width
SPK_H     = 3.0       # 扬声器开孔高度 / speaker cutout height
SPK_CX    = 18.0      # 扬声器中心X / speaker center X
SIM_W     = 12.0      # SIM卡槽开孔宽度 / SIM cutout width
SIM_H     = 2.5       # SIM卡槽开孔高度 / SIM cutout height
SIM_CX    = -18.0     # SIM中心X / SIM center X

# ===== 顶部开孔 / Top cutouts =====
IR_D      = 4.0       # 红外开孔直径 / IR blaster cutout diameter

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)


def build_case(wall_t: float, lip_h: float, shell_r: float, airbag: float = 0.0):
    """
    构建手机壳 / Build phone case

    Args:
        wall_t:  壁厚 / wall thickness
        lip_h:   屏幕包裹高度 / screen lip height
        shell_r: 外壳倒圆 / outer shell fillet radius
        airbag:  四角气囊加厚（0=无）/ corner airbag extra thickness (0=none)
    """
    # 内腔尺寸 = 手机 + 间隙 / cavity = phone + gap
    cav_w = PHONE_W + GAP * 2
    cav_l = PHONE_L + GAP * 2
    cav_t = PHONE_T + GAP
    cav_r = PHONE_R + GAP

    # 外壳尺寸 = 内腔 + 壁厚 / outer shell = cavity + wall
    out_w = cav_w + wall_t * 2
    out_l = cav_l + wall_t * 2
    out_t = cav_t + wall_t          # 底部有壁厚，顶部开口 / bottom has wall, top open
    out_r = cav_r + wall_t

    # Z 布局：壳体底面 z=0，手机背面贴壳体内底面
    # Z layout: case bottom at z=0, phone back rests on inner bottom

    # ── ① 外壳主体 / Outer shell body ──
    with BuildPart() as outer:
        with BuildSketch(Plane.XY):
            RectangleRounded(out_w, out_l, radius=out_r)
        extrude(amount=out_t + lip_h)
    result = outer.part

    # ── 内腔挖空 / Hollow out cavity ──
    with BuildPart() as cavity:
        with BuildSketch(Plane.XY.offset(wall_t)):
            RectangleRounded(cav_w, cav_l, radius=cav_r)
        extrude(amount=cav_t + lip_h + 1.0)  # 略超出顶面确保贯通 / slightly beyond top
    result = result - cavity.part

    # ── 外壳边缘倒圆（底面边缘）/ Fillet outer bottom edges ──
    try:
        bottom_face = result.faces().sort_by(Axis.Z)[0]
        bottom_edges = bottom_face.edges()
        result = fillet(result, bottom_edges, radius=shell_r)
    except Exception:
        pass

    # ── 内壁顶部边缘倒圆（唇边内侧）/ Fillet inner lip edges ──
    try:
        top_face = result.faces().sort_by(Axis.Z)[-1]
        inner_edges = [e for e in top_face.edges()
                       if e.center().X**2 + e.center().Y**2 <
                       (out_w/2)**2]
        if inner_edges:
            result = fillet(result, inner_edges, radius=0.3)
    except Exception:
        pass

    # ── ② 背面摄像头开孔（圆角矩形，贯穿底壁）/ Camera cutout through bottom ──
    cam_z = -0.5  # 从底面往下延伸确保贯穿 / extend below bottom to cut through
    with BuildPart() as cam_cut:
        with BuildSketch(Plane.XY.offset(cam_z)):
            with Locations([(CAM_CX, CAM_CY)]):
                RectangleRounded(CAM_W, CAM_H, radius=CAM_R)
        extrude(amount=wall_t + 2.0)
    result = result - cam_cut.part

    # ── 摄像头保护环（高于凸起）/ Camera protection ring ──
    ring_t = 1.0      # 保护环壁厚 / ring wall thickness
    ring_h = CAM_BUMP + 0.5  # 高于摄像头凸起 / taller than camera bump
    ring_outer_w = CAM_W + ring_t * 2
    ring_outer_h = CAM_H + ring_t * 2
    ring_outer_r = CAM_R + ring_t

    with BuildPart() as ring_outer:
        with BuildSketch(Plane.XY):
            with Locations([(CAM_CX, CAM_CY)]):
                RectangleRounded(ring_outer_w, ring_outer_h, radius=ring_outer_r)
        extrude(amount=-ring_h)  # 向 -Z（背面外侧）延伸 / extend outward from back
    with BuildPart() as ring_inner:
        with BuildSketch(Plane.XY):
            with Locations([(CAM_CX, CAM_CY)]):
                RectangleRounded(CAM_W, CAM_H, radius=CAM_R)
        extrude(amount=-ring_h - 0.1)
    ring_solid = ring_outer.part - ring_inner.part
    result = result + ring_solid

    # ── ③ 右侧按键开孔（贯穿右壁）/ Right-side button cutouts ──
    btn_x = out_w / 2 - wall_t / 2  # 右壁中心 / right wall center
    btn_z = wall_t + cav_t / 2      # 手机侧面中心高度 / phone side center height

    # 音量键 / Volume button
    vol_y = out_l / 2 - VOL_DY - VOL_LEN / 2
    vol_cut = Pos(btn_x, vol_y, btn_z) * Box(wall_t + 2.0, VOL_LEN, BTN_H)
    result = result - vol_cut

    # 电源键 / Power button
    pwr_y = out_l / 2 - PWR_DY - PWR_LEN / 2
    pwr_cut = Pos(btn_x, pwr_y, btn_z) * Box(wall_t + 2.0, PWR_LEN, BTN_H)
    result = result - pwr_cut

    # ── ④ 底部开孔（贯穿底壁）/ Bottom cutouts ──
    bot_y = -out_l / 2 + wall_t / 2  # 底壁中心 / bottom wall center
    bot_z = wall_t + cav_t / 2

    # USB-C
    usbc_cut = Pos(0, bot_y, bot_z) * Box(USBC_W, wall_t + 2.0, USBC_H)
    result = result - usbc_cut

    # 扬声器 / Speaker
    spk_cut = Pos(SPK_CX, bot_y, bot_z) * Box(SPK_W, wall_t + 2.0, SPK_H)
    result = result - spk_cut

    # SIM 卡槽 / SIM tray
    sim_cut = Pos(SIM_CX, bot_y, bot_z) * Box(SIM_W, wall_t + 2.0, SIM_H)
    result = result - sim_cut

    # ── ⑤ 顶部红外开孔 / Top IR cutout ──
    top_y = out_l / 2 - wall_t / 2
    ir_cut = Pos(0, top_y, bot_z) * Cylinder(radius=IR_D / 2 + HOLE_MRG,
                                              height=wall_t + 2.0,
                                              rotation=(90, 0, 0))
    result = result - ir_cut

    # ── ⑥ V3 四角气囊加厚 / V3 corner airbag reinforcement ──
    if airbag > 0:
        airbag_r = out_r + airbag
        for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            cx = sx * (out_w / 2 - out_r)
            cy = sy * (out_l / 2 - out_r)
            bump = Pos(cx, cy, (out_t + lip_h) / 2) * Cylinder(
                radius=airbag_r,
                height=out_t + lip_h
            )
            # 只保留壳体外侧的部分 / keep only the part outside the shell
            result = result + (bump - outer.part)

    return result


# ===== 三变体构建 / Build 3 variants =====
variant_params = {
    "V1_slim":     (1.2, 1.0, 1.5, 0.0),   # 轻薄 / slim
    "V2_standard": (1.5, 1.5, 2.0, 0.0),   # 标准（推荐）/ standard (recommended)
    "V3_rugged":   (2.0, 2.0, 3.0, 1.0),   # 防摔 / rugged with airbag corners
}

results = {}
for label, (wt, lh, sr, ab) in variant_params.items():
    solid = build_case(wt, lh, sr, ab)
    assert solid is not None, f"{label}: solid is None"
    assert solid.is_valid, f"{label}: BRep invalid"

    bb = solid.bounding_box()
    vol = solid.volume
    n_solids = len(solid.solids())
    print(f"{label}: bbox {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm  "
          f"vol={vol:.0f} mm³  solids={n_solids}")

    # 尺寸断言 / dimension assertions
    assert bb.size.Y > PHONE_L, f"{label}: Y too short ({bb.size.Y:.2f})"
    assert bb.size.X > PHONE_W, f"{label}: X too narrow ({bb.size.X:.2f})"
    assert n_solids == 1, f"{label}: expected 1 solid, got {n_solids}"
    results[label] = solid

v1 = results["V1_slim"]
v2 = results["V2_standard"]
v3 = results["V3_rugged"]

# ===== STEP 导出 + 重导入验证（V2）/ Export + reimport validation =====
step_path = os.path.join(output_dir, "xiaomi_k70_case_V2.step")
export_step(v2, step_path)
ri = import_step(step_path)
vd = abs(ri.volume - v2.volume) / v2.volume
print(f"STEP re-import deviation: {vd:.6%}")
assert vd < 0.001, f"STEP precision loss: {vd:.4%}"
print("✅ Layer 1+2+3 passed")

# ===== 三变体并排展示 / Side-by-side 3 variants =====
offset_x = max(s.bounding_box().size.X for s in results.values()) * 1.6
v2_show = v2.move(Location((offset_x, 0, 0)))
v3_show = v3.move(Location((offset_x * 2, 0, 0)))

# ===== OCP 自动预览 / OCP auto preview =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        show(v1, v2_show, v3_show,
             names=["V1_slim", "V2_standard", "V3_rugged"],
             colors=["steelblue", "orange", "seagreen"],
             reset_camera=Camera.ISO)
        time.sleep(1.0)
        # V2 单独截图 / V2 screenshots
        for cam_label, cam in [("ISO", Camera.ISO), ("FRONT", Camera.FRONT),
                                ("BACK", Camera.BACK), ("BOTTOM", Camera.BOTTOM)]:
            show(v2, names=["xiaomi_k70_case"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"xiaomi_k70_case_{cam_label}.png"))
            print(f"Screenshot: xiaomi_k70_case_{cam_label}.png ✓")
        # 恢复三变体展示 / restore 3-variant view
        show(v1, v2_show, v3_show,
             names=["V1_slim", "V2_standard", "V3_rugged"],
             colors=["steelblue", "orange", "seagreen"],
             reset_camera=Camera.ISO)
        print(f"OCP Viewer: 3变体并排预览已打开 port={active_port}")
    else:
        print("OCP Viewer: 未检测到 Viewer，请启动 OCP CAD Viewer 扩展")
except Exception as e:
    print(f"OCP preview skipped: {e}")

print(f"\n✅ 14-xiaomi-k70-case 完成\n   推荐 STEP: {step_path}")
