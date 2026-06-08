"""行星齿轮组【材质展示】静态 GLB(通用:木头 / 玻璃 / …)
================================================================
text-to-cad/cadpy 只做 per-part 颜色,无贴图无透射。本脚本扩展之:给 build123d
导出的 GLB(无 UV 无材质)程序化加 **平面 UV + baseColorTexture + PBR(可选玻璃透射)**。

用法:
    python material_preview.py wood      # 木头(贴图 textures/wood.png)
    python material_preview.py glass     # 玻璃(textures/glass.png + 透射折射)

贴图放 textures/<name>.png。静态(GLB 不带关节动画;动画版是 robot.urdf)。
"""
import math
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from planetary_lib import make_spur_gear, make_ring_gear, make_carrier
from build123d import Compound, Part, Location, export_gltf
from pygltflib import (GLTF2, Accessor, BufferView, Material, PbrMetallicRoughness,
                       Texture, Sampler, Image, TextureInfo, ARRAY_BUFFER, FLOAT)

# 材质配置:tex 贴图名 + PBR 参数(transmission>0 → 玻璃,加 KHR_materials_transmission/ior)
MATERIALS = {
    "wood":  {"metallic": 0.0, "roughness": 0.70, "tiles": 3.0, "transmission": 0.0},
    "glass": {"metallic": 0.0, "roughness": 0.12, "tiles": 2.0, "transmission": 0.9, "ior": 1.5},
    "metal": {"metallic": 1.0, "roughness": 0.25, "tiles": 2.0, "transmission": 0.0},
}

name = sys.argv[1] if len(sys.argv) > 1 else "wood"
cfg = MATERIALS.get(name)
if cfg is None:
    sys.exit(f"未知材质 {name},可选:{', '.join(MATERIALS)}")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
TEX = os.path.join(HERE, "textures", f"{name}.png")
if not os.path.exists(TEX):
    sys.exit(f"缺贴图 {TEX}(把 {name} 纹理放这里)")
os.makedirs(OUT, exist_ok=True)

# ===== 1) 建装配(带 clocking 咬合)=====
M, ZS, ZP, ZR, N = 2.0, 18, 12, 42, 3
A = (ZS + ZP) * M / 2
sun = make_spur_gear(ZS, M, 10, bore_r=5)
planet = make_spur_gear(ZP, M, 10, bore_r=2)
ring = make_ring_gear(ZR, M, 10).moved(Location((0, 0, 0), (0, 0, 1), 360.0 / ZR / 2))
carrier = make_carrier(A, N, 10).moved(Location((0, 0, -8)))
children = [Part(sun.wrapped, label="sun"), Part(ring.wrapped, label="ring"),
            Part(carrier.wrapped, label="carrier")]
for k in range(N):
    psi = 360.0 * k / N
    p = planet.moved(Location((0, 0, 0), (0, 0, 1), 15.0))
    p = p.moved(Location((A * math.cos(math.radians(psi)), A * math.sin(math.radians(psi)), 0)))
    children.append(Part(p.wrapped, label=f"planet_{k+1}"))
glb = os.path.join(OUT, f"planetary_{name}.glb")
export_gltf(Compound(children=children), glb, binary=True)

# ===== 2) 后处理:平面 UV + 贴图 + PBR(玻璃加透射)=====
g = GLTF2().load(glb)
blob = bytearray(g.binary_blob())


def read_pos(acc_idx):
    acc = g.accessors[acc_idx]
    bv = g.bufferViews[acc.bufferView]
    off = (bv.byteOffset or 0) + (acc.byteOffset or 0)
    return np.frombuffer(bytes(blob[off:off + acc.count * 12]), np.float32).reshape(acc.count, 3)


def append_uv(uv):
    while len(blob) % 4:
        blob.append(0)
    off = len(blob)
    blob.extend(uv.astype(np.float32).tobytes())
    g.bufferViews.append(BufferView(buffer=0, byteOffset=off, byteLength=len(uv) * 8, target=ARRAY_BUFFER))
    g.accessors.append(Accessor(bufferView=len(g.bufferViews) - 1, componentType=FLOAT, count=len(uv),
                                type="VEC2", min=[float(uv[:, 0].min()), float(uv[:, 1].min())],
                                max=[float(uv[:, 0].max()), float(uv[:, 1].max())]))
    return len(g.accessors) - 1


with open(TEX, "rb") as f:
    img_bytes = f.read()
while len(blob) % 4:
    blob.append(0)
img_off = len(blob)
blob.extend(img_bytes)
g.bufferViews.append(BufferView(buffer=0, byteOffset=img_off, byteLength=len(img_bytes)))
g.images.append(Image(bufferView=len(g.bufferViews) - 1, mimeType="image/png"))
g.samplers.append(Sampler(wrapS=10497, wrapT=10497))
g.textures.append(Texture(source=len(g.images) - 1, sampler=len(g.samplers) - 1))

mat = Material(name=name, doubleSided=True, pbrMetallicRoughness=PbrMetallicRoughness(
    baseColorTexture=TextureInfo(index=len(g.textures) - 1),
    baseColorFactor=[1, 1, 1, 1], metallicFactor=cfg["metallic"], roughnessFactor=cfg["roughness"]))
if cfg["transmission"] > 0:   # 玻璃:透射 + 折射率扩展
    mat.extensions = {"KHR_materials_transmission": {"transmissionFactor": cfg["transmission"]},
                      "KHR_materials_ior": {"ior": cfg.get("ior", 1.5)}}
    for ext in ("KHR_materials_transmission", "KHR_materials_ior"):
        if ext not in (g.extensionsUsed or []):
            g.extensionsUsed = (g.extensionsUsed or []) + [ext]
g.materials.append(mat)
mat_idx = len(g.materials) - 1

for mesh in g.meshes:
    for prim in mesh.primitives:
        pos = read_pos(prim.attributes.POSITION)
        mn, mx = pos.min(0), pos.max(0)
        span = np.where((mx - mn) == 0, 1, mx - mn)
        uv = np.stack([(pos[:, 0] - mn[0]) / span[0] * cfg["tiles"],
                       (pos[:, 1] - mn[1]) / span[1] * cfg["tiles"]], axis=1)
        prim.attributes.TEXCOORD_0 = append_uv(uv)
        prim.material = mat_idx

g.buffers[0].byteLength = len(blob)
g.set_binary_blob(bytes(blob))
g.save(glb)
extra = f" + 透射 {cfg['transmission']:g}/ior {cfg.get('ior','-')}" if cfg["transmission"] else ""
print(f"✓ {name}: {os.path.basename(TEX)} → {glb}(metallic {cfg['metallic']:g}/rough {cfg['roughness']:g}{extra})")
print("预览: bash ~/.agents/skills/build123d-cad/skills/viewer/scripts/start.sh "
      f"{glb} $(git rev-parse --show-toplevel)")
