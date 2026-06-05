# YOLOv8 Pallet Pose ROS 2 Workspace

基于 YOLOv8 和 RGB-D 深度相机的托盘柱脚检测与位姿估计 ROS 2 工程。
项目通过检测托盘部件类别 `block` 和 `front`，结合深度图计算托盘中心位置、
距离和相对角度，并向上位机发布结构化 ROS 话题。

## Demo

<video src="docs/pallet.mp4" controls width="100%">
  Your browser does not support the video tag.
</video>

如果 GitHub 页面没有直接渲染视频，可以打开：

[docs/pallet.mp4](docs/pallet.mp4)

## 功能特性

- 使用 YOLOv8 检测托盘柱脚和前沿部件。
- 从 RGB 图像输出检测框、类别、置信度等 `DetectionArray` 结果。
- 从深度图读取柱脚中心深度，计算托盘三维位置。
- 基于左右柱脚深度差估计托盘相对角度。
- 发布标准 `geometry_msgs/PoseStamped` 托盘位姿。
- 发布独立的 `std_msgs/Float64` 角度话题，便于上位机直接消费。
- 提供 debug 图像话题，用于查看检测框、深度和角度。

## 工程结构

```text
.
├── docs/
│   ├── pallet.mp4
│   └── 托盘识别技术方案.docx
├── src/
│   └── yolov8_ros/
│       ├── README.md
│       ├── requirements.txt
│       ├── yolov8_bringup/
│       │   └── launch/
│       │       ├── yolov8.launch.py
│       │       └── yolov8_3d.launch.py
│       ├── yolov8_msgs/
│       │   └── msg/
│       └── yolov8_ros/
│           ├── setup.py
│           ├── weights/
│           └── yolov8_ros/
│               ├── pallet_detector_node.py
│               ├── debug_node.py
│               ├── tracking_node.py
│               └── detect_3d_node.py
└── README.md
```

## 环境要求

- ROS 2 Humble 或兼容版本
- Python 3
- OpenCV
- PyTorch
- Ultralytics YOLOv8
- RGB-D 深度相机，例如 Orbbec Gemini 系列

Python 依赖见：

```text
src/yolov8_ros/requirements.txt
```

## 安装与构建

在 ROS 2 workspace 根目录执行：

```bash
pip3 install -r src/yolov8_ros/requirements.txt
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

如果在 Jetson 或其他嵌入式 GPU 平台运行，请确保 PyTorch、CUDA、TensorRT
和 Ultralytics 环境与设备版本匹配。

## 模型权重

默认 launch 文件使用：

```text
src/yolov8_ros/yolov8_ros/weights/fu3.pt
```

也可以通过 launch 参数指定其他模型：

```bash
ros2 launch yolov8_bringup yolov8.launch.py model:=/path/to/model.pt
```

模型类别约定：

| class id | class name | 含义 |
| --- | --- | --- |
| 0 | `block` | 托盘柱脚 |
| 1 | `front` | 托盘前沿 |

## 启动

基础检测、位姿估计和 debug 图像：

```bash
ros2 launch yolov8_bringup yolov8.launch.py
```

常用参数示例：

```bash
ros2 launch yolov8_bringup yolov8.launch.py \
  model:=/path/to/fu3.pt \
  input_image_topic:=/camera/color/image_raw \
  input_depth_topic:=/camera/depth/image_raw \
  input_depth_info_topic:=/camera/depth/camera_info \
  device:=cuda:0 \
  threshold:=0.65 \
  pallet_width_mm:=830.0
```

如需同时启用 tracking 和 3D detection：

```bash
ros2 launch yolov8_bringup yolov8_3d.launch.py
```

## 节点说明

### `pallet_detector_node`

源码：

```text
src/yolov8_ros/yolov8_ros/yolov8_ros/pallet_detector_node.py
```

订阅话题：

| 话题 | 类型 | 说明 |
| --- | --- | --- |
| `image_raw` | `sensor_msgs/Image` | RGB 图像 |
| `depth_image` | `sensor_msgs/Image` | 深度图 |
| `depth_info` | `sensor_msgs/CameraInfo` | 深度相机内参 |

发布话题：

| 话题 | 类型 | 说明 |
| --- | --- | --- |
| `detections` | `yolov8_msgs/DetectionArray` | YOLOv8 检测结果 |
| `pallet_pose` | `geometry_msgs/PoseStamped` | 托盘位姿 |
| `pallet_angle_degrees` | `std_msgs/Float64` | 托盘相对角度，单位为度 |

服务：

| 服务 | 类型 | 说明 |
| --- | --- | --- |
| `enable` | `std_srvs/SetBool` | 启用或暂停检测 |

### `debug_node`

源码：

```text
src/yolov8_ros/yolov8_ros/yolov8_ros/debug_node.py
```

订阅 `image_raw`、`depth_image`、`depth_info` 和 `detections`，
发布 `dbg_image`，用于可视化检测框、深度和角度。

## 位姿与角度计算

当前算法要求同一帧中检测到：

- 3 个 `block`
- 1 个 `front`

处理流程：

1. 获取 3 个 `block` 的检测框中心点。
2. 按图像 `x` 坐标选出最左和最右柱脚。
3. 在深度图中读取左右柱脚中心深度。
4. 对左右深度分别做三阶多项式校正。
5. 计算深度差：

```text
depth_difference = right_depth_corrected - left_depth_corrected
```

6. 根据托盘柱脚间距估计角度：

```text
angle_degrees = asin(depth_difference / pallet_width_mm) * 180 / pi
```

7. 选取中间柱脚作为托盘中心参考点，结合相机内参投影为相机坐标系下的三维位置。

## 输出检查

查看检测结果：

```bash
ros2 topic echo /yolo/detections
```

查看托盘位姿：

```bash
ros2 topic echo /yolo/pallet_pose
```

查看角度：

```bash
ros2 topic echo /yolo/pallet_angle_degrees
```

查看 debug 图像：

```bash
ros2 topic echo /yolo/dbg_image
```

也可以在 RViz2 或 `rqt_image_view` 中订阅 `/yolo/dbg_image`。

## 参考资料

- Ultralytics YOLOv8 GitHub: https://github.com/ultralytics/ultralytics
- Ultralytics YOLOv8 Documentation: https://docs.ultralytics.com
- ROS 2 Documentation: https://docs.ros.org

如果在论文、报告或项目文档中引用 YOLOv8，可使用以下软件引用格式：

```bibtex
@software{ultralytics_yolov8,
  author = {Ultralytics},
  title = {YOLOv8},
  year = {2023},
  url = {https://github.com/ultralytics/ultralytics}
}
```

## License

本项目沿用上游 ROS 2 YOLOv8 wrapper 的 GPL-3 license。详情见：

```text
src/yolov8_ros/LICENSE
```
