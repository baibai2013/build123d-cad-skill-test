"""
Test 22 — ESP32-S3-DevKitC-1 外壳建模
ESP32-S3-DevKitC-1 Enclosure (FDM 3D Printing)

部件 / Parts:
  - bottom_shell: 底壳（含 PCB 容纳腔、4 角低台、USB 开孔、snap-fit 凹槽）
                  Bottom shell with PCB pocket, corner posts, USB cutouts, snap-fit grooves
  - top_lid:      盖板（抽壳、按键压柱、LED 透光孔、散热槽、4 角压舌、snap-fit 悬臂）
                  Top lid with hollowed body, plungers, LED window, vents, corner tongues, clips

设计方案 / Design: 盖板夹持式（方案 A）— PCB 放底壳低台，盖板压舌夹紧
                   Lid-clamp approach — PCB sits on corner posts, lid tongues clamp top face

坐标系 / Coordinate system:
  世界原点 = 底壳外底面几何中心（center of outer bottom face）
  X = PCB 长边方向 / X = PCB long axis
  Y = PCB 短边方向 / Y = PCB short axis
  Z = 垂直向上 / Z = up

来源 / Sources:
  references/esp32-s3-devkitc-1/params.md (v2, Dave Cowden review)
  tests/22-esp32-s3-devkitc-enclosure/contract.yaml
"""

from build123d import *
import os

# ============================================================
# 全局参数常量 / Global parameter constants
# ============================================================

# PCB 事实尺寸（官方 DXF 数据）/ PCB facts (from official DXF)
PCB_L = 62.74   # mm，PCB 长（X 方向）/ PCB length along X
PCB_W = 25.40   # mm，PCB 宽（Y 方向）/ PCB width along Y
PCB_T =  1.60   # mm，PCB 厚（FR-4 标准）/ PCB thickness (FR-4 standard)

# PCB 本地坐标 — 特征中心点（来自 DXF PLACEMENT）
# PCB local coordinates — feature centers (from DXF PLACEMENT)
J2_LOCAL  = (6.00, 3.66)    # USB-to-UART 连接器中心 / USB-to-UART center
J4_LOCAL  = (19.40, 3.66)   # USB OTG 连接器中心 / USB OTG center
SW1_LOCAL = (6.76, 13.79)   # Boot 按键中心 / Boot button center
SW2_LOCAL = (17.17, 13.92)  # Reset 按键中心 / Reset button center
LED_LOCAL = (5.08, 31.60)   # RGB LED 中心 / RGB LED center

# 连接器物理尺寸 / Connector physical dimensions
USB_CONN_W     =  8.22  # mm，Micro-USB 连接器宽度 / connector width
USB_CONN_H     =  5.27  # mm，Micro-USB 连接器高度 / connector height
USB_CONN_PROTRUDE = 3.0 # mm，连接器 PCB 上方突出高度 / protrusion above PCB top
MODULE_H       =  3.1   # mm，WROOM-1 模块高度 / module height above PCB top
HEADER_TOP_H   =  8.5   # mm，排针 PCB 上方长度（焊接场景）/ header above PCB (soldered)

# 外壳设计决策 / Enclosure design decisions
WALL_T      = 2.0   # mm，壁厚 / wall thickness
BASE_T      = 2.0   # mm，底板厚 / base plate thickness
LID_T       = 2.0   # mm，顶罩厚 / lid plate thickness
GAP         = 0.4   # mm，PCB 装配间隙（单侧）/ PCB assembly clearance per side
PCB_STANDOFF = 4.0  # mm，PCB 悬空间距（容纳背面排针 3.5mm + 余量）/ PCB standoff height

# 盖板净空：焊排针场景 / Lid clearance: soldered headers scenario
# max(MODULE_H=3.1, HEADER_TOP_H=8.5) + 0.5 余量 = 9.0mm
LID_CLEARANCE = 9.0  # mm

# 散热槽参数 / Vent slot parameters
VENT_W     = 2.0    # mm，单条槽宽 / single vent width
VENT_L     = 20.0   # mm，单条槽长 / single vent length
VENT_COUNT = 3      # 条数 / count
VENT_PITCH = 4.0    # mm，中心间距 / center pitch
VENT_CX    = 15.0   # mm，散热槽组中心 X（模块上方，避开 LED）/ vent group center X

# USB 开孔尺寸(胶囊形状,USB-C 视觉)/ USB cutout (capsule shape, USB-C aesthetic)
# SlotOverall(长轴, 短轴): 10mm 水平 × 5mm 竖直,端部 R2.5mm 半圆
# SlotOverall(long, short): 10mm horizontal × 5mm vertical, ends R2.5mm
USB_CUT_W  = 10.0   # mm,长轴(水平,世界 X 方向)/ long axis (horizontal, world X)
USB_CUT_H  =  5.0   # mm,短轴(竖直,世界 Z 方向)/ short axis (vertical, world Z)

