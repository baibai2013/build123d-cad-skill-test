# build123d CAD Skill Test

build123d CAD Skill 的测试用例集合，验证各种建模操作和 OCP Viewer 可视化功能。

## 环境要求

- Python 3.13+
- build123d 0.10.x
- cadquery-ocp
- ocp-vscode（OCP CAD Viewer 扩展）
- Pillow（GIF 生成）

## 运行测试

```bash
cd tests/01-enclosure-box && python enclosure_box.py
cd tests/02-spur-gear && python gear_test.py
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

#### 04-flange — 法兰盘（旋转体 + 极坐标阵列）

| 功能 | 状态 | 说明 |
|------|------|------|
| Cylinder + 中心孔 | :white_check_mark: | 外径 80mm，高 8mm，中心孔 R15 |
| PolarLocations 螺栓孔阵列 | :white_check_mark: | PCD 60mm，6 孔均布 |
| CounterBoreHole 沉头孔 | :white_check_mark: | 沉头半径、沉头深度参数化 |

**涉及 API**：`Cylinder`, `Hole`, `PolarLocations`, `CounterBoreHole`, `export_step`

#### 05-stepped-shaft — 阶梯轴（旋转体 + 键槽切割）

| 功能 | 状态 | 说明 |
|------|------|------|
| BuildSketch(Plane.XZ) + revolve | :white_check_mark: | 多段阶梯轮廓旋转体 |
| 键槽切割（Mode.SUBTRACT extrude） | :white_check_mark: | 顶面定位草图减材料 |
| chamfer 端面倒角 | :white_check_mark: | 两端 0.5mm 倒角 |

**涉及 API**：`BuildSketch`, `Plane.XZ`, `Polyline`, `Line`, `make_face`, `revolve`, `chamfer`, `export_step`

#### 06-pipe-elbow — 弯管接头（Sweep 路径扫掠）

| 功能 | 状态 | 说明 |
|------|------|------|
| Edge.make_circle 弧线路径 | :x: | 弯曲半径 40mm，90° 弯管 |
| 空心截面 sweep | :x: | 外径 R15，壁厚 2mm |
| 路径起点 Plane 构造 | :x: | `Plane(path @ 0, z_dir=path % 0)` |

**涉及 API**：`Edge.make_circle`, `sweep`, `Circle`, `Mode.SUBTRACT`, `Plane`, `export_step`

#### 07-heat-sink — 散热片（GridLocations 鳍片）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box 底板 + 顶面定位 | :x: | 80×60×5mm 底板 |
| GridLocations 鳍片阵列 | :x: | 8 片鳍片，高 25mm，厚 1.5mm |
| 选择器取顶面作草图平面 | :x: | `sort_by(Axis.Z)[-1]` |

**涉及 API**：`Box`, `GridLocations`, `Rectangle`, `extrude`, `sort_by`, `export_step`

---

### 二、曲面建模（Surface）

#### 08-loft-transition — 多截面放样过渡

| 功能 | 状态 | 说明 |
|------|------|------|
| 多平面 BuildSketch + loft | :x: | 圆 → 方 → 圆 三截面放样 |
| Plane.XY.offset 多高度截面 | :x: | 三个不同高度的截面 |
| 曲面连续性检查 | :x: | G1 切线连续验证 |

**涉及 API**：`BuildSketch`, `Circle`, `Rectangle`, `loft`, `Plane.XY.offset`, `export_step`

#### 09-organic-shell — 有机曲面外壳

| 功能 | 状态 | 说明 |
|------|------|------|
| 多截面 Loft（5 个椭圆截面） | :x: | 变截面流线型壳体 |
| shell 抽壳 | :x: | 均匀壁厚抽壳 |
| Ellipse 参数化截面 | :x: | 长短轴随高度变化 |

**涉及 API**：`Ellipse`, `loft`, `shell`, `Plane.XY.offset`, `export_step`

#### 10-sweep-twist — 扭转扫掠

| 功能 | 状态 | 说明 |
|------|------|------|
| 直线路径 + 截面扭转 | :x: | 方截面扭转 90° |
| sweep transition 参数 | :x: | `sweep(path, transition=Transition.ROUND)` |

**涉及 API**：`sweep`, `Line`, `Rectangle`, `Transition`, `export_step`

---

### 三、关节装配（Joints）

#### 11-revolute-hinge — 旋转铰链

| 功能 | 状态 | 说明 |
|------|------|------|
| RigidJoint 固定连接 | :x: | 底座固定点 |
| RevoluteJoint 旋转铰链 | :x: | 1 DOF，angular_range=(0,120) |
| connect_to 自动定位 | :x: | RigidJoint.connect_to(RevoluteJoint) |
| 关节可视化 | :x: | `show(..., render_joints=True)` |

**涉及 API**：`RigidJoint`, `RevoluteJoint`, `connect_to`, `Compound`, `show(render_joints=True)`, `export_step`

#### 12-quadruped-leg — 四足腿链（多关节串联）

| 功能 | 状态 | 说明 |
|------|------|------|
| RevoluteJoint 串联链 | :x: | hip → knee → ankle → foot 四级 |
| angular_range 限位 | :x: | hip(±45°), knee(-90°~0°), ankle(±30°) |
| 多关节角度设置 | :x: | 各关节设定到指定角度 |
| 关节链运动验证 | :x: | 改变 hip 角度后下级跟随 |

**涉及 API**：`RevoluteJoint`, `RigidJoint`, `connect_to`, `Compound`, `label`, `export_step`

#### 13-ball-joint — 球铰万向节

| 功能 | 状态 | 说明 |
|------|------|------|
| BallJoint 3 DOF 连接 | :x: | 球铰 angular_range 三轴 |
| RigidJoint + BallJoint 对接 | :x: | 底座固定 + 头部万向 |

**涉及 API**：`BallJoint`, `RigidJoint`, `connect_to`, `export_step`

---

### 四、安装实战（Mounting）

#### 14-servo-mount — SG90 舵机安装座

| 功能 | 状态 | 说明 |
|------|------|------|
| 舵机腔体（Box 减材料） | :x: | SG90 尺寸 23.2×12.5×22mm |
| 耳片安装槽 | :x: | 舵机固定耳卡槽 |
| 输出轴孔 + 线缆出口 | :x: | 顶面轴孔 + 侧面线缆口 |
| 螺丝孔 | :x: | M2 安装孔 |

**涉及 API**：`Box`, `Hole`, `extrude(Mode.SUBTRACT)`, `fillet`, `export_step`

#### 15-pcb-enclosure — PCB 壳体（铜柱 + USB 开口 + 卡扣盖）

| 功能 | 状态 | 说明 |
|------|------|------|
| Box + shell 抽壳 | :x: | PCB 尺寸反推壳体内腔 |
| M2.5 铜柱（GridLocations） | :x: | 4 角铜柱对齐 PCB 安装孔 |
| USB-C 接口开口 | :x: | 侧面减材料，定位到 PCB 高度 |
| 散热通风槽 | :x: | 底面/侧面条形开口 |
| 卡扣盖板 | :x: | snap-fit 卡扣 + 装配预览 |

**涉及 API**：`Box`, `shell`, `GridLocations`, `Cylinder`, `Rectangle`, `extrude(Mode.SUBTRACT)`, `Pos`, `Compound`, `export_step`

#### 16-sensor-bracket — 传感器支架（HC-SR04）

| 功能 | 状态 | 说明 |
|------|------|------|
| L 型支架底板 | :x: | 带安装孔的底板 |
| 双圆形传感器窗口 | :x: | HC-SR04 两探头中心距 26mm |
| 角度调节槽 | :x: | 长圆孔允许俯仰调节 |

**涉及 API**：`Box`, `Hole`, `Locations`, `SlotOverall`, `fillet`, `export_step`

---

### 五、OCP 可视化（Viewer）

#### 17-show-params — show() 参数验证

| 功能 | 状态 | 说明 |
|------|------|------|
| 多对象多颜色 show | :x: | `show(a, b, colors=["steelblue","orange"])` |
| names 命名 | :x: | `names=["body","lid"]` → OCP 树状结构 |
| transparent 半透明 | :x: | `alphas=[0.5, 1.0]` 半透明检查 |
| reset_camera / Camera 枚举 | :x: | `Camera.FRONT`, `Camera.ISO` |

**涉及 API**：`show`, `Camera`, `colors`, `names`, `alphas`

#### 18-animation-explode — 爆炸动画（Animation API）

| 功能 | 状态 | 说明 |
|------|------|------|
| Animation + add_track 平移 | :x: | `add_track("/Group/name", "t", ...)` |
| 16s 循环时间轴 | :x: | 炸2s → 停10s → 合2s → 停2s |
| animate(speed) 播放 | :x: | speed=1 正常速度 |
| save_as_gif 导出 | :x: | fps=20，循环 GIF |

**涉及 API**：`Animation`, `add_track`, `animate`, `save_as_gif`

#### 19-animation-joint — 多关节运动动画

| 功能 | 状态 | 说明 |
|------|------|------|
| RevoluteJoint 角度 → rz 轨道 | :x: | 关节旋转映射到 OCP 动画 |
| 多轨道协调 | :x: | 四腿交替步态编排 |
| 时间轴错开 | :x: | 各关节不同相位 |

**涉及 API**：`Animation`, `add_track("rz")`, `RevoluteJoint`, `show`

#### 20-studio-material — PBR 材质渲染

| 功能 | 状态 | 说明 |
|------|------|------|
| StudioEnvironment 预设 | :x: | `show(..., preset="default")` |
| 金属 / 塑料材质 | :x: | PBR 材质赋予不同零件 |
| 截图对比 | :x: | `save_screenshot` 高质量渲染 |

**涉及 API**：`show`, `StudioEnvironment`, `save_screenshot`

---

### 六、制造工艺验证（Process）

#### 21-print-tolerance — 3D 打印公差测试件

| 功能 | 状态 | 说明 |
|------|------|------|
| 间隙配合测试（0.1~0.5mm 梯度） | :x: | 公母件配合，5 档间隙 |
| 最小壁厚验证 | :x: | 0.4 / 0.6 / 0.8 / 1.0mm 壁 |
| 悬臂角度测试 | :x: | 30° / 45° / 60° 悬臂 |
| STL 导出参数对比 | :x: | draft / standard / fine 三档精度 |

**涉及 API**：`Box`, `Cylinder`, `shell`, `export_stl`, `linear_tolerance`, `angular_tolerance`

#### 22-laser-dxf — 激光切割 DXF 导出

| 功能 | 状态 | 说明 |
|------|------|------|
| 2D 轮廓构建 | :x: | 安装板 + 内孔 + 减重槽 |
| export_dxf 导出 | :x: | 2D DXF 文件 |
| 切缝补偿（offset 轮廓） | :x: | 外扩/内缩 0.1mm |

**涉及 API**：`BuildSketch`, `Rectangle`, `Circle`, `offset`, `export_dxf`

---

### 七、运动仿真（Simulation）

#### 25-fk-leg-chain — FK 正运动学（DH 齐次变换 + OCP 可视化）

| 功能 | 状态 | 说明 |
|------|------|------|
| DH 参数定义三连杆 | :x: | d1=55mm, L1=100mm, L2=100mm |
| 齐次变换矩阵链 FK 计算 | :x: | numpy 4×4 矩阵 T01×T12×T23 |
| build123d Location 验证 | :x: | Pos*Rot 链结果与 numpy 一致 |
| OCP 可视化（关节球+骨骼线） | :x: | show() 多对象多颜色预览 |

**涉及 API**：`Sphere`, `Box`, `Pos`, `Rot`, `Location`, `show`, `export_step`, numpy `dh_matrix`

#### 26-ik-single-leg — IK 逆运动学（解析求解 + 双构型对比）

| 功能 | 状态 | 说明 |
|------|------|------|
| 三连杆解析 IK（余弦定理） | :x: | 输入足端 (x,y,z) → 求 θ1,θ2,θ3 |
| 双构型对比（knee_sign ±1） | :x: | 膝正弯/反弯两种姿态 |
| FK→IK→FK 往返验证 | :x: | 误差 < 0.01mm |
| OCP 双姿态并排显示 | :x: | 两种构型偏移 150mm 对比 |

**涉及 API**：`Sphere`, `Box`, `Pos`, `show`, `export_step`, 纯 Python `ik_leg`

#### 27-workspace-cloud — 工作空间点云（FK 遍历 + 可达性可视化）

| 功能 | 状态 | 说明 |
|------|------|------|
| 角度网格遍历 FK | :x: | 三轴各 15 步 → 3375 个足端点 |
| 点云下采样显示 | :x: | 随机采样 500 点避免 OCP 卡顿 |
| 肩关节标记 + 默认站姿 | :x: | 参考点 + 当前姿态对比 |

**涉及 API**：`Vertex`, `Sphere`, `Pos`, `show`, numpy FK 遍历

#### 28-gait-generator — 步态生成器（贝塞尔轨迹 + IK + OCP 动画）

| 功能 | 状态 | 说明 |
|------|------|------|
| 11 点贝塞尔摆动相轨迹 | :x: | MIT 标准 swing 曲线 |
| trot 对角步态相位表 | :x: | LF+RR 同相，RF+LR 同相 |
| IK 求解关节角度序列 | :x: | 步态→足端→IK→关节角度 |
| OCP Animation 四足动画 | :x: | 4s 循环，20fps 关键帧 |

**涉及 API**：`Box`, `Cylinder`, `Pos`, `Compound`, `Animation`, `add_track`, `animate`, `show`

#### 29-urdf-export — URDF 导出（build123d → URDF + STL）

| 功能 | 状态 | 说明 |
|------|------|------|
| build123d 零件构建 + label | :x: | body + upper_leg + lower_leg + foot |
| URDF XML 生成（link + joint） | :x: | revolute 关节 + limit 限位 |
| STL mesh 自动导出 | :x: | 每个 link 一个 .stl 文件 |
| 质量/惯性矩估算 | :x: | volume × density → inertial 标签 |
| yourdfpy 可选验证 | :x: | 加载 URDF 检查关节轴线 |

**涉及 API**：`Box`, `Cylinder`, `Compound`, `export_stl`, `export_step`, `show`, xml.etree

---

### 八、验证工具（Verification）

#### 23-validate-geometry — 几何验证

| 功能 | 状态 | 说明 |
|------|------|------|
| is_valid() BRep 有效性 | :x: | 多个零件的 BRep 检查 |
| volume > 0 断言 | :x: | 体积正值验证 |
| bounding_box 尺寸断言 | :x: | 包围盒与设计值对比 |
| do_children_intersect 碰撞 | :x: | 装配体碰撞检测 |

**涉及 API**：`is_valid`, `volume`, `bounding_box`, `Compound`, `do_children_intersect`

#### 24-export-formats — 多格式导出

| 功能 | 状态 | 说明 |
|------|------|------|
| STEP 导出 + 回读验证 | :x: | export_step → import_step → 体积对比 |
| STL 导出 + 文件大小合理性 | :x: | 不同精度档位 |
| BREP 导出 + 回读验证 | :x: | export_brep → import_brep 无损 |
| DXF 导出 | :x: | 2D 草图导出 |

**涉及 API**：`export_step`, `export_stl`, `export_brep`, `export_dxf`, `import_step`, `import_brep`

---

## 覆盖统计

| 类别 | 已完成 | 待开发 | 总计 |
|------|--------|--------|------|
| 零件建模 | 5 | 2 | 7 |
| 曲面建模 | 0 | 3 | 3 |
| 关节装配 | 0 | 3 | 3 |
| 安装实战 | 0 | 3 | 3 |
| OCP 可视化 | 0 | 4 | 4 |
| 制造工艺 | 0 | 2 | 2 |
| 运动仿真 | 0 | 5 | 5 |
| 验证工具 | 0 | 2 | 2 |
| **合计** | **5** | **24** | **29** |

---

## 目录结构

```
build123d-cad-skill-test/
├── README.md
├── .gitignore
├── .vscode/
│   └── settings.json             # Pylance 类型检查配置
├── tests/
│   ├── 01-enclosure-box/         # ✅ 外壳盒
│   │   ├── enclosure_box.py
│   │   └── output/
│   ├── 02-spur-gear/             # ✅ 直齿轮
│   │   ├── gear_test.py
│   │   └── output/
│   ├── 03-mounting-plate/        # ✅ 安装板
│   ├── 04-flange/                # ⬜ 法兰盘
│   ├── 05-stepped-shaft/         # ⬜ 阶梯轴
│   ├── 06-pipe-elbow/            # ⬜ 弯管接头
│   ├── 07-heat-sink/             # ⬜ 散热片
│   ├── 08-loft-transition/       # ⬜ 多截面放样
│   ├── 09-organic-shell/         # ⬜ 有机曲面
│   ├── 10-sweep-twist/           # ⬜ 扭转扫掠
│   ├── 11-revolute-hinge/        # ⬜ 旋转铰链
│   ├── 12-quadruped-leg/         # ⬜ 四足腿链
│   ├── 13-ball-joint/            # ⬜ 球铰万向
│   ├── 14-servo-mount/           # ⬜ 舵机座
│   ├── 15-pcb-enclosure/         # ⬜ PCB 壳体
│   ├── 16-sensor-bracket/        # ⬜ 传感器支架
│   ├── 17-show-params/           # ⬜ show() 参数
│   ├── 18-animation-explode/     # ⬜ 爆炸动画
│   ├── 19-animation-joint/       # ⬜ 关节动画
│   ├── 20-studio-material/       # ⬜ PBR 材质
│   ├── 21-print-tolerance/       # ⬜ 打印公差
│   ├── 22-laser-dxf/             # ⬜ 激光 DXF
│   ├── 23-validate-geometry/     # ⬜ 几何验证
│   ├── 24-export-formats/        # ⬜ 多格式导出
│   ├── 25-fk-leg-chain/         # ⬜ FK 正运动学
│   ├── 26-ik-single-leg/        # ⬜ IK 逆运动学
│   ├── 27-workspace-cloud/      # ⬜ 工作空间点云
│   ├── 28-gait-generator/       # ⬜ 步态生成器
│   └── 29-urdf-export/          # ⬜ URDF 导出
└── .claude/
    └── settings.local.json
```
