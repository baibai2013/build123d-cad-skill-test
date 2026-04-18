"""
13-redmi-k80-pro — Redmi K80 Pro 手机壳（3D打印 FDM）
Redmi K80 Pro phone case for FDM 3D printing

参数来源：references/redmi-k80-pro/params.md
Features:
  ① 壳体主体（外壳 = 手机尺寸 + 间隙 + 壁厚）/ Shell body
  ② 正面开口 + 屏幕保护唇边 / Front opening + screen lip
  ③ 背面圆形摄像头开孔 + 保护环 + 闪光灯开孔 / Circular camera cutout + ring + flash
  ④ 右侧音量键 + 电源键开孔 / Right-side button cutouts
  ⑤ 底部 USB-C + 扬声器 + SIM 开孔 / Bottom port cutouts
"""

from build123d import *
import os

# ===== 手机机身尺寸（建模基准）/ Phone body dimensions =====
PHONE_L = 160.26      # 长度 Y轴 / length Y-axis
PHONE_W = 74.95       # 宽度 X轴 / width X-axis
PHONE_T = 8.39        # 厚度 Z轴 / thickness Z-axis
PHONE_R = 9.0         # 竖边圆角 / corner radius

# ===== 手机壳通用参数 / Case common parameters =====
GAP       = 0.3       # 配合间隙（单侧）/ fitting clearance per side
HOLE_MRG  = 0.5       # 开孔余量（单侧）/ hole margin per side
LIP_INSET = 1.5       # 唇边内扣量（单侧）/ lip inward grip per side

# ===== 摄像头模组开孔（圆形「风暴眼」，左上）=====
# Camera module cutout (circular "storm eye", upper-left)
CAM_D     = 35.0      # 模组外径（照片提取35.5→35）/ module outer diameter (photo: 35.5)
CAM_CX    = 14.0      # 背面左偏（照片提取13.6→14）/ back-view left (photo: 13.6)
CAM_CY    = 60.0      # 中心Y偏移（照片提取59.5→60）/ center Y offset (photo: 59.5)
CAM_BUMP  = 2.5       # 摄像头凸起高度 / camera bump height

# 闪光灯（圆环外上方）/ Flash (above camera circle)
FLASH_DX  = -29.0     # 闪光灯距摄像头中心（照片提取-29.2→-29）/ flash from cam center (photo: -29.2)
FLASH_DY  = -2.0      # 闪光灯微偏下（照片提取-2.0）/ flash slightly below (photo: -2.0)
FLASH_L   = 12.0      # 闪光灯长度（照片提取12.5→12）/ flash length (photo: 12.5)
FLASH_W   = 4.5       # 闪光灯宽度（照片提取4.6→4.5）/ flash width (photo: 4.6)

# ===== 右侧按键开孔（图片校正位置）/ Right-side button cutouts =====
VOL_LEN   = 24.0      # 音量键开孔长度 / volume button cutout length
VOL_DY    = 38.0      # 音量键距顶边（侧面照片校正）/ volume from top (side-photo: ~38mm)
PWR_LEN   = 12.0      # 电源键开孔长度 / power button cutout length
PWR_DY    = 65.0      # 电源键距顶边（侧面照片校正）/ power from top (side-photo: ~65mm)
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

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)


