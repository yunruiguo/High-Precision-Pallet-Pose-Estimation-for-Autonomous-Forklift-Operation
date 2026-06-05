from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import rclpy
import tf_transformations
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped, Quaternion
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Float64
from std_srvs.srv import SetBool
from ultralytics import YOLO
from ultralytics.engine.results import Boxes, Keypoints, Masks, Results

from yolov8_msgs.msg import (
    BoundingBox2D,
    Detection,
    DetectionArray,
    KeyPoint2D,
    KeyPoint2DArray,
    Mask,
    Point2D,
)


@dataclass(frozen=True)
class PalletPart:
    class_name: str
    center: Tuple[int, int]
    depth_mm: float


class PalletDetectorNode(Node):
    """Run YOLOv8 pallet-part detection and publish pallet pose."""

    BLOCK_CLASS = "block"
    FRONT_CLASS = "front"

    def __init__(self) -> None:
        super().__init__("pallet_detector_node")

        self.declare_parameter("model", "yolov8m.pt")
        self.declare_parameter("device", "cuda:0")
        self.declare_parameter("threshold", 0.65)
        self.declare_parameter("enable", True)
        self.declare_parameter("pallet_width_mm", 830.0)

        model_path = self.get_parameter("model").get_parameter_value().string_value
        self.device = self.get_parameter("device").get_parameter_value().string_value
        self.threshold = (
            self.get_parameter("threshold").get_parameter_value().double_value
        )
        self.enabled = self.get_parameter("enable").get_parameter_value().bool_value
        self.pallet_width_mm = (
            self.get_parameter("pallet_width_mm").get_parameter_value().double_value
        )

        self.bridge = CvBridge()
        self.yolo = YOLO(model_path)
        self.yolo.fuse()

        self.depth_image: Optional[np.ndarray] = None
        self.camera_info: Optional[CameraInfo] = None

        self.right_depth_coefficients = np.array(
            [-3.69660699e03, 8.08522529e00, -4.48052336e-03, 9.38944948e-07]
        )
        self.left_depth_coefficients = np.array(
            [9.10299836e02, -4.69223155e-01, 7.34949655e-04, -1.15173886e-07]
        )

        self.detections_pub = self.create_publisher(DetectionArray, "detections", 10)
        self.pose_pub = self.create_publisher(PoseStamped, "pallet_pose", 10)
        self.angle_pub = self.create_publisher(Float64, "pallet_angle_degrees", 10)

        self.create_subscription(
            Image, "image_raw", self.image_callback, qos_profile_sensor_data
        )
        self.create_subscription(
            Image, "depth_image", self.depth_callback, qos_profile_sensor_data
        )
        self.create_subscription(
            CameraInfo, "depth_info", self.camera_info_callback, qos_profile_sensor_data
        )
        self.create_service(SetBool, "enable", self.enable_callback)

    def enable_callback(
        self, request: SetBool.Request, response: SetBool.Response
    ) -> SetBool.Response:
        self.enabled = request.data
        response.success = True
        return response

    def depth_callback(self, depth_msg: Image) -> None:
        self.depth_image = self.bridge.imgmsg_to_cv2(depth_msg)

    def camera_info_callback(self, msg: CameraInfo) -> None:
        self.camera_info = msg

    def image_callback(self, msg: Image) -> None:
        if not self.enabled or self.depth_image is None or self.camera_info is None:
            return

        cv_image = self.bridge.imgmsg_to_cv2(msg)
        result = self.run_inference(cv_image)
        detections = self.build_detection_array(result, msg)
        self.detections_pub.publish(detections)

        pallet_parts = self.extract_pallet_parts(detections)
        pallet_pose = self.build_pallet_pose(msg, pallet_parts)
        if pallet_pose is not None:
            pose_msg, angle_degrees = pallet_pose
            self.pose_pub.publish(pose_msg)
            self.angle_pub.publish(Float64(data=angle_degrees))

    def run_inference(self, cv_image: np.ndarray) -> Results:
        results = self.yolo.predict(
            source=cv_image,
            classes=[0, 1],
            verbose=False,
            stream=False,
            conf=self.threshold,
            device=self.device,
        )
        return results[0].cpu()

    def build_detection_array(self, result: Results, image_msg: Image) -> DetectionArray:
        detections_msg = DetectionArray()
        detections_msg.header = image_msg.header

        hypotheses = self.parse_hypotheses(result)
        boxes = self.parse_boxes(result)
        masks = self.parse_masks(result) if result.masks else []
        keypoints = self.parse_keypoints(result) if result.keypoints else []

        for index in range(len(result)):
            detection = Detection()

            if result.boxes:
                detection.class_id = hypotheses[index]["class_id"]
                detection.class_name = hypotheses[index]["class_name"]
                detection.score = hypotheses[index]["score"]
                detection.bbox = boxes[index]

            if masks:
                detection.mask = masks[index]

            if keypoints:
                detection.keypoints = keypoints[index]

            detections_msg.detections.append(detection)

        return detections_msg

    def parse_hypotheses(self, result: Results) -> List[Dict]:
        hypotheses = []
        box_data: Boxes
        for box_data in result.boxes:
            class_id = int(box_data.cls)
            hypotheses.append(
                {
                    "class_id": class_id,
                    "class_name": self.yolo.names[class_id],
                    "score": float(box_data.conf),
                }
            )
        return hypotheses

    @staticmethod
    def parse_boxes(result: Results) -> List[BoundingBox2D]:
        boxes = []
        box_data: Boxes
        for box_data in result.boxes:
            bbox = BoundingBox2D()
            xywh = box_data.xywh[0]
            bbox.center.position.x = float(xywh[0])
            bbox.center.position.y = float(xywh[1])
            bbox.size.x = float(xywh[2])
            bbox.size.y = float(xywh[3])
            boxes.append(bbox)
        return boxes

    @staticmethod
    def parse_masks(result: Results) -> List[Mask]:
        masks = []

        def create_point(x: float, y: float) -> Point2D:
            point = Point2D()
            point.x = x
            point.y = y
            return point

        mask_data: Masks
        for mask_data in result.masks:
            mask = Mask()
            mask.data = [
                create_point(float(point[0]), float(point[1]))
                for point in mask_data.xy[0].tolist()
            ]
            mask.height = result.orig_img.shape[0]
            mask.width = result.orig_img.shape[1]
            masks.append(mask)
        return masks

    def parse_keypoints(self, result: Results) -> List[KeyPoint2DArray]:
        keypoints = []
        points: Keypoints
        for points in result.keypoints:
            keypoint_array = KeyPoint2DArray()
            if points.conf is None:
                continue

            for keypoint_id, (point, confidence) in enumerate(
                zip(points.xy[0], points.conf[0])
            ):
                if confidence >= self.threshold:
                    keypoint = KeyPoint2D()
                    keypoint.id = keypoint_id + 1
                    keypoint.point.x = float(point[0])
                    keypoint.point.y = float(point[1])
                    keypoint.score = float(confidence)
                    keypoint_array.data.append(keypoint)

            keypoints.append(keypoint_array)
        return keypoints

    def extract_pallet_parts(self, detections: DetectionArray) -> List[PalletPart]:
        pallet_parts = []
        for detection in detections.detections:
            if detection.class_name not in {self.BLOCK_CLASS, self.FRONT_CLASS}:
                continue

            center_x = round(detection.bbox.center.position.x)
            center_y = round(detection.bbox.center.position.y)
            depth_mm = self.read_depth_mm(center_x, center_y)
            if depth_mm is None:
                continue

            pallet_parts.append(
                PalletPart(
                    class_name=detection.class_name,
                    center=(center_x, center_y),
                    depth_mm=depth_mm,
                )
            )
        return pallet_parts

    def build_pallet_pose(
        self, image_msg: Image, pallet_parts: List[PalletPart]
    ) -> Optional[Tuple[PoseStamped, float]]:
        block_parts = [part for part in pallet_parts if part.class_name == self.BLOCK_CLASS]
        front_parts = [part for part in pallet_parts if part.class_name == self.FRONT_CLASS]

        if len(block_parts) != 3 or len(front_parts) != 1:
            return None

        angle_degrees = self.calculate_pallet_angle_degrees(block_parts)
        middle_block = sorted(block_parts, key=lambda part: part.center[0])[1]
        position = self.pixel_to_camera_point(middle_block.center, middle_block.depth_mm)

        pose_msg = PoseStamped()
        pose_msg.header = image_msg.header
        pose_msg.pose.position.x = position[0]
        pose_msg.pose.position.y = position[1]
        pose_msg.pose.position.z = position[2]
        pose_msg.pose.orientation = self.angle_to_quaternion(angle_degrees)
        return pose_msg, angle_degrees

    def calculate_pallet_angle_degrees(self, block_parts: List[PalletPart]) -> float:
        left_block = min(block_parts, key=lambda part: part.center[0])
        right_block = max(block_parts, key=lambda part: part.center[0])

        left_depth = self.evaluate_polynomial(
            left_block.depth_mm, self.left_depth_coefficients
        )
        right_depth = self.evaluate_polynomial(
            right_block.depth_mm, self.right_depth_coefficients
        )
        depth_difference = right_depth - left_depth
        normalized_difference = np.clip(
            depth_difference / self.pallet_width_mm, -1.0, 1.0
        )
        return float(np.degrees(np.arcsin(normalized_difference)))

    def read_depth_mm(self, center_x: int, center_y: int) -> Optional[float]:
        if self.depth_image is None:
            return None
        if not (0 <= center_x < self.depth_image.shape[1]):
            return None
        if not (0 <= center_y < self.depth_image.shape[0]):
            return None

        depth_value = float(self.depth_image[center_y, center_x])
        if depth_value <= 0.0 or np.isnan(depth_value):
            return None
        return depth_value

    def pixel_to_camera_point(
        self, pixel: Tuple[int, int], depth_mm: float
    ) -> Tuple[float, float, float]:
        if self.camera_info is None:
            return 0.0, 0.0, depth_mm * 0.001

        fx = self.camera_info.k[0]
        fy = self.camera_info.k[4]
        cx = self.camera_info.k[2]
        cy = self.camera_info.k[5]
        u, v = pixel
        depth_m = depth_mm * 0.001

        x = -depth_m * (u - cx) / fx
        y = -depth_m * (v - cy) / fy
        return float(x), float(y), float(depth_m)

    @staticmethod
    def angle_to_quaternion(angle_degrees: float) -> Quaternion:
        qx, qy, qz, qw = tf_transformations.quaternion_from_euler(
            0.0, np.radians(angle_degrees), 0.0
        )
        quaternion = Quaternion()
        quaternion.x = float(qx)
        quaternion.y = float(qy)
        quaternion.z = float(qz)
        quaternion.w = float(qw)
        return quaternion

    @staticmethod
    def evaluate_polynomial(value: float, coefficients: np.ndarray) -> float:
        return float(
            sum(
                coefficient * (value ** index)
                for index, coefficient in enumerate(coefficients)
            )
        )


def main() -> None:
    rclpy.init()
    node = PalletDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
