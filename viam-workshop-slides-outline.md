# Viam Pick-and-Place Workshop: Slideshow Outline
## Pick-and-Place — xArm6 · RealSense D435 · Shape-Guided Picking

> Source of truth: `viam-workshop-v2.pdf` (60 pages). This outline mirrors the deck's
> content and ordering. Slide sub-numbers have been renumbered cleanly and sequentially
> per phase (the PDF export had duplicate/out-of-order labels — e.g. two `1.8`s, repeated
> `4.5–4.7`, and `4.8` exported last). Facilitator `> Note:` blocks are not on the slides
> themselves — they are speaker guidance.

---

## Timing Overview

| Phase | Topic | Time |
|-------|--------|------|
| 0 | Orientation | 8 min |
| 1 | Platform Mental Model | 15 min |
| 2 | Configure Resources + Explore the App | 20 min |
| 3 | Static Positions + Safety Obstacles | 20 min |
| 4 | Local Python Script | 30 min |
| 5 | Inline Module *(stretch goal)* | 15 min |
| 6 | Wrap + Next Steps | 5 min |
| — | Q&A distributed across phases | 7 min |
| **Total** | | **120 min** |

---

# PHASE 0 — ORIENTATION (8 min)

---

## [0.1] — Title Slide

- **DEVELOPER WORKSHOP · Viam**
- **Pick-and-Place Workshop**
- xArm6 · RealSense D435 · 2 Hours
- *Prerequisites required · Hands-on*

**Agenda:** 0 Orientation · 1 Platform Mental Model · 2 Configure Resources ·
3 Static Positions + Obstacles · 4 Local Python Script · 5 Inline Module *(stretch)* ·
6 Wrap + Next Steps

> Note: Keep this up during setup. Prerequisites (Python 3.10+, viam-sdk, a working terminal) were listed in the invite — confirm verbally that everyone has them before Phase 4.

---

## [0.2] — What We're Building Today

1. **Static positions** — save arm poses; test hardware and motion planning first
2. **Perception-guided script** — add shape detection → 3D localisation → pick-and-place loop
3. **Inline module** *(stretch)* — convert the working script to a service that runs autonomously on the robot

**Goal: working local script by end of Phase 4. The module is the bonus.**

> Note: Emphasise the three-step progression. Students who don't finish the module still leave with a working local script — that's a real success.

---

## [0.3] — Hardware Tour

| Component | Role |
|---|---|
| System76 Meerkat | Robot computer · x86_64 · Ubuntu |
| uFactory xArm6 | 6-DOF arm · direct Ethernet to Meerkat |
| uFactory Finger Gripper | End effector at the flange |
| Intel RealSense D435 | RGB + depth camera · USB · wrist-mounted on arm link |

- viam-agent and viam-server are **already running** on the Meerkat
- No SSH required today

> Note: Point out the wrist-mounted camera. Because it's on the arm, its frame parent is the arm link — this affects how we transform poses to world frame, which matters in Phase 4.

---

## [0.4] — Agenda & Timing

| # | Phase | Time |
|---|---|---|
| 0 | Orientation | 8 min |
| 1 | Platform Mental Model | 15 min |
| 2 | Configure Resources + Explore the App | 20 min |
| 3 | Static Positions + Safety Obstacles | 20 min |
| 4 | Local Python Script | 30 min |
| 5 | Inline Module *(stretch goal)* | 15 min |
| 6 | Wrap + Next Steps | 5 min |

- Q&A distributed per phase
- Goal: working script by end of Phase 4

---

## [0.5] — Activity: Log In and Find Your Machine **[LIVE DEMO]**

1. Go to **app.viam.com** and sign in
2. Navigate to org: `viam-dev` → location: `workshops`
3. Open your machine: `workshop-#` (your assigned number)
4. Confirm the green **Live** indicator

> Note: Everyone gets their own machine today. "Disconnected" usually means wrong org selector or wrong machine number. Walk the room.

---

# PHASE 1 — PLATFORM MENTAL MODEL (15 min)

*Three questions, three layers, one module system.*

---

## [1.1] — Three Questions to Answer First

- How does my **laptop** talk to the robot?
- How does the robot know what **hardware** it has?
- How do I add new **capabilities** without rebuilding everything?

> Note: Frame these explicitly. Don't answer yet.

---

## [1.2] — The Three Layers

*(Dark cards + diagram build: cloud → viam-agent + viam-server → hardware)*

- **CLOUD** `app.viam.com` — Config · Observability · OTA updates · WebRTC signaling
- **ON-DEVICE** `viam-agent → viam-server` — viam-agent keeps viam-server alive; viam-server downloads module binaries from the registry, instantiates resources, exposes gRPC APIs
- **COMPONENTS** Physical Hardware — xArm6 · RealSense D435 · Finger Gripper

> Note: Distinguish viam-agent (process manager, keeps viam-server alive) from viam-server (runtime, downloads modules). Students conflate these.

---

## [1.3] — How Your SDK Client Connects

*(Diagram: Your Laptop (SDK client code) ←WebRTC peer-to-peer→ Meerkat (viam-server))*

