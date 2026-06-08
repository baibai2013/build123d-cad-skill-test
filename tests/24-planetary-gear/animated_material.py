"""行星齿轮组【带贴图 + 带动画】GLB(glTF 节点动画)
========================================================
URDF 只能动不能带贴图;glTF 一个文件可同时带 PBR 贴图 + 节点 TRS 动画轨道。
本脚本:build123d 出 4 个齿轮几何 → pygltflib 重建节点层级 + 木纹材质(UV+贴图)
+ 行星运动学旋转动画轨道。cad-viewer 的 approach-B passthrough 加 AnimationMixer 播。

节点树:root → ring(静止) / sun(自转 θs) / carrier 枢轴(0.3θs, 带 carrier 网格)
        → planet_1/2/3(各在 r@ψk 平移,自转 -1.05θs,随 carrier 公转)
clocking 烤进网格:planet +15°、ring +半齿距,初始即啮合;动画保持齿比即保持啮合。
"""
import math, os, sys, struct
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from planetary_lib import make_spur_gear, make_ring_gear, make_carrier
from build123d import Compound, Part, Location, export_gltf
from pygltflib import (GLTF2, Node, Scene, Animation, AnimationChannel, AnimationChannelTarget,
                       AnimationSampler, Accessor, BufferView, Material, PbrMetallicRoughness,
                       Texture, Sampler, Image, TextureInfo, ARRAY_BUFFER, FLOAT)

M, ZS, ZP, ZR, N = 2.0, 18, 12, 42, 3
A_MM = (ZS + ZP) * M / 2.0                       # 30 mm 行星中心距
CLOCK, RINGCLOCK = 15.0, 360.0 / ZR / 2.0
CARRIER_MULT, PLANET_MULT = ZS/(ZS+ZR), -(ZS/ZP)*(ZR/(ZS+ZR))   # 0.30, -1.05
PERIOD, SUN_REVS, NKEY = 8.0, 2.0, 49            # 循环 8s,太阳 2 圈,49 关键帧
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output"); os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(HERE, "textures", "wood.png")
TILES = 3.0

# ── 1) 几何(clocking 烤进 planet/ring 网格),Compound 顺序 = [sun,planet,ring,carrier] ──
sun = make_spur_gear(ZS, M, 10, bore_r=5)
planet = make_spur_gear(ZP, M, 10, bore_r=2).moved(Location((0,0,0),(0,0,1), CLOCK))
ring = make_ring_gear(ZR, M, 10).moved(Location((0,0,0),(0,0,1), RINGCLOCK))
carrier = make_carrier(A_MM, N, 10)
glb = os.path.join(OUT, "planetary_animated.glb")
export_gltf(Compound(children=[Part(sun.wrapped,label="sun"), Part(planet.wrapped,label="planet"),
                               Part(ring.wrapped,label="ring"), Part(carrier.wrapped,label="carrier")]),
            glb, binary=True)

g = GLTF2().load(glb)
assert len(g.meshes) == 4, f"期望 4 网格,实得 {len(g.meshes)}"
M_SUN, M_PLANET, M_RING, M_CARRIER = 0, 1, 2, 3
blob = bytearray(g.binary_blob())

def read_pos(mesh_idx):
    acc = g.accessors[g.meshes[mesh_idx].primitives[0].attributes.POSITION]
    bv = g.bufferViews[acc.bufferView]; off=(bv.byteOffset or 0)+(acc.byteOffset or 0)
    return np.frombuffer(bytes(blob[off:off+acc.count*12]), np.float32).reshape(acc.count,3)

def append(arr, comp_type, acc_type, target=None):
    global blob
    while len(blob)%4: blob.append(0)
    off=len(blob); payload=arr.tobytes(); blob.extend(payload)
    bv=BufferView(buffer=0, byteOffset=off, byteLength=len(payload))
    if target is not None: bv.target=target
    g.bufferViews.append(bv);
    a=Accessor(bufferView=len(g.bufferViews)-1, componentType=comp_type, count=len(arr), type=acc_type)
    if acc_type=="VEC2": a.min=[float(arr[:,0].min()),float(arr[:,1].min())]; a.max=[float(arr[:,0].max()),float(arr[:,1].max())]
    if acc_type=="SCALAR": a.min=[float(arr.min())]; a.max=[float(arr.max())]
    g.accessors.append(a); return len(g.accessors)-1

