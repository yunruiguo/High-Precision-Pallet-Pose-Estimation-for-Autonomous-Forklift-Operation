from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share_path = get_package_share_path("yolov8_ros")
    default_model_path = package_share_path / "weights" / "fu3.pt"

    model = LaunchConfiguration("model")
    device = LaunchConfiguration("device")
    enable = LaunchConfiguration("enable")
    threshold = LaunchConfiguration("threshold")
    input_image_topic = LaunchConfiguration("input_image_topic")
    input_depth_topic = LaunchConfiguration("input_depth_topic")
    input_depth_info_topic = LaunchConfiguration("input_depth_info_topic")
    namespace = LaunchConfiguration("namespace")
    pallet_width_mm = LaunchConfiguration("pallet_width_mm")

    detector_node = Node(
        package="yolov8_ros",
        executable="pallet_detector_node",
        name="pallet_detector_node",
        namespace=namespace,
        parameters=[
            {
                "model": model,
                "device": device,
                "enable": enable,
                "threshold": threshold,
                "pallet_width_mm": pallet_width_mm,
            }
        ],
        remappings=[
            ("image_raw", input_image_topic),
            ("depth_image", input_depth_topic),
            ("depth_info", input_depth_info_topic),
        ],
    )

    debug_node = Node(
        package="yolov8_ros",
        executable="debug_node",
        name="debug_node",
        namespace=namespace,
        parameters=[{"pallet_width_mm": pallet_width_mm}],
        remappings=[
            ("image_raw", input_image_topic),
            ("depth_image", input_depth_topic),
            ("depth_info", input_depth_info_topic),
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "model",
                default_value=str(default_model_path),
                description="YOLOv8 model path.",
            ),
            DeclareLaunchArgument(
                "device",
                default_value="cuda:0",
                description="Inference device, for example cuda:0 or cpu.",
            ),
            DeclareLaunchArgument(
                "enable",
                default_value="True",
                description="Start detector enabled.",
            ),
            DeclareLaunchArgument(
                "threshold",
                default_value="0.65",
                description="Minimum detection confidence.",
            ),
            DeclareLaunchArgument(
                "input_image_topic",
                default_value="/camera/color/image_raw",
                description="RGB image topic.",
            ),
            DeclareLaunchArgument(
                "input_depth_topic",
                default_value="/camera/depth/image_raw",
                description="Depth image topic.",
            ),
            DeclareLaunchArgument(
                "input_depth_info_topic",
                default_value="/camera/depth/camera_info",
                description="Depth camera info topic.",
            ),
            DeclareLaunchArgument(
                "namespace",
                default_value="yolo",
                description="Namespace for pallet detection nodes.",
            ),
            DeclareLaunchArgument(
                "pallet_width_mm",
                default_value="830.0",
                description="Distance between left and right pallet block centers.",
            ),
            detector_node,
            debug_node,
        ]
    )
