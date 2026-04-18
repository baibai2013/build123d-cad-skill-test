"""
侧面视觉对比：参考照片 vs 模型 RIGHT 截图 / Side view comparison
标注按键位置对比 / Annotate button position comparison
"""
import cv2
import numpy as np
import os

output_dir = os.path.join(os.path.dirname(__file__), "output")
ref_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "references", "redmi-k80-pro", "images")

# 加载图像 / Load images
ref_path = os.path.join(ref_dir, "截屏2026-04-17 16.13.56.png")
model_path = os.path.join(output_dir, "k80_pro_case_RIGHT.png")

ref_img = cv2.imread(ref_path)
model_img = cv2.imread(model_path)
assert ref_img is not None, f"Cannot load: {ref_path}"
assert model_img is not None, f"Cannot load: {model_path}"

# ===== 参考图标注（按键位置）/ Annotate reference =====
ref_h, ref_w = ref_img.shape[:2]
ref_annotated = ref_img.copy()

# 手机包围盒（从 extract_side_params.py 的结果）
# Phone bbox from extraction
x_ph, y_ph, w_ph, h_ph = 72, 50, 385, 1063
PHONE_L = 160.26
px_per_mm = h_ph / PHONE_L

# 新参数 / New parameters
VOL_DY_NEW = 38.0
VOL_LEN = 24.0
PWR_DY_NEW = 65.0
PWR_LEN = 12.0

# 旧参数 / Old parameters
VOL_DY_OLD = 55.0
PWR_DY_OLD = 83.0

