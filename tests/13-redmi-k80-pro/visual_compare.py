"""
Layer 2 视觉验证：OpenCV 特征提取 + 对比
Visual verification: OpenCV feature extraction + comparison

对比参考照片（背面）与模型 BOTTOM 截图（旋转 180° 得到 USB 朝下的正确背面视角）
Compare reference back photo vs model BOTTOM screenshot (rotated 180° for USB-down orientation)
"""

import cv2
import numpy as np
import os

output_dir = os.path.join(os.path.dirname(__file__), "output")

# ===== 加载图像 / Load images =====
ref_path = os.path.join(output_dir, "截屏2026-04-17 14.44.52.png")
model_path = os.path.join(output_dir, "k80_pro_case_BACK_PROPER.png")

ref_img = cv2.imread(ref_path)
model_img = cv2.imread(model_path)

assert ref_img is not None, f"Cannot load reference: {ref_path}"
assert model_img is not None, f"Cannot load model: {model_path}"

# BACK_PROPER 已是正确背面视角（USB 朝下），无需旋转
# BACK_PROPER is already correct back view (USB at bottom), no rotation needed
model_rot = model_img

# ===== 转灰度 + 边缘检测 / Grayscale + edge detection =====
ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
model_gray = cv2.cvtColor(model_rot, cv2.COLOR_BGR2GRAY)

ref_edges = cv2.Canny(ref_gray, 50, 150)
model_edges = cv2.Canny(model_gray, 50, 150)

# ===== 圆检测（摄像头模组）/ Circle detection (camera module) =====
# 参考照片：只找最大的圆（摄像头模组）/ Reference: find the biggest circle (camera module)
ref_h, ref_w = ref_gray.shape[:2]
ref_min_r = int(ref_w * 0.15)
ref_max_r = int(ref_w * 0.45)
ref_circles = cv2.HoughCircles(
    ref_gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=ref_w // 3,
    param1=80, param2=50, minRadius=ref_min_r, maxRadius=ref_max_r
)
# 模型截图：白色背景上的圆 / Model: circle on white background
model_h, model_w = model_gray.shape[:2]
model_min_r = int(model_w * 0.05)
model_max_r = int(model_w * 0.25)
model_circles = cv2.HoughCircles(
    model_gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=model_w // 4,
    param1=80, param2=40, minRadius=model_min_r, maxRadius=model_max_r
)

# ===== 轮廓检测 / Contour detection =====
ref_contours, _ = cv2.findContours(ref_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
model_contours, _ = cv2.findContours(model_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# ===== 标注图像 / Annotate images =====
ref_annotated = ref_img.copy()
model_annotated = model_rot.copy()

# 标注圆 / Draw detected circles
def annotate_circles(img, circles, label):
    results = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i, (x, y, r) in enumerate(circles[0]):
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)
            cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
            h, w = img.shape[:2]
            cx_ratio = x / w
            cy_ratio = y / h
            r_ratio = r / w
            info = f"{label} circle {i}: center=({cx_ratio:.2f}, {cy_ratio:.2f}) r_ratio={r_ratio:.3f}"
            print(info)
            cv2.putText(img, f"r={r}px ({r_ratio:.3f}W)",
                        (int(x) - 40, int(y) - int(r) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            results.append({"cx": cx_ratio, "cy": cy_ratio, "r": r_ratio})
    return results

print("\n===== Circle Detection =====")
ref_results = annotate_circles(ref_annotated, ref_circles, "REF")
model_results = annotate_circles(model_annotated, model_circles, "MODEL")

# ===== 轮廓标注 / Draw contours =====
ref_contours_big = [c for c in ref_contours if cv2.contourArea(c) > 500]
model_contours_big = [c for c in model_contours if cv2.contourArea(c) > 500]
cv2.drawContours(ref_annotated, ref_contours_big, -1, (255, 0, 0), 1)
cv2.drawContours(model_annotated, model_contours_big, -1, (255, 0, 0), 1)

print(f"\nREF contours (area>500): {len(ref_contours_big)}")
print(f"MODEL contours (area>500): {len(model_contours_big)}")

# ===== 归一化位置比较 / Normalized position comparison =====
print("\n===== Feature Position Comparison =====")
if ref_results and model_results:
    ref_cam = ref_results[0]
    model_cam = model_results[0]
    dx = abs(ref_cam["cx"] - model_cam["cx"])
    dy = abs(ref_cam["cy"] - model_cam["cy"])
    dr = abs(ref_cam["r"] - model_cam["r"])
    print(f"Camera circle offset: dx={dx:.3f} dy={dy:.3f} dr={dr:.3f}")
    tol = 0.08
    cam_pass = dx < tol and dy < tol and dr < tol
    print(f"Camera position: {'PASS' if cam_pass else 'FAIL'} (tol={tol})")
else:
    print("WARNING: Circle detection incomplete")

# ===== 缩放拼接对比图 / Scale and create side-by-side comparison =====
target_h = 800
ref_scale = target_h / ref_annotated.shape[0]
model_scale = target_h / model_annotated.shape[0]
ref_resized = cv2.resize(ref_annotated, None, fx=ref_scale, fy=ref_scale)
model_resized = cv2.resize(model_annotated, None, fx=model_scale, fy=model_scale)

# 添加标题 / Add titles
def add_title(img, text):
    h, w = img.shape[:2]
    title_bar = np.zeros((40, w, 3), dtype=np.uint8)
    cv2.putText(title_bar, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return np.vstack([title_bar, img])

ref_titled = add_title(ref_resized, "Reference Photo (back)")
model_titled = add_title(model_resized, "Model (BACK_PROPER)")

# 高度对齐 / Align heights
max_h = max(ref_titled.shape[0], model_titled.shape[0])
def pad_height(img, target_h):
    if img.shape[0] < target_h:
        pad = np.zeros((target_h - img.shape[0], img.shape[1], 3), dtype=np.uint8)
        return np.vstack([img, pad])
    return img

ref_titled = pad_height(ref_titled, max_h)
model_titled = pad_height(model_titled, max_h)

comparison = np.hstack([ref_titled, model_titled])

comp_path = os.path.join(output_dir, "visual_comparison.png")
cv2.imwrite(comp_path, comparison)
print(f"\nComparison saved: {comp_path}")

# ===== 边缘对比图 / Edge comparison =====
ref_edges_color = cv2.cvtColor(ref_edges, cv2.COLOR_GRAY2BGR)
model_edges_color = cv2.cvtColor(model_edges, cv2.COLOR_GRAY2BGR)
ref_edges_resized = cv2.resize(ref_edges_color, None, fx=ref_scale, fy=ref_scale)
model_edges_resized = cv2.resize(model_edges_color, None, fx=model_scale, fy=model_scale)
ref_edges_titled = add_title(ref_edges_resized, "REF edges")
model_edges_titled = add_title(model_edges_resized, "MODEL edges")
ref_edges_titled = pad_height(ref_edges_titled, max_h)
model_edges_titled = pad_height(model_edges_titled, max_h)
edge_comparison = np.hstack([ref_edges_titled, model_edges_titled])
edge_path = os.path.join(output_dir, "edge_comparison.png")
cv2.imwrite(edge_path, edge_comparison)
print(f"Edge comparison saved: {edge_path}")
