"""
Test 22 — ESP32-S3-DevKitC-1 Enclosure Exploded Animation
外壳爆炸动画:bottom shell + PCB+模块一体 + top lid 三层垂直展开
(PCB 与 WROOM-1 模块焊接一体,爆炸时同步移动,不分离)

动画时间轴(16s 循环):
- 0→2s 炸开(各部件沿 Z 轴分离)
- 2→12s 停留在爆炸状态(便于观察 PCB 置于底壳低台 + 盖板压舌位置)
- 12→14s 合拢(零件回到装配位置)
- 14→16s 停留在装配状态,循环播放

输出:
- output/exploded_static.png    静态爆炸图(峰值帧)
- output/exploded_explode.gif   16s 循环动画(160 帧 @ 10fps)
"""
from build123d import *
from ocp_vscode import show, Animation, set_port, Camera, save_screenshot
from ocp_vscode.comms import port_check
from ocp_vscode.state import get_ports
from PIL import Image
import os
import time
import tempfile

# ===== 路径 / Paths =====
HERE = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(HERE, "output")

bottom_step_path = os.path.join(output_dir, "bottom_shell.step")
lid_step_path    = os.path.join(output_dir, "top_lid.step")

# ===== 装配常量(与主文件一致)/ Assembly constants (same as main file) =====
PCB_L, PCB_W, PCB_T = 62.74, 25.40, 1.60
BASE_T         = 2.0
PCB_STANDOFF   = 4.0
LID_CLEARANCE  = 9.0
LID_T          = 2.0
BOTTOM_H       = BASE_T + PCB_STANDOFF + PCB_T    # = 7.6
LID_H          = LID_CLEARANCE + LID_T             # = 11.0

# PCB 在装配时的中心 Z(底壳中心=0,底壳顶面=+3.8,PCB 底面在顶面上 0,PCB 中心+0.8)
# PCB center Z in assembly (bottom shell center=0, top=+3.8, PCB bottom on top, center at +0.8)
PCB_CENTER_Z   = -BOTTOM_H/2 + BASE_T + PCB_STANDOFF + PCB_T/2   # = 3.0

# WROOM-1 模块占位尺寸 / Module placeholder dimensions
MODULE_L, MODULE_W, MODULE_H = 25.5, 18.0, 3.1
MODULE_CENTER_Z = PCB_CENTER_Z + PCB_T/2 + MODULE_H/2

# ===== 爆炸距离(各部件沿 Z 向上偏移)/ Explosion offsets =====
# PCB 和 WROOM-1 模块焊接一体,同步移动(不分离)
# PCB and WROOM-1 module soldered together, moved as one unit
EXPLODE_PCB_ASSY = 12.0   # mm,PCB 组件(含模块)上移 / PCB assembly (with module) rises together
EXPLODE_LID      = 25.0   # mm,盖板上移 / lid rises

# ===== 加载 STEP 零件 / Load STEP parts =====
print("加载 STEP 文件 / Loading STEP files...")
bottom_shell = import_step(bottom_step_path)
lid_raw      = import_step(lid_step_path)   # 已含 +9.3 装配偏移 / already has +9.3 offset baked in

# ===== 构建装配态部件(动画起点)/ Build assembly-state parts (animation baseline) =====
# PCB + WROOM-1 模块焊接一体:用 Compound 合并,共享同一动画轨道
# PCB + WROOM-1 module soldered as one unit: merged via Compound, single animation track
pcb_only    = Box(PCB_L, PCB_W, PCB_T).moved(Location((0, 0, PCB_CENTER_Z)))
module_only = Box(MODULE_L, MODULE_W, MODULE_H).moved(Location((0, 0, MODULE_CENTER_Z)))
# Compound.label 便于 OCP 分组识别 / label for OCP group addressing
pcb_assy    = Compound([pcb_only, module_only], label="pcb_with_module")
# bottom_shell 和 lid_raw 均处于装配位置