- Connection signaled via app.viam.com — **traffic flows directly**. Cloud is a signaling server, not a relay.
- Direct connection — low latency, suitable for real-time control
- Works on LAN, VPN, or the internet — your script connects even off-site

---

## [1.4] — Config is the Source of Truth

- Machine config lives in the cloud as JSON
- viam-server polls for changes, applies within seconds — no SSH, no restarts
- Everything in the CONFIGURE tab is this JSON plus a UI wrapper

```json
{
  "components": [
    { "name": "arm-1", "model": "viam:ufactory:xArm6",
      "attributes": { "host": "192.168.1.100" } },
    { "name": "cam-1", "model": "viam:camera:realsense" }
  ]
}
```

---

## [1.5] — Resources: The Universal Abstraction

```
viam : ufactory : xArm6
 │         │        │
namespace family  model
```

- **Namespace** — who published it (`viam` · your-org · community)
- **Family** — the module or hardware family (`ufactory` · `camera` · `realsense`)
- **Model** — the specific implementation (`xArm6` · `lite6` · `xArm7`)

`arm.get_end_position()` works identically on an xArm6 or a Universal Robots UR5e. Stable API, swappable implementation.

---

## [1.6] — Components vs. Services

*(Two-column cards)*

**Components** — physical things or logical equivalents
- `arm` · `camera` · `gripper` · `switch` · `sensor` · `motor`
- Fixed API per type; model-specific implementation underneath

**Services** — higher-order capabilities across components
- `vision` — colour/shape/ML detection
- `motion` — plans arm trajectories
- `data_manager` — captures + syncs

> Note: Services depend on components but never talk to hardware directly. This is the composability model.

---

## [1.7] — The Resource Dependency Graph

*(Diagram: cam-1 → shape-detector → vision-segment → [script / module]; arm-1 · gripper-1 used directly)*

- `cam-1 (viam:camera:realsense)` → RGB + depth
- `shape-detector (devrel:shape-finder:detector)` → 2D bounding boxes
- `vision-segment (viam:vision:detections-to-segments)` → 3D point clouds using realsense depth
- `[script / module]` — your control logic; uses `arm-1` and `gripper-1` directly

Resources are composed together to create intelligent pipelines and automation.

> Note: Draw this on the whiteboard. The pipeline matters: the control logic calls vision-segment, not shape-detector directly.

---

## [1.8] — Modules: The Extension Mechanism

*(Step-by-step cards: config → download → subprocess → live resource)*

1. **Config:** `{ "model": "viam:ufactory:xArm6" }` — declared in the machine config on app.viam.com
2. viam-server **downloads the module binary** from the Viam Registry — cross-architecture: x86_64, arm64, and more
3. **Spawned as a subprocess**, connected via gRPC socket — isolated process; a crash in the module doesn't crash viam-server
4. **Arm resource is live** in the resource graph

Same mechanism for **hardware drivers** (xArm6 module) and **your control code** (Phase 5).

> Note: This is the first look at modules. In Phase 5 the same mechanism packages the student's own control logic. Plant the seed now.

---

## [1.9] — Phase 1 Summary

- Three layers: cloud → viam-agent → viam-server (downloads modules + runs resources)
- SDK: peer-to-peer WebRTC, signaled via cloud — low latency, no proxy
- Resources: `namespace:family:model` — stable API, swappable implementation
- Components handle hardware; services compose over them
- Your laptop connects directly to the robot — no cloud relay in the data path

*Questions?*

---

# PHASE 2 — CONFIGURE RESOURCES + EXPLORE THE APP (20 min)

*Test cards · 3D scene · colour-detection pipeline.*

---

## [2.1] — What To Configure

**Hardware components:**

| Name | Type | Model |
|---|---|---|
| `arm-1` | arm | `viam:ufactory:xArm6` |
| `gripper-1` | gripper | `viam:ufactory:gripper` |
| `cam-1` | camera | `viam:camera:realsense` |

> Note: Only hardware is configured here. The vision pipeline is added in Phase 4; the pose switches and obstacle geometries are configured in Phase 3.

---

## [2.2] — Activity: Explore the CONTROL Tab **[LIVE DEMO]**

Test each component in this order:
1. **Camera** — GetImage + GetPointCloud
2. **Arm** — GetJointPositions · jog joint 4 · GetEndPosition
3. **Gripper** — Grab · Open · IsHoldingSomething

> Note: Pose switches don't exist yet — students save and test them in Phase 3.

---

## [2.3] — Camera Test Card **[LIVE DEMO]**

- **GetImages** — poll image frames from the camera · get a live stream
- **GetPointCloud** — 3D depth data visualized in the browser

Latency is low — peer-to-peer WebRTC, not cloud-proxied.

> Note: Plant the idea that a pixel alone isn't enough to move the arm — you need depth. Point clouds give spatial location. This pays off in Phase 4 when vision-segment fuses RGB + depth.

---

## [2.4] — Arm Test Card **[LIVE DEMO]**

- **GetJointPositions** — read current joint angles (UI shows degrees by default; SDK uses radians or degrees)
- **MoveToJointPositions** — jog joint 4 by +5°, confirm the arm moves, hit Stop
- **GetEndPosition** — x/y/z in mm + OrientationVector (OX, OY, OZ, Theta)