# 底面 M3 固定孔(外壳整体固定到机架)/ M3 mounting holes on bottom face (mount to chassis)
# 位置 (±22, ±10) 避开 4 角低台(低台在 ±29.87, ±11.20)
# Positions (±22, ±10) clear of 4 corner posts (at ±29.87, ±11.20)
M3_HOLE_R    = 1.6    # mm,M3 通孔半径(公差余量)/ M3 clearance hole radius
M3_HOLE_X    = 22.0   # mm,|X| 位置 / X offset magnitude
M3_HOLE_Y    = 10.0   # mm,|Y| 位置 / Y offset magnitude

# Snap-fit 卡扣参数 / Snap-fit clip parameters
CLIP_W           = 6.0   # mm，卡扣宽度 / clip width
CLIP_CANTILEVER  = 6.0   # mm，悬臂长 / cantilever length
CLIP_HEAD_T      = 0.8   # mm，卡扣头凸出量 / clip head protrusion
CLIP_CHAMFER     = 0.4   # mm，导角 / lead-in chamfer
GROOVE_W         = 6.2   # mm，底壳凹槽宽 / bottom groove width
GROOVE_D         = 0.9   # mm，底壳凹槽深 / bottom groove depth

# 压舌参数 / Corner tongue parameters
TONGUE_SIZE    = 3.0   # mm，压舌边长 / tongue side length
TONGUE_PROTRUDE = 0.5  # mm，压舌向下凸出量 / tongue protrusion downward

# 低台参数 / Corner post parameters
POST_SIZE = 3.0  # mm，低台边长 / corner post side length

# ============================================================
# 派生参数 / Derived parameters
# ============================================================

# 外壳外形尺寸 / Shell outer dimensions
SHELL_L = PCB_L + 2 * (WALL_T + GAP)   # = 62.74 + 2×2.4 = 67.54 mm
SHELL_W = PCB_W + 2 * (WALL_T + GAP)   # = 25.40 + 2×2.4 = 30.20 mm

# 高度分解 / Height breakdown
BOTTOM_H = BASE_T + PCB_STANDOFF + PCB_T   # 底壳总高 / bottom shell total height
                                             # = 2.0 + 4.0 + 1.6 = 7.6 mm
LID_H    = LID_CLEARANCE + LID_T            # 盖板总高 / lid total height
                                             # = 9.0 + 2.0 = 11.0 mm
SHELL_T  = BOTTOM_H + LID_H - PCB_T        # 整体总高 / total assembly height
                                             # = 7.6 + 11.0 - 1.6 = 17.0 mm

# PCB 容纳腔内形尺寸（比 PCB 每侧大 GAP）
# PCB pocket inner dimensions (PCB + clearance each side)
POCKET_L = PCB_L + 2 * GAP   # = 63.54 mm
POCKET_W = PCB_W + 2 * GAP   # = 26.20 mm

# 注：BOTTOM_H 外壳参照外底面中心（Z=0）建模，外盒从 -BOTTOM_H/2 到 +BOTTOM_H/2（align CENTER）
# Note: BOTTOM_H box centered at origin; externally bottom face sits at Z = -BOTTOM_H/2

# ============================================================
# 坐标变换辅助函数 / Coordinate transform helper
# ============================================================

def world_from_pcb(local_xy):
    """
    将 PCB 本地坐标 (local_x, local_y) 转换为世界坐标 Location。
    Convert PCB local (local_x, local_y) to world Location.

    世界坐标系原点 = 底壳外底面几何中心（外盒 Z 向下最低面中心）。
    World origin = center of outer bottom face of bottom shell.

    底壳外底面 Z = -BOTTOM_H/2（因为底壳 Box 在原点居中）
    PCB 底面 Z   = -BOTTOM_H/2 + BASE_T + PCB_STANDOFF
                 = -BOTTOM_H/2 + 6.0
    PCB 本地 (0,0) 在 XY 平面中心: (-PCB_L/2, -PCB_W/2)

    Z 参考：-BOTTOM_H/2 + BASE_T + PCB_STANDOFF
           = -3.8 + 6.0 = 2.2  (PCB 底面 Z)
    """
    local_x, local_y = local_xy
    # PCB 世界原点（PCB 本地 (0,0) 的世界坐标，取 PCB 底面中点高度 Z）
    # PCB world origin: PCB local (0,0) in world coords at PCB bottom face Z
    pcb_origin_x = -PCB_L / 2                              # = -31.37
    pcb_origin_y = -PCB_W / 2                              # = -12.70
    pcb_origin_z = -BOTTOM_H / 2 + BASE_T + PCB_STANDOFF   # = -3.8 + 6.0 = 2.2
    return Location((pcb_origin_x + local_x,
                     pcb_origin_y + local_y,
                     pcb_origin_z))