def build_case(wall_t: float, lip_h: float, shell_r: float, airbag: float = 0.0):
    """
    构建 K80 Pro 手机壳 / Build K80 Pro phone case

    Args:
        wall_t:  壁厚 / wall thickness
        lip_h:   屏幕包裹高度 / screen lip height
        shell_r: 外壳底面倒圆 / outer shell bottom fillet radius
        airbag:  四角气囊加厚（0=无）/ corner airbag extra (0=none)
    """
    # 内腔 = 手机 + 间隙 / cavity = phone + gap
    cav_w = PHONE_W + GAP * 2
    cav_l = PHONE_L + GAP * 2
    cav_t = PHONE_T + GAP
    cav_r = PHONE_R + GAP

    # 外壳 = 内腔 + 壁厚 / outer = cavity + wall
    out_w = cav_w + wall_t * 2
    out_l = cav_l + wall_t * 2
    out_t = cav_t + wall_t
    out_r = cav_r + wall_t

    # Z 布局：z=0 壳底外表面，z=wall_t 内底面（手机背面贴此），顶面 z=out_t+lip_h
    # Z layout: z=0 outer bottom, z=wall_t inner bottom, top z=out_t+lip_h

    # ── ① 外壳主体 / Outer shell ──
    with BuildPart() as outer:
        with BuildSketch(Plane.XY):
            RectangleRounded(out_w, out_l, radius=out_r)
        extrude(amount=out_t + lip_h)
    outer_solid = outer.part
    result = outer_solid

    # ── 内腔挖空（分两层：手机体腔 + 屏幕开口）/ Hollow out (2-step: body + screen) ──
    # 第一层：手机体腔（完整尺寸，从内底到手机屏幕面）
    # Layer 1: body cavity (full size, from inner bottom to phone screen level)
    with BuildPart() as body_cav:
        with BuildSketch(Plane.XY.offset(wall_t)):
            RectangleRounded(cav_w, cav_l, radius=cav_r)
        extrude(amount=cav_t)
    result = result - body_cav.part

    # 第二层：屏幕开口（内缩 LIP_INSET，形成卡扣唇边）
    # Layer 2: screen opening (inset by LIP_INSET, creates grip lip)
    screen_w = cav_w - LIP_INSET * 2
    screen_l = cav_l - LIP_INSET * 2
    screen_r = max(cav_r - LIP_INSET, 1.0)
    with BuildPart() as screen_cav:
        with BuildSketch(Plane.XY.offset(wall_t + cav_t - 0.1)):
            RectangleRounded(screen_w, screen_l, radius=screen_r)
        extrude(amount=lip_h + 1.1)
    result = result - screen_cav.part

    # ── 底面边缘倒圆 / Bottom edge fillet ──
    try:
        bot_face = result.faces().sort_by(Axis.Z)[0]
        result = fillet(result, bot_face.edges(), radius=shell_r)
    except Exception:
        pass

    # ── 内壁唇边倒圆 / Inner lip fillet ──
    try:
        top_face = result.faces().sort_by(Axis.Z)[-1]
        inner_edges = [e for e in top_face.edges()
                       if e.center().X**2 + e.center().Y**2 < (out_w / 2) ** 2]
        if inner_edges:
            result = fillet(result, inner_edges, radius=0.3)
    except Exception:
        pass

    # ── ② 背面圆形摄像头开孔（贯穿底壁）/ Circular camera cutout (through bottom wall) ──
    cam_cut_r = CAM_D / 2 + HOLE_MRG
    cam_cut = Pos(CAM_CX, CAM_CY, wall_t / 2) * Cylinder(
        radius=cam_cut_r, height=wall_t + 2.0)
    result = result - cam_cut

    # ── 闪光灯开孔（横向药丸，长轴X方向）/ Flash cutout (horizontal pill, long axis = X) ──
    flash_x = CAM_CX + FLASH_DX
    flash_y = CAM_CY + FLASH_DY
    flash_cut_w = FLASH_L + HOLE_MRG * 2  # X 方向（长边）/ X-axis (long side)
    flash_cut_h = FLASH_W + HOLE_MRG * 2  # Y 方向（短边）/ Y-axis (short side)
    flash_r = min(flash_cut_w, flash_cut_h) / 2 - 0.1
    with BuildPart() as flash_cut:
        with BuildSketch(Plane.XY.offset(wall_t / 2 - (wall_t + 2.0) / 2)):
            with Locations([(flash_x, flash_y)]):
                RectangleRounded(flash_cut_w, flash_cut_h, radius=flash_r)
        extrude(amount=wall_t + 2.0)
    result = result - flash_cut.part

    # ── 摄像头保护环（圆形，向-Z凸出）/ Circular camera protection ring ──
    ring_wall = 1.0
    ring_h = CAM_BUMP + 0.5
    ring_outer_r = cam_cut_r + ring_wall
    ring_outer = Pos(CAM_CX, CAM_CY, -ring_h / 2) * Cylinder(
        radius=ring_outer_r, height=ring_h)
    ring_inner = Pos(CAM_CX, CAM_CY, -ring_h / 2 - 0.05) * Cylinder(
        radius=cam_cut_r, height=ring_h + 0.1)
    result = result + (ring_outer - ring_inner)

    # ── ③ 右侧按键开孔 / Right-side button cutouts ──
    btn_x = out_w / 2 - wall_t / 2
    btn_z = wall_t + cav_t / 2

    vol_y = out_l / 2 - VOL_DY - VOL_LEN / 2
    vol_cut = Pos(btn_x, vol_y, btn_z) * Box(wall_t + 2.0, VOL_LEN, BTN_H)
    result = result - vol_cut

    pwr_y = out_l / 2 - PWR_DY - PWR_LEN / 2
    pwr_cut = Pos(btn_x, pwr_y, btn_z) * Box(wall_t + 2.0, PWR_LEN, BTN_H)
    result = result - pwr_cut

    # ── ④ 底部开孔（胶囊/圆角形状）/ Bottom port cutouts (capsule/rounded) ──
    bot_z = wall_t + cav_t / 2
    btm_plane = Plane(
        origin=(0, -out_l / 2 - 0.5, bot_z),
        x_dir=(1, 0, 0),
        z_dir=(0, 1, 0),
    )

    # USB-C 胶囊形 / USB-C capsule shape
    usbc_r = USBC_H / 2 - 0.1
    with BuildPart() as usbc_cut:
        with BuildSketch(btm_plane):
            RectangleRounded(USBC_W, USBC_H, radius=usbc_r)
        extrude(amount=wall_t + 2.0)
    result = result - usbc_cut.part

    # 扬声器圆角矩形 / Speaker rounded rectangle
    spk_r = SPK_H / 2 - 0.1
    with BuildPart() as spk_cut:
        with BuildSketch(btm_plane):
            with Locations([(SPK_CX, 0)]):
                RectangleRounded(SPK_W, SPK_H, radius=spk_r)
        extrude(amount=wall_t + 2.0)
    result = result - spk_cut.part

    # SIM 卡槽圆角矩形 / SIM tray rounded rectangle
    sim_r = SIM_H / 2 - 0.1
    with BuildPart() as sim_cut:
        with BuildSketch(btm_plane):
            with Locations([(SIM_CX, 0)]):
                RectangleRounded(SIM_W, SIM_H, radius=sim_r)
        extrude(amount=wall_t + 2.0)
    result = result - sim_cut.part

    # ── ⑤ V3 四角气囊 / Corner airbag (V3 only) ──
    if airbag > 0:
        for sx, sy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            cx = sx * (out_w / 2 - out_r)
            cy = sy * (out_l / 2 - out_r)
            bump = Pos(cx, cy, (out_t + lip_h) / 2) * Cylinder(
                radius=out_r + airbag, height=out_t + lip_h)
            result = result + (bump - outer_solid)

    return result