> Note: Unit importance (degrees by default in UI, radians or degrees in SDK) will come up again in Phase 4. Plant the seed now.

---

## [2.5] — Gripper Test Card **[LIVE DEMO]**

- **Grab** — close the gripper fingers
- **Open** — open the gripper fingers
- **IsHoldingSomething** — use gripper feedback to determine this state

> Note: The workshop hardware is the uFactory finger gripper — Grab/Open just close and open the fingers.

---

## [2.6] — The 3D Scene Tab **[LIVE DEMO]**

- Live frame system tree rooted at `world`
- Arm geometry — collision meshes at the current pose
- Camera frame parented to arm link — moves with the arm as it articulates
- Gripper frame at the flange — what `motion.move` targets

```json
// Camera Frame
{ "orientation": { "type": "ov_degrees", "value": { "th": 270, "x": 0, "y": 0, "z": 1 } },
  "parent": "arm-1", "translation": { "x": -73, "y": 40, "z": 18 } }

// Gripper Frame
{ "orientation": { "type": "ov_degrees", "value": { "th": 0, "x": 0, "y": 0, "z": 1 } },
  "parent": "arm-1", "translation": { "x": 0, "y": 0, "z": 105 } }
```

> Note: The wrist-mounted camera frame is parented to `arm-1` and changes as the arm moves. Students must be at the home observation pose before detecting objects, so the camera has a known, repeatable view.

---

## [2.7] — Phase 2 Summary

- CONFIGURE tab: all resources visible as cards; JSON underneath
- 3D scene tab: live frame system and collision geometry — a debugging tool for Phase 4
- Camera is wrist-mounted — frame moves with the arm

*Questions?*

---

# PHASE 3 — STATIC POSITIONS + SAFETY OBSTACLES (20 min)

*Prove hardware works before adding perception.*

---

## [3.1] — Why Static Positions First?

**Problem:** If you add perception and motion planning at the same time, any bug could be in the detection, the frame transform, the pose calculation, the motion planner, or the gripper timing — with no way to isolate which.

| Step | What it validates |
|---|---|
| Arm reaches home pose | Observation position is safe and repeatable |
| Arm reaches approach pose | Arm can position above the workspace |
| Arm reaches grasp pose | Descent distance is correct for block height |
| Gripper opens and closes | Finger gripper timing is correct |
| Arm reaches travel pose | Carrying height clears bin and table edges |
| Arm reaches place pose | Bin position is correct |

---

## [3.2] — The Five Key Poses

*(Cards for each pose with description)*

| Switch | Purpose | Notes |
|---|---|---|
| `home-pose` | Observation position above workspace | Camera has clear, repeatable view of all blocks |
| `approach-pose` | Directly above pick zone | ~80–100mm above highest block · same x/y as `grasp-pose` |
| `grasp-pose` | At the block — gripper fingers level | Gripper open at this height · z matches block top |
| `travel-pose` | Safe carrying height | Arm slightly retracted · clears bins and walls |
| `place-pose` | Above the sorting bin | Arm drops block from here |

`approach-pose` and `grasp-pose` share the same x/y — only z differs. The descent between them should be straight down.

> Note: The deck previously titled this "Six Key Poses"; the table lists five, so it has been corrected. A LinearConstraint enforces the straight-down descent in Phase 4. Per-colour bins are an exercise (see [6.2]) — the core flow uses one `place-pose`.

---

## [3.3] — Capturing Poses: Arm Card + Switch Card **[LIVE DEMO]**

1. Jog the arm to the desired position using the arm test card (**MoveToJointPositions**)
2. Open the **switch test card** for that pose (e.g. `home-pose`)
3. **SetPosition(1)** → saves current joint positions to the switch
4. **SetPosition(2)** → arm moves back to the saved position; verify it returned correctly
5. Repeat for: `home-pose` · `approach-pose` · `grasp-pose` · `travel-pose` · `place-pose`

**SetPosition(1) = save · SetPosition(2) = execute · SetPosition(0) = idle**

> Note: The pose switches are `erh:vmodutils:arm-position-saver` components — add one per pose to the config before capturing. Students often try (2) before (1) — remind them to save first.

---

## [3.4] — WorldState: Configuring the Environment

The motion planner is collision-aware, but it can only avoid what it knows about.

**Without WorldState:** Planner avoids self-collision (arm vs. arm geometry) but has no knowledge of the table, bins, or workspace walls.

**With WorldState:** Planner treats configured geometries as hard obstacles — the arm cannot be planned through them. Safer and more predictable.

Obstacles we will configure:
- **Table surface** — prevents the arm from crashing into the table on any planned path
- **Sorting bins** — prevents the arm from driving through a bin while transiting
- **Safety walls (workspace boundary)** — virtual planes; prevent the arm from swinging into students

> Note: The safety walls are a real safety feature — make that concrete for the room.

---

## [3.5] — Obstacle Geometry: Measuring and Configuring **[LIVE DEMO]**

