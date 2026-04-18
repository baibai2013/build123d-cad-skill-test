"""
从参考照片提取 CAD 参数 / Extract CAD parameters from reference photo
输入：K80 Pro 背面照片
输出：归一化特征位置 → 换算为 mm 级 CAD 参数
"""

import cv2
import numpy as np
import os

output_dir = os.path.join(os.path.dirname(__file__), "output")
ref_path = os.path.join(output_dir, "截屏2026-04-17 14.44.52.png")

img = cv2.imread(ref_path)
assert img is not None, f"Cannot load: {ref_path}"
orig = img.copy()
h_img, w_img = img.shape[:2]

# ===== Step 1: 分离手机主体 / Isolate phone body =====
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (7, 7), 0)

# 自适应阈值 + 形态学操作找到手机轮廓
# Adaptive threshold + morphology to find phone outline
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)

contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

phone_contour = None
for c in contours:
    area = cv2.contourArea(c)
    if area > h_img * w_img * 0.15:
        phone_contour = c
        break

if phone_contour is None:
    print("WARNING: 未检测到手机轮廓，尝试边缘检测 / Phone contour not found, trying edge detection")
    edges = cv2.Canny(blurred, 30, 100)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours2, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours2 = sorted(contours2, key=cv2.contourArea, reverse=True)
    if contours2:
        phone_contour = contours2[0]

assert phone_contour is not None, "无法检测手机轮廓 / Cannot detect phone outline"

# 手机包围盒 / Phone bounding box
x_phone, y_phone, w_phone, h_phone = cv2.boundingRect(phone_contour)
print(f"手机包围盒 / Phone bbox: x={x_phone} y={y_phone} w={w_phone} h={h_phone}")
print(f"长宽比 / Aspect ratio: {h_phone/w_phone:.3f} (实际: {160.26/74.95:.3f})")

# 像素→mm 换算系数 / Pixel to mm scale
PHONE_L = 160.26
PHONE_W = 74.95
px_per_mm_x = w_phone / PHONE_W
px_per_mm_y = h_phone / PHONE_L
px_per_mm = (px_per_mm_x + px_per_mm_y) / 2
print(f"比例尺 / Scale: {px_per_mm:.2f} px/mm (X: {px_per_mm_x:.2f}, Y: {px_per_mm_y:.2f})")

# 手机中心 / Phone center
cx_phone = x_phone + w_phone / 2
cy_phone = y_phone + h_phone / 2

# ===== Step 2: 裁剪手机区域 / Crop phone region =====
margin = 20
x1 = max(0, x_phone - margin)
y1 = max(0, y_phone - margin)
x2 = min(w_img, x_phone + w_phone + margin)
y2 = min(h_img, y_phone + h_phone + margin)
phone_crop = img[y1:y2, x1:x2].copy()
crop_path = os.path.join(output_dir, "phone_cropped.png")
cv2.imwrite(crop_path, phone_crop)
print(f"裁剪图保存: {crop_path}")

# ===== Step 3: 检测摄像头圆形模组 / Detect camera circle =====
phone_gray = cv2.cvtColor(phone_crop, cv2.COLOR_BGR2GRAY)
phone_blur = cv2.GaussianBlur(phone_gray, (9, 9), 2)

min_r_px = int(12 * px_per_mm)
max_r_px = int(22 * px_per_mm)
circles = cv2.HoughCircles(
    phone_blur, cv2.HOUGH_GRADIENT, dp=1.2, minDist=int(30 * px_per_mm),
    param1=80, param2=45, minRadius=min_r_px, maxRadius=max_r_px
)

