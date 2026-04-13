"""
12-quadruped-leg Interactive Mode -- Jupyter Slider Control

Usage:
  1. Open this file in VS Code with Jupyter extension
  2. Or run: jupyter notebook, then open this as .ipynb
  3. Drag sliders to control hip / knee / ankle angles in real-time
  4. OCP CAD Viewer updates instantly

Requires: ipywidgets, ocp_vscode, build123d
"""

from build123d import *
from ocp_vscode import show, set_port, Camera
from ocp_vscode.comms import port_check
from ocp_vscode.state import get_ports
import math

# ===== Connect to OCP Viewer =====
active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
if active_port:
    set_port(active_port)
    print(f"OCP Viewer connected: port {active_port}")
else:
    print("No OCP Viewer detected. Start OCP CAD Viewer in VS Code first.")

# ===== Parameters =====
hip_r, hip_h       = 12, 20
femur_r, femur_h   = 4, 50
femur_jr            = 7
tibia_r, tibia_h   = 3, 45
tibia_jr            = 6
foot_r, foot_h     = 12, 6
foot_jr             = 5
lig_r               = 1.5
lig_off, lig_up, lig_down = 10, 10, 10

# ===== Build bones (once) =====
hip_body = Cylinder(radius=hip_r, height=hip_h)
hip_body.label = "hip_body"

femur_shaft = Cylinder(radius=femur_r, height=femur_h,
                       align=(Align.CENTER, Align.CENTER, Align.MAX))
femur = femur_shaft + Sphere(radius=femur_jr) + Sphere(radius=femur_jr).translate((0, 0, -femur_h))
femur.label = "femur"

tibia_shaft = Cylinder(radius=tibia_r, height=tibia_h,
                       align=(Align.CENTER, Align.CENTER, Align.MAX))
tibia = tibia_shaft + Sphere(radius=tibia_jr) + Sphere(radius=foot_jr).translate((0, 0, -tibia_h))
tibia.label = "tibia"

foot_pad = Cylinder(radius=foot_r, height=foot_h,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))
foot = foot_pad + Sphere(radius=foot_jr)
foot.label = "foot"

# ===== Joints =====
j_hip_rigid = RigidJoint("hip_out", to_part=hip_body,
    joint_location=Location((0, 0, -hip_h / 2), (0, -90, 0)))
j_hip_rev = RevoluteJoint("hip_in", to_part=femur,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-45, 45))

j_knee_rigid = RigidJoint("knee_out", to_part=femur,
    joint_location=Location((0, 0, -femur_h), (0, -90, 0)))
j_knee_rev = RevoluteJoint("knee_in", to_part=tibia,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-90, 0))

j_ankle_rigid = RigidJoint("ankle_out", to_part=tibia,
    joint_location=Location((0, 0, -tibia_h), (0, -90, 0)))
j_ankle_rev = RevoluteJoint("ankle_in", to_part=foot,
    axis=Axis((0, 0, 0), (0, 1, 0)), angular_range=(-30, 30))

# ===== FK Helpers =====
def make_bar(start, end, radius=lig_r):
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dz * dz)
    if length < 0.01:
        return Sphere(radius=radius)
    angle = math.degrees(math.atan2(dx, dz))
    bar = Cylinder(radius=radius, height=length,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(start[0], start[1], start[2]) * Rot(0, angle, 0) * bar

def compute_ligaments(hip_a, knee_a):
    h = math.radians(hip_a)
    k = math.radians(knee_a)
    hp_x, hp_z = 0, -hip_h / 2
    f_dx, f_dz = math.sin(h), -math.cos(h)
    kp_x = hp_x + f_dx * femur_h
    kp_z = hp_z + f_dz * femur_h
    fp_x, fp_z = math.cos(h), math.sin(h)
    total = h + k
    t_dx, t_dz = math.sin(total), -math.cos(total)
    tp_x, tp_z = math.cos(total), math.sin(total)

    fa_x = kp_x - f_dx * lig_up
    fa_z = kp_z - f_dz * lig_up
    f_front = (fa_x + fp_x * lig_off, 0, fa_z + fp_z * lig_off)
    f_rear  = (fa_x - fp_x * lig_off, 0, fa_z - fp_z * lig_off)

    ta_x = kp_x + t_dx * lig_down
    ta_z = kp_z + t_dz * lig_down
    t_front = (ta_x + tp_x * lig_off, 0, ta_z + tp_z * lig_off)
    t_rear  = (ta_x - tp_x * lig_off, 0, ta_z - tp_z * lig_off)

    lf = make_bar(f_front, t_front)
    lf.label = "lig_front"
    lr = make_bar(f_rear, t_rear)
    lr.label = "lig_rear"
    return lf, lr

NAMES  = ["hip_body", "femur", "tibia", "foot", "lig_front", "lig_rear"]
COLORS = ["gray", "steelblue", "orange", "green", "crimson", "crimson"]

def update_view(hip_a, knee_a, ankle_a):
    """Set pose and update OCP Viewer."""
    j_hip_rigid.connect_to(j_hip_rev, angle=hip_a)
    j_knee_rigid.connect_to(j_knee_rev, angle=knee_a)
    j_ankle_rigid.connect_to(j_ankle_rev, angle=ankle_a)
    lf, lr = compute_ligaments(hip_a, knee_a)
    show(hip_body, femur, tibia, foot, lf, lr,
         names=NAMES, colors=COLORS, reset_camera=Camera.KEEP)

# ===== Interactive Sliders =====
try:
    import ipywidgets as widgets
    from IPython.display import display

    hip_slider = widgets.FloatSlider(
        value=0, min=-45, max=45, step=1,
        description='Hip:', continuous_update=True,
        style={'description_width': '60px'},
        layout=widgets.Layout(width='400px'))

    knee_slider = widgets.FloatSlider(
        value=0, min=-90, max=0, step=1,
        description='Knee:', continuous_update=True,
        style={'description_width': '60px'},
        layout=widgets.Layout(width='400px'))

    ankle_slider = widgets.FloatSlider(
        value=0, min=-30, max=30, step=1,
        description='Ankle:', continuous_update=True,
        style={'description_width': '60px'},
        layout=widgets.Layout(width='400px'))

    def on_slider_change(change):
        update_view(hip_slider.value, knee_slider.value, ankle_slider.value)

    hip_slider.observe(on_slider_change, names='value')
    knee_slider.observe(on_slider_change, names='value')
    ankle_slider.observe(on_slider_change, names='value')

    # Show initial pose
    update_view(0, 0, 0)

    print("Drag sliders to control joint angles:")
    display(widgets.VBox([hip_slider, knee_slider, ankle_slider]))

except ImportError:
    # Fallback: simple terminal input loop
    print("ipywidgets not available. Using terminal input mode.")
    print("Enter joint angles as: hip knee ankle (e.g.: 20 -30 10)")
    print("Type 'q' to quit.\n")

    update_view(0, 0, 0)

    while True:
        try:
            inp = input("hip knee ankle > ").strip()
            if inp.lower() == 'q':
                break
            parts = inp.split()
            if len(parts) == 3:
                ha, ka, aa = float(parts[0]), float(parts[1]), float(parts[2])
                ha = max(-45, min(45, ha))
                ka = max(-90, min(0, ka))
                aa = max(-30, min(30, aa))
                update_view(ha, ka, aa)
                print(f"  -> hip={ha}, knee={ka}, ankle={aa}")
            else:
                print("  Usage: hip knee ankle (e.g.: 20 -30 10)")
        except (ValueError, EOFError):
            break
