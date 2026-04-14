"""
12-quadruped-leg Interactive Controller (Route A)
=================================================
tkinter GUI + build123d backend + OCP CAD Viewer frontend

Usage:
  1. Open OCP CAD Viewer in VS Code
  2. Run: python interactive_tkinter.py
  3. Drag sliders to control hip / knee / ankle angles
  4. OCP Viewer updates in real-time (~200ms per frame)

Architecture:
  tkinter (stdlib, zero install) -> build123d Joint system -> OCP show()
  - ttk.Scale sliders x 3 joints
  - Preset buttons (standing / walking / crouching)
  - Debounced updates (root.after) to limit OCP refresh rate

Design (Peter Corke + Dave Cowden):
  Peter Corke: "Define the kinematics first, then build geometry around it."
  Dave Cowden: "The code describes operations, not coordinates."
"""

from build123d import *
import tkinter as tk
from tkinter import ttk
import math, os, threading, time

# ===== Parameters (synced with quadruped_leg.py) =====

hip_r       = 11
hip_h       = 5
shaft_r     = 2.5
bolt_n      = 6
bolt_pcd    = 8
bolt_r      = 1.0

femur_l     = 50
femur_w_end = 11
femur_w_mid = 4
femur_t     = 3
pivot_r     = 2.5

tibia_l     = 45
tibia_w_knee= 9
tibia_w_mid = 3.5
tibia_w_ankle= 6
tibia_t     = 2.5

meta_l      = 18
meta_w      = 4.5
meta_t      = 2.5

foot_w      = 14
foot_top_w  = 5
foot_h      = 7
foot_arc_h  = 3
foot_t      = 3

lig_r       = 1.0
lig_off     = 4
lig_up      = 15
lig_down    = 15

# ===== Helper: make_bar in 3D =====

def make_bar(start, end, radius=lig_r):
    diff = end - start
    length = diff.length
    if length < 0.01:
        return Sphere(radius=radius)
    bar = Cylinder(radius=radius, height=length,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    plane = Plane(origin=(0, 0, 0), z_dir=diff.normalized())
    return Pos(start.X, start.Y, start.Z) * plane.location * bar

# ===== Build bones (synced with quadruped_leg.py — slender dog-bone) =====

with BuildPart() as hip_part:
    Cylinder(radius=hip_r, height=hip_h)
    Hole(radius=shaft_r)
    with PolarLocations(radius=bolt_pcd, count=bolt_n):
        Hole(radius=bolt_r)
hip_mount = hip_part.part
hip_mount.label = "hip_mount"

with BuildPart() as femur_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            ew = femur_w_end / 2
            mw = femur_w_mid / 2
            Line((ew, 0), (-ew, 0))
            Spline((-ew, 0), (-mw, -femur_l / 2), (-ew, -femur_l))
            Line((-ew, -femur_l), (ew, -femur_l))
            Spline((ew, -femur_l), (mw, -femur_l / 2), (ew, 0))
        make_face()
    extrude(amount=femur_t / 2, both=True)
femur_body = femur_part.part
hip_pivot   = Pos(0, 0, -(femur_w_end / 2)) * Rot(0, 90, 0) * \
              Cylinder(radius=pivot_r, height=femur_t * 3)
knee_pivot  = Pos(0, 0, -(femur_l - femur_w_end / 2)) * Rot(0, 90, 0) * \
              Cylinder(radius=pivot_r, height=femur_t * 3)
femur = femur_body - hip_pivot - knee_pivot
femur.label = "femur"

with BuildPart() as tibia_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            kw = tibia_w_knee / 2
            tw = tibia_w_mid / 2
            aw = tibia_w_ankle / 2
            Line((kw, 0), (-kw, 0))
            Spline((-kw, 0), (-tw, -tibia_l / 2), (-aw, -tibia_l))
            Line((-aw, -tibia_l), (aw, -tibia_l))
            Spline((aw, -tibia_l), (tw, -tibia_l / 2), (kw, 0))
        make_face()
    extrude(amount=tibia_t / 2, both=True)
tibia_body = tibia_part.part
knee_pivot_t  = Pos(0, 0, -(tibia_w_knee / 2)) * Rot(0, 90, 0) * \
                Cylinder(radius=pivot_r, height=tibia_t * 3)
ankle_pivot_t = Pos(0, 0, -(tibia_l - tibia_w_ankle / 2)) * Rot(0, 90, 0) * \
                Cylinder(radius=pivot_r - 0.5, height=tibia_t * 3)
tibia = tibia_body - knee_pivot_t - ankle_pivot_t
tibia.label = "tibia"

with BuildPart() as meta_part:
    with BuildSketch(Plane.YZ) as sk:
        with Locations([(0, -meta_l / 2)]):
            Rectangle(meta_w, meta_l)
        fillet(sk.vertices(), radius=meta_w / 2 - 0.5)
    extrude(amount=meta_t / 2, both=True)
meta_body = meta_part.part
ankle_hole_m = Pos(0, 0, -(meta_w / 2)) * Rot(0, 90, 0) * \
               Cylinder(radius=pivot_r - 0.5, height=meta_t * 3)
foot_hole_m  = Pos(0, 0, -(meta_l - meta_w / 2)) * Rot(0, 90, 0) * \
               Cylinder(radius=pivot_r - 0.5, height=meta_t * 3)
metatarsus = meta_body - ankle_hole_m - foot_hole_m
metatarsus.label = "metatarsus"

with BuildPart() as foot_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            tw = foot_top_w / 2
            bw = foot_w / 2
            sh = foot_h - foot_arc_h
            Line((-tw, 0), (tw, 0))
            Line((tw, 0), (bw, -sh))
            ThreePointArc((bw, -sh), (0, -foot_h), (-bw, -sh))
            Line((-bw, -sh), (-tw, 0))
        make_face()
    extrude(amount=foot_t / 2, both=True)
foot_pad = foot_part.part
foot_pad.label = "foot_pad"

# ===== Joints (4-level serial chain) =====

j_hip_rigid = RigidJoint("hip_out", to_part=hip_mount,
    joint_location=Location((0, 0, -hip_h / 2), (0, -90, 0)))
j_hip_rev = RevoluteJoint("hip_in", to_part=femur,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-45, 45))

