# 搜索计划：SG90 舵机支架（SG90 Bracket）

## 目标
- 构建 SG90 舵机 + M3 螺丝 + 608ZZ 轴承 的支架
- 生成可装配的 STEP 文件

## 已知参数（来自 data-sources/ — 全部命中，无须搜索）

### SG90 舵机（data-sources/servos.yaml:SG90，confidence=4/5）
- body: 22.8 × 12.2 × 22.7 mm（长×宽×高）
- 安装耳：ear_width_total=32.2mm, ear_thickness=2.5mm, ear_z_offset=15.5mm
- 安装孔：d=2.0mm, pitch=28.0mm
- FDM 打印间隙推荐：+0.2~0.3mm/侧

### M3 螺丝（data-sources/fasteners.yaml:M3_ISO4762，confidence=5/5）
- head: d=5.5, h=3.0, hex_key=2.5 mm
- clearance_hole.medium_fit: 3.4 mm（3D 打印推荐）
- counterbore: d=6.0, depth=3.3 mm
- 热压铜螺母预孔：⌀4.0 mm

### 608ZZ 轴承（data-sources/bearings.yaml:608ZZ，confidence=5/5）
- 内径 8.0 / 外径 22.0 / 宽度 7.0 mm
- 3D 打印压入孔：⌀21.8 mm（过盈 0.2mm）

## 搜索来源
（无 — 所有标准件已命中本地数据源，本次 R2 零 WebSearch）
