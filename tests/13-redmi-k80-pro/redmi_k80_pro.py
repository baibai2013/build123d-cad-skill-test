"""
13-redmi-k80-pro — Redmi K80 Pro 外形参考模型（v2 — 图片对照精建）
参考图片：references/redmi-k80-pro/images/ (GSMArena 官方产品图 × 3)
参数来源：references/redmi-k80-pro/params.md

特征清单：
  ① 机身直板 + 大 R 圆角 + Z 方向边缘倒圆
  ② 正面屏幕凹槽 + 前摄挖孔
  ③ 背面圆形摄像头模组（铝环凸起 + 3 镜头凹坑 + 闪光灯）
  ④ 右侧音量键 + 电源键凸起
  ⑤ 底部 USB-C 开口 + 扬声器格栅 + SIM 槽
"""

from build123d import *
import os, math

# ===== 机身总体 =====
L       = 160.26
W       = 74.95
T       = 8.39

# ===== 屏幕 =====
scr_w   = 72.0
scr_h   = 152.0
scr_d   = 0.15
scr_corner_r = 5.0
fc_r    = 1.8
fc_dy   = 5.0

# ===== 摄像头模组（v3 图片校正）=====
cam_D       = 34.0
cam_bump    = 2.5
cam_cx      = -16.0
cam_cy      = 60.0
main_r      = 7.2     # 主摄半径 ↑ 填满圆环
tele_r      = 6.2     # 长焦半径 ↑
ultra_r     = 5.2     # 超广角半径 ↑
lens_pcd    = 10.5    # 镜头中心到圆心 ↑ 更分散
lens_depth  = 1.0
flash_l     = 7.0
flash_w     = 2.5
flash_dx    = 2.0     # 闪光灯 X 偏移：几乎正上方，仅微偏右
flash_dy    = 21.0    # 闪光灯 Y 偏移：圆环外上方（半径17+间隙4=21）

# ===== 侧面按键（v3 图片校正：下移）=====
vol_len     = 22.0
vol_dy      = 55.0    # 距顶边 ↑ 约 34% 处（图片对照）
pwr_len     = 10.0
pwr_dy      = 83.0    # 电源键跟随下移
btn_protrude = 0.5
btn_w       = 2.5
btn_t       = 1.0

# ===== 底部开孔 =====
usbc_w      = 9.0
usbc_h      = 3.2
usbc_r      = 1.5
spk_w       = 14.0
spk_h       = 1.8
spk_cx      = 18.0
sim_w       = 10.0
sim_h       = 1.5
sim_cx      = -18.0

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)


def build_phone(corner_r: float, bump_h: float, main_radius: float):
    """构建完整手机外形（Algebra + Builder 混合）。"""
    tele_radius = main_radius - 1.0
    ultra_radius = main_radius - 1.75
    edge_r = min(1.5, corner_r * 0.4)

    # ── ① 机身主体 ──
    with BuildPart() as body:
        Box(W, L, T)
        fillet(body.edges().filter_by(Axis.Z), radius=corner_r)
        top_edges = body.faces().sort_by(Axis.Z)[-1].edges()
        bot_edges = body.faces().sort_by(Axis.Z)[0].edges()
        fillet(top_edges, radius=edge_r)
        fillet(bot_edges, radius=edge_r)
    result = body.part

    # ── ② 正面屏幕凹槽 ──
    scr_box = Pos(0, 0, T / 2) * extrude(
        RectangleRounded(scr_w, scr_h, radius=scr_corner_r),
        amount=-scr_d,
    )
    result = result - scr_box

    # 前摄挖孔（顶部居中）
    fc_y = L / 2 - fc_dy
    fc_hole = Pos(0, fc_y, T / 2) * extrude(Circle(fc_r), amount=-2.0)
    result = result - fc_hole

    # ── ③ 背面圆形摄像头模组 ──
    cam_ring_r = cam_D / 2
    cam_z = -T / 2 - bump_h / 2
    cam_bump_solid = Pos(cam_cx, cam_cy, cam_z) * Cylinder(
        radius=cam_ring_r, height=bump_h
    )
    result = result + cam_bump_solid

    # 倒圆（模组底面边缘）
    try:
        bump_face = result.faces().sort_by(Axis.Z)[0]
        circ_edges = bump_face.edges().filter_by(GeomType.CIRCLE)
        if len(circ_edges) > 0:
            outermost = circ_edges.sort_by(SortBy.LENGTH)[-1]
            result = fillet(result, [outermost], radius=0.6)
    except Exception:
        pass

    # 三镜头凹坑（v3 校正：左二右一 — 图片对照）
    # 主摄=左上(120°)  长焦=左下(240°)  超广角=右中(350°)
    angle_main  = math.radians(120)
    angle_tele  = math.radians(240)
    angle_ultra = math.radians(350)
    lens_z_top = -T / 2 - bump_h
    for ang, r in [(angle_main, main_radius), (angle_tele, tele_radius), (angle_ultra, ultra_radius)]:
        lx = cam_cx + lens_pcd * math.cos(ang)
        ly = cam_cy + lens_pcd * math.sin(ang)
        lens_hole = Pos(lx, ly, lens_z_top + lens_depth / 2) * Cylinder(
            radius=r, height=lens_depth + 0.01
        )
        result = result - lens_hole

    # 闪光灯凹槽
    fx = cam_cx + flash_dx
    fy = cam_cy + flash_dy
    flash_slot = Pos(fx, fy, lens_z_top + 0.25) * Box(flash_w, flash_l, 0.5)
    result = result - flash_slot

    # ── ④ 右侧按键 ──
    btn_x = W / 2 + btn_protrude / 2
    vol_y = L / 2 - vol_dy - vol_len / 2
    pwr_y = L / 2 - pwr_dy - pwr_len / 2
    vol_btn = Pos(btn_x, vol_y, 0) * Box(btn_protrude, vol_len, btn_w)
    pwr_btn = Pos(btn_x, pwr_y, 0) * Box(btn_protrude, pwr_len, btn_w)
    result = result + vol_btn + pwr_btn

    # ── ⑤ 底部开孔 ──
    bot_y = -L / 2
    usbc_cut = Pos(0, bot_y, 0) * Box(usbc_w, 4.0, usbc_h)
    result = result - usbc_cut

    spk_cut = Pos(spk_cx, bot_y, 0) * Box(spk_w, 3.0, spk_h)
    result = result - spk_cut

    sim_cut = Pos(sim_cx, bot_y, 0) * Box(sim_w, 3.0, sim_h)
    result = result - sim_cut

    return result


