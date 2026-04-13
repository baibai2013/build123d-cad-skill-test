"""
12-quadruped-leg -- Quadruped Leg: 3 Bones + 2 Ligaments + Foot + Hip Mount
Tests:
  6-part structure     -- hip_mount + femur + tibia + foot + 2 ligaments
  RevoluteJoint chain  -- hip -> knee -> ankle (3 DOF planar serial chain)
  angular_range limits -- hip(+-45), knee(-90~0), ankle(+-30)
  FK ligament geometry -- ligament bars computed via forward kinematics each frame
  Stance/swing gait    -- Peter Corke style: distinct stance(60%) / swing(40%) phases
  GIF animation        -- 40 frames walk cycle with FK-positioned ligaments

Design intent (Peter Corke + Dave Cowden):
  Reference: 3-segment planar leg (femur 245mm / tibia 220mm / foot 182mm).
  Scaled to test size (~1:5). Each bone = cylinder shaft + sphere joint heads.
  Two ligament bars span the knee joint (parallel linkage), positioned each frame
  via FK computation -- NOT rigidly attached to one bone.
  Peter Corke: "Define the kinematics first, then build geometry around it."
  Dave Cowden: "The code describes operations, not coordinates."
"""

from build123d import *
import os, math

# ===== Parameters (proportional to reference, ~1:5 scale) =====
# Hip mount
hip_r       = 12     # hip motor housing radius mm
hip_h       = 20     # hip housing height mm

# Femur (upper leg)
femur_r     = 4      # shaft radius mm
femur_h     = 50     # shaft length mm (ref: 245mm)
femur_jr    = 7      # joint sphere radius mm

# Tibia (lower leg)
tibia_r     = 3      # shaft radius mm
tibia_h     = 45     # shaft length mm (ref: 220mm)
tibia_jr    = 6      # joint sphere radius mm

# Foot
foot_r      = 12     # foot pad radius mm
foot_h      = 6      # foot pad height mm
foot_jr     = 5      # ankle sphere radius mm

# Ligaments (parallel linkage bars)
lig_r       = 1.5    # ligament bar radius mm
lig_off     = 10     # perpendicular offset from bone axis mm
lig_up      = 10     # attachment distance above knee on femur mm
lig_down    = 10     # attachment distance below knee on tibia mm

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
step_path = os.path.join(output_dir, "quadruped_leg.step")

# ===== Bone Models (Algebra Mode) =====

# Hip mount: motor housing, origin centered
hip_body = Cylinder(radius=hip_r, height=hip_h)
hip_body.label = "hip_body"

# Femur: origin at top (hip pivot z=0), shaft extends down to z=-femur_h
femur_shaft = Cylinder(radius=femur_r, height=femur_h,
                       align=(Align.CENTER, Align.CENTER, Align.MAX))
femur_top   = Sphere(radius=femur_jr)
femur_bot   = Sphere(radius=femur_jr).translate((0, 0, -femur_h))
femur = femur_shaft + femur_top + femur_bot
femur.label = "femur"

# Tibia: origin at top (knee pivot z=0), shaft extends down to z=-tibia_h
tibia_shaft = Cylinder(radius=tibia_r, height=tibia_h,
                       align=(Align.CENTER, Align.CENTER, Align.MAX))
tibia_top   = Sphere(radius=tibia_jr)
tibia_bot   = Sphere(radius=foot_jr).translate((0, 0, -tibia_h))
tibia = tibia_shaft + tibia_top + tibia_bot
tibia.label = "tibia"

# Foot: origin at top (ankle pivot z=0), pad extends down
foot_pad = Cylinder(radius=foot_r, height=foot_h,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))
foot_top = Sphere(radius=foot_jr)
foot = foot_pad + foot_top
foot.label = "foot"

# ===== Joints (3 DOF serial chain) =====
# Pattern: RigidJoint(parent bottom, ry=-90) + RevoluteJoint(child top, Y-axis)

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

# ===== FK Helpers (Peter Corke approach) =====

def set_pose(hip_a, knee_a, ankle_a):
    """Set main chain joint angles via connect_to."""
    j_hip_rigid.connect_to(j_hip_rev, angle=hip_a)
    j_knee_rigid.connect_to(j_knee_rev, angle=knee_a)
    j_ankle_rigid.connect_to(j_ankle_rev, angle=ankle_a)

