"""
从侧面参考图提取按键位置参数 / Extract button positions from side-view reference
输入：K80 Pro 3/4 背面左侧照片（可见左侧按键）
输出：按键距顶边 mm 值 → 与当前代码参数对比
"""

import cv2
import numpy as np
import os

output_dir = os.path.join(os.path.dirname(__file__), "output")
ref_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "references", "redmi-k80-pro", "images")
ref_path = os.path.join(ref_dir, "截屏2026-04-17 16.13.56.png")

img = cv2.imread(ref_path)
assert img is not None, f"Cannot load: {ref_path}"
orig = img.copy()
h_img, w_img = img.shape[:2]
print(f"图片尺寸 / Image size: {w_img} x {h_img}")

# ===== Step 1: 检测手机主体轮廓 / Detect phone body =====
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (7, 7), 0)

# 边缘检测 / Edge detection
edges = cv2.Canny(blurred, 30, 100)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
dilated = cv2.dilate(edges, kernel, iterations=2)

contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# 最大轮廓 = 手机 / Largest contour = phone
phone_contour = contours[0] if contours else None
assert phone_contour is not None, "无法检测手机轮廓 / Cannot detect phone"

x_ph, y_ph, w_ph, h_ph = cv2.boundingRect(phone_contour)
print(f"手机包围盒 / Phone bbox: x={x_ph} y={y_ph} w={w_ph} h={h_ph}")
print(f"长宽比 / Aspect ratio: {h_ph/w_ph:.3f}")

# ===== Step 2: 检测摄像头圆（作为尺寸锚点）/ Detect camera circle as anchor =====
phone_roi = img[y_ph:y_ph+h_ph, x_ph:x_ph+w_ph]
roi_gray = cv2.cvtColor(phone_roi, cv2.COLOR_BGR2GRAY)
roi_blur = cv2.GaussianBlur(roi_gray, (9, 9), 2)

# 摄像头圆在手机上半部分 / Camera circle in upper half
min_r = int(w_ph * 0.15)
max_r = int(w_ph * 0.40)
circles = cv2.HoughCircles(
    roi_blur, cv2.HOUGH_GRADIENT, dp=1.2, minDist=w_ph // 3,
    param1=80, param2=50, minRadius=min_r, maxRadius=max_r
)

cam_circle = None
if circles is not None:
    circles = np.uint16(np.around(circles))
    best_r = 0
    for (cx, cy, r) in circles[0]:
        if r > best_r:
            cam_circle = (int(cx), int(cy), int(r))
            best_r = r
    print(f"\n摄像头圆 / Camera circle (in ROI): cx={cam_circle[0]} cy={cam_circle[1]} r={cam_circle[2]}")

    # 已知摄像头直径 35mm → 算 px/mm 比例 / Known camera D=35mm → px/mm
    PHONE_L = 160.26
    CAM_D_MM = 35.0
    cam_r_px = cam_circle[2]
    px_per_mm_cam = (2 * cam_r_px) / CAM_D_MM
    print(f"摄像头尺度比例 / Camera scale: {px_per_mm_cam:.2f} px/mm")

    # 用手机高度做第二个估计 / Second estimate from phone height
    # 注意：透视会导致两个估计有差异 / Note: perspective causes difference
    px_per_mm_h = h_ph / PHONE_L
    print(f"手机高度比例 / Phone-height scale: {px_per_mm_h:.2f} px/mm")

    # 取平均或选择更可靠的（手机高度受透视影响更小）
    # Average or pick more reliable (phone height less affected by perspective)
    px_per_mm = px_per_mm_h  # 用高度比例，更可靠 / use height scale, more reliable
    print(f"使用比例 / Using scale: {px_per_mm:.2f} px/mm (基于手机高度)")

    # 摄像头中心在手机中的Y位置 / Camera center Y in phone coords
    cam_cy_from_top_px = cam_circle[1]  # ROI 内坐标 / in-ROI coords
    cam_cy_from_top_mm = cam_cy_from_top_px / px_per_mm
    print(f"摄像头中心距顶边 / Camera center from top: {cam_cy_from_top_mm:.1f} mm (预期 ~20mm)")
else:
    print("WARNING: 未检测到摄像头圆 / Camera circle not detected")
    # 降级：仅用手机高度比例 / Fallback: use phone height only
    PHONE_L = 160.26
    px_per_mm = h_ph / PHONE_L
    print(f"降级比例 / Fallback scale: {px_per_mm:.2f} px/mm")