# ============================================================
# 输出目录 / Output directory
# ============================================================
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

# ============================================================
# Part 1: 底壳 / Bottom Shell
# ============================================================
print("正在建模底壳 / Building bottom shell...")

with BuildPart() as bottom_part:

    # ── 1a. 底壳主体实体 / Bottom shell solid box ──────────────────
    # 外形 Box，在原点居中（底壳外底面 Z = -BOTTOM_H/2）
    # Outer box centered at origin (bottom face Z = -BOTTOM_H/2)
    Box(SHELL_L, SHELL_W, BOTTOM_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    # ── 1b. 内腔（PCB 容纳区）减材 / Internal cavity subtract ─────
    # 从顶面向下挖腔，腔深 = POCKET 深度（PCB_STANDOFF + PCB_T，留底板厚度 BASE_T）
    # Cut cavity from top face downward; depth = PCB_STANDOFF + PCB_T (leaving BASE_T floor)
    cavity_depth = PCB_STANDOFF + PCB_T   # = 5.6 mm

    top_face = bottom_part.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top_face):
        # 内腔平面尺寸 / Cavity plan dimensions
        # 宽度 = SHELL_L - 2*WALL_T（两侧各留 WALL_T 壁厚）
        inner_L = SHELL_L - 2 * WALL_T   # = 63.54 mm (含 GAP)
        inner_W = SHELL_W - 2 * WALL_T   # = 26.20 mm (含 GAP)
        Rectangle(inner_L, inner_W)
    extrude(amount=-cavity_depth, mode=Mode.SUBTRACT)

    # ── 1c. 4 角低台（PCB 夹持机构）/ Corner posts for PCB support ─
    # 底壳内底面向上凸起 PCB_STANDOFF（4mm），3×3mm 方块
    # Posts rise from inner floor by PCB_STANDOFF; 3×3mm square footprint
    # 低台顶面 Z = -BOTTOM_H/2 + BASE_T + PCB_STANDOFF = 2.2 (PCB 底面高度)
    inner_floor_z = -BOTTOM_H / 2 + BASE_T  # = -1.8 mm (内底面 Z)

    # PCB 4 角在世界坐标系中的位置（本地 4 角内缩 1.5mm）
    # PCB corners in world coords (inset 1.5mm from PCB local corners)
    # PCB 本地 4 角: (0,0), (PCB_L,0), (0,PCB_W), (PCB_L,PCB_W)
    # 内缩后: (1.5,1.5), (PCB_L-1.5,1.5), (1.5,PCB_W-1.5), (PCB_L-1.5,PCB_W-1.5)
    # 世界 X: pcb_origin_x + local_x_inset / World X: pcb_origin_x + local_x_inset
    pcb_ox = -PCB_L / 2   # = -31.37
    pcb_oy = -PCB_W / 2   # = -12.70

    post_positions = [
        (pcb_ox + 1.5,         pcb_oy + 1.5),          # 左前 / front-left
        (pcb_ox + PCB_L - 1.5, pcb_oy + 1.5),          # 右前 / front-right
        (pcb_ox + 1.5,         pcb_oy + PCB_W - 1.5),  # 左后 / rear-left
        (pcb_ox + PCB_L - 1.5, pcb_oy + PCB_W - 1.5),  # 右后 / rear-right
    ]

    # 在内底面建草图，extrude 向上 PCB_STANDOFF
    # Sketch on inner floor, extrude upward by PCB_STANDOFF
    inner_floor = bottom_part.faces().sort_by(Axis.Z)[0]  # 内底面（最低面）
    with BuildSketch(Plane.XY.offset(inner_floor_z)):
        for (px, py) in post_positions:
            with Locations(Location((px, py, 0))):
                Rectangle(POST_SIZE, POST_SIZE)
    extrude(amount=PCB_STANDOFF)

    # ── 1d. Snap-fit 凹槽（左右短边）/ Snap-fit grooves on short sides ─
    # (注：USB 开孔在盖板前壁，因 USB 连接器完全在盖板区域内)
    # (Note: USB cutouts are in the LID front wall; connectors protrude above PCB=bottom-shell top)
    # 底壳左右侧壁（X = ±SHELL_L/2）各在中部挖一个凹槽，供盖板卡扣嵌入
    # Groove on each short-side wall (X = ±SHELL_L/2) for lid clip engagement
    # 凹槽参数 / Groove dims: width GROOVE_W, depth GROOVE_D, height = CLIP_HEAD_T + 0.5
    groove_h = CLIP_HEAD_T + 0.5    # = 1.3 mm，凹槽高度（Z 方向）/ groove height

    # 凹槽中心 Z（在底壳顶端附近，距顶面 LID_T/2 + gap）
    # Groove center Z (near top of bottom shell, for clip alignment at assembly)
    # 当盖板对齐后，卡扣头中心 Z（相对盖板底内面）= CLIP_CANTILEVER = 6mm
    # 对应底壳世界坐标：底壳顶面 Z = BOTTOM_H/2，凹槽从这里向下 LID_T 内壁...
    # 简化：凹槽中心 Z = 底壳顶面 Z - 1.5mm（靠近顶面位置）
    groove_center_z = BOTTOM_H / 2 - 1.5  # ≈ 2.3 mm（底壳顶面下 1.5）

    # 左侧面 / Left face (X negative)
    left_face  = bottom_part.faces().sort_by(Axis.X)[0]
    right_face = bottom_part.faces().sort_by(Axis.X)[-1]

    # 左侧面坐标：sketch (x_sk, y_sk) → world (X_face, y_sk, x_sk)
    # 凹槽位于 world Z=groove_center_z, Y=0 → sketch (groove_center_z, 0)
    # Left face coords: sketch (x_sk, y_sk) -> world (X_face, y_sk, x_sk)
    # Groove at world Z=groove_center_z, Y=0 -> sketch (groove_center_z, 0)
    with BuildSketch(left_face):
        with Locations(Location((groove_center_z, 0, 0))):
            Rectangle(GROOVE_W, groove_h)
    extrude(amount=-GROOVE_D, mode=Mode.SUBTRACT)

    # 右侧面坐标：sketch (x_sk, y_sk) → world (X_face, -y_sk, x_sk)
    # 凹槽位于 world Z=groove_center_z, Y=0 → sketch (groove_center_z, 0)
    # Right face coords: sketch (x_sk, y_sk) -> world (X_face, -y_sk, x_sk)
    with BuildSketch(right_face):
        with Locations(Location((groove_center_z, 0, 0))):
            Rectangle(GROOVE_W, groove_h)
    extrude(amount=-GROOVE_D, mode=Mode.SUBTRACT)

    # ── 1e. 底面 4 角 M3 固定孔 / 4 × M3 mounting holes on outer bottom ─
    # 用于把整个外壳固定到机架 / For mounting the entire enclosure to a chassis
    # 位置 (±22, ±10) 避开 4 角低台(位于 ±29.87, ±11.20)
    # Positions (±22, ±10) clear of the 4 corner posts (at ±29.87, ±11.20)
    # 贯穿底板 BASE_T=2mm,穿出到内腔空气中 / Through BASE_T=2mm floor into cavity air
    outer_bottom = bottom_part.faces().sort_by(Axis.Z)[0]  # 外底面(最低面)/ outer bottom face
    with BuildSketch(outer_bottom):
        with Locations(
            Location(( M3_HOLE_X,  M3_HOLE_Y, 0)),
            Location((-M3_HOLE_X,  M3_HOLE_Y, 0)),
            Location(( M3_HOLE_X, -M3_HOLE_Y, 0)),
            Location((-M3_HOLE_X, -M3_HOLE_Y, 0)),
        ):
            Circle(M3_HOLE_R)
    # 外底面法向 -Z,extrude(amount<0) 沿 +Z 切入实体 / face normal -Z; negative amount cuts into solid
    extrude(amount=-BASE_T, mode=Mode.SUBTRACT)

