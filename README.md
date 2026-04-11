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

### 01-enclosure-box — 外壳盒（抽壳 + 扣合盖 + 文字 + 装配 + 爆炸动画）

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

### 02-spur-gear — 直齿圆柱齿轮（渐开线 + 逐齿融合）

| 功能 | 状态 | 说明 |
|------|------|------|
| 渐开线齿形计算 | :white_check_mark: | 模数 2，齿数 20，压力角 20 度 |
| 根圆柱 + 逐齿 Algebra Mode 融合 | :white_check_mark: | 避免大型非凸多边形 OCP 渲染问题 |
| 中心轴孔 + 键槽 | :white_check_mark: | 轴孔 R4mm，键槽宽 2mm |
| OCP Viewer 预览 | :white_check_mark: | show() 直接预览 |

**涉及 API**：`Cylinder`, `Wire.make_polygon`, `BRepBuilderAPI_MakeFace`, `BuildPart`, `BuildSketch`, `add`, `extrude`, `Box`, Algebra Mode (`+`, `-`), `export_step`

---

## 目录结构

```
build123d-cad-skill-test/
├── README.md
├── .gitignore
├── tests/
│   ├── 01-enclosure-box/
│   │   ├── enclosure_box.py
│   │   └── output/           # STEP, STL, GIF 导出产物
│   └── 02-spur-gear/
│       ├── gear_test.py
│       └── output/           # STEP 导出产物
└── .claude/
    └── settings.local.json
```
