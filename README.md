[English](README_EN.md) | 中文

# build123d CAD Skill Test

build123d CAD Skill 的测试用例集合，用来验证参数化建模、装配、标准件复用、OCP Viewer 可视化、URDF/GLB 动画和 Skill 行为回归。

当前仓库包含 **24 个已落地测试** 和 **15 个待开发场景**。已完成部分覆盖从基础零件、曲面、关节、参考物建模，到舵机安装座、ESP32-S3 外壳、四足 2-DOF 单腿、行星齿轮动画等综合案例。

## 快速导航

| 目标 | 推荐入口 |
|------|----------|
| 看基础 API 用法 | `tests/01-enclosure-box` ~ `tests/10-sweep-twist` |
| 看装配 / 关节 / 动画 | `tests/11-revolute-hinge`, `tests/12-quadruped-leg`, `tests/20-ball-joint` |
| 看 parts-lib 标件优先流程 | `tests/21-servo-mount`, `tests/23-quadruped-leg-2dof`, `tests/24-planetary-gear` |
| 看参考物建模 + 参数合同 | `tests/13-redmi-k80-pro`, `tests/14-xiaomi-k70-case`, `tests/22-esp32-s3-devkitc-enclosure` |
| 看 URDF / GLB 动画链路 | `tests/24-planetary-gear/planetary_anim_test.py`, `tests/24-planetary-gear/animated_material.py` |
| 看 Skill 行为回归 | `tests/15-playbook-dryrun` ~ `tests/19-hard-halt-dryrun` |

## 环境要求

