# Frame Calibration Worksheet

The pick-and-place pipeline only works if the robot's **frame system** matches
physical reality. Two frames must be measured and entered into the machine
config: the **gripper TCP** (tool center point) and the **camera** (wrist-mounted
extrinsics). Everything in Phase 4 — `transform_pose`, the world-frame pick point
— depends on these numbers being correct.

Work in millimeters. The arm base is the parent; `world` is coincident with the
arm base unless you configured an offset.

---

## 1. Gripper TCP frame

The gripper frame is parented to the arm flange (the last arm link). Its job is
to tell `motion.move` where the *tool tip* is relative to the flange.

| Quantity | How to measure | Value |
|---|---|---|
| Z translation (mm) | Flange face → finger convergence point, with calipers | `__________` |
| X translation (mm) | Usually 0 for a centered finger gripper | `0` |
| Y translation (mm) | Usually 0 for a centered finger gripper | `__________` |
| Orientation | Identity for a straight gripper (OX=0, OY=0, OZ=1, Theta=0) | `identity` |

> A finger gripper mounted straight on the flange is a pure +Z translation with
> identity orientation. If your gripper is offset or angled, measure X/Y and the
> orientation vector too.

Resulting frame translation: `{ "x": 0, "y": ___, "z": ___ }`

---

## 2. Camera frame (wrist-mounted RealSense)

The camera is parented to the arm link, so its frame **moves with the arm**. This
is why you must always detect from the `home-pose` — the transform is only valid
when the arm is in the pose the frame was calibrated for.

| Quantity | How to measure | Value |
|---|---|---|
| X translation (mm) | Flange center → camera optical center, X | `__________` |
| Y translation (mm) | Flange center → camera optical center, Y | `__________` |
| Z translation (mm) | Flange center → camera optical center, Z | `__________` |
| Orientation type | `ov_degrees` | `ov_degrees` |
| OX / OY / OZ | Optical axis direction (often 0, 0, 1) | `__________` |
| Theta (deg) | Rotation about the optical axis (e.g. 270) | `__________` |

> Use a known-angle mounting bracket to read the orientation. The deck's example
> camera frame was `translation { x: -73, y: 40, z: 18 }` with `ov_degrees`
> `{ th: 270, x: 0, y: 0, z: 1 }`, parented to `arm-1` — yours will differ.

---

## 3. Verification

1. Place an AprilTag (or a single cube) at a **known** world position.
2. Move the arm to `home-pose`.
3. Detect it and run `transform_pose` into the world frame.
4. Compare the reported world pose to the tape-measured position.
5. Iterate on the X/Y/Z/orientation values until the error is within tolerance
   (a few mm). A consistent offset in one axis points to a single wrong
   translation value; a rotation-dependent error points to the orientation.

When detected-vs-expected agrees at `home-pose`, the frames are calibrated and
Phase 4's pick points will land on the block.
