import asyncio
from typing import ClassVar, Mapping, Optional, Sequence, Tuple
from typing_extensions import Self
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, PoseInFrame, Pose
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import struct_to_dict, ValueTypes
from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.components.camera import Camera
from viam.components.switch import Switch
from viam.services.vision import VisionClient
from viam.services.motion import Motion
from viam.services.generic import Generic as GenericService

# offset from the gripper's claw-geometry TCP to the real fingertip contact point
GRIPPER_LENGTH_MM = -60
APPROACH_MM = -100  # clearance above the block top before descending
SETTLE_S = 0.3  # finger gripper settle time after grab


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


# IMPORTANT: Do not change the class name or the MODEL triplet below.
# The platform uses these auto-generated values to identify your module.
# Changing them will break your inline module.
class MyGenericService(GenericService, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(
        ModelFamily("viam", "fe19e048-ae78-4a43-af5c-ad071ae25ed8"), "generic-service"
    )
    arm: Arm
    gripper: Gripper
    camera: Camera
    home: Switch
    travel: Switch
    place_pose: Switch
    vision: VisionClient

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any required dependencies or optional dependencies based on that `config`.
        Args:
            config (ComponentConfig): The configuration for this resource
        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies and the
                second element is a list of optional dependencies
        """
        # Convert configuration attributes from a protobuf struct to a dictionary.
        attrs = struct_to_dict(config.attributes)

        required_deps = []
        optional_deps = []

        # arm
        if "arm" not in attrs or not attrs["arm"]:
            raise ValueError("attribute 'arm' (non-empty string) is required")
        required_deps.append(attrs["arm"])

        # gripper
        if "gripper" not in attrs or not attrs["gripper"]:
            raise ValueError("attribute 'gripper' (non-empty string) is required")
        required_deps.append(attrs["gripper"])

        # camera
        if "camera" not in attrs or not attrs["camera"]:
            raise ValueError("attribute 'camera' (non-empty string) is required")
        required_deps.append(attrs["camera"])

        # home_pose
        if "home_pose" not in attrs or not attrs["home_pose"]:
            raise ValueError("attribute 'home_pose' (non-empty string) is required")
        required_deps.append(attrs["home_pose"])

        if "travel_pose" not in attrs or not attrs["travel_pose"]:
            raise ValueError("attribute 'travel_pose' (non-empty string) is required")
        required_deps.append(attrs["travel_pose"])

        if "place_pose" not in attrs or not attrs["place_pose"]:
            raise ValueError("attribute 'place_pose' (non-empty string) is required")
        required_deps.append(attrs["place_pose"])

        # vision
        if "vision" not in attrs or not attrs["vision"]:
            raise ValueError("attribute 'vision' (non-empty string) is required")
        required_deps.append(attrs["vision"])

        # motion service
        required_deps.append("builtin")

        return required_deps, optional_deps

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter.
        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)
        Returns:
            Self: The resource
        """
        # Convert configuration attributes from a protobuf struct to a dictionary.
        self = super().new(config, dependencies)
        attrs = struct_to_dict(config.attributes)

        arm_name: str = attrs["arm"]
        self.arm = dependencies[Arm.get_resource_name(arm_name)]

        self.gripper_name: str = attrs["gripper"]
        self.gripper = dependencies[Gripper.get_resource_name(self.gripper_name)]

        self.camera_name: str = attrs["camera"]
        self.camera = dependencies[Camera.get_resource_name(self.camera_name)]

        home_pose_name: str = attrs["home_pose"]
        self.home = dependencies[Switch.get_resource_name(home_pose_name)]

        travel_pose_name: str = attrs["travel_pose"]
        self.travel = dependencies[Switch.get_resource_name(travel_pose_name)]

        place_pose_name: str = attrs["place_pose"]
        self.place_pose = dependencies[Switch.get_resource_name(place_pose_name)]

        vision_name: str = attrs["vision"]
        self.vision = dependencies[VisionClient.get_resource_name(vision_name)]

        self.motion = dependencies[Motion.get_resource_name("builtin")]

        return self

    async def run_pick_cycle(self) -> bool:
        """Run one detect-pick-place cycle. Returns False if no object was detected, True on a completed cycle."""
        # 1. Observe from home so the wrist-mounted camera frame is in a known position.
        await self.home.set_position(2)

        # 2. Detect. vision-segment fuses the 2D shape detections with depth into
        #    3D objects, each with a point cloud and a label.
        objects = await self.vision.get_object_point_clouds(self.camera_name)
        if not objects:
            print("No objects detected")
            return False

        # Largest object by point-cloud byte size (a proxy for point count).
        # point_cloud is raw PCD bytes, so use len(point_cloud), not .size.
        obj = max(objects, key=lambda o: len(o.point_cloud))
        geometry = obj.geometries.geometries[0]
        label = geometry.label
        print(f"Detected: {label}")

        # 3. Tag the detected pose with the camera frame; motion.move resolves it.
        obj_in_cam = PoseInFrame(reference_frame=self.camera_name, pose=geometry.center)

        # 4. Derive the approach and grasp poses from the object center.
        approach_pose = offset_pose(obj_in_cam.pose, APPROACH_MM)
        grasp_pose = offset_pose(obj_in_cam.pose, GRIPPER_LENGTH_MM)

        # 5. Pick: move above, open, descend down, grab, lift.
        await self.motion.move(
            component_name=self.gripper_name,
            destination=PoseInFrame(
                reference_frame=self.camera_name, pose=approach_pose
            ),
        )
        await self.gripper.open()
        await asyncio.sleep(SETTLE_S)
        await self.motion.move(
            component_name=self.gripper_name,
            destination=PoseInFrame(reference_frame=self.camera_name, pose=grasp_pose),
        )
        await self.gripper.grab()
        await asyncio.sleep(SETTLE_S)

        # 6. Place: lift to the safe carrying height, drop at the saved bin pose.
        await self.travel.set_position(2)
        await self.place_pose.set_position(2)
        await self.gripper.open()
        await self.home.set_position(2)

        return True

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        if command.get("action") == "pick_cycle":
            success = await self.run_pick_cycle()
            return {"success": success}
        return {}