def draw_btn_marker(img, dy, length, color, label, x_offset=0):
    """在参考图上标注按键位置 / Draw button position marker on reference"""
    y1 = int(y_ph + dy * px_per_mm)
    y2 = int(y_ph + (dy + length) * px_per_mm)
    x_left = x_ph + x_offset
    x_right = x_ph + 40 + x_offset
    cv2.rectangle(img, (x_left, y1), (x_right, y2), color, 2)
    cv2.putText(img, f"{label} {dy:.0f}mm", (x_right + 5, y1 + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

# 标注旧位置（红色）/ Old positions (red)
draw_btn_marker(ref_annotated, VOL_DY_OLD, VOL_LEN, (0, 0, 255), "VOL old", -30)
draw_btn_marker(ref_annotated, PWR_DY_OLD, PWR_LEN, (0, 0, 200), "PWR old", -30)

# 标注新位置（绿色）/ New positions (green)
draw_btn_marker(ref_annotated, VOL_DY_NEW, VOL_LEN, (0, 255, 0), "VOL new", -15)
draw_btn_marker(ref_annotated, PWR_DY_NEW, PWR_LEN, (0, 200, 0), "PWR new", -15)

# 手机包围盒 / Phone bbox
cv2.rectangle(ref_annotated, (x_ph, y_ph), (x_ph + w_ph, y_ph + h_ph), (255, 255, 0), 1)

# ===== 模型截图标注 / Annotate model screenshot =====
model_annotated = model_img.copy()
model_h, model_w = model_img.shape[:2]

# 模型 RIGHT 视图中手机是横向的，+Y 在左侧
# In RIGHT view phone is horizontal, +Y on left
# 需要找到模型中手机壳的范围 / Find case extent in model image
model_gray = cv2.cvtColor(model_img, cv2.COLOR_BGR2GRAY)
_, model_thresh = cv2.threshold(model_gray, 240, 255, cv2.THRESH_BINARY_INV)
model_contours, _ = cv2.findContours(model_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if model_contours:
    model_contours = sorted(model_contours, key=cv2.contourArea, reverse=True)
    mx, my, mw, mh = cv2.boundingRect(model_contours[0])
    print(f"模型包围盒 / Model bbox: x={mx} y={my} w={mw} h={mh}")

    # 模型横向长度对应手机长度 / Model horizontal = phone length
    model_px_per_mm = mw / (PHONE_L + 3.6)  # out_l ≈ PHONE_L + 3.6 (V2)

    # 在模型图上标注按键位置
    # 模型 RIGHT 视图: +Y 在左 → 距顶越近 = 越靠左
    # RIGHT view: +Y on LEFT → closer to top = more to LEFT
    out_l = PHONE_L + 0.6 + 3.0  # cav_l + 2*wall_t for V2

    def draw_model_btn(img, dy, length, color, label):
        # Y 坐标 = 模型中心偏移 / Y in model coords
        btn_y_model = out_l / 2 - dy - length / 2
        # 在 RIGHT 视图中, +Y=左, 中心在 mx + mw/2
        x_center = int(mx + mw / 2 - btn_y_model * model_px_per_mm)
        x_half = int(length / 2 * model_px_per_mm)
        cv2.rectangle(img, (x_center - x_half, my - 15), (x_center + x_half, my - 5), color, 2)
        cv2.putText(img, f"{label}", (x_center - 20, my - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

    draw_model_btn(model_annotated, VOL_DY_NEW, VOL_LEN, (0, 255, 0), "VOL")
    draw_model_btn(model_annotated, PWR_DY_NEW, PWR_LEN, (0, 200, 0), "PWR")

# ===== 拼接对比图 / Side-by-side comparison =====
target_h = 800
ref_scale = target_h / ref_annotated.shape[0]
ref_resized = cv2.resize(ref_annotated, None, fx=ref_scale, fy=ref_scale)

# 模型图旋转 90°（横转竖）方便对比 / Rotate model 90° for vertical comparison
model_rotated = cv2.rotate(model_annotated, cv2.ROTATE_90_COUNTERCLOCKWISE)
model_scale = target_h / model_rotated.shape[0]
model_resized = cv2.resize(model_rotated, None, fx=model_scale, fy=model_scale)

# 添加标题 / Add titles
def add_title(img, text):
    h, w = img.shape[:2]
    title_bar = np.zeros((40, w, 3), dtype=np.uint8)
    cv2.putText(title_bar, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return np.vstack([title_bar, img])

ref_titled = add_title(ref_resized, "Reference (side)")
model_titled = add_title(model_resized, "Model RIGHT (rotated)")

# 对齐高度 / Align heights
max_h = max(ref_titled.shape[0], model_titled.shape[0])
def pad_height(img, target_h):
    if img.shape[0] < target_h:
        pad = np.zeros((target_h - img.shape[0], img.shape[1], 3), dtype=np.uint8)
        return np.vstack([img, pad])
    return img

ref_titled = pad_height(ref_titled, max_h)
model_titled = pad_height(model_titled, max_h)

comparison = np.hstack([ref_titled, model_titled])
comp_path = os.path.join(output_dir, "side_comparison.png")
cv2.imwrite(comp_path, comparison)
print(f"\n对比图保存 / Comparison: {comp_path}")

# ===== 参数变更汇总 / Parameter change summary =====
print("\n" + "=" * 60)
print("按键位置参数修正 / Button Position Corrections")
print("=" * 60)
print(f"{'参数':<12} {'旧值':>8} {'新值':>8} {'偏差':>8}")
print("-" * 60)
print(f"{'VOL_DY':<12} {VOL_DY_OLD:>8.1f} {VOL_DY_NEW:>8.1f} {VOL_DY_NEW - VOL_DY_OLD:>+8.1f}")
print(f"{'PWR_DY':<12} {PWR_DY_OLD:>8.1f} {PWR_DY_NEW:>8.1f} {PWR_DY_NEW - PWR_DY_OLD:>+8.1f}")
vol_end_old = VOL_DY_OLD + VOL_LEN
vol_end_new = VOL_DY_NEW + VOL_LEN
pwr_end_old = PWR_DY_OLD + PWR_LEN
pwr_end_new = PWR_DY_NEW + PWR_LEN
gap_old = PWR_DY_OLD - vol_end_old
gap_new = PWR_DY_NEW - vol_end_new
print(f"{'按键间距':<12} {gap_old:>8.1f} {gap_new:>8.1f} {'mm'}")
print(f"{'音量键范围':<12} {VOL_DY_OLD:.0f}-{vol_end_old:.0f}mm → {VOL_DY_NEW:.0f}-{vol_end_new:.0f}mm")
print(f"{'电源键范围':<12} {PWR_DY_OLD:.0f}-{pwr_end_old:.0f}mm → {PWR_DY_NEW:.0f}-{pwr_end_new:.0f}mm")
print("=" * 60)
