"""
Viam Pick-and-Place Workshop — Reference Solution
=================================================

A complete, end-to-end version of `starter-script.py` with every TODO filled in:
connect -> run the static sequence -> detect -> transform to world frame ->
pick with motion planning -> place at the saved bin pose -> return home.

    uv run python reference-solution.py        # recommended
    # or, without uv:
    python3 reference-solution.py

NOTE: This is a reference, not a guarantee. The geometry, offsets, and gripper
settle timing below must be validated and tuned against YOUR hardware. Tune the
constants and the offset math before running near people or equipment, and keep
the LinearConstraint on the final descent so the arm comes straight down onto
the block instead of arcing into it.
"""

import asyncio

from viam.robot.client import RobotClient
from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.components.switch import Switch
from viam.services.motion import MotionClient
from viam.services.vision import VisionClient
from viam.proto.common import PoseInFrame, Pose
from viam.proto.service.motion import Constraints, LinearConstraint

# --- Tuning constants ---------------------------------------------------------
GRIPPER_LENGTH_MM = 60  # offset from the gripper's claw-geometry TCP to the real fingertip contact point
APPROACH_MM = 100  # clearance above the block top before descending
SETTLE_S = 0.3  # finger gripper settle time after grab

# --- Connection details (from the Connect tab -> Python SDK) ------------------
MACHINE_ADDRESS = "<paste from Connect tab>"
API_KEY = "<paste from Connect tab>"
API_KEY_ID = "<paste from Connect tab>"

# --- Resource names (must match the CONFIGURE tab exactly) --------------------
ARM_NAME = "arm-1"
GRIPPER_NAME = "gripper-1"
CAMERA_NAME = "cam-1"
VISION_NAME = "vision-segment"
HOME_POSE = "home-pose"
APPROACH_POSE = "approach-pose"
GRASP_POSE = "grasp-pose"
TRAVEL_POSE = "travel-pose"
PLACE_POSE = "place-pose"


def offset_pose(pose: Pose, z_offset_mm: float) -> Pose:
    """Raise or lower a pose in z while keeping x/y/orientation fixed."""
    return Pose(
        x=pose.x,
        y=pose.y,
        z=pose.z + z_offset_mm,
        o_x=pose.o_x,
        o_y=pose.o_y,
        o_z=pose.o_z,
        theta=pose.theta,
    )


async def connect() -> RobotClient:
    return await RobotClient.at_address(
        MACHINE_ADDRESS,
        options=RobotClient.Options.with_api_key(
            api_key=API_KEY,
            api_key_id=API_KEY_ID,
        ),
    )


async def run_static_sequence(
    home, approach, grasp, travel, place_pose, gripper
) -> None:
    """The Phase 3 sequence, driven from code. SetPosition(2) executes a saved pose."""
    await home.set_position(2)
    await approach.set_position(2)
    await gripper.open()
    await grasp.set_position(2)
    await gripper.grab()
    await asyncio.sleep(SETTLE_S)
    await travel.set_position(2)
    await place_pose.set_position(2)
    await gripper.open()
    await home.set_position(2)
    print("Static sequence complete")


async def pick_and_place(
    machine, arm, gripper, motion, vision, home, travel, place_pose
) -> bool:
    """One perception-guided pick-and-place cycle. Returns True if a block was sorted."""
    # 1. Observe from home so the wrist-mounted camera frame is in a known position.
    await home.set_position(2)

    # 2. Detect. vision-segment fuses the 2D shape detections with depth into
    #    3D objects, each with a point cloud and a label.
    objects = await vision.get_object_point_clouds(CAMERA_NAME)
    if not objects:
        print("No objects detected")
        return False

    # Largest object by point-cloud byte size (a proxy for point count).
    # point_cloud is raw PCD bytes, so use len(point_cloud), not .size.
    obj = max(objects, key=lambda o: len(o.point_cloud))
    geometry = obj.geometries.geometries[0]
    label = geometry.label
    print(f"Detected: {label}")

    # 3. The object pose is in the camera frame; the planner needs world frame.
    obj_in_cam = PoseInFrame(reference_frame=CAMERA_NAME, pose=geometry.center)
    obj_in_world = await machine.transform_pose(obj_in_cam, "world")

    # 4. Derive the approach and grasp poses from the object center.
    approach_pose = offset_pose(obj_in_world.pose, APPROACH_MM)
    grasp_pose = offset_pose(obj_in_world.pose, GRIPPER_LENGTH_MM)

    # 5. Pick: move above, open, descend straight down, grab, lift.
    # LinearConstraint = the tutorial's optional Phase 5 follow-up: forces a straight-down descent
    linear_down = Constraints(
        linear_constraint=[LinearConstraint(line_tolerance_mm=5.0)]
    )
    await motion.move(
        component_name=GRIPPER_NAME,
        destination=PoseInFrame(reference_frame="world", pose=approach_pose),
    )
    await gripper.open()
    await asyncio.sleep(SETTLE_S)
    await motion.move(
        component_name=GRIPPER_NAME,
        destination=PoseInFrame(reference_frame="world", pose=grasp_pose),
        constraints=linear_down,
    )
    await gripper.grab()
    await asyncio.sleep(SETTLE_S)

    # 6. Place: lift to the safe carrying height, drop at the saved bin pose.
    #    Hybrid approach — motion.move for the pick (Cartesian precision),
    #    saved switches for the place (pre-measured, reliable).
    await travel.set_position(2)
    await place_pose.set_position(2)
    await gripper.open()
    await home.set_position(2)
    return True


async def main() -> None:
    async with await connect() as machine:
        print(machine.resource_names)

        arm = Arm.from_robot(machine, ARM_NAME)
        gripper = Gripper.from_robot(machine, GRIPPER_NAME)
        motion = MotionClient.from_robot(machine, "builtin")
        vision = VisionClient.from_robot(machine, VISION_NAME)

        home = Switch.from_robot(machine, HOME_POSE)
        approach = Switch.from_robot(machine, APPROACH_POSE)
        grasp = Switch.from_robot(machine, GRASP_POSE)
        travel = Switch.from_robot(machine, TRAVEL_POSE)
        place_pose = Switch.from_robot(machine, PLACE_POSE)

        # Validate the hardware loop first.
        await run_static_sequence(home, approach, grasp, travel, place_pose, gripper)

        # Then sort blocks until none remain in view.
        while await pick_and_place(
            machine, arm, gripper, motion, vision, home, travel, place_pose
        ):
            pass
        print("Nothing left to sort")


if __name__ == "__main__":
    asyncio.run(main())