j_knee_rigid = RigidJoint("knee_out", to_part=femur,
    joint_location=Location((0, 0, -femur_l), (0, -90, 0)))
j_knee_rev = RevoluteJoint("knee_in", to_part=tibia,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-90, 0))

j_ankle_rigid = RigidJoint("ankle_out", to_part=tibia,
    joint_location=Location((0, 0, -tibia_l), (0, -90, 0)))
j_ankle_rev = RevoluteJoint("ankle_in", to_part=metatarsus,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-30, 30))

j_foot_rigid = RigidJoint("foot_out", to_part=metatarsus,
    joint_location=Location((0, 0, -meta_l)))
j_foot_mount = RigidJoint("foot_in", to_part=foot_pad)

NAMES  = ["hip_mount", "femur", "tibia", "metatarsus", "foot_pad", "lig_front", "lig_rear"]
COLORS = ["gray", "steelblue", "cadetblue", "dodgerblue", "darkgray", "crimson", "crimson"]

# ===== FK Helpers =====

def set_pose(hip_a, knee_a, ankle_a):
    j_hip_rigid.connect_to(j_hip_rev, angle=hip_a)
    j_knee_rigid.connect_to(j_knee_rev, angle=knee_a)
    j_ankle_rigid.connect_to(j_ankle_rev, angle=ankle_a)
    j_foot_rigid.connect_to(j_foot_mount)

def compute_ligaments():
    hp = j_hip_rigid.location.position
    kp = j_knee_rigid.location.position
    ap = j_ankle_rigid.location.position

    f_dir = (kp - hp).normalized()
    t_dir = (ap - kp).normalized()

    x_axis = Vector(1, 0, 0)
    f_perp = f_dir.cross(x_axis)
    if f_perp.length < 0.001:
        f_perp = Vector(0, 1, 0)
    else:
        f_perp = f_perp.normalized()

    t_perp = t_dir.cross(x_axis)
    if t_perp.length < 0.001:
        t_perp = Vector(0, 1, 0)
    else:
        t_perp = t_perp.normalized()

    fa = kp - f_dir * lig_up
    f_front = fa + f_perp * lig_off
    f_rear  = fa - f_perp * lig_off

    ta = kp + t_dir * lig_down
    t_front = ta + t_perp * lig_off
    t_rear  = ta - t_perp * lig_off

    lf = make_bar(f_front, t_front)
    lf.label = "lig_front"
    lr = make_bar(f_rear, t_rear)
    lr.label = "lig_rear"
    return lf, lr