- Python 3.13+
- build123d 0.10.x
- cadquery-ocp
- ocp-vscode（OCP CAD Viewer 扩展）
- Pillow（GIF 生成）
- [build123d-parts-lib](https://github.com/baibai2013/build123d-parts-lib)（标准件实体库，submodule 接入）

## 初始化（含 parts-lib 拉取）

```bash
git clone <this-repo>
cd build123d-cad-skill-test
git submodule update --init --recursive      # 拉 parts-lib
python3 -m venv .venv && source .venv/bin/activate
pip install build123d ocp-vscode pillow
pip install -e lib/parts-lib                 # editable 装 parts-lib
```

**parts-lib 使用示例**：

```python
from build123d_parts_lib.parts.servos.sg90            import make_sg90
from build123d_parts_lib.parts.fasteners.m3_iso4762   import make_m3_screw
from build123d_parts_lib.modules.threaded_insert_boss import make_m3_boss
from build123d_parts_lib.generators.clearance         import get_clearance_diameter
```

> **工作规则**：标件优先从 parts-lib 导入；新的通用标件通过 OCP 验证后沉淀回 parts-lib。

## 运行测试

```bash
cd tests/01-enclosure-box && python enclosure_box.py
cd tests/02-spur-gear && python gear_test.py
cd tests/20-ball-joint && python ball_joint.py
cd tests/22-esp32-s3-devkitc-enclosure && python esp32_s3_enclosure.py
cd tests/22-esp32-s3-devkitc-enclosure && python esp32_s3_enclosure_exploded.py
cd tests/23-quadruped-leg-2dof && python quadruped_leg.py
cd tests/24-planetary-gear && python planetary_test.py
cd tests/24-planetary-gear && python planetary_anim_test.py
```

输出文件生成在各测试目录的 `output/` 下。

---

## 测试清单

### 一、零件建模（Parts）

#### 01-enclosure-box — 外壳盒（抽壳 + 扣合盖 + 文字 + 装配 + 爆炸动画）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box + fillet + offset 抽壳 | :white_check_mark: | 外形 80x60x40mm，壁厚 2.5mm，竖边 R2 圆角 |
| 内壁唇边台阶（lip） | :white_check_mark: | lip_h=3mm, lip_inset=1.2mm |
| 盖子 + 底部凸台（snap-fit tab） | :white_check_mark: | lid_thick=3mm, tab 插入台阶，间隙 0.3mm |
| 顶面 Text 凸起文字 | :white_check_mark: | "baibai" 凸起 1mm，宽度约盖子 70% |
| 装配体定位（Pos 变换） | :white_check_mark: | 盖子定位到盒体顶面 |
| 爆炸图（Compound 导出） | :white_check_mark: | 爆炸距离 30mm |
| OCP Animation 爆炸动画 | :white_check_mark: | 炸1s - 停3s - 合1s - 停3s（8s循环） |
| save_screenshot 逐帧截屏 -> GIF | :white_check_mark: | 80帧 10fps，output/enclosure_explode.gif |

**涉及 API**：`Box`, `fillet`, `offset`(抽壳), `Rectangle`, `extrude`, `Text`, `Pos`, `Compound`, `export_step`, `export_stl`, `Animation`, `save_screenshot`

#### 02-spur-gear — 直齿圆柱齿轮（渐开线 + 逐齿融合）

| 功能 | 状态 | 说明 |
|------|------|------|
| 渐开线齿形计算 | :white_check_mark: | 模数 2，齿数 20，压力角 20 度 |
| 根圆柱 + 逐齿 Algebra Mode 融合 | :white_check_mark: | 避免大型非凸多边形 OCP 渲染问题 |
| 中心轴孔 + 键槽 | :white_check_mark: | 轴孔 R4mm，键槽宽 2mm |
| OCP Viewer 预览 | :white_check_mark: | show() 直接预览 |

**涉及 API**：`Cylinder`, `Wire.make_polygon`, `BRepBuilderAPI_MakeFace`, `BuildPart`, `BuildSketch`, `add`, `extrude`, `Box`, Algebra Mode (`+`, `-`), `export_step`

#### 03-mounting-plate — 安装板（基础入门）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box + GridLocations 孔阵列 | :white_check_mark: | 100×80×10mm，四角 M5 通孔 |
| fillet 顶面圆角 | :white_check_mark: | 顶面边 R3 圆角 |
| 选择器定位（sort_by 顶面） | :white_check_mark: | `faces().sort_by(Axis.Z)[-1]` 取顶面 |
| 参数化验证 | :white_check_mark: | 修改 margin 参数后孔位跟随 |

**涉及 API**：`Box`, `GridLocations`, `Hole`, `fillet`, `sort_by`, `export_step`

#### 04-flange — 法兰盘（Cylinder + 极坐标沉头孔阵列）

| 功能 | 状态 | 说明 |
|------|------|------|
| Cylinder + 中心通孔 | :white_check_mark: | 外径 80mm，高 8mm，中心孔 R15mm |
| PolarLocations 螺栓孔阵列 | :white_check_mark: | PCD 60mm，6 孔均布 |
| CounterBoreHole 沉头孔 | :white_check_mark: | 通孔 R4mm，沉头 R6.5mm，深 4mm |

**涉及 API**：`Cylinder`, `Hole`, `PolarLocations`, `CounterBoreHole`, `export_step`

#### 05-stepped-shaft — 阶梯轴（Polyline revolve + 参数化键槽 + chamfer）

| 功能 | 状态 | 说明 |
|------|------|------|
| BuildSketch(Plane.XZ) + revolve | :white_check_mark: | 多段阶梯半截面 Polyline 绕 Z 轴旋转 360° |
| 参数化键槽切割（key_angle 可旋转） | :white_check_mark: | 解析平面公式驱动键槽方位，默认 0°（-Y 面） |
| chamfer 两端倒角 | :white_check_mark: | 两端最小圆弧边各 0.5mm 倒角 |

**涉及 API**：`BuildSketch`, `Plane.XZ`, `Polyline`, `make_face`, `revolve`, `Plane(origin, x_dir, z_dir)`, `extrude(Mode.SUBTRACT)`, `chamfer`, `export_step`

#### 06-pipe-elbow — 弯管接头（Sweep 路径扫掠 + 两端连接口）

| 功能 | 状态 | 说明 |
|------|------|------|
| Edge.make_circle 弧线路径 | :white_check_mark: | XZ 平面 90° 弧，中心线半径 40mm |
| 空心截面 sweep | :white_check_mark: | 外径 R15mm，壁厚 2mm，内径 R13mm |
| 路径切线 Plane 构造 | :white_check_mark: | `Plane(path @ t, z_dir=path % t)`，t=0/1 |
| 两端连接口（大径管箍） | :white_check_mark: | hub_r=18mm，长 8mm，向外延伸用于管道对接 |

**涉及 API**：`Edge.make_circle`, `sweep`, `Circle`, `Mode.SUBTRACT`, `Plane`, `extrude`, `export_step`

#### 07-heat-sink — 针状散热片（Pin-Fin，GridLocations 针阵列）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box 底板 + 顶面定位 | :white_check_mark: | 30×30×3mm 底板 |
| GridLocations 针阵列 | :white_check_mark: | 6×6 方形针柱，高 8mm，截面 2×2mm，四面进风 |
| 选择器取顶面作草图平面 | :white_check_mark: | `sort_by(Axis.Z)[-1]` |

**涉及 API**：`Box`, `GridLocations`, `Rectangle`, `extrude`, `sort_by`, `export_step`

---

### 二、曲面建模（Surface）

#### 08-loft-transition — 多截面放样过渡

| 功能 | 状态 | 说明 |
|------|------|------|
| 多平面 BuildSketch + loft | :white_check_mark: | 圆 → 方 → 圆 三截面放样 |
| Plane.XY.offset 多高度截面 | :white_check_mark: | z=0/30/60 三个高度截面 |
| 曲面连续性检查 | :white_check_mark: | G1 连续性体积验证（56301 mm³） |

**涉及 API**：`BuildSketch`, `Circle`, `Rectangle`, `loft`, `Plane.XY.offset`, `export_step`

#### 09-organic-shell — 有机曲面外壳

| 功能 | 状态 | 说明 |
|------|------|------|
| 多截面 Loft（5 个椭圆截面） | :white_check_mark: | 变截面流线型壳体，体积 10920 mm³ |
| offset(openings=) 抽壳 | :white_check_mark: | 壁厚 2mm，底面开放 |
| Ellipse 参数化截面 | :white_check_mark: | 长短轴随高度变化（z=0~60） |

**涉及 API**：`Ellipse`, `loft`, `offset(openings=)`, `Plane.XY.offset`, `export_step`

#### 10-sweep-twist — 扭转扫掠

| 功能 | 状态 | 说明 |
|------|------|------|
| 直线路径 + 截面扭转 | :white_check_mark: | 矩形截面（20×10mm）扭转 90°，体积 13000 mm³ |
| sweep multisection 双截面 | :white_check_mark: | 首尾两截面方向不同，线性插值过渡 |
| Transition.ROUND 参数 | :white_check_mark: | `sweep(path, multisection=True, transition=Transition.ROUND)` |

**涉及 API**：`sweep`, `Edge.make_line`, `Plane(origin, x_dir, z_dir)`, `Transition`, `Rectangle`, `export_step`

---

### 三、关节装配（Joints）

#### 11-revolute-hinge — 动物骨骼膝关节 + 旋转动画

| 功能 | 状态 | 说明 |
|------|------|------|
| 大腿骨（Algebra Mode） | :white_check_mark: | 圆柱骨干(r=5, h=50) + 两端球形关节头，hip_r=8, joint_r=9 |
| 小腿骨（Algebra Mode） | :white_check_mark: | 骨干(r=4, h=45) + 两端球头，本地原点 = 膝关节轴心 |
| RigidJoint 固定膝点 | :white_check_mark: | 大腿骨 z=0 处固定关节点 |
| RevoluteJoint 膝关节 | :white_check_mark: | Y轴旋转，angular_range=(-120°, 10°) |
| connect_to 姿态定位 | :white_check_mark: | `j_thigh.connect_to(j_shin, angle=0/−60/−110)` |
| 逐帧截图 GIF 动画 | :white_check_mark: | 46帧 0°→−110°→0° 循环，Pillow 合成 GIF |
| OCP Animation 轨道 | :white_check_mark: | `add_track("ry")` 屈伸 6s 循环 |

**涉及 API**：`Cylinder(align=Align.MIN/MAX)`, `Sphere`, Algebra Mode(`+`), `RigidJoint`, `RevoluteJoint`, `connect_to`, `Compound`, `Animation`, `add_track`, `save_screenshot`, `export_step`

#### 12-quadruped-leg — 四足腿链（7 部件板状结构 + 参考图驱动）

| 功能 | 状态 | 说明 |
|------|------|------|
| 7 部件板状结构 | :white_check_mark: | hip_mount + femur + tibia + metatarsus + foot_pad + 2 ligaments |
| 锥形板材造型 | :white_check_mark: | Polyline 梯形轮廓 + fillet，匹配参考图 CNC 铝板 |
| 弧形脚掌 | :white_check_mark: | ThreePointArc 弧底 + 扇形扩展（ref: 182mm → 36mm） |
| RevoluteJoint 4 级串联 | :white_check_mark: | hip(±45°) → knee(-90°~0°) → ankle(±30°) → foot(fixed) |
| FK 韧带实时跟随 | :white_check_mark: | Joint.location.position 读取真实世界坐标，韧带紧贴膝关节 |
| 行走循环 GIF 动画 | :white_check_mark: | 40 帧 Peter Corke 步态（swing 40% / stance 60%） |
| OCP Animation 轨道 | :white_check_mark: | FK 平移关键帧，5 刚体独立轨道 |
| tkinter 交互控制 | :white_check_mark: | 滑条 × 3 + 预设按钮 + OCP 实时更新（Route A） |
| PyBullet 物理仿真 | :white_check_mark: | URDF + 重力/碰撞/关节力矩（Route B） |
| ipywidgets 交互 | :white_check_mark: | Jupyter slider 控制（备选交互方式） |
| STEP 重导入验证 | :white_check_mark: | 体积偏差 0.000000% |

**参考尺寸（1:5 缩放）**：Femur 245→50mm（锥形 18→14mm），Tibia 220→45mm（锥形 16→12mm），Foot 84×182→14×36mm（弧形）

**涉及 API**：`Polyline`, `make_face`, `fillet(vertices)`, `ThreePointArc`, `RevoluteJoint`, `RigidJoint`, `connect_to`, `Compound`, `PolarLocations`, `Hole`, `Animation`, `add_track`, `save_screenshot`, `export_step`

#### 20-ball-joint — 球铰万向节（BallJoint 3 DOF）

| 功能 | 状态 | 说明 |
|------|------|------|
| BallJoint 3 DOF 连接 | :white_check_mark: | `angular_range=((-45,45),(-45,45),(0,360))` |
| RigidJoint + BallJoint 对接 | :white_check_mark: | 底座 RigidJoint 锚点 + 球铰臂 BallJoint |
| 球碗底座（Box + 半球形凹穴） | :white_check_mark: | 40×40×15mm，cup_r=10mm，fillet 竖边 R3 |
| 球铰臂（Sphere + Cylinder 融合） | :white_check_mark: | ball_r=9mm，arm_r=4mm，arm_len=45mm，5mm 重叠保融合 |
| 三姿态 connect_to 并排展示 | :white_check_mark: | 直立(0°) / X 倾斜 30° / X+Z 倾斜 30°+45° |
| 三层验证（BRep/体积/STEP） | :white_check_mark: | 体积 socket≈21685mm³，ball_arm≈5087mm³，STEP 精度 ✅ |
| OCP 三姿态并排预览 | :white_check_mark: | `render_joints=True`，端口自动探测 |

**涉及 API**：`BallJoint`, `RigidJoint`, `connect_to`, `Rotation`, `Sphere`, `Cylinder`, `Box`, `fillet`, `export_step`, `import_step`

---

### 四、参考物建模（Reference Products）

#### 13-redmi-k80-pro — 红米 K80 Pro 外形参考模型

| 功能 | 状态 | 说明 |
|------|------|------|
| 参考图驱动尺寸反推（GSMArena × 3） | :white_check_mark: | R1 经验检索 + R2 多源交叉验证 |
| params.md 参数合同 + contract.yaml | :white_check_mark: | Layer 0 YAML 合同生成，约束覆盖率 100% |
| build123d 精建外形（圆角直板机身） | :white_check_mark: | 161×75×8mm，摄像头矩形岛、侧边曲面 |
| Layer 1 验证（体积/bbox/BRep） | :white_check_mark: | 4 阶段流水线，自动修复循环 ≤3 轮 |
| Layer 2 视觉比对（截图 + AI 对比） | :white_check_mark: | 多角度截图与参考图比对，偏差分析 |
| extract_params.py 尺寸提取工具 | :white_check_mark: | 从图片自动提取 + 交叉验证参数 |
| visual_compare.py 视觉比对工具 | :white_check_mark: | 4 种后端自动降级（AI → OpenCV → manual） |

**涉及 API**：`Box`, `fillet`, `offset(openings=)`, `Hole`, `extrude(Mode.SUBTRACT)`, `export_step`

#### 14-xiaomi-k70-case — 小米 K70 手机壳（FDM 3D 打印）

| 功能 | 状态 | 说明 |
|------|------|------|
| 手机壳参数化建模（FDM 工艺） | :white_check_mark: | K70 外形参数化，壁厚 1.5mm，镂空减重 |
| part_face_mapping.yaml 面映射 | :white_check_mark: | 每个特征面与设计意图的映射记录 |
| 相机孔 / 按键孔 / 充电口精确定位 | :white_check_mark: | 选择器定位，非硬编码坐标 |
| 3D 打印工艺约束验证 | :white_check_mark: | 壁厚 ≥1.2mm，悬臂 ≤45°，公差 +0.3mm |
| STEP 导出 + 重导入验证 | :white_check_mark: | 体积偏差 < 0.1% |

**涉及 API**：`Box`, `offset(openings=)`, `Hole`, `extrude(Mode.SUBTRACT)`, `fillet`, `export_step`

---

### 五、Playbook & Skill 验证（Dry-run）

> 本类测试均为**纯对话验证**——不跑 build123d 代码，只对照 Playbook 检查 AI 行为是否合规。

#### 15-playbook-dryrun — Playbook R1~R5 行为回归

| 场景 | 状态 | 验证点 |
|------|------|--------|
| Scenario A：完整 R1~R5（K70 壳） | :white_check_mark: | 8 个产出报告块，R2.7 不遗漏 |
| Scenario B：有 STEP + 跳 Layer 2 | :white_check_mark: | R2.5/R2.7 显式 skip，6 个报告块 |
| Scenario C：有 STEP + 要 Layer 2（陷阱） | :white_check_mark: | R2.5 skip + R2.7 执行，不混淆 |

#### 16-experience-dryrun — Experience 经验缓存行为回归

| 场景 | 状态 | 验证点 |
|------|------|--------|
| Scenario D：冷启动（无经验文件） | :white_check_mark: | R1 报 `[miss]`，R5 新建 experience 文件 |
| Scenario E：精确命中 | :white_check_mark: | R1 报 `[hit]`，参数+坑注入正确 |
| Scenario F：同类命中 | :white_check_mark: | R1 报 `[partial]`，作参考不直接复用 |

#### 17-skill-optimization-dryrun — SKILL.md 去内容化 + Quote-back 强制

| 场景 | 状态 | 验证点 |
|------|------|--------|
| Scenario G：参考物建模（R Playbook） | :white_check_mark: | AI Read Playbook，每 Step 首行有 Quote-back |
| Scenario H：单部件建模（S Playbook） | :white_check_mark: | AI Read Playbook，不凭记忆走 |
| Scenario I：多部件装配（P Playbook） | :white_check_mark: | AI Read Playbook，Phase 产出报告格式合规 |

#### 18-assembly-contract-dryrun — 装配合同 + bbox 预检

| 场景 | 状态 | 验证点 |
|------|------|--------|
| Scenario J：两关节机械臂（≥2 部件） | :white_check_mark: | Step 2e 产出 assembly_contract.yaml + precheck_bbox.md |
| Scenario K：故意漏翻译 1 条装配关系 | :white_check_mark: | 触发 FM-12，cross_refs 覆盖不全被 catch |

#### 19-hard-halt-dryrun — 确认门强制执行（halt-gate-enforcement）

| 场景 | 状态 | 验证点 |
|------|------|--------|
| Scenario L：AI 越过 S2 草图确认门 | :white_check_mark: | 触发 FM-1，回补产出 + 重出 halt |
| Scenario M：多部件 Phase 1 确认门 | :white_check_mark: | 触发 FM-13，halt 正确生效 |
| Scenario N：参考物 R3.5 视觉确认门 | :white_check_mark: | 触发 FM-10，回补正确 |

**结构核对**：10/10 全通过 ✅（SKILL.md §确认门执行契约 + 3 Playbook FM 条款）

---

### 七、安装实战（Mounting）

#### 21-servo-mount — SG90 舵机安装座（extrude subtract-only + 精确腔体）

| 功能 | 状态 | 说明 |
|------|------|------|
| 舵机本体腔（从顶面向下切） | :white_check_mark: | SG90 标准尺寸 22.8×12.2×22.7mm，间隙 0.3mm，壁厚 2.5mm |
| 耳片台阶槽（两侧开槽） | :white_check_mark: | 耳宽 32.2mm，耳厚 2.5mm，草图差集 `Rectangle - Rectangle` |
| M2 攻丝孔（4 个） | :white_check_mark: | 孔距 27.6mm，从顶面穿入耳片，深 ear_t + 2mm |
| 线缆出口（-X 侧面） | :white_check_mark: | 9×6mm 矩形出口，墙厚方向贯通 |
| 底面 M3 固定孔（4 角） | :white_check_mark: | 安装座固定到机架，距外壁 5mm |
| 外廓竖边圆角 | :white_check_mark: | R1.5mm，`fillet(filter_by(Axis.Z))` |
| 三层验证（BRep/bbox/STEP） | :white_check_mark: | bbox 28.4×37.8×25.2mm，填充率 70.3%，STEP 精度 ✅ |

**涉及 API**：`Box`, `Rectangle`, `extrude(Mode.SUBTRACT)`, `fillet`, `filter_by(Axis.Z)`, `export_step`, `import_step`

#### 22-esp32-s3-devkitc-enclosure — ESP32-S3-DevKitC-1 开发板外壳（参考物建模 + 2 部件 snap-fit）

| 功能 | 状态 | 说明 |
|------|------|------|
| 官方 DXF 机械图反推 PCB 尺寸 | :white_check_mark: | 62.74×25.40×1.6mm，无安装孔（社区流传错误），2×Micro-USB（非 USB-C） |
| 坐标契约（pcb_origin_world）| :white_check_mark: | PCB 本地→世界坐标 Location 变换，消灭硬编码派生坐标 |
| 底壳 + 盖板夹持方案 | :white_check_mark: | 4 角低台（高 4mm）+ 盖板压舌（凸 0.5mm）夹 PCB，无需螺孔 |
| `offset` 抽壳（shell 替代） | :white_check_mark: | 盖板 `offset(amount=-lid_t, openings=bottom_face)` |
| 2 × USB 胶囊开孔 | :white_check_mark: | `SlotOverall(10, 5, rotation=90)` USB-C 视觉，派生自 J2(6.00,3.66) + J4(19.40,3.66) |
| Boot/Reset 按键压柱 | :white_check_mark: | 3mm 柔性突柱，派生自 SW1(6.76,13.79) + SW2(17.17,13.92) |
| RGB LED 透光孔 + 3 条散热槽 | :white_check_mark: | LED d=3.5mm (5.08,31.60)，顶板散热 2×20mm×3 |
| Snap-fit 卡扣（左右短边）| :white_check_mark: | 悬臂 6mm + 头厚 0.8mm + 导角 0.4mm |
| **底面 4 × M3 固定孔** | :white_check_mark: | 1.6mm 半径，位置 (±22, ±10) 避开 4 角低台 |
| Layer 0 参数合同 + 静态检查 | :white_check_mark: | 9 features / 47 constraints / 0 conflicts |
| 三层验证（BRep/体积/STEP） | :white_check_mark: | 底壳 6248mm³ / 盖板 7196mm³ / STEP 精度 0.0000% |
| 2 部件装配 + 爆炸动画 GIF | :white_check_mark: | 3 层（bottom / PCB+模块一体 / lid）16s 循环，160 帧@10fps |

**涉及 API**：`Box`, `Cylinder`, `SlotOverall(rotation=90)`, `Circle`, `offset(openings=)`, `extrude(Mode.SUBTRACT)`, `BuildSketch(face)`, `fillet`, `import_step`, `Location`, `Compound`, `Animation.add_track`, `animation.set_relative_time`

**Dave Cowden review 沉淀**：params.md + contract.yaml 经 2 轮 review：修正 body_ref 自循环、加坐标契约节、盖板净空按"焊/不焊排针"分裂、删冗余派生参数、snap-fit 补悬臂长度

#### 23-quadruped-leg-2dof — 四足机器人 2-DOF 单腿装配（parts-lib 优先）

| 功能 | 状态 | 说明 |
|------|------|------|
| SG90 舵机 × 2 | :white_check_mark: | `make_sg90()` 标件导入，髋/膝双舵机布局 |
| SG90 安装座 × 2 | :white_check_mark: | `make_sg90_bracket()`，wall_thickness=2.5mm，print_clearance=0.3mm |
| 大腿 / 小腿连杆 | :white_check_mark: | `make_leg_segment()`，FEMUR_LEN=70mm，TIBIA_LEN=55mm |
| 半球脚垫 | :white_check_mark: | `make_foot_cap()`，底部削平，脚杆柄长 6mm |
| M3 螺丝可视化 | :white_check_mark: | parts-lib M3 螺丝用于髋支架固定展示 |
| 直接变换装配 | :white_check_mark: | `Pos` / `Rot` 定位髋支架、股骨、膝支架、胫骨、脚垫 |
| 三层验证 | :white_check_mark: | BRep 有效性、体积/bbox 范围、STEP 导出重导入偏差 < 0.1% |
| OCP Viewer 预览 | :white_check_mark: | 多对象 names/colors 展示，自动探测 OCP 端口 |

**涉及 API**：`Compound`, `Pos`, `Rot`, `Location`, `export_step`, `import_step`, `show`, `Camera`, parts-lib `make_sg90`, `make_sg90_bracket`, `make_leg_segment`, `make_foot_cap`, `make_m3_screw`

#### pcb-enclosure — PCB 壳体（带螺孔版，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box + shell 抽壳 | :x: | 适用于含 M2.5 安装孔的 PCB |
| M2.5 铜柱（GridLocations） | :x: | 4 角铜柱对齐 PCB 安装孔 |
| USB-C 接口开口 | :x: | 侧面减材料，定位到 PCB 高度 |
| 散热通风槽 | :x: | 底面/侧面条形开口 |
| 卡扣盖板 | :x: | snap-fit 卡扣 + 装配预览 |

**涉及 API**：`Box`, `shell`, `GridLocations`, `Cylinder`, `Rectangle`, `extrude(Mode.SUBTRACT)`, `Pos`, `Compound`, `export_step`

#### sensor-bracket — 传感器支架（HC-SR04）（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| L 型支架底板 | :x: | 带安装孔的底板 |
| 双圆形传感器窗口 | :x: | HC-SR04 两探头中心距 26mm |
| 角度调节槽 | :x: | 长圆孔允许俯仰调节 |

**涉及 API**：`Box`, `Hole`, `Locations`, `SlotOverall`, `fillet`, `export_step`

---

### 八、OCP 可视化（Viewer）

#### show-params — show() 参数验证（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 多对象多颜色 show | :x: | `show(a, b, colors=["steelblue","orange"])` |
| names 命名 | :x: | `names=["body","lid"]` → OCP 树状结构 |
| transparent 半透明 | :x: | `alphas=[0.5, 1.0]` 半透明检查 |
| reset_camera / Camera 枚举 | :x: | `Camera.FRONT`, `Camera.ISO` |

**涉及 API**：`show`, `Camera`, `colors`, `names`, `alphas`

#### animation-explode — 爆炸动画（Animation API）（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| Animation + add_track 平移 | :x: | `add_track("/Group/name", "t", ...)` |
| 16s 循环时间轴 | :x: | 炸2s → 停10s → 合2s → 停2s |
| animate(speed) 播放 | :x: | speed=1 正常速度 |
| save_as_gif 导出 | :x: | fps=20，循环 GIF |

**涉及 API**：`Animation`, `add_track`, `animate`, `save_as_gif`

#### animation-joint — 多关节运动动画（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| RevoluteJoint 角度 → rz 轨道 | :x: | 关节旋转映射到 OCP 动画 |
| 多轨道协调 | :x: | 四腿交替步态编排 |
| 时间轴错开 | :x: | 各关节不同相位 |

**涉及 API**：`Animation`, `add_track("rz")`, `RevoluteJoint`, `show`

#### studio-material — PBR 材质渲染（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| StudioEnvironment 预设 | :x: | `show(..., preset="default")` |
| 金属 / 塑料材质 | :x: | PBR 材质赋予不同零件 |
| 截图对比 | :x: | `save_screenshot` 高质量渲染 |

**涉及 API**：`show`, `StudioEnvironment`, `save_screenshot`

---

### 九、制造工艺验证（Process）

#### print-tolerance — 3D 打印公差测试件（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 间隙配合测试（0.1~0.5mm 梯度） | :x: | 公母件配合，5 档间隙 |
| 最小壁厚验证 | :x: | 0.4 / 0.6 / 0.8 / 1.0mm 壁 |
| 悬臂角度测试 | :x: | 30° / 45° / 60° 悬臂 |
| STL 导出参数对比 | :x: | draft / standard / fine 三档精度 |

**涉及 API**：`Box`, `Cylinder`, `shell`, `export_stl`, `linear_tolerance`, `angular_tolerance`

#### laser-dxf — 激光切割 DXF 导出（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 2D 轮廓构建 | :x: | 安装板 + 内孔 + 减重槽 |
| export_dxf 导出 | :x: | 2D DXF 文件 |
| 切缝补偿（offset 轮廓） | :x: | 外扩/内缩 0.1mm |

**涉及 API**：`BuildSketch`, `Rectangle`, `Circle`, `offset`, `export_dxf`

---

### 十、运动仿真（Simulation）

#### fk-leg-chain — FK 正运动学（DH 齐次变换 + OCP 可视化，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| DH 参数定义三连杆 | :x: | d1=55mm, L1=100mm, L2=100mm |
| 齐次变换矩阵链 FK 计算 | :x: | numpy 4×4 矩阵 T01×T12×T23 |
| build123d Location 验证 | :x: | Pos*Rot 链结果与 numpy 一致 |
| OCP 可视化（关节球+骨骼线） | :x: | show() 多对象多颜色预览 |

**涉及 API**：`Sphere`, `Box`, `Pos`, `Rot`, `Location`, `show`, `export_step`, numpy `dh_matrix`

#### ik-single-leg — IK 逆运动学（解析求解 + 双构型对比，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 三连杆解析 IK（余弦定理） | :x: | 输入足端 (x,y,z) → 求 θ1,θ2,θ3 |
| 双构型对比（knee_sign ±1） | :x: | 膝正弯/反弯两种姿态 |
| FK→IK→FK 往返验证 | :x: | 误差 < 0.01mm |
| OCP 双姿态并排显示 | :x: | 两种构型偏移 150mm 对比 |

**涉及 API**：`Sphere`, `Box`, `Pos`, `show`, `export_step`, 纯 Python `ik_leg`

#### workspace-cloud — 工作空间点云（FK 遍历 + 可达性可视化，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 角度网格遍历 FK | :x: | 三轴各 15 步 → 3375 个足端点 |
| 点云下采样显示 | :x: | 随机采样 500 点避免 OCP 卡顿 |
| 肩关节标记 + 默认站姿 | :x: | 参考点 + 当前姿态对比 |

**涉及 API**：`Vertex`, `Sphere`, `Pos`, `show`, numpy FK 遍历

#### gait-generator — 步态生成器（贝塞尔轨迹 + IK + OCP 动画，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| 11 点贝塞尔摆动相轨迹 | :x: | MIT 标准 swing 曲线 |
| trot 对角步态相位表 | :x: | LF+RR 同相，RF+LR 同相 |
| IK 求解关节角度序列 | :x: | 步态→足端→IK→关节角度 |
| OCP Animation 四足动画 | :x: | 4s 循环，20fps 关键帧 |

**涉及 API**：`Box`, `Cylinder`, `Pos`, `Compound`, `Animation`, `add_track`, `animate`, `show`

#### urdf-export — URDF 导出（build123d → URDF + STL，待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| build123d 零件构建 + label | :x: | body + upper_leg + lower_leg + foot |
| URDF XML 生成（link + joint） | :x: | revolute 关节 + limit 限位 |
| STL mesh 自动导出 | :x: | 每个 link 一个 .stl 文件 |
| 质量/惯性矩估算 | :x: | volume × density → inertial 标签 |
| yourdfpy 可选验证 | :x: | 加载 URDF 检查关节轴线 |

**涉及 API**：`Box`, `Cylinder`, `Compound`, `export_stl`, `export_step`, `show`, xml.etree

---

### 十一、验证工具（Verification）

#### validate-geometry — 几何验证（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| is_valid() BRep 有效性 | :x: | 多个零件的 BRep 检查 |
| volume > 0 断言 | :x: | 体积正值验证 |
| bounding_box 尺寸断言 | :x: | 包围盒与设计值对比 |
| do_children_intersect 碰撞 | :x: | 装配体碰撞检测 |

**涉及 API**：`is_valid`, `volume`, `bounding_box`, `Compound`, `do_children_intersect`

#### export-formats — 多格式导出（待开发）

| 功能 | 状态 | 说明 |
|------|------|------|
| STEP 导出 + 回读验证 | :x: | export_step → import_step → 体积对比 |
| STL 导出 + 文件大小合理性 | :x: | 不同精度档位 |
| BREP 导出 + 回读验证 | :x: | export_brep → import_brep 无损 |
| DXF 导出 | :x: | 2D 草图导出 |

**涉及 API**：`export_step`, `export_stl`, `export_brep`, `export_dxf`, `import_step`, `import_brep`

---

### 十二、传动与动画（Transmission & Animation）

#### 24-planetary-gear — 行星齿轮组（渐开线齿轮 + URDF/GLB 动画）

| 功能 | 状态 | 说明 |
|------|------|------|
| 渐开线外齿轮封装 | :white_check_mark: | 复用 02-spur-gear 思路，封装 `make_spur_gear()` |
| 内齿圈生成 | :white_check_mark: | 环坯减外齿刀生成内齿，满足 `z_r = z_s + 2*z_p` |
| 行星架建模 | :white_check_mark: | 薄盘 + 3 个行星销孔 + 中心让位孔 |
| 啮合约束校验 | :white_check_mark: | 中心距、齿数、行星等分约束 assert 检查 |
| parts-lib 标件集成 | :white_check_mark: | 弹性销、M3 内六角螺钉、SG90 舵机驱动实体 |
| STEP + GLB sidecar 导出 | :white_check_mark: | `planetary_gear.step` + `.planetary_gear.step.glb` 供 viewer 直接渲染 |
| 可动画 URDF | :white_check_mark: | `joints.yaml` 生成 continuous + mimic 关节，viewer 中拖 `j_sun` 或 play 驱动 |
| 木纹/PBR GLB 动画 | :white_check_mark: | `animated_material.py` 生成带贴图和节点动画的 `planetary_animated.glb` |
| Headless 验证脚本 | :white_check_mark: | `verify_headless.py` / `verify_anim.py` / `verify_console.py` 检查预览链路 |

**涉及 API**：`Cylinder`, `Wire.make_polygon`, `BuildPart`, `BuildSketch`, `extrude`, `scale`, `PolarLocations`, `Compound`, `Part`, `Location`, `export_step`, `export_gltf`, `export_stl`, `yaml.safe_dump`, `pygltflib`

---

## 覆盖统计

| 类别 | 已完成 | 待开发 | 总计 |
|------|--------|--------|------|
| 零件建模 | 7 | 0 | 7 |
| 曲面建模 | 3 | 0 | 3 |
| 关节装配 | 3 | 0 | 3 |
| 参考物建模 | 2 | 0 | 2 |
| Playbook/Skill 验证 | 5 | 0 | 5 |
| 安装实战 / 机器人装配 | 3 | 2 | 5 |
| 传动与动画 | 1 | 0 | 1 |
| OCP 可视化 | 0 | 4 | 4 |
| 制造工艺 | 0 | 2 | 2 |
| 运动仿真 | 0 | 5 | 5 |
| 验证工具 | 0 | 2 | 2 |
| **合计** | **24** | **15** | **39** |

---

## 目录结构

```
build123d-cad-skill-test/
├── README.md
├── lib/
│   └── parts-lib/                # ← git submodule，baibai2013/build123d-parts-lib
│                                 #   pip install -e 后可 from build123d_parts_lib.* import
├── tests/
│   ├── 01-enclosure-box/         # ✅ 外壳盒
│   │   ├── enclosure_box.py
│   │   └── output/
│   ├── 02-spur-gear/             # ✅ 直齿轮
│   │   ├── gear_test.py
│   │   └── output/
│   ├── 03-mounting-plate/        # ✅ 安装板
│   ├── 04-flange/                # ✅ 法兰盘
│   ├── 05-stepped-shaft/         # ✅ 阶梯轴
│   ├── 06-pipe-elbow/            # ✅ 弯管接头
│   ├── 07-heat-sink/             # ✅ 散热片
│   ├── 08-loft-transition/       # ✅ 多截面放样
│   ├── 09-organic-shell/         # ✅ 有机曲面
│   ├── 10-sweep-twist/           # ✅ 扭转扫掠
│   ├── 11-revolute-hinge/        # ✅ 旋转铰链
│   ├── 12-quadruped-leg/         # ✅ 四足腿链
│   ├── 13-redmi-k80-pro/         # ✅ 参考物建模 — 红米 K80 Pro
│   ├── 14-xiaomi-k70-case/       # ✅ 参考物建模 — K70 手机壳（FDM）
│   ├── 15-playbook-dryrun/       # ✅ Playbook R1~R5 行为回归
│   ├── 16-experience-dryrun/     # ✅ Experience 经验缓存行为回归
│   ├── 17-skill-optimization-dryrun/ # ✅ SKILL.md 去内容化 + Quote-back
│   ├── 18-assembly-contract-dryrun/  # ✅ 装配合同 + bbox 预检 dryrun
│   ├── 19-hard-halt-dryrun/      # ✅ 确认门强制执行验证
│   ├── 20-ball-joint/            # ✅ 球铰万向节（BallJoint 3 DOF）
│   │   ├── ball_joint.py
│   │   └── output/
│   ├── 21-servo-mount/           # ✅ SG90 舵机安装座（subtract-only）
│   │   ├── servo_mount.py
│   │   └── output/
│   ├── 22-esp32-s3-devkitc-enclosure/  # ✅ ESP32-S3 开发板外壳（参考物 + 2 部件 snap-fit）
│   │   ├── esp32_s3_enclosure.py        # 主建模（底壳 + 盖板）
│   │   ├── esp32_s3_enclosure_exploded.py  # 爆炸动画 + GIF
│   │   ├── contract.yaml                # Layer 0 参数合同
│   │   └── output/                      # STEP × 3 + exploded_explode.gif
│   ├── 23-quadruped-leg-2dof/     # ✅ 四足 2-DOF 单腿装配（parts-lib 优先）
│   │   ├── quadruped_leg.py
│   │   └── output/                # 单件 STEP + leg_assembly.step
│   ├── 24-planetary-gear/         # ✅ 行星齿轮组（STEP / URDF / GLB 动画）
│   │   ├── planetary_test.py
│   │   ├── planetary_anim_test.py
│   │   ├── animated_material.py
│   │   ├── planetary_lib.py
│   │   └── output/                # STEP / GLB / joints.yaml / URDF 产物
│   ├── （待开发）pcb-enclosure/      # ⬜ PCB 壳体（带螺孔版）
│   ├── （待开发）sensor-bracket/     # ⬜ 传感器支架
│   ├── （待开发）show-params/        # ⬜ show() 参数
│   ├── （待开发）animation-explode/  # ⬜ 爆炸动画
│   ├── （待开发）animation-joint/    # ⬜ 关节动画
│   ├── （待开发）studio-material/    # ⬜ PBR 材质
│   ├── （待开发）print-tolerance/    # ⬜ 打印公差
│   ├── （待开发）laser-dxf/          # ⬜ 激光 DXF
│   ├── （待开发）validate-geometry/  # ⬜ 几何验证
│   ├── （待开发）export-formats/     # ⬜ 多格式导出
│   ├── （待开发）fk-leg-chain/       # ⬜ FK 正运动学
│   ├── （待开发）ik-single-leg/      # ⬜ IK 逆运动学
│   ├── （待开发）workspace-cloud/    # ⬜ 工作空间点云
│   ├── （待开发）gait-generator/     # ⬜ 步态生成器
│   └── （待开发）urdf-export/        # ⬜ URDF 导出
├── docs/                           # 设计方案与实施计划
├── references/                     # skill 参考资料的本地快照/快测
└── generated/                      # 工具脚本临时产物
```

---

## 免责声明

本仓库为 build123d CAD Skill 的功能探索与验证测试集，以记录和学习为主要目的，所有内容按现状提供。测试结果及生成模型仅供参考，OCP 视觉验证作为辅助手段，建议结合具体需求进行独立评估。

---

## License / 许可

Apache License 2.0 — 商业可用，含专利授权条款。详见 [LICENSE](LICENSE)。