# 底壳 Part / Bottom shell part object
bottom_shell = bottom_part.part
print(f"  底壳建模完成 / Bottom shell done — valid: {bottom_shell.is_valid}")
print(f"  底壳体积 / Volume: {bottom_shell.volume:.1f} mm³")
print(f"  底壳 BBox / BBox: {bottom_shell.bounding_box()}")

# ============================================================
# Part 2: 盖板 / Top Lid
# ============================================================
print("正在建模盖板 / Building top lid...")

with BuildPart() as lid_part:

    # ── 2a. 盖板主体实体 / Lid solid box ──────────────────────────
    # 盖板建模在其自身局部坐标系中（稍后偏移装配）
    # Lid modeled in its own local coord system (offset for assembly later)
    Box(SHELL_L, SHELL_W, LID_H, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    # ── 2b. 抽壳（开口朝下）/ Hollow out lid (open at bottom) ──────
    # 盖板保留顶面 LID_T 厚度，四周壁厚 WALL_T，底面开口
    # Keep top plate LID_T thick, side walls WALL_T thick, open at bottom
    cavity_inner_L = SHELL_L - 2 * WALL_T  # = 63.54 mm
    cavity_inner_W = SHELL_W - 2 * WALL_T  # = 26.20 mm

    # 从底面（开口面）向内（上）切，深 = LID_H - LID_T（保留顶板）
    # Cut from bottom face inward (upward, negative extrude for -Z normal face)
    # 底面法向 = -Z，amount=-depth 向 +Z 方向切入实体
    lid_inner_depth = LID_H - LID_T  # = 9.0 mm

    bot_face = lid_part.faces().sort_by(Axis.Z)[0]  # 底面（最低面）/ bottom face
    with BuildSketch(bot_face):
        Rectangle(cavity_inner_L, cavity_inner_W)
    extrude(amount=-lid_inner_depth, mode=Mode.SUBTRACT)  # 向上（+Z）切入实体

    # 内顶面 Z（腔体内顶面，保留 LID_T 顶板后的内面）
    # Inner top face Z = LID_H/2 - LID_T (lid local coords)
    # = 5.5 - 2.0 = 3.5 mm
    lid_inner_top_z = LID_H / 2 - LID_T   # = 3.5 mm（局部坐标 / lid local Z）

    # ── 2b2. USB 开孔（前端 Y- 方向壁面）/ USB cutouts in lid front wall ─
    # USB 连接器突出 PCB 顶面（= 底壳顶面）以上，完全在盖板区域内
    # USB connectors protrude above PCB top (= bottom-shell top), entirely in lid zone
    #
    # 盖板局部坐标：底面 Z = -LID_H/2 = -5.5mm，盖板与底壳合体后对齐 PCB 顶面
    # Lid local: bottom face Z = -LID_H/2 = -5.5; aligns with PCB top at assembly
    #
    # USB 连接器中心 Z（盖板局部）：
    #   盖板局部 0 = 盖板中心；底面 = -5.5mm = PCB 顶面（装配对齐）
    #   连接器中心 = PCB 顶面 + USB_CONN_PROTRUDE/2 = 底面 + 1.5mm
    #   → 盖板局部 Z = -LID_H/2 + 1.5 = -5.5 + 1.5 = -4.0 mm
    # USB connector center Z (lid local):
    #   lid bottom = -LID_H/2 = PCB top at assembly
    #   usb center = lid_bottom + USB_CONN_PROTRUDE/2 = -5.5 + 1.5 = -4.0 mm
    usb_center_z_lid = -LID_H / 2 + USB_CONN_PROTRUDE / 2  # = -5.5 + 1.5 = -4.0 mm

    # J2/J4 世界 X（与底壳相同）/ J2/J4 world X (same as bottom shell)
    j2_world_x = pcb_ox + J2_LOCAL[0]   # = -31.37 + 6.00 = -25.37
    j4_world_x = pcb_ox + J4_LOCAL[0]   # = -31.37 + 19.40 = -11.97

    # 盖板前端面（Y 最小面）/ Lid front face (min Y)
    lid_front_face = lid_part.faces().sort_by(Axis.Y)[0]

    # 盖板前端面坐标：sketch (x_sk, y_sk) → world (−y_sk, Y_face, x_sk)
    # 要在 world X=j2_world_x, Z=usb_center_z_lid → sketch (usb_center_z_lid, -j2_world_x)
    # Lid front face: sketch (x_sk, y_sk) -> world (-y_sk, Y_face, x_sk)
    # To reach world X=j2_x, Z=usb_z -> sketch (usb_z, -j2_x)
    #
    # USB-C 胶囊开孔:SlotOverall(long, short) 默认长轴沿 sketch x,
    # 用 rotation=90 让长轴沿 sketch y(= 世界 X,水平方向)
    # USB-C capsule cutout: SlotOverall's long axis is sketch-x by default;
    # rotation=90 turns it to sketch-y (= world X, horizontal)
    with BuildSketch(lid_front_face):
        with Locations(Location((usb_center_z_lid, -j2_world_x, 0))):
            SlotOverall(USB_CUT_W, USB_CUT_H, rotation=90)
        with Locations(Location((usb_center_z_lid, -j4_world_x, 0))):
            SlotOverall(USB_CUT_W, USB_CUT_H, rotation=90)
    extrude(amount=-WALL_T, mode=Mode.SUBTRACT)

    # ── 2c. Boot/Reset 按键压柱 / Button plungers ─────────────────
    # 从盖板内顶面向下凸出，圆柱直径 3mm
    # Cylinders hang down from lid inner top face; d=3mm
    # 压柱高度 = LID_CLEARANCE - 按键顶到 PCB 上表面高度 - 间隙
    # Plunger height = LID_CLEARANCE - button_top_above_pcb - gap_to_button
    button_top_h = 1.5  # mm，贴片按键高度 / SMD button height above PCB
    plunger_gap  = 0.3  # mm，压柱与按键间隙 / plunger to button gap
    plunger_h = LID_CLEARANCE - button_top_h - plunger_gap  # = 9.0-1.5-0.3 = 7.2 mm

    # 按键压柱 XY（在盖板内，与底壳装配后对齐 PCB 按键位置）
    # Plunger XY in lid local coords (aligns with PCB buttons after assembly)
    sw1_world = world_from_pcb(SW1_LOCAL)
    sw2_world = world_from_pcb(SW2_LOCAL)
    sw1_x = sw1_world.position.X   # = -31.37 + 6.76 = -24.61
    sw1_y = sw1_world.position.Y   # = -12.70 + 13.79 = 1.09
    sw2_x = sw2_world.position.X   # = -31.37 + 17.17 = -14.20
    sw2_y = sw2_world.position.Y   # = -12.70 + 13.92 = 1.22

    # 在盖板内顶面建圆形草图，向下（-Z）extrude 压柱
    # Sketch on lid inner top face; extrude downward (-Z) for plungers
    # 内顶面：法向 = -Z，中心 Z ≈ LID_H/2 - LID_T = 3.5mm（lid local）
    # Inner top face: normal = -Z, center Z ≈ LID_H/2 - LID_T (lid local)
    # 用 sort_by(Axis.Z) 按 Z 排序取倒数第二高的水平面（= 内顶面，在顶板下方）
    # Select 2nd-highest horizontal face = inner top face (just below top plate)
    inner_top_face = sorted(
        [f for f in lid_part.faces() if abs(f.normal_at().Z) > 0.9],
        key=lambda f: f.center().Z
    )[-2]   # 第二高水平面 = 内顶面 / 2nd highest horizontal face = inner top

    # 内顶面（法向=-Z）坐标：sketch (x_sk, y_sk) → world (x_sk, -y_sk, Z_face)
    # 要在 world X=sw1_x, Y=sw1_y → sketch (sw1_x, -sw1_y)
    # Inner top face (normal=-Z): sketch (x_sk, y_sk) -> world (x_sk, -y_sk, Z_face)
    # To reach world X=sw1_x, Y=sw1_y -> sketch (sw1_x, -sw1_y)
    with BuildSketch(inner_top_face):
        with Locations(Location((sw1_x, -sw1_y, 0))):
            Circle(radius=1.5)   # d=3.0mm
        with Locations(Location((sw2_x, -sw2_y, 0))):
            Circle(radius=1.5)
    extrude(amount=plunger_h)   # 内顶面法向 = -Z，正量向下凸出压柱

    # ── 2d. LED 透光孔（贯穿顶板）/ LED window through top plate ────
    led_world = world_from_pcb(LED_LOCAL)
    led_x = led_world.position.X   # = -31.37 + 5.08 = -26.29
    led_y = led_world.position.Y   # = -12.70 + 31.60 = 18.90

    top_face_lid = lid_part.faces().sort_by(Axis.Z)[-1]  # 盖板顶面（外）/ lid outer top
    with BuildSketch(top_face_lid):
        with Locations(Location((led_x, led_y, 0))):
            Circle(radius=1.75)   # d=3.5mm
    extrude(amount=-LID_T, mode=Mode.SUBTRACT)

    # ── 2e. 散热槽（顶板 3 条）/ Vent slots in top plate (3x) ──────
    # 平行于 Y 方向，位于模块上方（VENT_CX=15mm），避开 LED 区域（LED_X=-26.3）
    # Parallel to Y axis, centered at VENT_CX on top plate; avoids LED zone
    top_face_lid = lid_part.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top_face_lid):
        for i in range(VENT_COUNT):
            vx = VENT_CX + (i - (VENT_COUNT - 1) / 2) * VENT_PITCH  # X = 11, 15, 19
            with Locations(Location((vx, 0, 0))):
                Rectangle(VENT_W, VENT_L)
    extrude(amount=-LID_T, mode=Mode.SUBTRACT)

    # ── 2f. 4 角压舌（盖板内侧向下凸出 0.5mm）/ Corner tongues ──────
    # 盖板合上后压在 PCB 上表面 4 角，夹紧 PCB
    # When lid closes, tongues press on PCB top face at 4 corners; clamp PCB
    # 压舌从盖板内顶面向下凸出，与底壳低台 XY 对齐
    # Tongues extrude from inner top face downward; XY aligned with bottom corner posts
    # 重新查找内顶面（增加特征后面列表可能变化）
    # Re-find inner top face (face list may change after adding plungers)
    inner_top_face2 = sorted(
        [f for f in lid_part.faces() if abs(f.normal_at().Z) > 0.9],
        key=lambda f: f.center().Z
    )[-2]   # 第二高水平面 = 内顶面
    # 内顶面坐标同压柱：sketch (x_sk, y_sk) → world (x_sk, -y_sk, Z_face)
    # 要在 world (px, py) → sketch (px, -py)
    # Same coord mapping as plungers: to reach world (px, py) -> sketch (px, -py)
    with BuildSketch(inner_top_face2):
        for (px, py) in post_positions:
            with Locations(Location((px, -py, 0))):
                Rectangle(TONGUE_SIZE, TONGUE_SIZE)
    extrude(amount=TONGUE_PROTRUDE)   # 内顶面法向 = -Z，正量向下凸出压舌

    # ── 2g. Snap-fit 卡扣（左右短边外侧）/ Snap-fit clips on short side faces ─
    # 方案：在盖板外侧短边面（X = ±SHELL_L/2）近底部位置向外凸出卡扣头
    # 合盖时卡扣头弹性通过底壳凹槽口，嵌入凹槽，实现锁定
    # Approach: protrude clip heads outward from lid outer short-side faces near bottom
    # When lid closes, clip head snaps past groove lip into bottom shell groove
    #
    # 卡扣头 Z 中心（盖板局部）= 盖板底面 Z + 1.3mm（在底面附近，对齐底壳凹槽）
    # Clip Z center in lid local: near lid bottom face, aligns with bottom shell groove
    clip_z_local = -LID_H / 2 + 1.3   # = -5.5 + 1.3 = -4.2 mm（局部坐标）

    left_face_lid  = lid_part.faces().sort_by(Axis.X)[0]
    right_face_lid = lid_part.faces().sort_by(Axis.X)[-1]

    # 左侧外面（X 最小，法向 -X）建草图，向外（-X 方向）凸出 CLIP_HEAD_T
    # Left outer face (most negative X, normal = -X); extrude outward in -X
    # 注意：BuildSketch 在法向 -X 的面上，extrude(amount=+t) 向 -X 凸出（向外）
    # Note: on face with normal -X, extrude(+t) goes outward in -X direction
    left_face_lid2  = lid_part.faces().sort_by(Axis.X)[0]
    right_face_lid2 = lid_part.faces().sort_by(Axis.X)[-1]

    # 左侧面坐标：sketch (x_sk, y_sk) → world (X_face, y_sk, x_sk)
    # 要在 world Z=clip_z_local, Y=0 → sketch (clip_z_local, 0)
    # Left face: sketch (x_sk, y_sk) -> world (X_face, y_sk, x_sk)
    # To reach world Z=clip_z_local, Y=0 -> sketch (clip_z_local, 0)
    with BuildSketch(left_face_lid2):
        with Locations(Location((clip_z_local, 0, 0))):
            Rectangle(CLIP_HEAD_T + 0.4, CLIP_W)  # sketch: x=Z-size, y=Y-size
    extrude(amount=CLIP_HEAD_T)  # 向外（-X 方向）凸出 clip head

    # 右侧外面（X 最大，法向 +X）建草图，向外（+X 方向）凸出 CLIP_HEAD_T
    # Right outer face (most positive X, normal = +X); extrude outward in +X
    # 右侧面坐标：sketch (x_sk, y_sk) → world (X_face, -y_sk, x_sk)
    # 要在 world Z=clip_z_local, Y=0 → sketch (clip_z_local, 0)
    # Right face: sketch (x_sk, y_sk) -> world (X_face, -y_sk, x_sk)
    with BuildSketch(right_face_lid2):
        with Locations(Location((clip_z_local, 0, 0))):
            Rectangle(CLIP_HEAD_T + 0.4, CLIP_W)
    extrude(amount=CLIP_HEAD_T)  # 向外（+X 方向）凸出 clip head