cam_circle = None
if circles is not None:
    circles = np.uint16(np.around(circles))
    best = None
    best_r = 0
    for (cx, cy, r) in circles[0]:
        if r > best_r:
            best = (cx, cy, r)
            best_r = r
    cam_circle = best
    print(f"\n摄像头圆检测 / Camera circle detected:")
    print(f"  crop坐标: cx={cam_circle[0]} cy={cam_circle[1]} r={cam_circle[2]}")

    cam_cx_px = cam_circle[0] + x1 - margin
    cam_cy_px = cam_circle[1] + y1 - margin
    cam_r_px = cam_circle[2]

    cam_cx_mm = (cam_cx_px - cx_phone) / px_per_mm
    cam_cy_mm = -(cam_cy_px - cy_phone) / px_per_mm
    cam_d_mm = 2 * cam_r_px / px_per_mm
    cam_from_top_mm = (cam_cy_px - y_phone) / px_per_mm_y

    print(f"  背面视角 / Back view:")
    print(f"    cx_back = {cam_cx_mm:+.1f} mm (负=左, 正=右)")
    print(f"    cy (距中心) = {cam_cy_mm:+.1f} mm (正=上)")
    print(f"    从顶边 = {cam_from_top_mm:.1f} mm")
    print(f"    直径 = {cam_d_mm:.1f} mm")

    # 背面左偏 → 模型坐标 +X / Back-view left → model +X
    cam_cx_model = -cam_cx_mm
    print(f"  模型参数 / Model params:")
    print(f"    CAM_CX = {cam_cx_model:+.1f} (当前: +16.0)")
    print(f"    CAM_CY = {cam_cy_mm:+.1f} (当前: +60.0)")
    print(f"    CAM_D  = {cam_d_mm:.1f} (当前: 34.0)")
else:
    print("WARNING: 未检测到摄像头圆 / Camera circle not detected")

