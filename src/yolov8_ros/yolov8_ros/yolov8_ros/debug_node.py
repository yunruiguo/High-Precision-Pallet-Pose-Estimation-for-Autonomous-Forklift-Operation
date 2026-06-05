import time
from typing import List, Optional, Tuple

import cv2
import message_filters
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image

from yolov8_msgs.msg import BoundingBox2D, Detection, DetectionArray


class PalletDebugNode(Node):
    """Draw pallet detections, depth, and angle on the debug image."""

    BLOCK_CLASS = "block"
    FRONT_CLASS = "front"
    BOX_THICKNESS = 2

    def __init__(self) -> None:
        super().__init__("pallet_debug_node")

        self.declare_parameter("pallet_width_mm", 830.0)
        self.declare_parameter("stable_update_interval", 2.0)
        self.pallet_width_mm = (
            self.get_parameter("pallet_width_mm").get_parameter_value().double_value
        )
        self.stable_update_interval = (
            self.get_parameter("stable_update_interval")
            .get_parameter_value()
            .double_value
        )

        self.bridge = CvBridge()
        self.camera_info: Optional[CameraInfo] = None
        self.last_update_time = 0.0
        self.stable_angle_degrees: Optional[float] = None
        self.stable_left_depth: Optional[float] = None
        self.stable_right_depth: Optional[float] = None

        self.debug_image_pub = self.create_publisher(Image, "dbg_image", 10)

        image_sub = message_filters.Subscriber(
            self, Image, "image_raw", qos_profile=qos_profile_sensor_data
        )
        detections_sub = message_filters.Subscriber(
            self, DetectionArray, "detections", qos_profile=10
        )
        depth_sub = message_filters.Subscriber(
            self, Image, "depth_image", qos_profile=qos_profile_sensor_data
        )
        self.create_subscription(
            CameraInfo, "depth_info", self.camera_info_callback, qos_profile_sensor_data
        )

        self.synchronizer = message_filters.ApproximateTimeSynchronizer(
            (image_sub, detections_sub, depth_sub), 10, 0.5
        )
        self.synchronizer.registerCallback(self.detections_callback)

    def camera_info_callback(self, msg: CameraInfo) -> None:
        self.camera_info = msg

    def detections_callback(
        self,
        image_msg: Image,
        detections_msg: DetectionArray,
        depth_msg: Image,
    ) -> None:
        cv_image = self.bridge.imgmsg_to_cv2(image_msg)
        depth_image = self.bridge.imgmsg_to_cv2(depth_msg)

        block_centers = []
        for detection in detections_msg.detections:
            cv_image = self.draw_detection(cv_image, detection, depth_image)
            if detection.class_name == self.BLOCK_CLASS:
                center = self.get_detection_center(detection)
                if self.is_valid_pixel(center, depth_image):
                    block_centers.append(center)

        if len(block_centers) == 3:
            cv_image = self.draw_pallet_angle(cv_image, block_centers, depth_image)

        self.debug_image_pub.publish(
            self.bridge.cv2_to_imgmsg(cv_image, encoding=image_msg.encoding)
        )

    def draw_detection(
        self,
        cv_image: np.ndarray,
        detection: Detection,
        depth_image: np.ndarray,
    ) -> np.ndarray:
        center_x, center_y = self.get_detection_center(detection)
        if not self.is_valid_pixel((center_x, center_y), depth_image):
            return cv_image

        depth_mm = float(depth_image[center_y, center_x])
        color = self.get_class_color(detection.class_name)
        top_left, bottom_right = self.get_box_corners(detection.bbox)

        cv2.rectangle(cv_image, top_left, bottom_right, color, self.BOX_THICKNESS)
        cv2.circle(cv_image, (center_x, center_y), 2, (0, 0, 255), 2)

        coordinate_text = self.format_coordinate_text(center_x, center_y, depth_mm)
        text_position = (top_left[0] + 5, top_left[1] + 25)
        cv2.putText(
            cv_image,
            coordinate_text,
            text_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        return cv_image

    def draw_pallet_angle(
        self,
        cv_image: np.ndarray,
        block_centers: List[Tuple[int, int]],
        depth_image: np.ndarray,
    ) -> np.ndarray:
        left_center = min(block_centers, key=lambda center: center[0])
        right_center = max(block_centers, key=lambda center: center[0])
        left_depth = float(depth_image[left_center[1], left_center[0]])
        right_depth = float(depth_image[right_center[1], right_center[0]])

        angle_degrees = self.calculate_angle_degrees(left_depth, right_depth)
        self.update_stable_angle(angle_degrees, left_depth, right_depth)

        if self.stable_angle_degrees is None:
            return cv_image

        cv2.line(cv_image, left_center, right_center, (204, 33, 10), 2)

        text_color = (0, 255, 255)
        cv2.putText(
            cv_image,
            f"Left Depth: {self.stable_left_depth:.1f} mm",
            (int(cv_image.shape[1] * 0.05), int(cv_image.shape[0] * 0.10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            text_color,
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            cv_image,
            f"Right Depth: {self.stable_right_depth:.1f} mm",
            (int(cv_image.shape[1] * 0.05), int(cv_image.shape[0] * 0.15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            text_color,
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            cv_image,
            f"Angle: {self.stable_angle_degrees:.2f} deg",
            (int(cv_image.shape[1] * 0.05), int(cv_image.shape[0] * 0.20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            text_color,
            1,
            cv2.LINE_AA,
        )
        return cv_image

    def update_stable_angle(
        self,
        angle_degrees: float,
        left_depth: float,
        right_depth: float,
    ) -> None:
        current_time = time.time()
        if current_time - self.last_update_time < self.stable_update_interval:
            return

        self.last_update_time = current_time
        self.stable_angle_degrees = angle_degrees
        self.stable_left_depth = left_depth
        self.stable_right_depth = right_depth

    def format_coordinate_text(
        self,
        center_x: int,
        center_y: int,
        depth_mm: float,
    ) -> str:
        if self.camera_info is None:
            return f"({center_x}, {center_y}, {depth_mm * 0.001:.2f} m)"

        x, y, z = self.pixel_to_camera_point((center_x, center_y), depth_mm)
        return f"({x:.2f}, {y:.2f}, {z:.2f} m)"

    def pixel_to_camera_point(
        self,
        pixel: Tuple[int, int],
        depth_mm: float,
    ) -> Tuple[float, float, float]:
        if self.camera_info is None:
            return 0.0, 0.0, depth_mm * 0.001

        fx = self.camera_info.k[0]
        fy = self.camera_info.k[4]
        cx = self.camera_info.k[2]
        cy = self.camera_info.k[5]
        u, v = pixel
        depth_m = depth_mm * 0.001
        return (
            float(-depth_m * (u - cx) / fx),
            float(-depth_m * (v - cy) / fy),
            float(depth_m),
        )

    def calculate_angle_degrees(self, left_depth: float, right_depth: float) -> float:
        depth_difference = right_depth - left_depth
        normalized_difference = np.clip(
            depth_difference / self.pallet_width_mm, -1.0, 1.0
        )
        return float(np.degrees(np.arcsin(normalized_difference)))

    @staticmethod
    def get_detection_center(detection: Detection) -> Tuple[int, int]:
        return (
            round(detection.bbox.center.position.x),
            round(detection.bbox.center.position.y),
        )

    @staticmethod
    def get_box_corners(bbox: BoundingBox2D) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        top_left = (
            int(bbox.center.position.x - bbox.size.x / 2.0),
            int(bbox.center.position.y - bbox.size.y / 2.0),
        )
        bottom_right = (
            int(bbox.center.position.x + bbox.size.x / 2.0),
            int(bbox.center.position.y + bbox.size.y / 2.0),
        )
        return top_left, bottom_right

    @staticmethod
    def get_class_color(class_name: str) -> Tuple[int, int, int]:
        if class_name == PalletDebugNode.BLOCK_CLASS:
            return 255, 0, 0
        if class_name == PalletDebugNode.FRONT_CLASS:
            return 0, 255, 0
        return 180, 180, 180

    @staticmethod
    def is_valid_pixel(pixel: Tuple[int, int], image: np.ndarray) -> bool:
        x, y = pixel
        return 0 <= x < image.shape[1] and 0 <= y < image.shape[0]


def main() -> None:
    rclpy.init()
    node = PalletDebugNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