# 盖板 Part / Lid part object
top_lid = lid_part.part
print(f"  盖板建模完成 / Top lid done — valid: {top_lid.is_valid}")
print(f"  盖板体积 / Volume: {top_lid.volume:.1f} mm³")
print(f"  盖板 BBox / BBox: {top_lid.bounding_box()}")

# ============================================================
# 装配预览位置 / Assembly positioning
# ============================================================
# 盖板平移到底壳上方装配位置
# Translate lid to sit on top of bottom shell
# 底壳顶面 Z = BOTTOM_H/2；盖板底面 Z（局部）= -LID_H/2
# 平移量 dZ = BOTTOM_H/2 + LID_H/2 - PCB_T (PCB 在两者间被夹)
# Translation dZ: align lid bottom with bottom shell top
assembly_offset_z = BOTTOM_H / 2 + LID_H / 2  # = 3.8 + 5.5 = 9.3 mm
lid_part_positioned = lid_part.part.moved(Location((0, 0, assembly_offset_z)))

print(f"\n装配偏移 Z / Assembly offset Z: {assembly_offset_z:.2f} mm")

# ============================================================
# 三层验证 / Three-layer validation
# ============================================================
print("\n===== 三层验证 / Three-layer validation =====")

# ── Layer 1: BRep 几何有效性 / BRep geometry validity ────────
print("Layer 1: BRep is_valid...")
assert bottom_shell.is_valid, "底壳 BRep 无效 / Bottom shell BRep invalid"
assert top_lid.is_valid,      "盖板 BRep 无效 / Top lid BRep invalid"
print("  PASS — 底壳 / bottom_shell is_valid, 盖板 / top_lid is_valid")