def make_bar(start, end, radius=lig_r):
    """Create a solid cylinder bar from start to end in XZ plane."""
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
    """Compute ligament bar geometry from joint angles using FK.

    Forward kinematics: given hip and knee angles, compute the world-space
    attachment points on femur and tibia, then create solid bars between them.
    This is the Peter Corke way: kinematics first, geometry second.
    """
    h = math.radians(hip_a)
    k = math.radians(knee_a)

    # Hip pivot (bottom of hip_mount, world coords)
    hp_x, hp_z = 0, -hip_h / 2

    # Femur direction: at angle=0, points -Z (down). Positive angle -> +X (forward).
    f_dx =  math.sin(h)
    f_dz = -math.cos(h)

    # Knee pivot (end of femur)
    kp_x = hp_x + f_dx * femur_h
    kp_z = hp_z + f_dz * femur_h

    # Femur perpendicular (90 deg in XZ plane)
    fp_x =  math.cos(h)
    fp_z =  math.sin(h)

    # Tibia direction (accumulated angle)
    total = h + k
    t_dx =  math.sin(total)
    t_dz = -math.cos(total)
    tp_x =  math.cos(total)
    tp_z =  math.sin(total)

    # Femur-side: lig_up above knee along femur, offset perpendicular
    fa_x = kp_x - f_dx * lig_up
    fa_z = kp_z - f_dz * lig_up
    f_front = (fa_x + fp_x * lig_off, 0, fa_z + fp_z * lig_off)
    f_rear  = (fa_x - fp_x * lig_off, 0, fa_z - fp_z * lig_off)

    # Tibia-side: lig_down below knee along tibia, offset perpendicular
    ta_x = kp_x + t_dx * lig_down
    ta_z = kp_z + t_dz * lig_down
    t_front = (ta_x + tp_x * lig_off, 0, ta_z + tp_z * lig_off)
    t_rear  = (ta_x - tp_x * lig_off, 0, ta_z - tp_z * lig_off)

    lf = make_bar(f_front, t_front)
    lf.label = "lig_front"
    lr = make_bar(f_rear, t_rear)
    lr.label = "lig_rear"
    return lf, lr

# ===== Connect chain: straight leg =====
set_pose(0, 0, 0)
lig_front, lig_rear = compute_ligaments(0, 0)

assembly = Compound([hip_body, femur, tibia, foot, lig_front, lig_rear],
                    label="quadruped_leg")

# ===== Validation Layer 1 + 2 =====
assert hip_body.is_valid,  "hip_body BRep invalid"
assert femur.is_valid,     "femur BRep invalid"
assert tibia.is_valid,     "tibia BRep invalid"
assert foot.is_valid,      "foot BRep invalid"
assert assembly.is_valid,  "assembly BRep invalid"
assert len(assembly.solids()) == 6, f"expected 6 solids, got {len(assembly.solids())}"

print(f"Hip body volume:  {hip_body.volume:.2f} mm^3")
print(f"Femur volume:     {femur.volume:.2f} mm^3")
print(f"Tibia volume:     {tibia.volume:.2f} mm^3")
print(f"Foot volume:      {foot.volume:.2f} mm^3")
print(f"Assembly solids:  {len(assembly.solids())}")

# Verify straight pose: foot well below hip
bb_foot = foot.bounding_box()
bb_hip  = hip_body.bounding_box()
total_chain = hip_h / 2 + femur_h + tibia_h
assert bb_foot.min.Z < bb_hip.min.Z - total_chain * 0.8, \
    f"Foot not below hip: foot Z_min={bb_foot.min.Z:.1f}"
print(f"Straight pose: foot Z_min={bb_foot.min.Z:.1f}, hip Z_min={bb_hip.min.Z:.1f}")

# Chain kinematics: change angles, verify foot moves
foot_z_straight = foot.bounding_box().center().Z

set_pose(30, -45, 15)
foot_z_bent = foot.bounding_box().center().Z
assert abs(foot_z_bent - foot_z_straight) > 5, \
    f"Foot did not move: straight={foot_z_straight:.1f}, bent={foot_z_bent:.1f}"
print(f"Chain kinematics: foot Z {foot_z_straight:.1f} -> {foot_z_bent:.1f} (delta={abs(foot_z_bent - foot_z_straight):.1f})")