**Facilitator provides:** table dimensions, bin dimensions.
**Students measure:** bin centre position relative to the arm base.

```json
// obstacle component config
"geometries": [
  { "label": "table", "type": "box", "x": 1200, "y": 800, "z": 30 }
]
```

```json
// obstacle-open-box component config
{
  "length": 210,
  "width": 150,
  "height": 25,
  "thickness": 1,
  "to_move": "gripper-1",
  "offset": 100
}
```

- Measure bin centre x/y: move the arm over the bin → read x, y from GetEndPosition
- Pose z for the bin = half its height (150mm bin → z = 75)
- Pose z for the table = -15 (half of 30mm thickness; sits below world z=0)
- Safety walls: thin boxes at the workspace boundary edges

> Note: Obstacles are `erh:vmodutils:obstacle` / `erh:vmodutils:obstacle-open-box` components. Pose z is the centre of the box geometry. They apply to motion planning automatically once configured.

---

## [3.6] — Test the Full Static Sequence **[LIVE DEMO]**

From the CONTROL tab, trigger switches in order. Watch the 3D scene tab for any obstacle collisions.

```
home-pose (2)      → arm moves to observation position
approach-pose (2)  → arm positions above pick zone
[open gripper]     → fingers spread, ready to receive
grasp-pose (2)     → arm descends to block height
[close gripper]    → fingers close
travel-pose (2)    → arm lifts to safe carrying height
place-pose (2)     → arm moves to sorting bin
[open gripper]     → drop, block lands in bin
home-pose (2)      → return to start
```

*Success: the arm completes the full sequence, with no collision errors in the LOGS tab.*

> Note: If motion planning fails at any step, the 3D scene tab shows what the planner sees. Common issues: approach pose too close to the table obstacle, travel pose colliding with bin geometry. Adjust the pose, re-save, re-test.

---

# PHASE 4 — LOCAL PYTHON SCRIPT (30 min)

*Fast feedback · `from_robot` · perception loop. Students write a Python script on their laptop that connects to the robot and controls it.*

---

## [4.1] — Why Local Script Before Module?

| | Local Script | Inline Module |
|---|---|---|
| Feedback loop | Instant (run from terminal) | >1 min (Python cloud build) |
| Connection | `RobotClient.at_address()` — explicit | Dependency injection via `validate_config` |
| Runs on | Your laptop | The robot (Meerkat) |
| Auto-restarts | ✗ | ✓ (viam-server manages subprocess) |
| Best for | Learning · iterating · debugging | Production · fleet · unattended |

**Rule of thumb:** get it working as a script first. Converting to a module is mostly packaging — same logic, different entry point.

---

## [4.2] — Prerequisite Check

```bash
# Check Python version (must be 3.10+)
python3 --version
```

```bash
# Check viam-sdk is installed
python3 -c "import viam; print(viam.__version__)"
```

```bash
pip install viam-sdk
# or:  uv add viam-sdk  /  mise x -- pip install viam-sdk
```

> Note: This should be done before the workshop. If anyone doesn't have it, pair them with a neighbour — don't let this block Phase 4 for the group.

---

## [4.3] — Connect to Your Robot from the Connect Tab **[LIVE DEMO]**

In the app: **Connect tab** → **Python SDK** → copy the starter snippet. Replace nothing yet — run it first.

```python
import asyncio
from viam.robot.client import RobotClient
# ... rest of the component imports

async def main():
    async with await RobotClient.at_address(
        "<your-machine-address>",
        options=RobotClient.Options.with_api_key(
            api_key="<from Connect tab>",
            api_key_id="<from Connect tab>",
        ),
    ) as machine:
        print(machine.resource_names)  # list all available resources

asyncio.run(main())
```

Run it. You should see `arm-1`, `gripper-1`, `cam-1`, the poses as Switches, and obstacles as grippers.

> Note: API key is per-student, generated from the machine's Connect tab. The address works over the internet via WebRTC signaling — students don't need to be on the same network as the robot. Note the client variable is `machine` here, matching the Connect-tab snippet.

---

## [4.4] — Get Resources and Run the Static Sequence **[LIVE DEMO]**

```python
from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.components.switch import Switch

    arm       = Arm.from_robot(machine, "arm-1")
    gripper   = Gripper.from_robot(machine, "gripper-1")
    home      = Switch.from_robot(machine, "home-pose")
    approach  = Switch.from_robot(machine, "approach-pose")
    grasp     = Switch.from_robot(machine, "grasp-pose")
    travel    = Switch.from_robot(machine, "travel-pose")
    place_bin = Switch.from_robot(machine, "place-pose")

    await home.set_position(2)
    await approach.set_position(2)
    await gripper.open()
    await grasp.set_position(2)
    await gripper.grab()
    await asyncio.sleep(0.3)  # finger gripper settle
    await travel.set_position(2)
    await place_bin.set_position(2); await gripper.open(); await home.set_position(2)
```

*Same sequence as Phase 3 — now in code. Run it.*

> Note: `from_robot` is the local-script equivalent of dependency injection in a module. In Phase 5, `validate_config + cast()` replaces this. Making that connection explicit helps students understand why modules look the way they do.

---

