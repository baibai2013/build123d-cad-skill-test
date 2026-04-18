# build123d-cad Skill 升级：朝向约定 + Skybox 公共工具

**日期**：2026-04-17
**触发**：tests/13-redmi-k80-pro 实战中发现 OCP Camera preset 与用户直觉的「正面/背面」不一致，反复踩坑；skybox_unfold.py 代码无法在后续 test 中复用。
**状态**：设计中

---

## 1. 问题陈述

K80 Pro 手机壳实战中暴露 3 个系统性问题：

1. **OCP Camera 语义陷阱**：`Camera.FRONT` 实际看 `-Y` 面（对手机来说是底部短边），不是用户期望的屏幕面。每次建新模型都要重新试错一遍。
2. **skybox 截图代码不可复用**：tests/13 的 `skybox_unfold.py` 是一次性脚本，BACK 面的旋转补偿（Z180 镜像）靠反复试出来，换一个产品就要重算。
3. **用户视角 vs 模型坐标**脱钩：AI 建模时用的 `+X / +Y / +Z` 是模型本地坐标，与用户说的「正面/背面/顶部/底部」之间缺少显式声明，容易错位。

根因是 skill 缺少**朝向约定层**——建模前没有强制声明「哪个模型轴对应用户视角的哪个面」。

---

## 2. 设计目标

- 在现有 Layer 0 合同中增加 `orientation` 块，声明即契约
- 把 skybox 6 视图生成做成**可复用的公共脚本**，由 orientation 驱动
- 让 Layer 2 视觉对比按语义自动配对参考照片
- 不破坏老 test，迁移渐进

**非目标**：不重构现有 Layer 0/1/2 验证层级；不改动 build123d 代码本身；不做 3D 坐标轴可视化（已有 OCP 视角可用）。

---

## 3. 架构

```
新增：
  references/ocp/orientation-and-skybox.md    约定说明 + OCP Camera 对照表 + skybox 模板
  scripts/validate/orientation_resolve.py     纯函数：orientation → rotate 序列
  scripts/validate/skybox_unfold.py           通用 skybox 6 视图生成器（可 import / CLI）

改动：
  references/verify/layer0-contract.md        新增 orientation 块 schema
  references/verify/layer2-visual.md          引用 orientation 驱动图片配对
  SKILL.md（skill 主文）                      R3.5 增 orientation 子步 + OCP Camera 硬规则
  scripts/validate/contract_verify.py         Layer 0 静态检查 orientation 块
```

**数据流**：

```
contract.yaml::orientation
        │
        ▼
orientation_resolve.py（纯函数）
        │
        ├──► skybox_unfold.py  →  6 张独立 PNG
        │
        └──► visual_compare.py →  按语义配对参考照片
```

---

## 4. contract.yaml orientation 块 schema

```yaml
orientation:
  # (a) 轴含义：模型本地坐标 → 物理尺寸
  axes:
    X: width       # 宽度
    Y: length      # 长度
    Z: thickness   # 厚度

  # (b) 用户视角下 6 个面的语义名和模型法线
  #     key = 人类标签；value = 模型法线方向（±X/±Y/±Z）
  faces:
    front:  "+Z"   # 用户直视的那面（例：屏幕）
    back:   "-Z"   # 对面（例：摄像头）
    up:     "+Y"   # 物品平放桌上时的顶部短边
    down:   "-Y"   # 底部短边
    left:   "-X"
    right:  "+X"

  # (c) 默认用户视角，生成 front 截图 / Layer 2 默认参考面
  default_view: front
```

**硬约束（Layer 0 静态检查）**：

- `axes` 的 3 个键必须是 `{X, Y, Z}`，value 来自固定词表 `{width, length, thickness, height, depth}`
- `faces` 必须 6 项、3 对方向互斥（不能同时出现 `+Z` 和另一个 face 也是 `+Z`）
- `default_view` 必须出现在 `faces` 里
- 全块可选；缺失时 skybox_unfold 抛 `OrientationMissingError`，老 test 不受影响

---

## 5. orientation_resolve.py API

纯函数、零副作用、可单测：

```python
def resolve_rotations(orientation: dict, face_name: str) -> list[tuple[Axis, float]]:
    """返回把 face_name 对应的面转到 OCP Camera.FRONT 方向 (-Y) 所需的 rotate 序列。"""

def iter_faces(orientation: dict) -> Iterator[tuple[str, list[tuple[Axis, float]]]]:
    """遍历 6 个面，yield (face_name, rotations)，供 skybox_unfold 消费。"""

def validate_orientation(orientation: dict) -> list[str]:
    """Layer 0 静态检查；返回错误列表，空列表表示通过。"""
```

**旋转推导逻辑**：