# ===== Step 3: 检测左侧边缘按键 / Detect left-edge buttons =====
# 这张图是 3/4 背面左侧视角，按键在手机左侧边缘
# This is a 3/4 back-left view, buttons are on the left edge

# 方法：在手机左侧窄条区域搜索水平暗线条（按键缝隙）
# Method: search for horizontal dark lines in a narrow strip along the left edge

# 左侧边缘区域（手机包围盒左 15%）/ Left edge strip (15% of phone width)
edge_strip_w = int(w_ph * 0.15)
edge_strip = phone_roi[0:h_ph, 0:edge_strip_w]
edge_gray = cv2.cvtColor(edge_strip, cv2.COLOR_BGR2GRAY)

# 增强对比度 / Enhance contrast
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
edge_enhanced = clahe.apply(edge_gray)

# 边缘检测 / Edge detection on strip
edge_edges = cv2.Canny(edge_enhanced, 40, 120)

# 水平投影（按行求和，找按键位置峰值）/ Horizontal projection (sum per row)
h_proj = np.sum(edge_edges, axis=1).astype(float)
h_proj_smooth = cv2.GaussianBlur(h_proj.reshape(-1, 1), (21, 1), 5).flatten()

# 找峰值区域 / Find peak regions
threshold = np.mean(h_proj_smooth) + 1.5 * np.std(h_proj_smooth)
peaks = h_proj_smooth > threshold

# 提取连续区域 / Extract contiguous regions
regions = []
in_region = False
start = 0
for i in range(len(peaks)):
    if peaks[i] and not in_region:
        start = i
        in_region = True
    elif not peaks[i] and in_region:
        regions.append((start, i))
        in_region = False
if in_region:
    regions.append((start, len(peaks)))

# 过滤：按键区域应在手机上半部（Y < 70% 手机高度）且有一定长度
# Filter: buttons should be in upper portion and have minimum length
min_btn_len_px = 5 * px_per_mm   # 最少 5mm
max_btn_len_px = 35 * px_per_mm  # 最多 35mm

print(f"\n检测到 {len(regions)} 个候选区域 / Detected {len(regions)} candidate regions")
button_regions = []
for (y_start, y_end) in regions:
    length_px = y_end - y_start
    length_mm = length_px / px_per_mm
    from_top_mm = y_start / px_per_mm
    center_mm = (y_start + y_end) / 2 / px_per_mm

    if min_btn_len_px < length_px < max_btn_len_px and from_top_mm < 120:
        button_regions.append({
            "y_start": y_start, "y_end": y_end,
            "from_top_mm": from_top_mm,
            "length_mm": length_mm,
            "center_mm": center_mm,
        })
        print(f"  候选按键: 距顶 {from_top_mm:.1f}mm, 长 {length_mm:.1f}mm, "
              f"center={center_mm:.1f}mm")

# ===== Step 4: 尝试第二种方法 - 垂直梯度检测 / Alt method: vertical gradient =====
print("\n===== 垂直梯度法 / Vertical gradient method =====")

# 用 Sobel 检测垂直方向变化（按键是水平缝隙）
# Sobel for vertical changes (buttons have horizontal gaps)
sobel_y = cv2.Sobel(edge_enhanced, cv2.CV_64F, 0, 1, ksize=3)
sobel_abs = np.abs(sobel_y)
sobel_proj = np.mean(sobel_abs, axis=1)
sobel_smooth = cv2.GaussianBlur(sobel_proj.reshape(-1, 1).astype(np.float32), (15, 1), 3).flatten()

# 找显著峰值对（每个按键有上下两条边）/ Find significant peak pairs (button top/bottom)
sob_threshold = np.mean(sobel_smooth) + 2.0 * np.std(sobel_smooth)
sob_peaks = []
for i in range(1, len(sobel_smooth) - 1):
    if (sobel_smooth[i] > sob_threshold and
        sobel_smooth[i] > sobel_smooth[i-1] and
        sobel_smooth[i] > sobel_smooth[i+1]):
        sob_peaks.append(i)

print(f"梯度峰值 / Gradient peaks: {len(sob_peaks)}")
for p in sob_peaks:
    from_top = p / px_per_mm
    print(f"  y={p}px = {from_top:.1f}mm from top")

