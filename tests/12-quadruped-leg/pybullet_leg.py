"""
12-quadruped-leg PyBullet Simulation (Route B)
==============================================
Physics simulation with URDF + interactive slider control.

Usage:
  1. Run: python pybullet_leg.py
  2. PyBullet GUI opens with the quadruped leg
  3. Use sliders to control hip / knee / ankle angles
  4. Real-time physics (gravity + collision + joint torques)

Architecture:
  URDF (quadruped_leg.urdf) → PyBullet loadURDF → addUserDebugParameter sliders
  - Real physics: gravity, joint damping, collision
  - Mass/inertia from reference drawing (1:5 scale)
  - Joint limits enforced by URDF

Design (Peter Corke):
  "Learn by doing — run the simulation, see what happens, then refine."

Reference dimensions (1:5 scale from drawing):
  Femur: 50mm (original 245mm), m=0.012kg
  Tibia: 45mm (original 220mm), m=0.005kg
  Metatarsus: 17mm (original 84mm), m=0.001kg
  Foot: 36mm wide (original 182mm), m=0.003kg
"""

import os
import sys
import math
import time

try:
    import pybullet as p
    import pybullet_data
except ImportError:
    print("PyBullet not installed. Install with: pip install pybullet")
    print("Then re-run this script.")
    sys.exit(1)

# ===== Paths =====
script_dir = os.path.dirname(os.path.abspath(__file__))
urdf_path  = os.path.join(script_dir, "quadruped_leg.urdf")

if not os.path.exists(urdf_path):
    print(f"URDF not found: {urdf_path}")
    print("Run quadruped_leg.py first to generate the URDF, or check the file exists.")
    sys.exit(1)

# ===== PyBullet Setup =====
physics_client = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

# Load ground plane
plane_id = p.loadURDF("plane.urdf")

# Load leg URDF (suspended above ground for testing)
# Start position: hip at z=0.2m (200mm above ground)
start_pos = [0, 0, 0.2]
start_orn = p.getQuaternionFromEuler([0, 0, 0])
leg_id = p.loadURDF(urdf_path, start_pos, start_orn, useFixedBase=True)

# ===== Camera Setup =====
p.resetDebugVisualizerCamera(
    cameraDistance=0.25,
    cameraYaw=45,
    cameraPitch=-30,
    cameraTargetPosition=[0, 0, 0.1]
)

# ===== Joint Info =====
num_joints = p.getNumJoints(leg_id)
joint_info = {}
for i in range(num_joints):
    info = p.getJointInfo(leg_id, i)
    name = info[1].decode('utf-8')
    joint_type = info[2]
    lower = info[8]
    upper = info[9]
    joint_info[name] = {
        'index': i,
        'type': joint_type,
        'lower': lower,
        'upper': upper,
    }
    print(f"Joint {i}: {name}, type={joint_type}, range=[{math.degrees(lower):.0f}, {math.degrees(upper):.0f}] deg")

# ===== Interactive Sliders =====
hip_slider   = p.addUserDebugParameter("Hip (deg)",   -45,  45, 0)
knee_slider  = p.addUserDebugParameter("Knee (deg)",  -90,   0, 0)
ankle_slider = p.addUserDebugParameter("Ankle (deg)", -30,  30, 0)

# Preset buttons (simulated with debug parameters)
mode_slider = p.addUserDebugParameter("Preset: 0=free 1=stand 2=walk 3=crouch", 0, 3, 0)

# Joint indices
hip_idx   = joint_info['hip_joint']['index']
knee_idx  = joint_info['knee_joint']['index']
ankle_idx = joint_info['ankle_joint']['index']

# ===== Gait parameters =====
gait_active = False
gait_slider = p.addUserDebugParameter("Gait: 0=off 1=walk", 0, 1, 0)
gait_speed  = p.addUserDebugParameter("Gait speed", 0.5, 3.0, 1.0)

print("\n===== Quadruped Leg PyBullet Simulation =====")
print("Controls:")
print("  - Hip/Knee/Ankle sliders: direct joint angle control")
print("  - Preset slider: 0=free, 1=standing, 2=walking, 3=crouching")
print("  - Gait slider: 0=manual, 1=auto walk cycle")
print("  - Gait speed: walk cycle frequency multiplier")
print("  - Close window or Ctrl+C to exit")
print("=" * 48)

# ===== Presets =====
PRESETS = {
    1: (0, 0, 0),        # standing
    2: (20, -30, 10),    # walking mid-stance
    3: (30, -60, 20),    # crouching
}

# ===== Main Loop =====
prev_mode = 0
t_start = time.time()

try:
    while True:
        # Read sliders
        mode = int(round(p.readUserDebugParameter(mode_slider)))
        gait_on = int(round(p.readUserDebugParameter(gait_slider)))
        speed = p.readUserDebugParameter(gait_speed)

        if gait_on == 1:
            # Auto walk cycle (Peter Corke gait: 40% swing, 60% stance)
            t = ((time.time() - t_start) * speed) % 1.0
            if t < 0.4:
                # Swing phase
                phase = t / 0.4
                hip_a   = -20 + 40 * phase
                knee_a  = -50 * math.sin(math.pi * phase)
                ankle_a =  15 * math.sin(math.pi * phase)
            else:
                # Stance phase
                phase = (t - 0.4) / 0.6
                hip_a   =  20 - 40 * phase
                knee_a  = -5 * math.sin(math.pi * phase)
                ankle_a = -5 * math.sin(math.pi * phase)
        elif mode in PRESETS and mode != prev_mode:
            hip_a, knee_a, ankle_a = PRESETS[mode]
            prev_mode = mode
        elif mode == 0:
            hip_a   = p.readUserDebugParameter(hip_slider)
            knee_a  = p.readUserDebugParameter(knee_slider)
            ankle_a = p.readUserDebugParameter(ankle_slider)
            prev_mode = 0
        else:
            hip_a, knee_a, ankle_a = PRESETS.get(mode, (0, 0, 0))

        # Apply joint targets (position control)
        p.setJointMotorControl2(
            leg_id, hip_idx,
            p.POSITION_CONTROL,
            targetPosition=math.radians(hip_a),
            force=10, maxVelocity=5)

        p.setJointMotorControl2(
            leg_id, knee_idx,
            p.POSITION_CONTROL,
            targetPosition=math.radians(knee_a),
            force=10, maxVelocity=5)

        p.setJointMotorControl2(
            leg_id, ankle_idx,
            p.POSITION_CONTROL,
            targetPosition=math.radians(ankle_a),
            force=5, maxVelocity=5)

        # Step simulation
        p.stepSimulation()
        time.sleep(1.0 / 240)  # 240 Hz physics

except KeyboardInterrupt:
    print("\nSimulation ended.")
finally:
    p.disconnect()
