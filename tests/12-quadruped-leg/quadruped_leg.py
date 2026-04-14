"""
12-quadruped-leg -- Quadruped Leg: 7 Parts (Slender Structural Links)
Tests:
  7-part structure     -- hip_mount + femur + tibia + metatarsus + foot_pad + 2 ligaments
  Slender link style   -- CNC aluminum arm/plate geometry (dog-bone profile)
  RevoluteJoint chain  -- hip -> knee -> ankle (3 DOF) + foot (rigid)
  angular_range limits -- hip(+-45), knee(-90~0), ankle(+-30)
  FK ligament geometry -- ligament bars computed from Joint.location.position each frame
  Stance/swing gait    -- Peter Corke style: swing(40%) / stance(60%)
  GIF animation        -- 40 frames walk cycle

Reference: MIT-style quadruped robot leg
  - Colocated hip & knee motors at hip housing
  - Slender structural arms for femur and tibia
  - Parallel linkage bars transmit knee torque across joint
  - Small crescent foot pad for ground contact

Design (Peter Corke + Dave Cowden):
  Peter Corke: "Define the kinematics first, then build geometry around it."
  Dave Cowden: "The code describes operations, not coordinates."
"""

from build123d import *
import os, math

# ===== Parameters =====

# Hip mount (motor housing disk)
hip_r       = 11     # motor housing radius mm (22mm diameter, compact)
hip_h       = 5      # housing thickness mm
shaft_r     = 2.5    # center shaft hole radius
bolt_n      = 6      # bolt count
bolt_pcd    = 8      # bolt PCD radius
bolt_r      = 1.0    # bolt hole radius

# Femur (slender structural arm — dog-bone profile)
femur_l     = 50     # length mm (MIT 245mm / 5)
femur_w_end = 11     # width at pivot ends mm (bearing ear bulge)
femur_w_mid = 4      # width at narrow waist mm (slender CNC arm)
femur_t     = 3      # plate thickness mm
pivot_r     = 2.5    # pivot hole radius

# Tibia (slender structural arm — dog-bone with slight ankle taper)
tibia_l     = 45     # length mm (MIT 220mm / 5)
tibia_w_knee= 9      # width at knee end mm
tibia_w_mid = 3.5    # width at mid-section mm (thinner than femur)
tibia_w_ankle= 6     # width at ankle end mm
tibia_t     = 2.5    # plate thickness mm (thinner plate than femur)

# Metatarsus (short connector link)
meta_l      = 18     # length mm (MIT 84mm / 5 ≈ 17mm, digitigrade)
meta_w      = 4.5    # width mm
meta_t      = 2.5    # plate thickness mm

# Foot pad (small crescent rocker)
foot_w      = 14     # width at bottom mm (small ground contact pad)
foot_top_w  = 5      # width at top (ankle connection)
foot_h      = 7      # total height mm
foot_arc_h  = 3      # arc depth at bottom mm
foot_t      = 3      # thickness mm

# Ligaments (parallel linkage bars — transmit knee motor torque)
lig_r       = 1.0    # ligament bar radius mm (thin linkage bars)
lig_off     = 4      # perpendicular offset from bone axis mm
lig_up      = 15     # attachment distance above knee on femur mm
lig_down    = 15     # attachment distance below knee on tibia mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path = os.path.join(output_dir, "quadruped_leg.step")

# ===== Helper: make_bar in 3D =====