# ===== Step 4: 检测闪光灯 / Detect flash capsule =====
if cam_circle is not None:
    # 在摄像头右侧区域搜索闪光灯 / Search for flash to the right of camera
    cam_cx_crop, cam_cy_crop, cam_r_crop = cam_circle
    search_x1 = int(cam_cx_crop + cam_r_crop * 0.8)
    search_x2 = min(phone_crop.shape[1], int(cam_cx_crop + cam_r_crop * 2.0))
    search_y1 = max(0, int(cam_cy_crop - cam_r_crop * 0.6))
    search_y2 = int(cam_cy_crop + cam_r_crop * 0.6)

    if search_x2 > search_x1 and search_y2 > search_y1:
        roi = phone_crop[search_y1:search_y2, search_x1:search_x2]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # 闪光灯通常比周围更亮 / Flash is usually brighter
        _, flash_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        flash_contours, _ = cv2.findContours(flash_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        flash_found = None
        for fc in flash_contours:
            area = cv2.contourArea(fc)
            min_flash_area = (2 * px_per_mm) * (5 * px_per_mm)
            max_flash_area = (6 * px_per_mm) * (12 * px_per_mm)
            if min_flash_area < area < max_flash_area:
                rect = cv2.minAreaRect(fc)
                (rx, ry), (rw, rh), angle = rect
                aspect = max(rw, rh) / (min(rw, rh) + 0.01)
                if 1.5 < aspect < 6.0:
                    flash_found = rect
                    flash_contour = fc
                    break

        if flash_found:
            (fx, fy), (fw, fh), fangle = flash_found
            fx_abs = fx + search_x1
            fy_abs = fy + search_y1

            flash_cx_px = fx_abs + x1 - margin
            flash_cy_px = fy_abs + y1 - margin

            flash_dx_mm = (flash_cx_px - cam_cx_px) / px_per_mm
            flash_dy_mm = -(flash_cy_px - cam_cy_px) / px_per_mm

            flash_long = max(fw, fh) / px_per_mm
            flash_short = min(fw, fh) / px_per_mm
            is_horizontal = fw > fh

            print(f"\n闪光灯检测 / Flash detected:")
            print(f"  尺寸: {flash_long:.1f} x {flash_short:.1f} mm")
            print(f"  方向: {'横向' if is_horizontal else '竖向'} / {'horizontal' if is_horizontal else 'vertical'}")
            print(f"  距摄像头中心: dx={flash_dx_mm:+.1f} dy={flash_dy_mm:+.1f} mm (背面视角)")
            flash_dx_model = -flash_dx_mm
            flash_dy_model = flash_dy_mm
            print(f"  模型参数 / Model params:")
            print(f"    FLASH_DX = {flash_dx_model:+.1f} (当前: -21.0)")
            print(f"    FLASH_DY = {flash_dy_model:+.1f} (当前: +1.0)")
            print(f"    FLASH_L  = {flash_long:.1f} (当前: 7.0)")
            print(f"    FLASH_W  = {flash_short:.1f} (当前: 2.5)")

            # 在 ROI 上标注 / Annotate ROI
            box = cv2.boxPoints(flash_found)
            box = np.intp(box)
            cv2.drawContours(roi, [box], 0, (0, 255, 0), 2)
        else:
            print("\nWARNING: 闪光灯未检测到 / Flash not detected in search region")
            # 保存搜索区域用于调试 / Save search ROI for debug
            roi_path = os.path.join(output_dir, "flash_search_roi.png")
            cv2.imwrite(roi_path, roi)
            print(f"  搜索区域保存: {roi_path}")

# ===== Step 5: 标注结果图 / Generate annotated result =====
annotated = orig.copy()

# 手机轮廓 / Phone outline
cv2.drawContours(annotated, [phone_contour], -1, (0, 255, 0), 2)
cv2.rectangle(annotated, (x_phone, y_phone), (x_phone + w_phone, y_phone + h_phone), (255, 0, 0), 2)

# 摄像头圆 / Camera circle
if cam_circle is not None:
    abs_cx = int(cam_circle[0] + x1 - margin)
    abs_cy = int(cam_circle[1] + y1 - margin)
    abs_r = int(cam_circle[2])
    cv2.circle(annotated, (abs_cx, abs_cy), abs_r, (0, 255, 255), 2)
    cv2.circle(annotated, (abs_cx, abs_cy), 4, (0, 0, 255), -1)
    cv2.putText(annotated, f"D={cam_d_mm:.0f}mm", (abs_cx - 40, abs_cy - abs_r - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

# 手机中心十字 / Phone center crosshair
cv2.line(annotated, (int(cx_phone) - 20, int(cy_phone)), (int(cx_phone) + 20, int(cy_phone)), (0, 0, 255), 1)
cv2.line(annotated, (int(cx_phone), int(cy_phone) - 20), (int(cx_phone), int(cy_phone) + 20), (0, 0, 255), 1)

# 标注尺寸 / Dimension annotations
cv2.putText(annotated, f"{PHONE_W:.1f}mm", (x_phone + w_phone // 3, y_phone - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
cv2.putText(annotated, f"{PHONE_L:.1f}mm", (x_phone - 60, y_phone + h_phone // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

result_path = os.path.join(output_dir, "photo_annotated.png")
cv2.imwrite(result_path, annotated)
print(f"\n标注图保存 / Annotated: {result_path}")

# ===== Step 6: 参数对比汇总 / Parameter comparison summary =====
print("\n" + "=" * 60)
print("参数对比汇总 / Parameter Comparison Summary")
print("=" * 60)
print(f"{'参数':<12} {'照片提取':>10} {'当前代码':>10} {'偏差':>8}")
print("-" * 60)
if cam_circle is not None:
    print(f"{'CAM_CX':<12} {cam_cx_model:>+10.1f} {16.0:>+10.1f} {cam_cx_model - 16.0:>+8.1f}")
    print(f"{'CAM_CY':<12} {cam_cy_mm:>+10.1f} {60.0:>+10.1f} {cam_cy_mm - 60.0:>+8.1f}")
    print(f"{'CAM_D':<12} {cam_d_mm:>10.1f} {34.0:>10.1f} {cam_d_mm - 34.0:>+8.1f}")
if flash_found:
    print(f"{'FLASH_DX':<12} {flash_dx_model:>+10.1f} {-21.0:>+10.1f} {flash_dx_model - (-21.0):>+8.1f}")
    print(f"{'FLASH_DY':<12} {flash_dy_model:>+10.1f} {1.0:>+10.1f} {flash_dy_model - 1.0:>+8.1f}")
    print(f"{'FLASH_L':<12} {flash_long:>10.1f} {7.0:>10.1f} {flash_long - 7.0:>+8.1f}")
    print(f"{'FLASH_W':<12} {flash_short:>10.1f} {2.5:>10.1f} {flash_short - 2.5:>+8.1f}")
print("=" * 60)
