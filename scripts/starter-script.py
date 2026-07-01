"""
Viam Pick-and-Place Workshop — Starter Script
==============================================

Copy your connection details from the machine's Connect tab -> Python SDK.
Fill in the TODOs in order. Run after each section to verify before moving on.

    uv run python starter-script.py        # recommended (uv reads ../scripts/pyproject.toml)
    # or, without uv:
    python3 starter-script.py

Prerequisites:
    python3 --version                                # must be 3.10+
    uv add viam-sdk                                  # or: pip install viam-sdk
    uv run python -c "import viam; print(viam.__version__)"
"""

import asyncio

from viam.robot.client import RobotClient
from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.components.switch import Switch
from viam.services.motion import MotionClient
from viam.services.vision import VisionClient
from viam.proto.common import PoseInFrame, Pose

# --- Tuning constants ---------------------------------------------------------
GRIPPER_LENGTH_MM = 60  # offset from the gripper's claw-geometry TCP to the real fingertip contact point
APPROACH_MM = 100  # clearance above the cube top before descending


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


# --- TODO 1: paste address + API key from the Connect tab ---------------------
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


async def connect() -> RobotClient:
    return await RobotClient.at_address(
        MACHINE_ADDRESS,
        options=RobotClient.Options.with_api_key(
            api_key=API_KEY,
            api_key_id=API_KEY_ID,
        ),
    )


async def main() -> None:
    async with await connect() as machine:
        # TODO 2: confirm the connection — list every resource on the machine.
        # You should see arm-1, gripper-1, cam-1, the poses as Switches,
        # and the obstacles as grippers.
        print(machine.resource_names)

        # TODO 3: get typed resource handles.
        arm = Arm.from_robot(machine, ARM_NAME)
        gripper = Gripper.from_robot(machine, GRIPPER_NAME)
        motion = MotionClient.from_robot(machine, "builtin")
        vision = VisionClient.from_robot(machine, VISION_NAME)

        home = Switch.from_robot(machine, HOME_POSE)
        approach = Switch.from_robot(machine, APPROACH_POSE)
        grasp = Switch.from_robot(machine, GRASP_POSE)
        travel = Switch.from_robot(machine, TRAVEL_POSE)
        place_pose = Switch.from_robot(machine, PLACE_POSE)

        # TODO 4: run the static sequence (Phase 4.4).
        # Same order you tested manually from the Control tab in Phase 3.
        # SetPosition(2) executes a saved pose.
        await home.set_position(2)
        await approach.set_position(2)
        await gripper.open()
        await grasp.set_position(2)
        await gripper.grab()
        await asyncio.sleep(0.3)  # finger gripper settle
        await travel.set_position(2)
        await place_pose.set_position(2)
        await gripper.open()
        await home.set_position(2)
        print("Static sequence complete")

        # TODO 5: add perception (Phase 5.5).
        # Uncomment and complete. Must be at home before detecting because the
        # camera is wrist-mounted — its frame moves with the arm.
        #
        # await home.set_position(2)
        # objects = await vision.get_object_point_clouds(CAMERA_NAME)
        # if not objects:
        #     print("No objects detected")
        #     return
        # obj = max(objects, key=lambda o: len(o.point_cloud))
        # label = obj.geometries.geometries[0].label
        # print(f"Detected: {label}")
        #
        # # Transform the object pose from camera frame to world frame.
        # obj_in_cam = PoseInFrame(
        #     reference_frame=CAMERA_NAME,
        #     pose=obj.geometries.geometries[0].center,
        # )
        # obj_in_world = await machine.transform_pose(obj_in_cam, "world")

        # TODO 6: compute the approach and grasp poses (Phase 5.6).
        # The approach pose is worked for you — a clearance standoff above the block:
        #     approach_pose = offset_pose(obj_in_world.pose, APPROACH_MM)
        #
        # Now YOU compute the grasp pose. motion.move drives the gripper-1 frame
        # (the gripper's TCP, already offset down the arm) to the target — so the
        # grasp offset is the gripper-TCP-to-fingertip depth (GRIPPER_LENGTH_MM),
        # not the whole arm reach. Fill in the offset:
        #     grasp_pose = offset_pose(obj_in_world.pose, ___)   # TODO: your offset

        # TODO 7: run the full perception-guided pick loop (Phase 5.6).
        # Hybrid approach: motion.move for the pick (Cartesian precision),
        # arm-position-saver switches for the place (pre-measured, reliable).
        #
        # await motion.move("gripper-1", PoseInFrame(reference_frame="world", pose=approach_pose))
        # await gripper.open()
        # await motion.move("gripper-1", PoseInFrame(reference_frame="world", pose=grasp_pose))
        # await gripper.grab()
        # await asyncio.sleep(0.3)
        # await travel.set_position(2)
        # await place_pose.set_position(2)
        # await gripper.open()
        # await home.set_position(2)


if __name__ == "__main__":
    asyncio.run(main())
