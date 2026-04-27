# ESP32-S3-DevKitC-1 原始规格

> 本文件由 cad-scraper 自动生成，日期：2026-04-27
> 所有数据均标注来源，不确定值注明置信度。

---

## 产品标识

| 字段 | 值 |
|---|---|
| 全名 | ESP32-S3-DevKitC-1 |
| 版本 | v1.1（市场上同时存在 v1.0 初始版） |
| 发布年份 | 2021（v1.0），2022-04-29（v1.1 PCB 日期） |
| 制造商 | Espressif Systems（乐鑫科技） |
| 搭载模块 | ESP32-S3-WROOM-1 / WROOM-1U / WROOM-2（可选） |
| 来源 | [官方用户指南 v1.1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html)，DXF 文件头注释 `#35632 Rev 1.1 2022.04.29` |

### v1.0 与 v1.1 主要差异

| 项目 | v1.0 | v1.1 |
|---|---|---|
| RGB LED 引脚 | GPIO48 | GPIO38 |
| 来源 | [用户指南 Hardware Revision Details 章节](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html) | 同左 |

---

## 整板三维尺寸

| 维度 | 数值 | 置信度 | 来源 |
|---|---|---|---|
| 宽（短边） | 25.40 mm | 高（官方文本标注） | DXF TEXT 标注 `25.40mm`，官方用户指南文字 |
| 长（长边） | 62.74 mm | 高（官方文本标注） | DXF TEXT 标注 `62.74mm`（实测边线坐标 62.865 含 0.5mm 圆角） |
| 厚（PCB） | 1.6 mm（标准 PCB） | 中（官方未明确标出，搜索结果一致） | 行业标准 + WebSearch 多源确认 |
| 角部圆角半径 | 0.5 mm（倒角） | 中 | DXF 边线从 (0,0.5) 到 (0.5,0) 推算 |
| 安装孔 | **无** | 高（官方 DXF 无安装孔，社区多人确认） | DXF DRILLHOLE 层无大孔，官方论坛讨论 |

> 注：25.40mm = 1 英寸，62.74mm ≈ 2.47 英寸。部分第三方资料引用 44.78×55.88mm 或 69.85×25.4mm 为其他版本尺寸，经 DXF 直接测量，本文件 v1.1 为 **25.40 × 62.74 mm**。

---

## 安装孔（4个）

**ESP32-S3-DevKitC-1 v1.1 PCB 无安装孔（No Mounting Holes）。**

| 孔 | 中心 XY | 孔径 | 来源 |
|---|---|---|---|
| H1~H4 | N/A | N/A | DXF `DRILLHOLE` 层仅含排针过孔（直径 0.65mm 及以下），无独立安装孔；官方论坛确认设计无安装孔 |

> 如需固定板卡，需使用外加夹具或 3D 打印支架。

---

## 关键元件 XY 位置

坐标系：以 PCB 左下角为原点 (0, 0)，X 轴向右，Y 轴向上，单位 mm。  
数据来源：**官方 DXF 文件** `DXF_ESP32-S3-DevKitC-1_V1.1_20220429.dxf`（直接测量，置信度高）。

| 元件 | 中心 / 参考点 XY (mm) | 高度（含封装） | 来源 |
|---|---|---|---|
| USB-to-UART 端口 (J2, Micro-USB) | 中心 (6.00, 3.66) | ~3.0 mm (Micro-USB 连接器标准) | DXF PLACEMENT_OUTLINE_TOP 框 X:[1.89,10.11] Y:[1.03,6.30]，组件标注 J2 |
| ESP32-S3 USB OTG 端口 (J4, Micro-USB/USB-B) | 中心 (19.40, 3.66) | ~3.0 mm | DXF PLACEMENT_OUTLINE_TOP 框 X:[15.29,23.51] Y:[1.03,6.30]，组件标注 J4 |
| Boot 按键 (SW1) | 参考 (6.76, 13.79)，按键体约 (7.25, 14.3) | ~1.5 mm（贴片按键） | DXF TEXT `SW1` at (6.756, 13.790)，`BOOT` 标注 at (5.867, 16.393) |
| Reset 按键 (SW2) | 参考 (17.17, 13.92)，按键体约 (17.7, 14.4) | ~1.5 mm（贴片按键） | DXF TEXT `SW2` at (17.170, 13.917)，`RESET` 标注 at (16.154, 16.395) |
| RGB LED WS2812 (GPIO38, v1.1) | 参考 (5.08, 31.60) | ~1.0 mm（5050 封装） | DXF TEXT `RGB@IO38` at (5.077, 31.598) |
| ESP32-S3-WROOM-1 模块（中心） | 中心约 (12.70, 36~38)，宽度 = 板宽 25.40mm | 模块高 3.1 mm（不含天线 PCB 部分） | 模块宽 18mm 居中于板宽 25.4mm（偏移 3.7mm），纵向上方区域；DXF PLACEMENT_OUTLINE_BOTTOM 引脚边界 Y:[6.44, 62.82] |
| 左排针 J1（22 pin） | X=1.27mm，Y=7.96~61.30mm，间距 2.54mm | 针高约 2.54 mm（标准排针） | DXF TOOL_BOT 层，22 孔确认 |
| 右排针 J3（22 pin） | X=24.13mm，Y=7.96~61.30mm，间距 2.54mm | 针高约 2.54 mm（标准排针） | DXF TOOL_BOT 层，22 孔确认 |
| 5V→3.3V LDO（稳压器） | 待反推（位于板卡背面，U2 附近） | 待反推 | DXF TEXT `U2` at (15.80, 33.31)，但 LDO 可能在背面 |
| 3.3V 电源 LED（D 系列） | 待反推（靠近电源输入端） | 待反推 | DXF 中有多个 D 标注，需结合原理图确认具体位置 |