# ===== Connect to OCP Viewer =====

try:
    from ocp_vscode import show, set_port, Camera
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if active_port:
        set_port(active_port)
        print(f"OCP Viewer connected: port {active_port}")
    else:
        print("No OCP Viewer detected. Start OCP CAD Viewer in VS Code first.")
        active_port = None
except ImportError:
    print("ocp_vscode not installed. Install with: pip install ocp-vscode")
    active_port = None
    show = None

# ===== Show initial pose =====
set_pose(0, 0, 0)
lf, lr = compute_ligaments()
if show and active_port:
    show(hip_mount, femur, tibia, metatarsus, foot_pad, lf, lr,
         names=NAMES, colors=COLORS, reset_camera=Camera.ISO)

# ===== tkinter GUI =====

class LegController:
    def __init__(self, root):
        self.root = root
        root.title("Quadruped Leg Controller")
        root.resizable(False, False)

        self.hip_var   = tk.DoubleVar(value=0)
        self.knee_var  = tk.DoubleVar(value=0)
        self.ankle_var = tk.DoubleVar(value=0)

        self._pending_update = None
        self._update_interval = 150

        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.grid(sticky="nsew")

        ttk.Label(main, text="Quadruped Leg Controller",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0,
                  columnspan=3, pady=(0, 10))

        joints = [
            ("Hip",   self.hip_var,   -45,  45),
            ("Knee",  self.knee_var,  -90,   0),
            ("Ankle", self.ankle_var, -30,  30),
        ]

        for i, (name, var, lo, hi) in enumerate(joints):
            row = i + 1
            ttk.Label(main, text=f"{name}:", width=8).grid(
                row=row, column=0, sticky="w", padx=(0, 5))

            scale = ttk.Scale(main, from_=lo, to=hi, orient="horizontal",
                              variable=var, length=300,
                              command=lambda v, n=name: self._on_slider_change())
            scale.grid(row=row, column=1, padx=5)

            lbl = ttk.Label(main, textvariable=var, width=6)
            lbl.grid(row=row, column=2, padx=(5, 0))
            var.trace_add("write", lambda *_, v=var, l=lbl:
                          l.config(text=f"{v.get():.0f}\u00b0"))

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)

        presets = [
            ("Standing",  10,   -25,   8),
            ("Walking",   30,   -50,  15),
            ("Crouching", -10,  -70,  25),
            ("Kick",      -30,  -10,  25),
        ]

        for name, ha, ka, aa in presets:
            btn = ttk.Button(btn_frame, text=name,
                             command=lambda h=ha, k=ka, a=aa:
                             self._set_preset(h, k, a))
            btn.pack(side="left", padx=3)

        status_frame = ttk.Frame(main)
        status_frame.grid(row=5, column=0, columnspan=3, pady=(5, 0), sticky="ew")

        port_text = f"OCP Viewer: port {active_port}" if active_port else "OCP Viewer: not connected"
        ttk.Label(status_frame, text=port_text,
                  foreground="green" if active_port else "red").pack(side="left")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="right")

    def _set_preset(self, hip_a, knee_a, ankle_a):
        self.hip_var.set(hip_a)
        self.knee_var.set(knee_a)
        self.ankle_var.set(ankle_a)
        self._schedule_update()

    def _on_slider_change(self):
        self._schedule_update()

    def _schedule_update(self):
        if self._pending_update:
            self.root.after_cancel(self._pending_update)
        self._pending_update = self.root.after(
            self._update_interval, self._do_update)

    def _do_update(self):
        self._pending_update = None
        ha = self.hip_var.get()
        ka = self.knee_var.get()
        aa = self.ankle_var.get()

        self.status_var.set("Updating...")
        self.root.update_idletasks()

        try:
            set_pose(ha, ka, aa)
            lf, lr = compute_ligaments()

            if show and active_port:
                show(hip_mount, femur, tibia, metatarsus, foot_pad, lf, lr,
                     names=NAMES, colors=COLORS, reset_camera=Camera.KEEP)

            self.status_var.set(f"hip={ha:.0f} knee={ka:.0f} ankle={aa:.0f}")
        except Exception as e:
            self.status_var.set(f"Error: {e}")


def main():
    root = tk.Tk()
    app = LegController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