def make_bar(start, end, radius=lig_r):
    """Create a solid cylinder bar between two Vector points in 3D."""
    diff = end - start
    length = diff.length
    if length < 0.01:
        return Sphere(radius=radius)
    bar = Cylinder(radius=radius, height=length,
                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    plane = Plane(origin=(0, 0, 0), z_dir=diff.normalized())
    return Pos(start.X, start.Y, start.Z) * plane.location * bar

# ===== Part 1: Hip mount (motor housing disk) =====

with BuildPart() as hip_part:
    Cylinder(radius=hip_r, height=hip_h)
    Hole(radius=shaft_r)
    with PolarLocations(radius=bolt_pcd, count=bolt_n):
        Hole(radius=bolt_r)
hip_mount = hip_part.part
hip_mount.label = "hip_mount"

# ===== Part 2: Femur (slender dog-bone structural arm) =====
# Wider at both pivot ends, narrow concave waist in middle

with BuildPart() as femur_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            ew = femur_w_end / 2   # end half-width
            mw = femur_w_mid / 2   # mid half-width
            # Top edge (hip end)
            Line((ew, 0), (-ew, 0))
            # Left concave side: hip → waist → knee
            Spline((-ew, 0), (-mw, -femur_l / 2), (-ew, -femur_l))
            # Bottom edge (knee end)
            Line((-ew, -femur_l), (ew, -femur_l))
            # Right concave side: knee → waist → hip
            Spline((ew, -femur_l), (mw, -femur_l / 2), (ew, 0))
        make_face()
    extrude(amount=femur_t / 2, both=True)
femur_body = femur_part.part

# Pivot holes through thickness (X direction)
hip_pivot  = Pos(0, 0, -(femur_w_end / 2)) * Rot(0, 90, 0) * \
             Cylinder(radius=pivot_r, height=femur_t * 3)
knee_pivot = Pos(0, 0, -(femur_l - femur_w_end / 2)) * Rot(0, 90, 0) * \
             Cylinder(radius=pivot_r, height=femur_t * 3)
femur = femur_body - hip_pivot - knee_pivot
femur.label = "femur"

# ===== Part 3: Tibia (slender dog-bone arm, slight ankle taper) =====

with BuildPart() as tibia_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            kw = tibia_w_knee / 2    # knee half-width
            tw = tibia_w_mid / 2     # mid half-width
            aw = tibia_w_ankle / 2   # ankle half-width
            # Top edge (knee end)
            Line((kw, 0), (-kw, 0))
            # Left concave side: knee → waist → ankle
            Spline((-kw, 0), (-tw, -tibia_l / 2), (-aw, -tibia_l))
            # Bottom edge (ankle end)
            Line((-aw, -tibia_l), (aw, -tibia_l))
            # Right concave side: ankle → waist → knee
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

# ===== Part 4: Metatarsus (short connector link) =====

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

# ===== Part 5: Foot pad (small crescent rocker) =====

with BuildPart() as foot_part:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            tw = foot_top_w / 2     # narrow top
            bw = foot_w / 2         # wide bottom
            sh = foot_h - foot_arc_h  # straight portion height
            # Top edge
            Line((-tw, 0), (tw, 0))
            # Right side (tapers outward)
            Line((tw, 0), (bw, -sh))
            # Bottom arc (crescent)
            ThreePointArc((bw, -sh), (0, -foot_h), (-bw, -sh))
            # Left side
            Line((-bw, -sh), (-tw, 0))
        make_face()
    extrude(amount=foot_t / 2, both=True)
foot_pad = foot_part.part
foot_pad.label = "foot_pad"

# ===== Joints (4-level serial chain) =====
# Pattern: RigidJoint(parent bottom, ry=-90) + RevoluteJoint(child top, Y-axis)

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

# ===== FK Helpers (Peter Corke approach) =====

def set_pose(hip_a, knee_a, ankle_a):
    """Set main chain joint angles via connect_to."""
    j_hip_rigid.connect_to(j_hip_rev, angle=hip_a)
    j_knee_rigid.connect_to(j_knee_rev, angle=knee_a)
    j_ankle_rigid.connect_to(j_ankle_rev, angle=ankle_a)
    j_foot_rigid.connect_to(j_foot_mount)

def compute_ligaments():
    """Compute ligament bar geometry from actual Joint world positions.

    Reads joint pivot positions DIRECTLY from the Joint system,
    eliminating coordinate-system mismatch. Must be called AFTER set_pose().
    """
    hp = j_hip_rigid.location.position    # hip pivot
    kp = j_knee_rigid.location.position   # knee pivot
    ap = j_ankle_rigid.location.position  # ankle pivot

    f_dir = (kp - hp).normalized()    # femur direction
    t_dir = (ap - kp).normalized()    # tibia direction

    # Perpendicular offset direction: bone_dir × X_axis
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

    # Femur-side: lig_up above knee along femur, offset perpendicular
    fa = kp - f_dir * lig_up
    f_front = fa + f_perp * lig_off
    f_rear  = fa - f_perp * lig_off

    # Tibia-side: lig_down below knee along tibia, offset perpendicular
    ta = kp + t_dir * lig_down
    t_front = ta + t_perp * lig_off
    t_rear  = ta - t_perp * lig_off

    lf = make_bar(f_front, t_front)
    lf.label = "lig_front"
    lr = make_bar(f_rear, t_rear)
    lr.label = "lig_rear"
    return lf, lr

# ===== Connect chain: straight leg =====
set_pose(0, 0, 0)
lig_front, lig_rear = compute_ligaments()

PARTS = [hip_mount, femur, tibia, metatarsus, foot_pad, lig_front, lig_rear]
NAMES  = ["hip_mount", "femur", "tibia", "metatarsus", "foot_pad", "lig_front", "lig_rear"]
COLORS = ["gray", "steelblue", "cadetblue", "dodgerblue", "darkgray", "crimson", "crimson"]

assembly = Compound(PARTS, label="quadruped_leg")

# ===== Validation Layer 1 + 2 =====
assert hip_mount.is_valid,    "hip_mount BRep invalid"
assert femur.is_valid,        "femur BRep invalid"
assert tibia.is_valid,        "tibia BRep invalid"
assert metatarsus.is_valid,   "metatarsus BRep invalid"
assert foot_pad.is_valid,     "foot_pad BRep invalid"
assert assembly.is_valid,     "assembly BRep invalid"
assert len(assembly.solids()) == 7, f"expected 7 solids, got {len(assembly.solids())}"

print(f"Hip mount volume:  {hip_mount.volume:.2f} mm^3")
print(f"Femur volume:      {femur.volume:.2f} mm^3")
print(f"Tibia volume:      {tibia.volume:.2f} mm^3")
print(f"Metatarsus volume: {metatarsus.volume:.2f} mm^3")
print(f"Foot pad volume:   {foot_pad.volume:.2f} mm^3")
print(f"Assembly solids:   {len(assembly.solids())}")

# Verify straight pose: foot well below hip
bb_foot = foot_pad.bounding_box()
bb_hip  = hip_mount.bounding_box()
total_chain = hip_h / 2 + femur_l + tibia_l + meta_l
assert bb_foot.min.Z < bb_hip.min.Z - total_chain * 0.5, \
    f"Foot not below hip: foot Z_min={bb_foot.min.Z:.1f}"
print(f"Straight pose: foot Z_min={bb_foot.min.Z:.1f}, hip Z_min={bb_hip.min.Z:.1f}")

# Chain kinematics: change angles, verify foot moves
foot_z_straight = foot_pad.bounding_box().center().Z

set_pose(30, -45, 15)
foot_z_bent = foot_pad.bounding_box().center().Z
assert abs(foot_z_bent - foot_z_straight) > 5, \
    f"Foot did not move: straight={foot_z_straight:.1f}, bent={foot_z_bent:.1f}"
print(f"Chain kinematics: foot Z {foot_z_straight:.1f} -> {foot_z_bent:.1f} "
      f"(delta={abs(foot_z_bent - foot_z_straight):.1f})")

# Ligament proximity check at bent pose
lig_f_bent, lig_r_bent = compute_ligaments()
assert lig_f_bent.is_valid, "ligament_front invalid at bent pose"
assert lig_r_bent.is_valid, "ligament_rear invalid at bent pose"
kp_bent = j_knee_rigid.location.position
lig_f_dist = (Vector(*tuple(lig_f_bent.bounding_box().center())) - kp_bent).length
lig_r_dist = (Vector(*tuple(lig_r_bent.bounding_box().center())) - kp_bent).length
assert lig_f_dist < 25, f"lig_front too far from knee: {lig_f_dist:.1f}mm"
assert lig_r_dist < 25, f"lig_rear too far from knee: {lig_r_dist:.1f}mm"
print(f"Ligament proximity: front={lig_f_dist:.1f}mm, rear={lig_r_dist:.1f}mm from knee")
print(f"Ligament FK check: front vol={lig_f_bent.volume:.1f}, rear vol={lig_r_bent.volume:.1f}")

# Reset to straight
set_pose(0, 0, 0)
lig_front, lig_rear = compute_ligaments()
assembly = Compound([hip_mount, femur, tibia, metatarsus, foot_pad, lig_front, lig_rear],
                    label="quadruped_leg")
print("Layer 1+2 passed")

# ===== Validation Layer 3: STEP re-import =====
asm_vol = assembly.volume
export_step(assembly, step_path)
reimported = import_step(step_path)
vol_diff = abs(reimported.volume - asm_vol) / asm_vol
print(f"STEP re-import volume deviation: {vol_diff:.6%}")
assert vol_diff < 0.001, f"STEP precision loss: {vol_diff:.4%}"
print("Layer 3 passed")

# ===== OCP Preview + Animation =====
try:
    from ocp_vscode import show, set_port, Camera, save_screenshot
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    def show_pose(hip_a, knee_a, ankle_a, camera=Camera.ISO):
        """Set pose, compute ligaments, show all 7 parts."""
        set_pose(hip_a, knee_a, ankle_a)
        lf, lr = compute_ligaments()
        show(hip_mount, femur, tibia, metatarsus, foot_pad, lf, lr,
             names=NAMES, colors=COLORS, reset_camera=camera)

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if not active_port:
        print("OCP Viewer: no running Viewer detected")
    else:
        set_port(active_port)

        # --- Static screenshots: 3 poses ---
        poses = [
            (10,  -25,   8, "standing"),
            (30,  -50,  15, "walking"),
            (-10, -70,  25, "crouching"),
        ]
        for hip_a, knee_a, ankle_a, label in poses:
            show_pose(hip_a, knee_a, ankle_a)
            time.sleep(0.6)
            save_screenshot(os.path.join(output_dir, f"pose_{label}.png"))
            print(f"Screenshot saved: pose_{label}.png")

        # --- Walk cycle GIF: 40 frames (Peter Corke gait) ---
        show_pose(0, 0, 0, camera=Camera.FRONT)
        time.sleep(0.5)

        n_frames = 40
        frame_paths = []
        for idx in range(n_frames):
            t = idx / n_frames
            if t < 0.4:
                # Swing phase: foot lifts, moves forward
                p = t / 0.4
                hip_a   = -20 + 40 * p
                knee_a  = -50 * math.sin(math.pi * p)
                ankle_a =  15 * math.sin(math.pi * p)
            else:
                # Stance phase: foot on ground, pushes backward
                p = (t - 0.4) / 0.6
                hip_a   =  20 - 40 * p
                knee_a  = -5 * math.sin(math.pi * p)
                ankle_a = -5 * math.sin(math.pi * p)

            show_pose(hip_a, knee_a, ankle_a, camera=Camera.KEEP)
            time.sleep(0.15)
            fpath = os.path.join(output_dir, f"anim_{idx:03d}.png")
            save_screenshot(fpath)
            frame_paths.append(fpath)

        print(f"Animation frames saved: {len(frame_paths)} frames")

        # --- Compile GIF ---
        try:
            from PIL import Image
            imgs = [Image.open(p) for p in frame_paths]
            gif_path = os.path.join(output_dir, "quadruped_leg_walk.gif")
            imgs[0].save(gif_path, save_all=True, append_images=imgs[1:],
                         loop=0, duration=80)
            for p in frame_paths:
                os.remove(p)
            print(f"GIF saved: quadruped_leg_walk.gif ({len(imgs)} frames)")
        except ImportError:
            print("Pillow not installed, GIF skipped")

        # --- Final ISO screenshot ---
        show_pose(0, 0, 0)
        time.sleep(0.5)
        save_screenshot(os.path.join(output_dir, "quadruped_leg_ISO.png"))

        # --- OCP Animation: FK-computed translation keyframes ---
        try:
            from ocp_vscode import Animation

            set_pose(0, 0, 0)
            rigid_names = ["femur", "tibia", "metatarsus", "foot_pad"]
            rigid_parts = [femur, tibia, metatarsus, foot_pad]
            init_pos = {}
            for name, part in zip(rigid_names, rigid_parts):
                c = part.bounding_box().center()
                init_pos[name] = (c.X, c.Y, c.Z)

            show(hip_mount, femur, tibia, metatarsus, foot_pad,
                 names=["hip_mount"] + rigid_names,
                 colors=["gray", "steelblue", "steelblue", "dodgerblue", "darkgray"],
                 reset_camera=Camera.ISO)
            time.sleep(0.3)

            kf_data = [
                (0,   -20,   0,    0),
                (1.2,   0, -50,   15),
                (2.4,  20,   0,    0),
                (4.2,   0,  -5,   -5),
                (6,   -20,   0,    0),
            ]

            kf_times = [kf[0] for kf in kf_data]
            tracks = {n: [] for n in rigid_names}

            for _, ha, ka, aa in kf_data:
                set_pose(ha, ka, aa)
                for name, part in zip(rigid_names, rigid_parts):
                    c = part.bounding_box().center()
                    ref = init_pos[name]
                    tracks[name].append([c.X - ref[0], c.Y - ref[1], c.Z - ref[2]])

            anim = Animation()
            for name in tracks:
                anim.add_track(f"/Group/{name}", "t", kf_times, tracks[name])
            anim.animate(speed=1)

            set_pose(0, 0, 0)
            print("OCP Animation playing (FK translation keyframes)")
        except Exception as e:
            print(f"OCP Animation skipped: {e}")

        print(f"OCP Viewer: port {active_port}")

except Exception as e:
    print(f"OCP preview skipped: {e}")

print("\n12-quadruped-leg all tests passed")