# ── Layer 2: 体积范围断言 / Volume range assertions ───────────
print("Layer 2: 体积范围 / Volume range...")
bottom_vol = bottom_shell.volume
lid_vol    = top_lid.volume

# 底壳：外盒 SHELL_L*SHELL_W*BOTTOM_H = 67.54*30.20*7.6 ≈ 15499 mm³
# 减去内腔（63.54*26.20*5.6 ≈ 9317）和其他特征，估计 5000~15000mm³
BOTTOM_VOL_MIN, BOTTOM_VOL_MAX = 5000, 30000
LID_VOL_MIN,    LID_VOL_MAX    = 3000, 25000

assert BOTTOM_VOL_MIN <= bottom_vol <= BOTTOM_VOL_MAX, \
    f"底壳体积 {bottom_vol:.0f} mm³ 超出预期范围 [{BOTTOM_VOL_MIN}, {BOTTOM_VOL_MAX}]"
assert LID_VOL_MIN <= lid_vol <= LID_VOL_MAX, \
    f"盖板体积 {lid_vol:.0f} mm³ 超出预期范围 [{LID_VOL_MIN}, {LID_VOL_MAX}]"
print(f"  PASS — 底壳 {bottom_vol:.0f} mm³ in [{BOTTOM_VOL_MIN}, {BOTTOM_VOL_MAX}]")
print(f"  PASS — 盖板 {lid_vol:.0f} mm³ in [{LID_VOL_MIN}, {LID_VOL_MAX}]")

