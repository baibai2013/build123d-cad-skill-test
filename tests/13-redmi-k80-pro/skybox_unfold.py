"""
Skybox 十字展开图 / Skybox cross-unfolded view
以手机壳正面（屏幕开口面）为中心，展开 6 个面
Center = FRONT (screen face), unfold into cross layout:

              [UP]
    [LEFT] [FRONT] [RIGHT] [BACK]
             [DOWN]

原理 / Principle:
  固定视角 Camera.FRONT（相机在 -Y 方向，看 -Y 面）
  通过 rotate 把每个目标面转到 -Y 方向朝相机
  Fixed view Camera.FRONT; rotate model so target face points to -Y (toward camera)
"""
from build123d import Axis, Location
import os, sys, time
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from redmi_k80_pro_case import v2, output_dir

# ===== 6 个面的旋转策略 / Per-face rotation strategy =====
# 使目标面朝 -Y（Camera.FRONT 相机方向）/ target face → -Y (camera)
face_rotations = {
    "FRONT": [(Axis.X,  90)],                   # 屏幕+唇边 / screen+lip
    # BACK: Axis.X 90 让摄像头面朝相机方向，再 Axis.Z 180 镜像
    # 确保摄像头在画面左上（而非右下/下方）/ camera shows upper-left
    "BACK":  [(Axis.X,  90), (Axis.Z, 180)],    # 摄像头+闪光灯 / camera+flash
    "UP":    [(Axis.X, 180)],                   # 顶部短边 / top edge
    "DOWN":  [],                                # USB/扬声器/SIM 底端
    "LEFT":  [(Axis.Z,  90)],                   # 光面 / smooth side
    "RIGHT": [(Axis.Z, -90)],                   # 按键面 / button side
}

# ===== 生成各面截图 / Capture each face =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    assert active_port, "OCP Viewer 未启动 / OCP Viewer not running"
    set_port(active_port)

    for face, rots in face_rotations.items():
        m = v2
        for axis, deg in rots:
            m = m.rotate(axis, deg)
        show(m, names=[f"skybox_{face}"], reset_camera=Camera.FRONT)
        time.sleep(0.8)
        save_screenshot(os.path.join(output_dir, f"skybox_{face}.png"))
        print(f"  skybox_{face}.png ✓")
except Exception as e:
    print(f"截图生成失败 / Screenshot generation failed: {e}")
    sys.exit(1)

# ===== 拼接十字展开图 / Compose cross layout =====
# 读取每张图 + 自动裁剪白边 / load + auto-crop whitespace
def load_and_crop(path, pad=20):
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    mask = np.any(arr < 250, axis=2)
    if not mask.any():
        return img
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    r0, r1 = rows[0], rows[-1]
    c0, c1 = cols[0], cols[-1]
    r0 = max(0, r0 - pad); c0 = max(0, c0 - pad)
    r1 = min(arr.shape[0], r1 + pad); c1 = min(arr.shape[1], c1 + pad)
    return Image.fromarray(arr[r0:r1, c0:c1])

faces = {f: load_and_crop(os.path.join(output_dir, f"skybox_{f}.png"))
         for f in face_rotations}

# 统一每格尺寸（限制最大 700×500 防止画布过大）
# Unify cell size (cap at 700×500 to keep canvas ≤2800×1500)
MAX_CELL_W = 700
MAX_CELL_H = 500
cell_w = min(MAX_CELL_W, max(img.size[0] for img in faces.values()))
cell_h = min(MAX_CELL_H, max(img.size[1] for img in faces.values()))

def fit_cell(img, w, h, bg=(255, 255, 255)):
    """按比例缩放 + 居中 / scale proportionally + center"""
    iw, ih = img.size
    ratio = min(w / iw, h / ih) * 0.92
    nw, nh = int(iw * ratio), int(ih * ratio)
    resized = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), bg)
    canvas.paste(resized, ((w - nw) // 2, (h - nh) // 2))
    return canvas

cells = {f: fit_cell(img, cell_w, cell_h) for f, img in faces.items()}

# 绘制十字 / Draw cross layout (4 cols × 3 rows)
#  col:   0       1       2       3
#  row0:  .       UP      .       .
#  row1: LEFT  FRONT   RIGHT   BACK
#  row2:  .     DOWN      .       .
total_w = cell_w * 4
total_h = cell_h * 3
canvas = Image.new("RGB", (total_w, total_h), (255, 255, 255))

positions = {
    "UP":    (1, 0),
    "LEFT":  (0, 1),
    "FRONT": (1, 1),
    "RIGHT": (2, 1),
    "BACK":  (3, 1),
    "DOWN":  (1, 2),
}
for face, (cx, cy) in positions.items():
    canvas.paste(cells[face], (cx * cell_w, cy * cell_h))

# 添加标签 / Add labels
from PIL import ImageDraw, ImageFont
draw = ImageDraw.Draw(canvas)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except Exception:
    font = ImageFont.load_default()

face_desc = {
    "FRONT": "FRONT (screen + lip)",
    "BACK":  "BACK (camera + flash)",
    "UP":    "UP (top edge)",
    "DOWN":  "DOWN (USB/speaker/SIM)",
    "LEFT":  "LEFT (smooth side)",
    "RIGHT": "RIGHT (buttons)",
}
for face, (cx, cy) in positions.items():
    x = cx * cell_w + 20
    y = cy * cell_h + 20
    label = face_desc[face]
    bbox = draw.textbbox((x, y), label, font=font)
    draw.rectangle(bbox, fill=(0, 0, 0))
    draw.text((x, y), label, fill=(255, 255, 0), font=font)

# 网格线 / Grid lines for visual separation
grid_color = (180, 180, 180)
for i in range(5):
    x = i * cell_w
    draw.line([(x, 0), (x, total_h)], fill=grid_color, width=2)
for j in range(4):
    y = j * cell_h
    draw.line([(0, y), (total_w, y)], fill=grid_color, width=2)

# 标题 / Title
title = "Redmi K80 Pro Case - Skybox Unfolded (FRONT center)"
title_bar_h = 80
titled = Image.new("RGB", (total_w, total_h + title_bar_h), (30, 30, 30))
titled.paste(canvas, (0, title_bar_h))
tdraw = ImageDraw.Draw(titled)
try:
    tfont = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)
except Exception:
    tfont = ImageFont.load_default()
tdraw.text((30, 15), title, fill=(255, 255, 255), font=tfont)

out_path = os.path.join(output_dir, "skybox_unfolded.png")
titled.save(out_path, "PNG")
print(f"\n✅ Skybox 展开图已保存 / Skybox saved: {out_path}")
print(f"   画布尺寸 / Canvas: {titled.size[0]}x{titled.size[1]}")
