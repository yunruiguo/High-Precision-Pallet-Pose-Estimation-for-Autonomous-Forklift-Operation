from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share_path = get_package_share_path("yolov8_ros")
    default_model_path = package_share_path / "weights" / "fu3.pt"

    model = LaunchConfiguration("model")
    tracker = LaunchConfiguration("tracker")
    device = LaunchConfiguration("device")
    enable = LaunchConfiguration("enable")
    threshold = LaunchConfiguration("threshold")
    input_image_topic = LaunchConfiguration("input_image_topic")
    input_depth_topic = LaunchConfiguration("input_depth_topic")
    input_depth_info_topic = LaunchConfiguration("input_depth_info_topic")
    depth_image_units_divisor = LaunchConfiguration("depth_image_units_divisor")
    target_frame = LaunchConfiguration("target_frame")
    maximum_detection_threshold = LaunchConfiguration("maximum_detection_threshold")
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

    tracking_node = Node(
        package="yolov8_ros",
        executable="tracking_node",
        name="tracking_node",
        namespace=namespace,
        parameters=[{"tracker": tracker}],
        remappings=[("image_raw", input_image_topic)],
    )

    detect_3d_node = Node(
        package="yolov8_ros",
        executable="detect_3d_node",
        name="detect_3d_node",
        namespace=namespace,
        parameters=[
            {
                "target_frame": target_frame,
                "maximum_detection_threshold": maximum_detection_threshold,
                "depth_image_units_divisor": depth_image_units_divisor,
            }
        ],
        remappings=[
            ("depth_image", input_depth_topic),
            ("depth_info", input_depth_info_topic),
            ("detections", "tracking"),
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
            ("detections", "detections_3d"),
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
                "tracker",
                default_value="bytetrack.yaml",
                description="Ultralytics tracker config.",
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
                "depth_image_units_divisor",
                default_value="1000",
                description="Divisor used to convert raw depth to meters.",
            ),
            DeclareLaunchArgument(
                "target_frame",
                default_value="base_link",
                description="Target frame for 3D detections.",
            ),
            DeclareLaunchArgument(
                "maximum_detection_threshold",
                default_value="0.3",
                description="Maximum depth threshold for 3D detection filtering.",
            ),
            DeclareLaunchArgument(
                "namespace",
                default_value="yolo",
                description="Namespace for YOLOv8 nodes.",
            ),
            DeclareLaunchArgument(
                "pallet_width_mm",
                default_value="830.0",
                description="Distance between left and right pallet block centers.",
            ),
            detector_node,
            tracking_node,
            detect_3d_node,
            debug_node,
        ]
    )