# ── 2) 每网格平面 UV + 木纹材质 ──
with open(TEX,"rb") as f: img=f.read()
while len(blob)%4: blob.append(0)
io=len(blob); blob.extend(img)
g.bufferViews.append(BufferView(buffer=0, byteOffset=io, byteLength=len(img)))
g.images.append(Image(bufferView=len(g.bufferViews)-1, mimeType="image/png"))
g.samplers.append(Sampler(wrapS=10497, wrapT=10497))
g.textures.append(Texture(source=len(g.images)-1, sampler=len(g.samplers)-1))
g.materials.append(Material(name="wood", doubleSided=True, pbrMetallicRoughness=PbrMetallicRoughness(
    baseColorTexture=TextureInfo(index=len(g.textures)-1), metallicFactor=0.0, roughnessFactor=0.7)))
mat=len(g.materials)-1
for mi in range(4):
    pos=read_pos(mi); mn,mx=pos.min(0),pos.max(0); span=np.where((mx-mn)==0,1,mx-mn)
    uv=np.stack([(pos[:,0]-mn[0])/span[0]*TILES,(pos[:,1]-mn[1])/span[1]*TILES],1).astype(np.float32)
    uvacc=append(uv,FLOAT,"VEC2",ARRAY_BUFFER)
    for p in g.meshes[mi].primitives: p.attributes.TEXCOORD_0=uvacc; p.material=mat

# ── 3) 节点树 ──
A_M = A_MM/1000.0  # 关节平移用米? 不——几何是 mm,节点 translation 用 mm 与几何同单位
A_T = A_MM
def qZ(deg):
    r=math.radians(deg)/2; return [0.0,0.0,math.sin(r),math.cos(r)]
nodes=[]
def add_node(**kw): nodes.append(Node(**kw)); return len(nodes)-1
sun_n=add_node(mesh=M_SUN, name="sun")
ring_n=add_node(mesh=M_RING, name="ring")
planet_ns=[]
for k in range(N):
    psi=2*math.pi*k/N
    planet_ns.append(add_node(mesh=M_PLANET, name=f"planet_{k+1}",
                              translation=[A_T*math.cos(psi), A_T*math.sin(psi), 0.0]))
carrier_n=add_node(mesh=M_CARRIER, name="carrier", children=planet_ns)
# 根:不烤朝向,统一由 cad-viewer passthrough 绕 X -90° 处理(避免双重旋转)
root_n=add_node(name="root", children=[sun_n, ring_n, carrier_n])
g.nodes=nodes; g.scenes=[Scene(nodes=[root_n])]; g.scene=0

# ── 4) 动画:时间 + 各节点四元数关键帧 ──
times=np.linspace(0, PERIOD, NKEY).astype(np.float32)
time_acc=append(times, FLOAT, "SCALAR")
def quat_track(mult):
    qs=np.array([qZ(360.0*SUN_REVS*mult*(t/PERIOD)) for t in times], np.float32)
    return append(qs, FLOAT, "VEC4")
chans=[]; samps=[]
def anim(node, mult):
    s=len(samps); samps.append(AnimationSampler(input=time_acc, output=quat_track(mult), interpolation="LINEAR"))
    chans.append(AnimationChannel(sampler=s, target=AnimationChannelTarget(node=node, path="rotation")))
anim(sun_n, 1.0); anim(carrier_n, CARRIER_MULT)
for pn in planet_ns: anim(pn, PLANET_MULT)
g.animations=[Animation(name="spin", samplers=samps, channels=chans)]

g.buffers[0].byteLength=len(blob); g.set_binary_blob(bytes(blob)); g.save(glb)
print(f"✓ 带贴图+动画 GLB: {glb}")
print(f"  节点 {len(g.nodes)} / 动画通道 {len(chans)} / 关键帧 {NKEY} / 循环 {PERIOD}s")
print(f"  mimic: carrier×{CARRIER_MULT:.2f} planet×{PLANET_MULT:.2f}")