## [4.5] — Adding Perception

**Vision pipeline (configure these now):**

| Name | Type | Model |
|---|---|---|
| `shape-detector` | vision | `devrel:shape-finder:detector` |
| `vision-segment` | vision | `viam:vision:detections-to-segments` |

> Note: This is the vision pipeline configuration — it lives in Phase 4 now (not Phase 2), so students add it right before they use it.

---

## [4.6] — Vision Pipeline: Shape Detection → 3D Segmentation

*(Pipeline diagram with boxes and arrows)*

```
cam-1 (RGB) ──►  shape-detector  ──►  vision-segment  ──► [pick-and-place logic]
cam-1 (depth) ───────────────────────►
```

- `cam-1` provides **RGB** (→ shape-detector) and **depth** (→ vision-segment)
- `shape-detector` → 2D bounding boxes with shape-colour labels
- `vision-segment` fuses 2D boxes with depth → a 3D point cloud per object
- The **label** on each 3D object from vision-segment is how the pick-and-place logic knows what to target

Independently testable — test `shape-detector` first, then `vision-segment`.

---

## [4.7] — Vision Pipeline Test **[LIVE DEMO]**

On `shape-detector`:
- **GetDetections** → `cam-1` → 2D bounding boxes with shape-colour labels and confidence scores

On `vision-segment`:
- **GetObjectPointClouds** → `cam-1` → 3D objects, each with a point cloud and a label from `shape-detector`

> Note: Same label from both services, but `vision-segment` adds the 3D spatial location. This is what the pick-and-place code uses.

---

## [4.8] — The Frame System: Why Transforms Matter

*(Tree diagram)*

```
world
  └── arm-1 base
        ├── arm link 6
        │     └── gripper-1   ← TCP frame: tool center point
        └── cam-1             ← wrist-mounted, moves with the arm
```

- `vision-segment` returns 3D objects in the **camera frame** — coordinates relative to the camera lens
- `motion.move` needs the destination in **world frame** (or any configured frame)
- `machine.transform_pose()` converts between any two frames in the tree

> Note: Because the camera is wrist-mounted, you MUST be at the home observation pose before detecting — otherwise the camera frame is at some other position and transforms will be wrong. This is a common source of mysterious incorrect pick points.

---

## [4.9] — Adding Perception **[LIVE DEMO]**

```python
from viam.services.vision import VisionClient
from viam.services.motion import MotionClient
from viam.proto.common import PoseInFrame

vision = VisionClient.from_robot(machine, "vision-segment")
motion = MotionClient.from_robot(machine, "builtin")

# 1. Must be at home before detecting (wrist camera!)
await home.set_position(2)

# 2. Detect
objects = await vision.get_object_point_clouds("cam-1")
if not objects:
    print("No objects"); return
obj = max(objects, key=lambda o: len(o.point_cloud))

# 3. Transform from camera frame to world frame
obj_in_cam   = PoseInFrame(reference_frame="cam-1", pose=obj.geometries.geometries[0].center)
obj_in_world = await machine.transform_pose(obj_in_cam, "world")

# 4. TODO: compute approach and grasp poses from obj_in_world.pose
```

The `offset_pose` helper is in the starter script — it raises or lowers z by a given mm while keeping x/y/orientation fixed.

> Note: Students fill in the TODO block. The key exercise is computing approach and grasp poses from the detected object centre.

---

## [4.10] — Full Perception-Guided Pick Loop **[LIVE DEMO]**

```python
from viam.proto.service.motion import Constraints, LinearConstraint

approach = # determine approach pose from obj_in_world
grasp    = # determine grasp pose from obj_in_world

# Approach → open → descend → grab → lift
await motion.move(component_name="gripper-1", destination=PoseInFrame("world", approach))
await gripper.open()
await motion.move(component_name="gripper-1", destination=PoseInFrame("world", grasp))
await gripper.grab()
await asyncio.sleep(0.3)

# Lift to travel pose, then move to bin using the saved switch
await travel.set_position(2)       # safe carrying height
await place_pose.set_position(2)   # place at correct bin
await gripper.open()
await home.set_position(2)         # return for next cycle
```

**Hybrid approach:** `motion.move` for the pick (Cartesian precision); arm-position-saver switches for the place (pre-measured, reliable).

> Note: The hybrid approach works well in practice and avoids requiring a calibrated place-pose computation.

---

## [4.11] — Passing WorldState to the Motion Service

Obstacles in the machine config apply automatically. Pass WorldState programmatically to add per-call dynamic obstacles.

```python
from viam.proto.common import (
    WorldState, GeometriesInFrame, Geometry,
    Pose, RectangularPrism, Vector3,
)

table = Geometry(
    center=Pose(x=0, y=0, z=-15, o_x=0, o_y=0, o_z=1, theta=0),
    box=RectangularPrism(dims_mm=Vector3(x=1200, y=800, z=30)),
    label="table",
)
obstacles   = GeometriesInFrame(reference_frame="world", geometries=[table])
world_state = WorldState(obstacles=[obstacles])

# Pass to every motion.move call
await motion.move("gripper-1", PoseInFrame("world", approach),
                  world_state=world_state, constraints=linear_5mm)
```