# ===== 三变体 =====
variants = {
    "V1_conservative": (7.5,  2.0, 6.8),
    "V2_reference":    (9.0,  2.5, 7.2),
    "V3_reinforced":   (10.5, 3.0, 7.6),
}

results = {}
for label, (cr, bh, mr) in variants.items():
    solid = build_phone(cr, bh, mr)
    assert solid is not None, f"{label}: solid is None"
    assert solid.is_valid, f"{label}: BRep invalid"
    bb = solid.bounding_box()
    vol = solid.volume
    n_solids = len(solid.solids())
    print(f"{label}: bbox {bb.size.X:.2f}×{bb.size.Y:.2f}×{bb.size.Z:.2f} mm  vol={vol:.0f} mm³  solids={n_solids}")
    assert abs(bb.size.Y - L) < 3.0, f"{label}: Y span {bb.size.Y}"
    assert bb.size.Z < T + bh + 5.0, f"{label}: Z span too large {bb.size.Z}"
    results[label] = solid

v1 = results["V1_conservative"]
v2 = results["V2_reference"]
v3 = results["V3_reinforced"]

# ===== STEP 导出 V2 =====
step_path = os.path.join(output_dir, "redmi_k80_pro_V2.step")
export_step(v2, step_path)
ri = import_step(step_path)
vd = abs(ri.volume - v2.volume) / v2.volume
print(f"STEP re-import deviation: {vd:.6%}")
assert vd < 0.001, f"STEP precision loss: {vd:.4%}"
print("✅ Layer 1+2+3 passed")

# ===== 并排展示 =====
offset_x = max(s.bounding_box().size.X for s in results.values()) * 1.6
v2_m = v2.move(Location((offset_x, 0, 0)))
v3_m = v3.move(Location((offset_x * 2, 0, 0)))

# ===== OCP =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        show(v1, v2_m, v3_m,
             names=["V1_conservative", "V2_reference", "V3_reinforced"],
             colors=["steelblue", "orange", "seagreen"],
             reset_camera=Camera.ISO)
        time.sleep(1.0)
        for cam_label, cam in [("ISO", Camera.ISO), ("FRONT", Camera.FRONT), ("BACK", Camera.BACK), ("TOP", Camera.TOP), ("BOTTOM", Camera.BOTTOM)]:
            show(v2, names=["redmi_k80_pro"], reset_camera=cam)
            time.sleep(0.8)
            save_screenshot(os.path.join(output_dir, f"redmi_k80_pro_{cam_label}.png"))
            print(f"Screenshot: redmi_k80_pro_{cam_label}.png ✓")
        print(f"OCP Viewer: 预览已打开 port={active_port}")
    else:
        print("OCP Viewer: 未检测到 Viewer")
except Exception as e:
    print(f"OCP preview skipped: {e}")

print(f"\n✅ 13-redmi-k80-pro v2 完成\n   推荐 STEP: {step_path}")