1. 目标面法线方向 → 3×3 旋转矩阵（单步 90° 或组合）
2. 选择使目标法线对齐 `-Y` 的最短 rotate 序列
3. `back` 面追加 `(Axis.Z, 180)` 作为左右镜像补偿（来自 K80 实战）—— 这是为了让「背面摄像头」在照片里出现在左上而不是右下。注释解释由来。

---

## 6. skybox_unfold.py 用法

**import 模式**（测试项目内）：

```python
from scripts.validate.skybox_unfold import generate_skybox

generate_skybox(
    part=v2,
    contract_path="contract.yaml",
    output_dir="output/",
    prefix="skybox_",
)
# 产出：output/skybox_front.png, skybox_back.png, skybox_up.png,
#       skybox_down.png, skybox_left.png, skybox_right.png（6 张独立 PNG）
```

**CLI 模式**：

```bash
python -m scripts.validate.skybox_unfold \
    --contract tests/13-redmi-k80-pro/contract.yaml \
    --part-module tests.13-redmi-k80-pro.redmi_k80_pro_case \
    --part-var v2 \
    --output-dir tests/13-redmi-k80-pro/output
```

**关键设计选择**：

- 6 张**独立** PNG，不再生成合成大图（test 13 经验：合成大图尺寸难控、信息稀释）
- 文件名用语义小写（`skybox_front.png`），与 orientation 的 `faces` key 一一对应
- 依赖 OCP Viewer 运行中；探测端口的标准模式（`get_ports() + port_check()`）从 skill 已有约定继承

---

## 7. workflow 集成

**R3.5（Layer 0 合同生成）新增子步**：

> AI 必须先询问：「物品平放在桌面、人站立观察时，哪个面是用户直视的『正面』？」
> 根据答复写 `orientation.faces.front` 以及剩余 5 面，然后才开始写 dims/pos/constraints。

**skill 主文新增硬规则**：

> **OCP Camera 警告**：`Camera.FRONT` 看模型 **-Y 面**，不是用户语义的「正面」。
> 要生成 6 视图请用 `scripts/validate/skybox_unfold.py`，不要直接调 `Camera.FRONT/BACK/…` 硬扣语义。
> Camera.RIGHT 看 +X 面，Camera.TOP 看 +Z 面——这些映射写在 `references/ocp/orientation-and-skybox.md` 的对照表里。

**Layer 2 视觉对比接入**：

参考照片按 `references/<product>/images/front.jpg / back.jpg / ...` 命名，`visual_compare.py` 通过 orientation 自动配对模型的 `skybox_<face>.png`，不再需要手工 `--ref-photo` 和 `--model-screenshot` 成对指定。

---

## 8. 向后兼容

- 老 test（01~12）的 contract.yaml 不含 orientation → 调用 skybox_unfold 时抛 `OrientationMissingError`，打印迁移提示；不影响已有建模代码和验证流程
- test 13 作为首个迁移样本：保留原 `skybox_unfold.py` 作为「迁移前参照」，并在同目录新增一个调用公共模块的版本，commit 信息里标明两者关系
- 未来 tests/14+ 默认走新流程；skill 里 R3.5 的 orientation 询问为必答项

---

## 9. 测试策略

- `orientation_resolve.py` 有单元测试：覆盖 6 面旋转序列、非法配置（方向冲突 / 缺 default_view / 非法轴词）
- `skybox_unfold.py` 有集成测试：用 test 13 的 v2 模型跑一遍，断言 6 张 PNG 都生成且非空
- `contract_verify.py --check-only` 的现有 Layer 0 测试扩展：加含/缺 orientation 的两种 fixture

---

## 10. 风险与开放问题

- **风险**：BACK 面的 `(Z, 180)` 补偿是从手机这个品类经验来的。如果未来做的产品「背面」没有方向性（如对称齿轮），这个补偿反而带来 180° 错位。
  **缓解**：orientation 块加可选字段 `back_mirror: true/false`（默认 true），允许用户显式关闭
- **开放问题**：orientation 未来是否要扩展到**非立方体产品**（球面、异形件）？当前只支持 6 面立方体语义。暂不覆盖，未来如果出现需求再迭代
- **开放问题**：是否把 orientation 作为 build123d Assembly 的 Joint 默认参照系？当前不做，装配有独立 Joint 坐标系管理

---

## 11. 交付物清单

1. `references/ocp/orientation-and-skybox.md` — 约定文档 + OCP Camera 对照表
2. `scripts/validate/orientation_resolve.py` — 纯函数库 + 单测
3. `scripts/validate/skybox_unfold.py` — CLI + import API + 集成测试
4. `references/verify/layer0-contract.md` 补章 — orientation 块 schema
5. `references/verify/layer2-visual.md` 补章 — 语义化图片配对
6. `SKILL.md` — R3.5 orientation 子步 + OCP Camera 硬规则段
7. `scripts/validate/contract_verify.py` — 扩展 orientation 静态检查
8. `tests/13-redmi-k80-pro/skybox_unfold.py` — 迁移为调用公共模块的示例