# ===== OCP 预览 + 动画 + GIF =====
try:
    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if not active_port:
        print("OCP Viewer 未检测到,请启动 OCP CAD Viewer 扩展")
        raise SystemExit(0)

    set_port(active_port)

    # 先 show 装配态(作为动画基准)/ Show assembly state first (animation baseline)
    # PCB + 模块一体(pcb_assy Compound),只占一个动画轨道
    # PCB + module as one unit (pcb_assy Compound), single animation track
    show(
        bottom_shell, pcb_assy, lid_raw,
        names=["bottom_shell", "pcb_with_module", "top_lid"],
        colors=["steelblue", "green", "orange"],
        reset_camera=Camera.ISO,
    )
    print(f"OCP Viewer 装配态已显示 / Assembly state shown (port {active_port})")

    time.sleep(2)    # 等待 Viewer 渲染就绪 / wait for renderer

    # ===== 构建 16 秒循环动画 / Build 16s loop animation =====
    # 时间轴:0→2 炸开, 2→12 停留, 12→14 合拢, 14→16 停留
    # Time axis: 0→2 explode, 2→12 hold, 12→14 collapse, 14→16 hold
    t_keys = [0, 2, 12, 14, 16]

    anim = Animation()
    # 底壳不动 / Bottom stays fixed
    anim.add_track("/Group/bottom_shell", "t", t_keys,
                   [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0]])
    # PCB + 模块一体上移 EXPLODE_PCB_ASSY mm(同步,不分离)
    # PCB + module move together as one unit (soldered, inseparable)
    anim.add_track("/Group/pcb_with_module", "t", t_keys,
                   [[0,0,0], [0,0,EXPLODE_PCB_ASSY], [0,0,EXPLODE_PCB_ASSY], [0,0,0], [0,0,0]])
    # 盖板上移 EXPLODE_LID mm
    anim.add_track("/Group/top_lid", "t", t_keys,
                   [[0,0,0], [0,0,EXPLODE_LID], [0,0,EXPLODE_LID], [0,0,0], [0,0,0]])

    anim.animate(speed=1)
    print("✅ 爆炸动画已启动(16s 循环)/ Explosion animation running (16s loop)")

    time.sleep(2)    # 等待动画初始化 / wait for animation to initialize

    # ===== 逐帧截屏合成 GIF / Frame-by-frame screenshot → GIF =====
    gif_fps       = 10
    gif_duration  = 16           # 秒
    n_frames      = gif_fps * gif_duration   # 160 帧
    frame_delay   = round(1000 / gif_fps)    # 每帧 100ms

    frames = []
    tmp_path = os.path.join(tempfile.gettempdir(), "ocp_esp32_frame.png")

    print(f"GIF 截屏中 ({n_frames} 帧)...", end=" ", flush=True)
    for i in range(n_frames):
        frac = i / n_frames
        anim.set_relative_time(frac)
        time.sleep(0.25)             # 等待渲染 / wait for render
        save_screenshot(tmp_path)
        time.sleep(0.15)             # 等待文件写入 / wait for file write
        img = Image.open(tmp_path).convert("RGB")
        frames.append(img.copy())
        if i % 20 == 0:
            print(f"{100*i//n_frames}%", end=" ", flush=True)

    print("100%")

    # 保存静态峰值帧(t=6s 时,动画正好在停留爆炸态)
    # Save static peak frame (t=6s, during exploded hold phase)
    peak_idx = int(6 / gif_duration * n_frames)   # 帧号 60
    peak_png = os.path.join(output_dir, "exploded_static.png")
    frames[peak_idx].save(peak_png)
    print(f"静态爆炸峰值 / Static peak frame: {peak_png}")

    # 合成 GIF(无限循环)
    gif_path = os.path.join(output_dir, "exploded_explode.gif")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_delay,
        loop=0,
    )
    print(f"GIF 导出完成 / GIF export complete: {gif_path}")

    # 恢复动画正常播放(非 frac 控制)
    anim.animate(speed=1)

except Exception as e:
    print(f"动画/GIF 生成失败 / Animation/GIF failed: {e}")
    import traceback
    traceback.print_exc()

print("\n===== 爆炸动画测试完成 / Explosion animation test complete =====")