> Note: If obstacles are already in the machine config motion service attributes, the planner includes them automatically — explicit WorldState in code is **additive** (e.g. the cube being held).

---

## [4.12] — Common Errors + Debugging Guide

| Symptom | Likely cause | Fix |
|---|---|---|
| `motion.move` times out | IK infeasible or obstacle in path | Check 3D scene tab — obstacle blocking path or pose unreachable |
| Pick point drifts / is wrong | Detecting while not at `home-pose` | Add `await home.set_position(2)` + sleep before detecting |
| Pick point incorrect y axis | Camera frame vs. world frame confused | Verify `transform_pose` call — `reference_frame` must match camera name |
| Cube drops mid-transit | Gripper settle time too short | Add `await asyncio.sleep(0.3)` after `gripper.grab()` |
| `get_object_point_clouds` empty | Cube not in frame or threshold too high | Test GetObjectPointClouds in Control tab first; check hue threshold |
| `from_robot` raises KeyError | Resource name doesn't match config | Check exact name in CONFIGURE tab — case sensitive, no spaces |

> Note: The 3D scene tab is the most useful debugging tool for motion planning failures — look at what geometry the planner sees.

---

## [4.13] — Phase 4 Summary

- `RobotClient.at_address()` + `Type.from_robot()` → get all resource handles directly
- Static sequence first — same as Phase 3 but in Python, confirms everything works
- Must be at `home-pose` before detecting — wrist-mounted camera frame changes with arm position
- `get_object_point_clouds()` → `machine.transform_pose()` → compute pick point
- Hybrid: `motion.move` for pick (Cartesian), switches for place (pre-measured)

*If your script runs end-to-end, you have completed the core workshop goal.*

---

# PHASE 5 — INLINE MODULE (STRETCH GOAL, 15 min)

*Convert your working script to an autonomous on-robot service — no laptop required.*

---

## [5.1] — Script → Module: What Changes and Why

*(Two-column comparison)*

| | Local Script | Inline Module |
|---|---|---|
| Runs on | Your laptop | The robot (Meerkat) |
| Survives net loss | ✗ (script dies) | ✓ (viam-server restarts it) |
| Auto-restarts | ✗ | ✓ |
| OTA-deployable | ✗ (run manually) | ✓ (config change → deploy) |
| Feedback loop | Instant | >1 min (Python cloud build) |
| Connection | `RobotClient.at_address()` | Dependency injection |

> Note: The ~1 min build time is not a bug — it's the cost of cross-platform compilation. Worth it for production; use the local script while iterating.

---

## [5.2] — Modules: The Extension Mechanism

*(Step-by-step cards: config → download → subprocess → live resource)*

1. **Config:** `{ "model": "devrel:cube-sorter:sorter-svc" }` — declared in the machine config on app.viam.com
2. viam-server **downloads the module binary** from the Viam Registry — cross-architecture: x86_64, arm64, and more
3. **Spawned as a subprocess**, connected via gRPC socket — isolated; a crash in the module doesn't crash viam-server
4. **Resource is live** — appears in the Control tab

Same mechanism for hardware drivers and your control code.

> Note: This is the same mechanism shown in [1.8], now applied to the student's own sorter logic instead of the xArm6 driver.

---

## [5.3] — The Inline Module Editor **[LIVE DEMO]**

1. CONFIGURE tab → **+** → **Control code**
2. Browser-based Python editor opens with generic service boilerplate pre-filled
3. Code saved to machine config → compiled in the cloud → deployed to robot (~1 min)
4. Module appears as a resource in the Control tab — testable via the DoCommand panel

Reference: `docs.viam.com/build-modules/write-an-inline-module`

---

## [5.4] — `from_robot` → Dependency Injection

Same resources, same names — different access pattern. `validate_config` declares what to inject; `reconfigure` receives it.

**Local script:**
```python
# you hold the robot client
arm  = Arm.from_robot(robot, "arm-1")
home = Switch.from_robot(robot, "home-pose")
```

**Inline module:**
```python
# viam-server injects resources
@classmethod
def validate_config(cls, config):
    attrs = struct_to_dict(config.attributes)
    return [attrs["arm"], attrs["start_pose"], ...], []

def reconfigure(self, config, deps):
    attrs = struct_to_dict(config.attributes)
    self.arm  = cast(Arm,    deps[Arm.get_resource_name(attrs["arm"])])
    self.home = cast(Switch, deps[Switch.get_resource_name("home-pose")])
```

The resource names are identical: `"arm-1"`, `"home-pose"`, etc. Only the access pattern changes — `from_robot` vs. `cast` + `get_resource_name`.

> Note: Students who've done Phase 4 should recognise every resource name here — they're the same strings they passed to `from_robot`. The cast step is new; the dependency names are identical.

---

## [5.5] — `do_command` + Scheduled Job

```python
async def do_command(self, command, *, timeout=None, **kwargs):
    if command.get("command") == "start":
        await self._sort_all()  # your Phase 4 loop, adapted
        return {"status": "done"}
    return {"error": "unknown command"}
```

