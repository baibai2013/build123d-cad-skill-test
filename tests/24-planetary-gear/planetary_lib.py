"""行星齿轮纯函数库(无副作用,供静态测试与 URDF 动画测试共用)。

渐开线齿廓复用 02-spur-gear 方法。所有齿轮**建在原点**(URDF 里靠关节 origin 摆位)。
"""
from build123d import *  # noqa: F403
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace  # type: ignore[import-untyped]
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir  # type: ignore[import-untyped]
import math

_XY = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _face_from_pts(pts_2d):
    wire = Wire.make_polygon([(x, y, 0) for x, y in pts_2d], close=True)
    return Face(BRepBuilderAPI_MakeFace(_XY, wire.wrapped, True).Face())


def _tooth_pts(idx, teeth, base_r, root_r, add_r, steps):
    pa = 2 * math.pi / teeth
    ht = math.pi / (2 * teeth)
    a_i = pa * idx
    inv_max = math.sqrt(max(0.0, (add_r / base_r) ** 2 - 1))
    left, right = [], []
    for s in range(steps + 1):
        ia = inv_max * (s / steps)
        r = base_r * math.sqrt(1 + ia ** 2)
        if r < root_r:
            continue
        r = min(r, add_r)
        th = a_i + ht - ia + math.atan(ia)
        left.append((r * math.cos(th), r * math.sin(th)))
    for s in range(steps, -1, -1):
        ia = inv_max * (s / steps)
        r = base_r * math.sqrt(1 + ia ** 2)
        if r < root_r:
            continue
        r = min(r, add_r)
        th = a_i - ht + ia - math.atan(ia)
        right.append((r * math.cos(th), r * math.sin(th)))
    if not left or not right:
        return None
    th_r = math.atan2(right[-1][1], right[-1][0])
    th_l = math.atan2(left[0][1], left[0][0])
    if th_l < th_r:
        th_l += 2 * math.pi
    arc = [(root_r * math.cos(th_r + (th_l - th_r) * k / 4),
            root_r * math.sin(th_r + (th_l - th_r) * k / 4)) for k in range(1, 4)]
    return left + right + arc


def make_spur_gear(teeth, module=2.0, face_width=10.0, pressure_a=20.0, steps=6, bore_r=0.0):
    """外齿渐开线直齿轮,中心在原点。"""
    pitch_r = module * teeth / 2
    add_r = pitch_r + module
    root_r = pitch_r - 1.25 * module
    base_r = pitch_r * math.cos(math.radians(pressure_a))
    gear = Cylinder(radius=root_r, height=face_width)
    for i in range(teeth):
        pts = _tooth_pts(i, teeth, base_r, root_r, add_r, steps)
        if pts is None:
            continue
        with BuildPart() as tooth:
            with BuildSketch(Plane.XY.offset(-face_width / 2)):
                add(_face_from_pts(pts))
            extrude(amount=face_width)
        gear = gear + tooth.part
    if bore_r > 0:
        gear = gear - Cylinder(radius=bore_r, height=face_width * 1.1)
    return gear


def make_ring_gear(z_ring, module=2.0, face_width=10.0, outer_pad=2.5):
    """内齿圈:环坯减外齿刀 → 内齿。中心在原点。"""
    pitch_r = module * z_ring / 2
    outer_r = pitch_r + outer_pad * module
    blank = Cylinder(radius=outer_r, height=face_width)
    cutter = make_spur_gear(z_ring, module=module, face_width=face_width * 1.2)
    return blank - cutter


def make_carrier(a_center, n_planet, face_width=10.0, hub_r=6.0, plate_t=4.0):
    """行星架:薄盘 + N 销孔 + 中心孔。中心在原点(z=0 平面)。"""
    plate = Cylinder(radius=a_center + 6, height=plate_t)
    plate = plate - Cylinder(radius=hub_r, height=plate_t * 1.1)
    for k in range(n_planet):
        ang = 2 * math.pi * k / n_planet
        pin = Cylinder(radius=2.2, height=plate_t * 1.1)
        plate = plate - pin.moved(Location((a_center * math.cos(ang), a_center * math.sin(ang), 0)))
    return plate