> 注 1：J4 端口类型需进一步核实。官方用户指南描述 ESP32-S3 USB Port 为"ESP32-S3 full-speed USB OTG"，从 DXF 连接器占位尺寸（8.2mm×5.3mm）推测可能是 Micro-USB 或 USB-C。实物照片显示两个 USB 口均为 Micro-USB（原始版），或 v1.1 有一个 USB-C（待反推实物确认）。

> 注 2：所有坐标为 DXF 文件中的 TEXT/PLACEMENT 标注位置，为组件标签参考点，实际元件几何中心偏差约 ±1mm。

---

## ESP32-S3-WROOM-1 模块规格（搭载模块）

| 参数 | 数值 | 来源 |
|---|---|---|
| 尺寸（长×宽×高） | 25.5 × 18.0 × 3.1 mm（±0.35mm） | [ESP32-S3-WROOM-1 数据手册](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) |
| 天线类型（WROOM-1） | PCB 天线（板载） | 同上 |
| 天线类型（WROOM-1U） | 外置天线座（U.FL/IPEX），尺寸 18.0×19.2×3.2mm | 同上 |
| 工作温度 | -40°C 至 +85°C | 同上 |
| 重量 | ~3.3 g | 同上 |

---

## 排针引脚间距

| 参数 | 数值 | 来源 |
|---|---|---|
| 引脚间距（pitch） | 2.54 mm（标准 0.1 英寸） | DXF TEXT 标注 `2.54mm`；DXF TOOL_BOT 层实测孔间距确认 |
| 排针内侧间距（J1-J3 内边缘） | 1.27mm × 2 = 2.54mm → 两排间距 ~22.86mm（约 0.9 英寸） | DXF TOOL_BOT X=1.27 和 X=24.13，间距 22.86mm |
| 可面包板插入 | 是（占用面包板 9 列空间） | 官方文档描述 |

---

## 图片清单

| 文件名 | 内容 | 来源 URL |
|---|---|---|
| `images/official_01_front.png` | 3D 等轴渲染正视图（含 WROOM-1 模块） | `https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/_images/esp32-s3-devkitc-1-v1.1-isometric.png` |
| `images/official_02_annotated.png` | 正面实物照片（含元件编号标注） | `https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/_images/ESP32-S3-DevKitC-1_v2-annotated-photo.png` |
| `images/official_03_pinlayout.jpg` | 引脚分配图（v1.1 版本，792×540px） | `https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/_images/ESP32-S3_DevKitC-1_pinlayout_v1.1.jpg` |
| `images/official_04_systemblock.png` | 系统框图（电源、USB、ESP32-S3 连接关系） | `https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/_images/ESP32-S3-DevKitC-1_v2-SystemBlock.png` |

> 全部 4 张图片已下载成功。

---

## STEP / 机械图状态

| 类型 | 状态 | 链接 / 说明 |
|---|---|---|
| 官方尺寸 PDF | 已找到 | `https://dl.espressif.com/dl/schematics/esp_idf/DXF_ESP32-S3-DevKitC-1_V1.1_20220429.pdf`（本地缓存 124KB） |
| 官方 DXF 机械图 | 已下载分析 | `https://dl.espressif.com/dl/schematics/esp_idf/DXF_ESP32-S3-DevKitC-1_V1.1_20220429.dxf`（本地 `/tmp/esp32s3_dimensions.dxf`，743KB，已成功解析坐标） |
| 官方 PCB 布局 PDF | 已找到 | `https://dl.espressif.com/dl/schematics/PCB_ESP32-S3-DevKitC-1_V1.1_20220429.pdf`（1.2MB 图像型 PDF，文字不可提取） |
| 官方原理图 PDF | 已找到 | `https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf` |
| STEP 3D 模型（官方） | 未找到（Espressif 未提供官方 STEP） | 官方 GitHub 无 STEP 文件 |
| STEP 3D 模型（GrabCAD） | 已找到页面，需登录下载 | `https://grabcad.com/library/esp32-s3-devkitc-1-1`（社区上传，非官方，需验证尺寸） |

---

## 待反推数据

| 数据项 | 原因 | 建议方法 |
|---|---|---|
| USB 口类型（Micro-USB vs USB-C） | DXF 布局图内无类型标注，官方描述有歧义 | 查看实物照片 `official_02_annotated.png` 中 J2/J4 标注 |
| 板厚 1.6mm 确认 | DXF/PDF 均无板厚明确标注 | 查阅 PCB 布局 PDF 板材说明，或实物测量 |
| LDO 及 3.3V 指示 LED 精确位置 | DXF 坐标为大概方位，未精确确认 | 结合原理图 SCH_ESP32-S3-DevKitC-1_V1.1 追溯 U2、D 系列元件 |
| 模块在板上的 Y 轴起始位置 | 模块占位边界 PLACEMENT 未见大面积矩形 | 量测官方实物照片 + 模块数据手册焊盘尺寸反推 |
| 实物最大高度（含 USB 连接器） | 未测量，3D 建模需此值 | 实物测量或参考 USB 连接器规格书 |

---

## 参考文档

1. **官方用户指南 v1.1**：`https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html`
2. **官方 DXF 机械图**：`https://dl.espressif.com/dl/schematics/esp_idf/DXF_ESP32-S3-DevKitC-1_V1.1_20220429.dxf`
3. **官方原理图**：`https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf`
4. **官方 PCB 布局**：`https://dl.espressif.com/dl/schematics/PCB_ESP32-S3-DevKitC-1_V1.1_20220429.pdf`
5. **ESP32-S3-WROOM-1 数据手册**：`https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf`
6. **GrabCAD 社区 3D 模型**：`https://grabcad.com/library/esp32-s3-devkitc-1-1`
