# 搜索计划：ESP32-S3-DevKitC-1

## 目标
- 获取 PCB 三维尺寸（L×W×T）+ 板高（含 ESP32-S3-WROOM 模块与排针）
- 获取 4 个 M2 安装孔的中心间距与孔径
- 获取 USB-C 接口 / Boot / Reset 按键 / RGB LED 在板上的位置与尺寸
- 获取官方产品图（正面 + 背面 + 侧面至少各 1 张）
- 尝试获取 STEP / PCB 机械图

## 搜索来源
1. Espressif 官方文档（硬件参考手册）
   - https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html
   - 获取：整板尺寸、布局图、接口位置
2. Espressif 官方 Schematic + PCB 机械图 PDF
   - https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DEVKITC-1_V1_20210312A.pdf
   - https://dl.espressif.com/dl/schematics/PCB_ESP32-S3-DEVKITC-1_V1_20210312AA.pdf
   - 获取：板厚、元件高度、安装孔精确坐标、接口位置精确 XY
3. espressif/esp-dev-kits GitHub 仓（机械图 DXF / STEP 若有）
   - https://github.com/espressif/esp-dev-kits
4. GrabCAD / Printables（社区现成 STEP 兜底）
   - "ESP32-S3-DevKitC-1 STEP"

## 预期资料类型
- 官方 PDF 机械图（★★★★★ 置信度）
- 官网规格文本（★★★★★ 置信度）
- 社区 STEP 模型（★★★★，交叉验证）
- 产品图 JPG（★★★，用于视觉对齐）

## 分叉判定预报
- 本次计划做 Layer 2 视觉对比 → R2.7 必做
- 若官方机械图 PDF 提供精确尺寸，则 R2.5 可能无需像素反推（视 R2 结果而定）