```json
{
  "jobs": [{
    "name": "sort-cycle", "schedule": "30s",
    "resource": "cube-sorter-svc", "method": "DoCommand",
    "command": { "command": "start" }
  }]
}
```

- Every 30s: viam-server calls `do_command({"command": "start"})`
- One sort cycle runs, returns, the job sleeps until the next interval
- Also triggerable manually from the CONTROL tab DoCommand panel

Reference: `docs.viam.com/manage/software/scheduled-jobs`

---

## [5.6] — Phase 5 Summary

- Module = your Phase 4 script, packaged to run on the robot autonomously
- `from_robot(robot, name)` → `cast(Type, dependencies[Type.get_resource_name(name)])`
- `validate_config` declares which resources to inject; `reconfigure` casts and stores them
- `do_command` wraps your sort cycle; a scheduled job triggers it on a cadence
- Cloud build time (~1 min) is the tradeoff for on-robot autonomous execution

*Questions?*

---

# PHASE 6 — WRAP + NEXT STEPS (5 min)

*What we covered · exercises · references.*

---

## [6.1] — What We Covered

- Three layers: cloud → viam-agent → viam-server (downloads modules + runs resources)
- Resource model: `namespace:family:model` — stable API, swappable hardware
- Vision pipeline: shape-detector (2D) → vision-segment (3D objects with labels)
- Five key poses captured via arm-position-saver; tested manually from the Control tab
- WorldState: table, bins, safety walls as obstacle geometry for the motion planner
- Local script: `from_robot` → static sequence → perception → full pick-and-place loop
- Wrist-mounted camera: must detect from `home-pose` for correct world-frame transforms
- *(Stretch)* Inline module: `from_robot` → `cast` + `get_resource_name`; `do_command` + job

---

## [6.2] — Exercises to Continue

- **Add a new colour bin** — jog arm, save switch, add to the bins dict — no code change needed for the core logic
- **Add a LinearConstraint to the descent** — prevents the arm arcing into the cube; add a `constraints=` argument to the grasp `motion.move` call
- **Loop over all detected objects** — sort each object in the list before returning to home; handle colour ordering by priority
- **Add `get_status` to `do_command`** — return current phase and last label sorted; useful for a web UI calling the module

---

## [6.3] — Reference Links + Thank You

**What questions do you have?**

| Resource | URL |
|---|---|
| Pick an object (motion planning) | docs.viam.com/motion-planning/move-an-arm/pick-an-object |
| Write an inline module | docs.viam.com/build-modules/write-an-inline-module |
| Scheduled jobs | docs.viam.com/manage/software/scheduled-jobs |
| Define obstacles | docs.viam.com/motion-planning/obstacles/overview |
| Frame system | docs.viam.com/motion-planning/frame-system/overview |
| Switch API | docs.viam.com/components/switch |
| arm-position-saver module | app.viam.com/module/erh/vmodutils |
| Cube-sorter Go source | github.com/viam-devrel/cube-sorter |

Hardware stays set up — experiment after the session.
Viam Discord: **discord.gg/viam**

---

# APPENDIX — FACILITATOR REFERENCE

---

## [A.1] — Slide Count by Phase

*("+1" = phase divider slide.)*

| Phase | Slides | Time |
|---|---|---|
| 0 — Orientation | 5 | 8 min |
| 1 — Mental Model | 9 + 1 | 15 min |
| 2 — Configure + App | 7 + 1 | 20 min |
| 3 — Static Positions + WorldState | 6 + 1 | 20 min |
| 4 — Local Python Script | 13 + 1 | 30 min |
| 5 — Inline Module (stretch) | 6 + 1 | 15 min |
| 6 — Wrap | 3 + 1 | 5 min |
| Appendix | 4 | — |

---

## [A.2] — Changes from v1 + Rationale

| v1 | v2 | Why |
|---|---|---|
| Phase 3: APIs & Composability (abstract) | Dissolved — content moved to Phase 4 as live context | Too abstract before students have written any code |
| Phase 4: Inline module (immediate) | Phase 4: Local script first | Fast feedback, simpler API, no dependency injection complexity |
| No static positions phase | Phase 3: static positions + WorldState | Isolates hardware bugs from perception bugs; safety obstacles |
| Module as core goal | Module as explicit stretch goal | Students couldn't reach it; prevents all-or-nothing outcome |
| No WorldState phase | Phase 3 includes WorldState + obstacles | Safety (arm near students) and practical (planner needs context) |

---

## [A.3] — Common Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `set_position(2)` does nothing | Switch not yet saved | Must call `set_position(1)` to save before `set_position(2)` to execute |
| Machine "Disconnected" | Wrong org or machine number | Check org selector in top-left |
| `from_robot` raises KeyError | Resource name mismatch | Check exact name in CONFIGURE tab — case sensitive |
| Pick point wrong or drifting | Detecting while not at `home-pose` | Add `await home.set_position(2)` + sleep before detecting |
| `motion.move` times out | IK infeasible or obstacle in path | 3D scene tab — check arm path vs. obstacles |
| Cube drops during transit | Gripper settle time too short | `await asyncio.sleep(0.3)` after `gripper.grab()` |
| `get_object_point_clouds` empty | Cube not in frame / threshold high | Test in Control tab; check hue threshold on color-detector |
| Inline module build takes forever | Expected — Python cloud build | ~1 min is normal; use local script during iteration |