# ===== 三变体 / 3 variants =====
variant_params = {
    "V1_slim":     (1.2, 1.0, 1.5, 0.0),
    "V2_standard": (1.5, 1.5, 2.0, 0.0),
    "V3_rugged":   (2.0, 2.0, 3.0, 1.0),
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

    assert bb.size.Y > PHONE_L, f"{label}: Y too short ({bb.size.Y:.2f})"
    assert bb.size.X > PHONE_W, f"{label}: X too narrow ({bb.size.X:.2f})"
    assert n_solids == 1, f"{label}: expected 1 solid, got {n_solids}"
    results[label] = solid

v1 = results["V1_slim"]
v2 = results["V2_standard"]
v3 = results["V3_rugged"]

# ===== STEP 导出 + 重导入验证（V2）/ Export + reimport (V2) =====
step_path = os.path.join(output_dir, "redmi_k80_pro_case_V2.step")
export_step(v2, step_path)
ri = import_step(step_path)
vd = abs(ri.volume - v2.volume) / v2.volume
print(f"STEP re-import deviation: {vd:.6%}")
assert vd < 0.001, f"STEP precision loss: {vd:.4%}"
print("✅ Layer 1+2+3 passed")

# ===== 三变体并排 / Side-by-side =====
offset_x = max(s.bounding_box().size.X for s in results.values()) * 1.6
v2_show = v2.move(Location((offset_x, 0, 0)))
v3_show = v3.move(Location((offset_x * 2, 0, 0)))

# ===== OCP 预览 / OCP preview =====
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
        # TOP = 俯视屏幕面（看唇边卡扣）/ top-down screen face (grip lip visible)
        # BOTTOM = 仰视背面（摄像头/闪光灯）/ bottom-up back face (camera/flash)
        # FRONT = 正视底端短边（USB-C/扬声器/SIM）/ front view of bottom edge
        # BACK = 正视顶端短边 / back view of top edge
        for cam_label, cam in [("ISO", Camera.ISO), ("TOP", Camera.TOP),
                                ("BOTTOM", Camera.BOTTOM), ("FRONT", Camera.FRONT),
                                ("BACK", Camera.BACK)]:
            show(v2, names=["redmi_k80_pro_case"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"k80_pro_case_{cam_label}.png"))
            print(f"Screenshot: k80_pro_case_{cam_label}.png ✓")
        # 正确背面视角（Rz180 + BOTTOM = USB朝下，摄像头左上）
        # Proper back view (Rz180 + BOTTOM = USB at bottom, camera upper-left)
        v2_back = v2.rotate(Axis.Z, 180)
        show(v2_back, names=["redmi_k80_pro_case_back"], reset_camera=Camera.BOTTOM)
        time.sleep(0.8)
        save_screenshot(os.path.join(output_dir, "k80_pro_case_BACK_PROPER.png"))
        print("Screenshot: k80_pro_case_BACK_PROPER.png ✓")
        show(v1, v2_show, v3_show,
             names=["V1_slim", "V2_standard", "V3_rugged"],
             colors=["steelblue", "orange", "seagreen"],
             reset_camera=Camera.ISO)
        print(f"OCP Viewer: 3变体并排预览已打开 port={active_port}")
    else:
        print("OCP Viewer: 未检测到 Viewer，请启动 OCP CAD Viewer 扩展")
except Exception as e:
    print(f"OCP preview skipped: {e}")

print(f"\n✅ 13-redmi-k80-pro case 完成\n   推荐 STEP: {step_path}")