# ── Layer 3: 导出 STEP 重导入体积对比 / STEP export-reimport volume check ─
print("Layer 3: STEP 导出重导入体积对比 / STEP export-reimport volume check...")

bottom_step = os.path.join(output_dir, "bottom_shell.step")
lid_step    = os.path.join(output_dir, "top_lid.step")
asm_step    = os.path.join(output_dir, "assembly.step")

# 导出 / Export
export_step(bottom_shell, bottom_step)
export_step(lid_part_positioned, lid_step)
assembly = Compound([bottom_shell, lid_part_positioned])
export_step(assembly, asm_step)
print(f"  STEP 已导出 / STEP exported:")
print(f"    {bottom_step}")
print(f"    {lid_step}")
print(f"    {asm_step}")

# 重导入体积对比 / Reimport and compare volume
from build123d import import_step
bottom_reimport = import_step(bottom_step)
lid_reimport    = import_step(lid_step)

bottom_vol_re = bottom_reimport.volume
lid_vol_re    = lid_reimport.volume

bottom_diff = abs(bottom_vol_re - bottom_vol) / bottom_vol
lid_diff    = abs(lid_vol_re    - lid_vol)    / lid_vol

assert bottom_diff < 0.001, \
    f"底壳 STEP 重导入体积偏差 {bottom_diff*100:.4f}% 超过 0.1%"
assert lid_diff < 0.001, \
    f"盖板 STEP 重导入体积偏差 {lid_diff*100:.4f}% 超过 0.1%"
print(f"  PASS — 底壳偏差 {bottom_diff*100:.4f}%（<0.1%）")
print(f"  PASS — 盖板偏差 {lid_diff*100:.4f}%（<0.1%）")
print("===== 三层验证全部通过 / All 3-layer validations PASSED =====\n")

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
        show(bottom_shell, lid_part_positioned,
             names=["bottom_shell", "top_lid"],
             colors=["steelblue", "orange"],
             reset_camera=Camera.ISO)
        print("OCP Viewer 预览已打开 / OCP Viewer preview opened")
    else:
        print("OCP Viewer 未检测到 / OCP Viewer not detected")
except Exception as e:
    print(f"OCP 预览跳过 / OCP preview skipped: {e}")