# Ligament geometry at bent pose
lig_f_bent, lig_r_bent = compute_ligaments(30, -45)
assert lig_f_bent.is_valid, "ligament_front invalid at bent pose"
assert lig_r_bent.is_valid, "ligament_rear invalid at bent pose"
print(f"Ligament FK check: front vol={lig_f_bent.volume:.1f}, rear vol={lig_r_bent.volume:.1f}")

# Reset to straight
set_pose(0, 0, 0)
lig_front, lig_rear = compute_ligaments(0, 0)
assembly = Compound([hip_body, femur, tibia, foot, lig_front, lig_rear],
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
    from ocp_vscode import show, set_port, Camera, save_screenshot, Animation
    from ocp_vscode.comms import port_check
    from ocp_vscode.state import get_ports
    import time

    NAMES  = ["hip_body", "femur", "tibia", "foot", "lig_front", "lig_rear"]
    COLORS = ["gray", "steelblue", "orange", "green", "crimson", "crimson"]

    def show_pose(hip_a, knee_a, ankle_a, camera=Camera.ISO):
        """Set pose, compute ligaments, show all 6 parts."""
        set_pose(hip_a, knee_a, ankle_a)
        lf, lr = compute_ligaments(hip_a, knee_a)
        show(hip_body, femur, tibia, foot, lf, lr,
             names=NAMES, colors=COLORS, reset_camera=camera)

    active_port = next((int(p) for p in get_ports() if port_check(int(p))), None)
    if not active_port:
        print("OCP Viewer: no running Viewer detected")
    else:
        set_port(active_port)

        # --- Static screenshots: 3 poses ---
        poses = [
            (0,    0,   0,  "standing"),
            (20,  -30,  10, "walking"),
            (30,  -60,  20, "crouching"),
        ]
        for hip_a, knee_a, ankle_a, label in poses:
            show_pose(hip_a, knee_a, ankle_a)
            time.sleep(0.6)
            save_screenshot(os.path.join(output_dir, f"pose_{label}.png"))
            print(f"Screenshot saved: pose_{label}.png")

        # --- Walk cycle GIF: 40 frames (Peter Corke gait) ---
        # Swing phase (0..40%): foot lifts, moves forward
        # Stance phase (40..100%): foot on ground, pushes backward
        show_pose(0, 0, 0)
        time.sleep(0.5)

        n_frames = 40
        frame_paths = []
        for idx in range(n_frames):
            t = idx / n_frames

            if t < 0.4:
                p = t / 0.4
                hip_a   = -20 + 40 * p
                knee_a  = -50 * math.sin(math.pi * p)
                ankle_a =  15 * math.sin(math.pi * p)
            else:
                p = (t - 0.4) / 0.6
                hip_a   =  20 - 40 * p
                knee_a  = -5 * math.sin(math.pi * p)
                ankle_a = -5 * math.sin(math.pi * p)

            show_pose(hip_a, knee_a, ankle_a, camera=None)
            time.sleep(0.2)
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
                         loop=0, duration=80)     # 80ms/frame = 12.5fps
            for p in frame_paths:
                os.remove(p)
            print(f"GIF saved: quadruped_leg_walk.gif ({len(imgs)} frames)")
        except ImportError:
            print("Pillow not installed, GIF skipped")

        # --- Final ISO screenshot (straight + joints visible) ---
        show_pose(0, 0, 0)
        time.sleep(0.5)
        save_screenshot(os.path.join(output_dir, "quadruped_leg_ISO.png"))

        # --- OCP Animation: FK-computed translation keyframes ---
        # OCP's flat scene graph can't cascade rotations in a serial chain.
        # Solution: compute real FK positions at keyframes, use "t" tracks.
        try:
            set_pose(0, 0, 0)
            init_pos = {}
            for name, part in [("femur", femur), ("tibia", tibia), ("foot", foot)]:
                c = part.bounding_box().center()
                init_pos[name] = (c.X, c.Y, c.Z)

            # Keyframes matching the gait phases
            kf_data = [
                (0,   -20,   0,    0),     # swing start
                (1.2,   0, -50,   15),     # swing peak (knee max bend)
                (2.4,  20,   0,    0),     # swing end / stance start
                (4.2,   0,  -5,   -5),     # mid-stance
                (6,   -20,   0,    0),     # loop
            ]

            kf_times = [kf[0] for kf in kf_data]
            tracks = {"femur": [], "tibia": [], "foot": []}

            for _, ha, ka, aa in kf_data:
                set_pose(ha, ka, aa)
                for name, part in [("femur", femur), ("tibia", tibia), ("foot", foot)]:
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