# ===== Step 5: 第三种方法 - 模板匹配用形态学 / Method 3: morphological button detection =====
print("\n===== 形态学法 / Morphological method =====")

# 在手机左侧 10% 宽度区域找按键的凹陷特征
# Find button indentation features in left 10% strip
strip_w = int(w_ph * 0.10)
strip = phone_roi[0:h_ph, 0:strip_w]
strip_gray = cv2.cvtColor(strip, cv2.COLOR_BGR2GRAY)

# 自适应阈值 / Adaptive threshold
strip_thresh = cv2.adaptiveThreshold(strip_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV, 15, 5)

# 竖向闭合（连接按键上下边缘）/ Vertical close to connect button edges
v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 7))
strip_closed = cv2.morphologyEx(strip_thresh, cv2.MORPH_CLOSE, v_kernel, iterations=2)

# 找连通域 / Find connected components
strip_contours, _ = cv2.findContours(strip_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

morph_btns = []
for c in strip_contours:
    x, y, w, h = cv2.boundingRect(c)
    area = cv2.contourArea(c)
    if h > 5 * px_per_mm and w > 1 and area > 20:  # 至少 5mm 高
        from_top = y / px_per_mm
        length = h / px_per_mm
        if from_top < 120 and length < 40:
            morph_btns.append({"from_top": from_top, "length": length, "y": y, "h": h})
            print(f"  形态学按键: 距顶 {from_top:.1f}mm, 长 {length:.1f}mm")

# ===== Step 6: 综合分析 + 标注 / Comprehensive analysis + annotation =====
print("\n===== 综合分析 / Combined Analysis =====")

# 汇总所有方法的发现 / Combine findings from all methods
all_findings = []

if button_regions:
    for br in button_regions:
        all_findings.append(("projection", br["from_top_mm"], br["length_mm"]))

if morph_btns:
    for mb in morph_btns:
        all_findings.append(("morphology", mb["from_top"], mb["length"]))

# 聚类相近的检测结果 / Cluster nearby detections
# 按 from_top 排序 / Sort by from_top
all_findings.sort(key=lambda x: x[1])
for method, ft, ln in all_findings:
    print(f"  [{method:12s}] from_top={ft:6.1f}mm  length={ln:5.1f}mm")

# ===== Step 7: 用目视估计做参考（基于摄像头位置锚定）=====
# Visual estimation anchored to camera position
print("\n===== 目视锚定估计 / Visual anchor estimation =====")
if cam_circle is not None:
    # 摄像头中心距手机顶边 / Camera center from phone top
    cam_top_mm = cam_cy_from_top_mm
    cam_bottom_mm = cam_top_mm + CAM_D_MM / 2  # 摄像头下边缘 / camera bottom edge
    print(f"摄像头中心距顶 / Cam center from top: {cam_top_mm:.1f}mm")
    print(f"摄像头下边缘距顶 / Cam bottom from top: {cam_bottom_mm:.1f}mm")

    # 在原图上标注摄像头和参考线 / Annotate camera and reference lines
    annotated = orig.copy()
    # 手机包围盒 / Phone bbox
    cv2.rectangle(annotated, (x_ph, y_ph), (x_ph + w_ph, y_ph + h_ph), (0, 255, 0), 2)
    # 摄像头圆 / Camera circle
    if cam_circle:
        abs_cx = x_ph + cam_circle[0]
        abs_cy = y_ph + cam_circle[1]
        abs_r = cam_circle[2]
        cv2.circle(annotated, (abs_cx, abs_cy), abs_r, (0, 255, 255), 2)
        cv2.circle(annotated, (abs_cx, abs_cy), 4, (0, 0, 255), -1)

    # 标注当前代码的按键位置 / Mark current code button positions
    curr_vol_dy = 55.0  # 当前值
    curr_pwr_dy = 83.0
    vol_len = 24.0
    pwr_len = 12.0

    # 转换为像素 / Convert to pixels
    def mm_to_px_y(mm_from_top):
        return int(y_ph + mm_from_top * px_per_mm)

    # 当前音量键位置（红色虚线）/ Current volume position (red dashed)
    vol_y1 = mm_to_px_y(curr_vol_dy)
    vol_y2 = mm_to_px_y(curr_vol_dy + vol_len)
    cv2.line(annotated, (x_ph - 30, vol_y1), (x_ph + 50, vol_y1), (0, 0, 255), 1)
    cv2.line(annotated, (x_ph - 30, vol_y2), (x_ph + 50, vol_y2), (0, 0, 255), 1)
    cv2.putText(annotated, f"VOL curr={curr_vol_dy:.0f}mm", (x_ph + 55, vol_y1 + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # 当前电源键位置（红色虚线）/ Current power position (red dashed)
    pwr_y1 = mm_to_px_y(curr_pwr_dy)
    pwr_y2 = mm_to_px_y(curr_pwr_dy + pwr_len)
    cv2.line(annotated, (x_ph - 30, pwr_y1), (x_ph + 50, pwr_y1), (0, 0, 255), 1)
    cv2.line(annotated, (x_ph - 30, pwr_y2), (x_ph + 50, pwr_y2), (0, 0, 255), 1)
    cv2.putText(annotated, f"PWR curr={curr_pwr_dy:.0f}mm", (x_ph + 55, pwr_y1 + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # 在投影检测到的区域用绿色标注 / Green marks for detected regions
    for br in button_regions:
        by1 = y_ph + br["y_start"]
        by2 = y_ph + br["y_end"]
        cv2.rectangle(annotated, (x_ph - 20, by1), (x_ph + 30, by2), (0, 255, 0), 2)
        cv2.putText(annotated, f"{br['from_top_mm']:.0f}mm L={br['length_mm']:.0f}mm",
                    (x_ph + 35, by1 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)

    # 保存标注图 / Save annotated
    ann_path = os.path.join(output_dir, "side_annotated.png")
    cv2.imwrite(ann_path, annotated)
    print(f"标注图保存 / Annotated: {ann_path}")

    # 保存水平投影图 / Save projection plot
    proj_img = np.zeros((h_ph, 300, 3), dtype=np.uint8)
    if len(h_proj_smooth) > 0:
        max_val = h_proj_smooth.max() if h_proj_smooth.max() > 0 else 1
        for y in range(min(h_ph, len(h_proj_smooth))):
            x_val = int(h_proj_smooth[y] / max_val * 280)
            cv2.line(proj_img, (0, y), (x_val, y), (0, 255, 0), 1)
        # 阈值线 / Threshold line
        th_x = int(threshold / max_val * 280)
        cv2.line(proj_img, (th_x, 0), (th_x, h_ph), (0, 0, 255), 1)
    proj_path = os.path.join(output_dir, "side_projection.png")
    cv2.imwrite(proj_path, proj_img)
    print(f"投影图保存 / Projection: {proj_path}")

# ===== Step 8: 参数建议 / Parameter recommendations =====
print("\n" + "=" * 60)
print("参数建议 / Parameter Recommendations")
print("=" * 60)
print(f"{'参数':<12} {'当前值':>10} {'建议值':>10} {'来源'}")
print("-" * 60)

# 基于检测结果综合判断 / Based on combined detection results
# 如果检测结果不够可靠，给出基于目视的估计
if button_regions and len(button_regions) >= 2:
    # 第一个区域 = 音量键，第二个 = 电源键
    vol_from_top = button_regions[0]["from_top_mm"]
    vol_length = button_regions[0]["length_mm"]
    pwr_from_top = button_regions[1]["from_top_mm"]
    pwr_length = button_regions[1]["length_mm"]
    print(f"{'VOL_DY':<12} {55.0:>10.1f} {vol_from_top:>10.1f} {'投影检测'}")
    print(f"{'VOL_LEN':<12} {24.0:>10.1f} {vol_length:>10.1f} {'投影检测'}")
    print(f"{'PWR_DY':<12} {83.0:>10.1f} {pwr_from_top:>10.1f} {'投影检测'}")
    print(f"{'PWR_LEN':<12} {12.0:>10.1f} {pwr_length:>10.1f} {'投影检测'}")
else:
    # 透视图检测不可靠，给出保守目视估计
    # Perspective detection unreliable, give conservative visual estimate
    print("自动检测结果不足，给出基于目视的粗略估计：")
    print("(3/4 透视图中按键检测精度有限)")
    print(f"{'VOL_DY':<12} {55.0:>10.1f} {'~38-42':>10} {'目视估计（偏上方向）'}")
    print(f"{'PWR_DY':<12} {83.0:>10.1f} {'~58-65':>10} {'目视估计（偏上方向）'}")
print("=" * 60)
