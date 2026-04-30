English | [中文](README.md)

# build123d CAD Skill Test

A test case collection for the build123d CAD Skill — validates various modelling operations and OCP Viewer visualisation features.

## Requirements

- Python 3.13+
- build123d 0.10.x
- cadquery-ocp
- ocp-vscode (OCP CAD Viewer extension)
- Pillow (GIF generation)
- [build123d-parts-lib](https://github.com/baibai2013/build123d-parts-lib) (standard part solid library, integrated as submodule)

## Initialisation (including parts-lib fetch)

```bash
git clone <this-repo>
cd build123d-cad-skill-test
git submodule update --init --recursive      # pull parts-lib
python3 -m venv .venv && source .venv/bin/activate
pip install build123d ocp-vscode pillow
pip install -e lib/parts-lib                 # editable install of parts-lib
```

**parts-lib usage examples**:

```python
from build123d_parts_lib.parts.servos.sg90            import make_sg90
from build123d_parts_lib.parts.fasteners.m3_iso4762   import make_m3_screw
from build123d_parts_lib.modules.threaded_insert_boss import make_m3_boss
from build123d_parts_lib.generators.clearance         import get_clearance_diameter
```

> **Working rules**: standard parts are imported from parts-lib first; new general-purpose standard parts are contributed back to parts-lib after OCP verification.

## Running Tests

```bash
cd tests/01-enclosure-box && python enclosure_box.py
cd tests/02-spur-gear && python gear_test.py
cd tests/20-ball-joint && python ball_joint.py
cd tests/22-esp32-s3-devkitc-enclosure && python esp32_s3_enclosure.py
cd tests/22-esp32-s3-devkitc-enclosure && python esp32_s3_enclosure_exploded.py
```

Output files are generated under `output/` in each test directory.

---

## Test Registry

### I. Parts Modelling

#### 01-enclosure-box — Enclosure Box (shell + snap-fit lid + text + assembly + exploded animation)

| Feature | Status | Notes |
|---------|--------|-------|
| Box + fillet + offset shell | :white_check_mark: | 80×60×40 mm body, 2.5 mm wall, vertical edge R2 fillet |
| Inner wall lip step | :white_check_mark: | lip_h=3 mm, lip_inset=1.2 mm |
| Lid + bottom snap-fit tab | :white_check_mark: | lid_thick=3 mm, tab fits into step, 0.3 mm clearance |
| Top face raised text | :white_check_mark: | "baibai" raised 1 mm, width ~70% of lid |
| Assembly positioning (Pos transform) | :white_check_mark: | Lid positioned to top face of body |
| Exploded view (Compound export) | :white_check_mark: | Explode distance 30 mm |
| OCP Animation exploded animation | :white_check_mark: | Explode 1s – hold 3s – close 1s – hold 3s (8s loop) |
| save_screenshot frame-by-frame → GIF | :white_check_mark: | 80 frames 10 fps, output/enclosure_explode.gif |

**APIs**: `Box`, `fillet`, `offset` (shell), `Rectangle`, `extrude`, `Text`, `Pos`, `Compound`, `export_step`, `export_stl`, `Animation`, `save_screenshot`

#### 02-spur-gear — Spur Gear (involute + per-tooth union)

| Feature | Status | Notes |
|---------|--------|-------|
| Involute tooth profile calculation | :white_check_mark: | Module 2, 20 teeth, 20° pressure angle |
| Root cylinder + per-tooth Algebra Mode union | :white_check_mark: | Avoids OCP rendering issues with large non-convex polygons |
| Centre bore + keyway | :white_check_mark: | Bore R4 mm, keyway width 2 mm |
| OCP Viewer preview | :white_check_mark: | Direct preview via show() |

**APIs**: `Cylinder`, `Wire.make_polygon`, `BRepBuilderAPI_MakeFace`, `BuildPart`, `BuildSketch`, `add`, `extrude`, `Box`, Algebra Mode (`+`, `-`), `export_step`

#### 03-mounting-plate — Mounting Plate (basics)

| Feature | Status | Notes |
|---------|--------|-------|
| Box + GridLocations hole array | :white_check_mark: | 100×80×10 mm, four-corner M5 through holes |
| fillet on top face edges | :white_check_mark: | Top edge R3 fillet |
| Selector positioning (sort_by top face) | :white_check_mark: | `faces().sort_by(Axis.Z)[-1]` |
| Parametric validation | :white_check_mark: | Hole positions follow when margin parameter changes |

**APIs**: `Box`, `GridLocations`, `Hole`, `fillet`, `sort_by`, `export_step`

#### 04-flange — Flange (Cylinder + polar counterbore array)

| Feature | Status | Notes |
|---------|--------|-------|
| Cylinder + centre through hole | :white_check_mark: | OD 80 mm, height 8 mm, centre bore R15 mm |
| PolarLocations bolt hole array | :white_check_mark: | PCD 60 mm, 6 holes equally spaced |
| CounterBoreHole | :white_check_mark: | Through hole R4 mm, counterbore R6.5 mm, depth 4 mm |

**APIs**: `Cylinder`, `Hole`, `PolarLocations`, `CounterBoreHole`, `export_step`

#### 05-stepped-shaft — Stepped Shaft (Polyline revolve + parametric keyway + chamfer)

| Feature | Status | Notes |
|---------|--------|-------|
| BuildSketch(Plane.XZ) + revolve | :white_check_mark: | Multi-step half-profile Polyline revolved 360° about Z |
| Parametric keyway cut (key_angle rotatable) | :white_check_mark: | Analytic plane formula drives keyway orientation, default 0° (−Y face) |
| chamfer on both ends | :white_check_mark: | 0.5 mm chamfer on smallest circular edge at each end |

**APIs**: `BuildSketch`, `Plane.XZ`, `Polyline`, `make_face`, `revolve`, `Plane(origin, x_dir, z_dir)`, `extrude(Mode.SUBTRACT)`, `chamfer`, `export_step`

#### 06-pipe-elbow — Pipe Elbow (Sweep path + two end connectors)

| Feature | Status | Notes |
|---------|--------|-------|
| Edge.make_circle arc path | :white_check_mark: | 90° arc in XZ plane, centreline radius 40 mm |
| Hollow cross-section sweep | :white_check_mark: | OD R15 mm, wall 2 mm, ID R13 mm |
| Path-tangent Plane construction | :white_check_mark: | `Plane(path @ t, z_dir=path % t)`, t=0/1 |
| Two end connectors (larger-diameter hubs) | :white_check_mark: | hub_r=18 mm, length 8 mm, outward extension for pipe mating |

**APIs**: `Edge.make_circle`, `sweep`, `Circle`, `Mode.SUBTRACT`, `Plane`, `extrude`, `export_step`

#### 07-heat-sink — Pin-Fin Heat Sink (GridLocations pin array)

| Feature | Status | Notes |
|---------|--------|-------|
| Box base + top-face positioning | :white_check_mark: | 30×30×3 mm base |
| GridLocations pin array | :white_check_mark: | 6×6 square pins, height 8 mm, 2×2 mm cross-section, four-sided airflow |
| Selector to pick top face as sketch plane | :white_check_mark: | `sort_by(Axis.Z)[-1]` |

**APIs**: `Box`, `GridLocations`, `Rectangle`, `extrude`, `sort_by`, `export_step`

---

### II. Surface Modelling

#### 08-loft-transition — Multi-section Loft Transition

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-plane BuildSketch + loft | :white_check_mark: | Circle → Rectangle → Circle three-section loft |
| Plane.XY.offset multi-height sections | :white_check_mark: | Three sections at z=0/30/60 |
| Surface continuity check | :white_check_mark: | G1 continuity volume validation (56301 mm³) |

**APIs**: `BuildSketch`, `Circle`, `Rectangle`, `loft`, `Plane.XY.offset`, `export_step`

#### 09-organic-shell — Organic Surface Shell

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-section Loft (5 elliptical sections) | :white_check_mark: | Variable-section streamlined shell, volume 10920 mm³ |
| offset(openings=) shell | :white_check_mark: | 2 mm wall, open bottom |
| Ellipse parametric sections | :white_check_mark: | Major/minor axes vary with height (z=0–60) |

**APIs**: `Ellipse`, `loft`, `offset(openings=)`, `Plane.XY.offset`, `export_step`

#### 10-sweep-twist — Twisted Sweep

| Feature | Status | Notes |
|---------|--------|-------|
| Linear path + section twist | :white_check_mark: | 20×10 mm rectangular section twisted 90°, volume 13000 mm³ |
| sweep multisection dual-section | :white_check_mark: | Start/end sections face different directions, linear interpolation |
| Transition.ROUND parameter | :white_check_mark: | `sweep(path, multisection=True, transition=Transition.ROUND)` |

**APIs**: `sweep`, `Edge.make_line`, `Plane(origin, x_dir, z_dir)`, `Transition`, `Rectangle`, `export_step`

---

### III. Joint Assembly

#### 11-revolute-hinge — Animal Bone Knee Joint + Rotation Animation

| Feature | Status | Notes |
|---------|--------|-------|
| Femur (Algebra Mode) | :white_check_mark: | Cylindrical shaft (r=5, h=50) + spherical joint heads at both ends, hip_r=8, joint_r=9 |
| Tibia (Algebra Mode) | :white_check_mark: | Shaft (r=4, h=45) + spherical heads, local origin = knee joint axis |
| RigidJoint fixed knee point | :white_check_mark: | Fixed joint at femur z=0 |
| RevoluteJoint knee | :white_check_mark: | Y-axis rotation, angular_range=(−120°, 10°) |
| connect_to pose positioning | :white_check_mark: | `j_thigh.connect_to(j_shin, angle=0/−60/−110)` |
| Frame-by-frame screenshot GIF | :white_check_mark: | 46 frames 0°→−110°→0° loop, Pillow GIF synthesis |
| OCP Animation track | :white_check_mark: | `add_track("ry")` flex/extend 6s loop |

**APIs**: `Cylinder(align=Align.MIN/MAX)`, `Sphere`, Algebra Mode(`+`), `RigidJoint`, `RevoluteJoint`, `connect_to`, `Compound`, `Animation`, `add_track`, `save_screenshot`, `export_step`

#### 12-quadruped-leg — Quadruped Leg Chain (7-part plate structure, reference-image driven)

| Feature | Status | Notes |
|---------|--------|-------|
| 7-part plate structure | :white_check_mark: | hip_mount + femur + tibia + metatarsus + foot_pad + 2 ligaments |
| Tapered plate geometry | :white_check_mark: | Polyline trapezoid profile + fillet, matches reference CNC aluminium plate |
| Arc foot pad | :white_check_mark: | ThreePointArc arc base + fan-shaped extension (ref: 182 mm → 36 mm) |
| RevoluteJoint 4-level chain | :white_check_mark: | hip(±45°) → knee(−90°~0°) → ankle(±30°) → foot(fixed) |
| FK ligament real-time follow | :white_check_mark: | Joint.location.position reads true world coordinates, ligaments hug knee joint |
| Walking cycle GIF animation | :white_check_mark: | 40 frames Peter Corke gait (swing 40% / stance 60%) |
| OCP Animation tracks | :white_check_mark: | FK translation keyframes, 5 rigid body separate tracks |
| tkinter interactive control | :white_check_mark: | 3 sliders + preset buttons + OCP live update (Route A) |
| PyBullet physics simulation | :white_check_mark: | URDF + gravity/collision/joint torques (Route B) |
| ipywidgets interaction | :white_check_mark: | Jupyter slider control (alternative interaction method) |
| STEP re-import verification | :white_check_mark: | Volume deviation 0.000000% |

**Reference dimensions (1:5 scale)**: Femur 245→50 mm (tapered 18→14 mm), Tibia 220→45 mm (tapered 16→12 mm), Foot 84×182→14×36 mm (arc)

**APIs**: `Polyline`, `make_face`, `fillet(vertices)`, `ThreePointArc`, `RevoluteJoint`, `RigidJoint`, `connect_to`, `Compound`, `PolarLocations`, `Hole`, `Animation`, `add_track`, `save_screenshot`, `export_step`

#### 20-ball-joint — Ball-and-Socket Joint (BallJoint 3 DOF)

| Feature | Status | Notes |
|---------|--------|-------|
| BallJoint 3 DOF connection | :white_check_mark: | `angular_range=((−45,45),(−45,45),(0,360))` |
| RigidJoint + BallJoint mating | :white_check_mark: | Base RigidJoint anchor + ball-arm BallJoint |
| Cup base (Box + hemispherical socket) | :white_check_mark: | 40×40×15 mm, cup_r=10 mm, vertical edge R3 fillet |
| Ball arm (Sphere + Cylinder union) | :white_check_mark: | ball_r=9 mm, arm_r=4 mm, arm_len=45 mm, 5 mm overlap for union |
| Three-pose connect_to side-by-side | :white_check_mark: | Upright (0°) / X-tilt 30° / X+Z tilt 30°+45° |
| Three-layer verification (BRep/volume/STEP) | :white_check_mark: | socket≈21685 mm³, ball_arm≈5087 mm³, STEP precision ✅ |
| OCP three-pose side-by-side preview | :white_check_mark: | `render_joints=True`, auto port detection |

**APIs**: `BallJoint`, `RigidJoint`, `connect_to`, `Rotation`, `Sphere`, `Cylinder`, `Box`, `fillet`, `export_step`, `import_step`

---

### IV. Reference Product Modelling

#### 13-redmi-k80-pro — Redmi K80 Pro External Reference Model

| Feature | Status | Notes |
|---------|--------|-------|
| Reference-image-driven dimension reconstruction (GSMArena ×3) | :white_check_mark: | R1 empirical lookup + R2 multi-source cross-validation |
| params.md parameter contract + contract.yaml | :white_check_mark: | Layer 0 YAML contract generated, constraint coverage 100% |
| build123d precise external geometry (rounded slab body) | :white_check_mark: | 161×75×8 mm, rectangular camera island, side surface curves |
| Layer 1 validation (volume/bbox/BRep) | :white_check_mark: | 4-stage pipeline, auto-repair loop ≤3 rounds |
| Layer 2 visual comparison (screenshot + AI comparison) | :white_check_mark: | Multi-angle screenshots vs reference, deviation analysis |
| extract_params.py dimension extraction tool | :white_check_mark: | Auto-extract + cross-validate parameters from images |
| visual_compare.py visual comparison tool | :white_check_mark: | 4 backends with auto-fallback (AI → OpenCV → manual) |

**APIs**: `Box`, `fillet`, `offset(openings=)`, `Hole`, `extrude(Mode.SUBTRACT)`, `export_step`

#### 14-xiaomi-k70-case — Xiaomi K70 Phone Case (FDM 3D printing)

| Feature | Status | Notes |
|---------|--------|-------|
| Phone case parametric modelling (FDM process) | :white_check_mark: | K70 parametric geometry, 1.5 mm wall, cutout weight reduction |
| part_face_mapping.yaml face mapping | :white_check_mark: | Mapping record of each feature face to design intent |
| Camera / button / charging port precise positioning | :white_check_mark: | Selector positioning, no hard-coded coordinates |
| 3D printing process constraint validation | :white_check_mark: | Wall ≥1.2 mm, overhang ≤45°, tolerance +0.3 mm |
| STEP export + re-import verification | :white_check_mark: | Volume deviation < 0.1% |

**APIs**: `Box`, `offset(openings=)`, `Hole`, `extrude(Mode.SUBTRACT)`, `fillet`, `export_step`

---

### V. Playbook & Skill Validation (Dry-run)

> All tests in this category are **dialogue-only validation** — no build123d code is executed; AI behaviour is checked against the Playbook.

#### 15-playbook-dryrun — Playbook R1–R5 Behaviour Regression

| Scenario | Status | Validation Points |
|----------|--------|-------------------|
| Scenario A: full R1–R5 (K70 case) | :white_check_mark: | 8 output report blocks, R2.7 not omitted |
| Scenario B: has STEP + skip Layer 2 | :white_check_mark: | R2.5/R2.7 explicit skip, 6 report blocks |
| Scenario C: has STEP + request Layer 2 (trap) | :white_check_mark: | R2.5 skip + R2.7 executed, not confused |

#### 16-experience-dryrun — Experience Cache Behaviour Regression

| Scenario | Status | Validation Points |
|----------|--------|-------------------|
| Scenario D: cold start (no experience file) | :white_check_mark: | R1 reports `[miss]`, R5 creates new experience file |
| Scenario E: exact hit | :white_check_mark: | R1 reports `[hit]`, parameters + pitfalls injected correctly |
| Scenario F: same-category hit | :white_check_mark: | R1 reports `[partial]`, used as reference, not direct reuse |

#### 17-skill-optimization-dryrun — SKILL.md De-content + Quote-back Enforcement

| Scenario | Status | Validation Points |
|----------|--------|-------------------|
| Scenario G: reference product modelling (R Playbook) | :white_check_mark: | AI reads Playbook, each Step has Quote-back as first line |
| Scenario H: single-part modelling (S Playbook) | :white_check_mark: | AI reads Playbook, does not rely on memory |
| Scenario I: multi-part assembly (P Playbook) | :white_check_mark: | AI reads Playbook, Phase output report format compliant |

#### 18-assembly-contract-dryrun — Assembly Contract + bbox Pre-check

| Scenario | Status | Validation Points |
|----------|--------|-------------------|
| Scenario J: two-joint arm (≥2 parts) | :white_check_mark: | Step 2e outputs assembly_contract.yaml + precheck_bbox.md |
| Scenario K: deliberately omit 1 assembly relation | :white_check_mark: | Triggers FM-12, cross_refs coverage gap caught |

#### 19-hard-halt-dryrun — Confirmation Gate Enforcement

| Scenario | Status | Validation Points |
|----------|--------|-------------------|
| Scenario L: AI skips S2 sketch confirmation gate | :white_check_mark: | Triggers FM-1, back-fills output + re-issues halt |
| Scenario M: multi-part Phase 1 confirmation gate | :white_check_mark: | Triggers FM-13, halt takes effect correctly |
| Scenario N: reference product R3.5 visual confirmation gate | :white_check_mark: | Triggers FM-10, back-fill correct |

**Structure check**: 10/10 all pass ✅ (SKILL.md §Confirmation Gate Execution Contract + 3 Playbook FM clauses)

---

### VII. Mounting Practice

#### 21-servo-mount — SG90 Servo Mount (extrude subtract-only + precise cavity)

| Feature | Status | Notes |
|---------|--------|-------|
| Servo body cavity (cut down from top face) | :white_check_mark: | SG90 standard 22.8×12.2×22.7 mm, 0.3 mm clearance, 2.5 mm wall |
| Ear tab step slots (both sides) | :white_check_mark: | Ear width 32.2 mm, ear thickness 2.5 mm, sketch difference `Rectangle − Rectangle` |
| M2 tapped holes (×4) | :white_check_mark: | Hole pitch 27.6 mm, through top face into ears, depth ear_t + 2 mm |
| Cable exit (−X side face) | :white_check_mark: | 9×6 mm rectangular opening, through wall thickness |
| Bottom M3 mounting holes (4 corners) | :white_check_mark: | Mount to frame, 5 mm from outer wall |
| Vertical edge fillet on perimeter | :white_check_mark: | R1.5 mm, `fillet(filter_by(Axis.Z))` |
| Three-layer verification (BRep/bbox/STEP) | :white_check_mark: | bbox 28.4×37.8×25.2 mm, fill ratio 70.3%, STEP precision ✅ |

**APIs**: `Box`, `Rectangle`, `extrude(Mode.SUBTRACT)`, `fillet`, `filter_by(Axis.Z)`, `export_step`, `import_step`

#### 22-esp32-s3-devkitc-enclosure — ESP32-S3-DevKitC-1 Dev Board Enclosure (reference product + 2-part snap-fit)

| Feature | Status | Notes |
|---------|--------|-------|
| Official DXF reverse-engineering PCB dimensions | :white_check_mark: | 62.74×25.40×1.6 mm, no mounting holes (community error corrected), 2×Micro-USB (not USB-C) |
| Coordinate contract (pcb_origin_world) | :white_check_mark: | PCB local→world Location transform, eliminates hard-coded derived coordinates |
| Bottom shell + lid clamp scheme | :white_check_mark: | 4-corner low pads (h=4 mm) + lid press tabs (0.5 mm protrusion) grip PCB, no screw holes needed |
| `offset` shell (shell substitute) | :white_check_mark: | Lid `offset(amount=−lid_t, openings=bottom_face)` |
| 2×USB capsule cutouts | :white_check_mark: | `SlotOverall(10, 5, rotation=90)` USB-C visual, derived from J2(6.00,3.66) + J4(19.40,3.66) |
| Boot/Reset button press pillars | :white_check_mark: | 3 mm flexible pillars, derived from SW1(6.76,13.79) + SW2(17.17,13.92) |
| RGB LED light-pipe hole + 3 vent slots | :white_check_mark: | LED d=3.5 mm at (5.08,31.60), top panel vents 2×20 mm×3 |
| Snap-fit clips (left/right short sides) | :white_check_mark: | 6 mm cantilever + 0.8 mm head + 0.4 mm lead-in chamfer |
| Bottom 4×M3 mounting holes | :white_check_mark: | r=1.6 mm, positions (±22, ±10) clear of 4-corner pads |
| Layer 0 parameter contract + static check | :white_check_mark: | 9 features / 47 constraints / 0 conflicts |
| Three-layer verification (BRep/volume/STEP) | :white_check_mark: | Bottom shell 6248 mm³ / lid 7196 mm³ / STEP precision 0.0000% |
| 2-part assembly + exploded GIF | :white_check_mark: | 3 layers (bottom / PCB+modules / lid), 16s loop, 160 frames @10fps |

**APIs**: `Box`, `Cylinder`, `SlotOverall(rotation=90)`, `Circle`, `offset(openings=)`, `extrude(Mode.SUBTRACT)`, `BuildSketch(face)`, `fillet`, `import_step`, `Location`, `Compound`, `Animation.add_track`, `animation.set_relative_time`

**Dave Cowden review notes**: params.md + contract.yaml through 2 review rounds: corrected body_ref self-reference, added coordinate contract section, split lid clearance for "with/without soldered headers", removed redundant derived parameters, added snap-fit cantilever length

#### pcb-enclosure — PCB Enclosure (with screw holes, pending)

| Feature | Status | Notes |
|---------|--------|-------|
| Box + shell | :x: | For PCBs with M2.5 mounting holes |
| M2.5 standoffs (GridLocations) | :x: | 4-corner standoffs aligned to PCB mounting holes |
| USB-C opening | :x: | Side wall cutout, positioned to PCB height |
| Ventilation slots | :x: | Bottom/side strip openings |
| Snap-fit lid | :x: | Snap-fit clips + assembly preview |

#### sensor-bracket — Sensor Bracket (HC-SR04) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| L-bracket base plate | :x: | Base plate with mounting holes |
| Dual circular sensor windows | :x: | HC-SR04 two transducer centre distance 26 mm |
| Angle adjustment slot | :x: | Slotted hole allows tilt adjustment |

---

### VIII. OCP Visualisation (Viewer)

#### show-params — show() Parameter Validation (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-object multi-colour show | :x: | `show(a, b, colors=["steelblue","orange"])` |
| names labelling | :x: | `names=["body","lid"]` → OCP tree structure |
| transparent semi-transparency | :x: | `alphas=[0.5, 1.0]` transparency inspection |
| reset_camera / Camera enum | :x: | `Camera.FRONT`, `Camera.ISO` |

#### animation-explode — Exploded Animation (Animation API) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| Animation + add_track translation | :x: | `add_track("/Group/name", "t", ...)` |
| 16s loop timeline | :x: | Explode 2s → hold 10s → close 2s → hold 2s |
| animate(speed) playback | :x: | speed=1 normal speed |
| save_as_gif export | :x: | fps=20, looping GIF |

#### animation-joint — Multi-joint Motion Animation (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| RevoluteJoint angle → rz track | :x: | Joint rotation mapped to OCP animation |
| Multi-track coordination | :x: | Four-leg alternating gait choreography |
| Timeline phase offset | :x: | Different phases per joint |

#### studio-material — PBR Material Rendering (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| StudioEnvironment preset | :x: | `show(..., preset="default")` |
| Metal / plastic materials | :x: | PBR material assigned to different parts |
| Screenshot comparison | :x: | `save_screenshot` high-quality render |

---

### IX. Manufacturing Process Validation

#### 21-print-tolerance — 3D Printing Tolerance Test Pieces (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| Clearance fit test (0.1–0.5 mm gradient) | :x: | Male/female fit, 5 clearance steps |
| Minimum wall thickness validation | :x: | 0.4 / 0.6 / 0.8 / 1.0 mm walls |
| Overhang angle test | :x: | 30° / 45° / 60° overhangs |
| STL export parameter comparison | :x: | draft / standard / fine three precision levels |

#### 22-laser-dxf — Laser Cutting DXF Export (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| 2D profile construction | :x: | Mounting plate + internal holes + lightening slots |
| export_dxf export | :x: | 2D DXF file |
| Kerf compensation (offset profile) | :x: | Outward/inward 0.1 mm |

---

### X. Motion Simulation

#### 25-fk-leg-chain — FK Forward Kinematics (DH homogeneous transforms + OCP visualisation) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| DH parameters for 3-link chain | :x: | d1=55 mm, L1=100 mm, L2=100 mm |
| Homogeneous transform chain FK | :x: | numpy 4×4 T01×T12×T23 |
| build123d Location validation | :x: | Pos*Rot chain result matches numpy |
| OCP visualisation (joint spheres + bone lines) | :x: | show() multi-object multi-colour preview |

#### 26-ik-single-leg — IK Inverse Kinematics (analytic + dual-configuration comparison) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| 3-link analytic IK (law of cosines) | :x: | Input foot (x,y,z) → solve θ1,θ2,θ3 |
| Dual-configuration comparison (knee_sign ±1) | :x: | Knee-forward / knee-backward two poses |
| FK→IK→FK round-trip validation | :x: | Error < 0.01 mm |
| OCP dual-pose side-by-side | :x: | Two configurations offset 150 mm apart |

#### 27-workspace-cloud — Workspace Point Cloud (FK sweep + reachability visualisation) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| Angle grid FK sweep | :x: | 3 axes × 15 steps → 3375 foot-tip points |
| Point cloud downsampling | :x: | Random sample 500 points to avoid OCP slowdown |
| Shoulder joint marker + default stance | :x: | Reference point + current pose comparison |

#### 28-gait-generator — Gait Generator (Bézier trajectory + IK + OCP animation) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| 11-point Bézier swing-phase trajectory | :x: | MIT standard swing curve |
| Trot diagonal gait phase table | :x: | LF+RR in-phase, RF+LR in-phase |
| IK joint angle sequence | :x: | Gait → foot → IK → joint angles |
| OCP Animation quadruped animation | :x: | 4s loop, 20fps keyframes |

#### 29-urdf-export — URDF Export (build123d → URDF + STL) (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| build123d parts + labels | :x: | body + upper_leg + lower_leg + foot |
| URDF XML generation (link + joint) | :x: | revolute joints + limit constraints |
| STL mesh auto-export | :x: | One .stl file per link |
| Mass/inertia estimation | :x: | volume × density → inertial tag |
| yourdfpy optional validation | :x: | Load URDF, check joint axes |

---

### XI. Verification Tools

#### 23-validate-geometry — Geometry Validation (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| is_valid() BRep validity | :x: | BRep check on multiple parts |
| volume > 0 assertion | :x: | Positive volume validation |
| bounding_box dimension assertion | :x: | Bounding box vs design values |
| do_children_intersect collision | :x: | Assembly collision detection |

#### 24-export-formats — Multi-format Export (pending)

| Feature | Status | Notes |
|---------|--------|-------|
| STEP export + re-read validation | :x: | export_step → import_step → volume comparison |
| STL export + file size sanity | :x: | Different precision levels |
| BREP export + re-read validation | :x: | export_brep → import_brep lossless |
| DXF export | :x: | 2D sketch export |

---

## Coverage Summary

| Category | Done | Pending | Total |
|----------|------|---------|-------|
| Parts modelling | 7 | 0 | 7 |
| Surface modelling | 3 | 0 | 3 |
| Joint assembly | 3 | 0 | 3 |
| Reference product modelling | 3 | 0 | 3 |
| Playbook/Skill validation | 5 | 0 | 5 |
| Mounting practice | 2 | 2 | 4 |
| OCP visualisation | 0 | 4 | 4 |
| Manufacturing process | 0 | 2 | 2 |
| Motion simulation | 0 | 5 | 5 |
| Verification tools | 0 | 2 | 2 |
| **Total** | **23** | **15** | **38** |

---

## Directory Structure

```
build123d-cad-skill-test/
├── README.md
├── README_EN.md
├── lib/
│   └── parts-lib/                # ← git submodule, baibai2013/build123d-parts-lib
│                                 #   from build123d_parts_lib.* import after pip install -e
├── tests/
│   ├── 01-enclosure-box/         # ✅ Enclosure box
│   ├── 02-spur-gear/             # ✅ Spur gear
│   ├── 03-mounting-plate/        # ✅ Mounting plate
│   ├── 04-flange/                # ✅ Flange
│   ├── 05-stepped-shaft/         # ✅ Stepped shaft
│   ├── 06-pipe-elbow/            # ✅ Pipe elbow
│   ├── 07-heat-sink/             # ✅ Heat sink
│   ├── 08-loft-transition/       # ✅ Multi-section loft
│   ├── 09-organic-shell/         # ✅ Organic surface
│   ├── 10-sweep-twist/           # ✅ Twisted sweep
│   ├── 11-revolute-hinge/        # ✅ Revolute hinge
│   ├── 12-quadruped-leg/         # ✅ Quadruped leg chain
│   ├── 13-redmi-k80-pro/         # ✅ Reference product — Redmi K80 Pro
│   ├── 14-xiaomi-k70-case/       # ✅ Reference product — K70 phone case (FDM)
│   ├── 15-playbook-dryrun/       # ✅ Playbook R1–R5 behaviour regression
│   ├── 16-experience-dryrun/     # ✅ Experience cache behaviour regression
│   ├── 17-skill-optimization-dryrun/ # ✅ SKILL.md de-content + Quote-back
│   ├── 18-assembly-contract-dryrun/  # ✅ Assembly contract + bbox pre-check dryrun
│   ├── 19-hard-halt-dryrun/      # ✅ Confirmation gate enforcement validation
│   ├── 20-ball-joint/            # ✅ Ball-and-socket joint (BallJoint 3 DOF)
│   ├── 21-servo-mount/           # ✅ SG90 servo mount (subtract-only)
│   ├── 22-esp32-s3-devkitc-enclosure/  # ✅ ESP32-S3 dev board enclosure (reference + 2-part snap-fit)
│   ├── (pending) pcb-enclosure/  # ⬜ PCB enclosure (with screw holes)
│   ├── (pending) sensor-bracket/ # ⬜ Sensor bracket
│   ├── (pending) show-params/    # ⬜ show() parameters
│   ├── (pending) animation-explode/ # ⬜ Exploded animation
│   ├── (pending) animation-joint/   # ⬜ Joint animation
│   ├── (pending) studio-material/   # ⬜ PBR materials
│   ├── (pending) print-tolerance/   # ⬜ Print tolerance
│   ├── (pending) laser-dxf/         # ⬜ Laser DXF
│   ├── (pending) validate-geometry/ # ⬜ Geometry validation
│   ├── (pending) export-formats/    # ⬜ Multi-format export
│   ├── (pending) fk-leg-chain/      # ⬜ FK forward kinematics
│   ├── (pending) ik-single-leg/     # ⬜ IK inverse kinematics
│   ├── (pending) workspace-cloud/   # ⬜ Workspace point cloud
│   ├── (pending) gait-generator/    # ⬜ Gait generator
│   └── (pending) urdf-export/       # ⬜ URDF export
├── docs/                           # Design documents and implementation plans
├── references/                     # Local snapshots / quick-test resources for skill references
└── generated/                      # Temporary tool script outputs
```

---

## Disclaimer

This repository is a feature exploration and validation test collection for the build123d CAD Skill, intended primarily for documentation and learning. All content is provided as-is. Test results and generated models are for reference only; OCP visual verification serves as an auxiliary means — independent evaluation based on specific requirements is recommended.

---

## License

Apache License 2.0 — Commercial use allowed, with explicit patent grant. See [LICENSE](LICENSE).