---

## [A.4] — Phase 4 Starter Script Template

Copy connection details from the Connect tab → Python SDK. Fill in the TODOs in order. Run after each section.

The full runnable template lives in this repo at **`scripts/starter-script.py`** (with a complete **`scripts/reference-solution.py`** alongside it) — hand it out as a file. The PDF slide shows only the header (imports, constants, `offset_pose` helper); the complete version below is the handout.

```python
"""
Viam Pick-and-Place Workshop — Starter Script
Copy your connection details from the machine's Connect tab → Python SDK.
Fill in the TODOs in order. Run after each section to verify.
"""
import asyncio

from viam.robot.client import RobotClient
from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.components.switch import Switch
from viam.services.motion import MotionClient
from viam.services.vision import VisionClient
from viam.proto.common import (
    PoseInFrame, Pose, WorldState, GeometriesInFrame,
)
from viam.proto.service.motion import Constraints, LinearConstraint

# --- Tuning constants ---
GRIPPER_LENGTH_MM = 60   # measure from flange to finger tips
APPROACH_MM       = 100  # clearance above cube top before descending


def offset_pose(pose, z_offset_mm):
    """Raise/lower a pose in z while keeping x/y/orientation fixed."""
    return Pose(
        x=pose.x, y=pose.y, z=pose.z + z_offset_mm,
        o_x=pose.o_x, o_y=pose.o_y, o_z=pose.o_z, theta=pose.theta,
    )


# --- TODO 1: paste address + API key from Connect tab ---
MACHINE_ADDRESS = "<paste>"
API_KEY         = "<paste>"
API_KEY_ID      = "<paste>"

# --- Resource names (must match CONFIGURE tab exactly) ---
ARM_NAME      = "arm-1"
GRIPPER_NAME  = "gripper-1"
CAMERA_NAME   = "cam-1"
VISION_NAME   = "vision-segment"
HOME_POSE     = "home-pose"
APPROACH_POSE = "approach-pose"
GRASP_POSE    = "grasp-pose"
TRAVEL_POSE   = "travel-pose"
PLACE_POSE    = "place-pose"


async def main():
    async with await RobotClient.at_address(
        MACHINE_ADDRESS,
        options=RobotClient.Options.with_api_key(
            api_key=API_KEY,
            api_key_id=API_KEY_ID,
        ),
    ) as machine:
        # TODO 2: Get resource handles
        arm       = Arm.from_robot(machine, ARM_NAME)
        gripper   = Gripper.from_robot(machine, GRIPPER_NAME)
        motion    = MotionClient.from_robot(machine, "builtin")
        vision    = VisionClient.from_robot(machine, VISION_NAME)

        home      = Switch.from_robot(machine, HOME_POSE)
        approach  = Switch.from_robot(machine, APPROACH_POSE)
        grasp     = Switch.from_robot(machine, GRASP_POSE)
        travel    = Switch.from_robot(machine, TRAVEL_POSE)
        place_bin = Switch.from_robot(machine, PLACE_POSE)

        # TODO 3: Run the static sequence (Phase 4.4)
        await home.set_position(2)
        await approach.set_position(2)
        await gripper.open()
        await grasp.set_position(2)
        await gripper.grab()
        await asyncio.sleep(0.3)  # finger gripper settle
        await travel.set_position(2)
        await place_bin.set_position(2)
        await gripper.open()
        await home.set_position(2)
        print("Static sequence complete")

        # TODO 4: Add perception + motion.move (Phase 4.9 / 4.10)
        # await home.set_position(2)          # must be at home for camera frame
        # objects = await vision.get_object_point_clouds(CAMERA_NAME)
        # if not objects:
        #     print("No objects detected"); return
        # obj = max(objects, key=lambda o: len(o.point_cloud))
        #
        # # Transform object pose from camera frame to world frame
        # obj_in_cam   = PoseInFrame(
        #     reference_frame=CAMERA_NAME,
        #     pose=obj.geometries.geometries[0].center,
        # )
        # obj_in_world = await machine.transform_pose(obj_in_cam, "world")
        #
        # # TODO: compute approach_pose and grasp_pose from obj_in_world.pose
        # # approach_pose = offset_pose(obj_in_world.pose, APPROACH_MM)
        # # grasp_pose    = offset_pose(obj_in_world.pose, GRIPPER_LENGTH_MM)
        #
        # # TODO: motion.move to approach, open, descend to grasp, grab, travel, place
        # # await motion.move("gripper-1", PoseInFrame("world", approach_pose))
        # # await gripper.open()
        # # await motion.move("gripper-1", PoseInFrame("world", grasp_pose))
        # # await gripper.grab()
        # # await asyncio.sleep(0.3)
        # # await travel.set_position(2)
        # # await place_bin.set_position(2)
        # # await gripper.open()
        # # await home.set_position(2)


if __name__ == "__main__":
    asyncio.run(main())
```
