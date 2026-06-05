# 🚀 High-Precision Pallet Pose Estimation for Autonomous Forklift Operation

[![Python](https://img.shields.io/badge/Python-98.1%25-blue?style=flat-square&logo=python)](https://www.python.org/)
[![CMake](https://img.shields.io/badge/CMake-1.9%25-brightgreen?style=flat-square&logo=cmake)](https://cmake.org/)
[![ROS2](https://img.shields.io/badge/ROS-2%20Humble-blueviolet?style=flat-square&logo=ros)](https://docs.ros.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-orange?style=flat-square)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-GPL--3.0-red?style=flat-square)](LICENSE)

Real-time high-precision pallet pose estimation system based on YOLOv8 and RGB-D depth cameras for autonomous forklift operation. This project achieves robust detection and localization of pallet components through deep learning.

**Key Capability:** Simultaneously detect pallet feet (`block`) and front edge (`front`), fuse depth maps for 3D position calculation, estimate relative angle, and publish structured ROS 2 topics for forklift control systems.

---

## 📹 Video Demo

> Click to watch demonstration video or download locally

<div align="center">

[![Video Demo](docs/thumbnail.jpg)](docs/pallet.mp4)

**[📥 Download Full Video](docs/pallet.mp4)** | **[🎬 Watch on GitHub](docs/pallet.mp4)**

</div>

---

## ✨ Key Features

<table>
<tr>
<td>

### 🎯 Detection & Recognition
- YOLOv8 high-precision object detection
- Simultaneous identification of pallet feet and edge
- Multi-class confidence output
- Real-time bounding box visualization

</td>
<td>

### 📍 Pose Estimation
- RGB-D depth camera fusion
- Precise 3D position calculation
- Real-time relative angle estimation
- Polynomial depth correction algorithm

</td>
<td>

### 🔄 ROS 2 Integration
- Standard geometry message format
- DetectionArray structured output
- PoseStamped pose publishing
- Independent angle topic interface

</td>
</tr>
</table>

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│          RGB-D Camera (Orbbec Gemini Series)            │
│                    ↓                                     │
│        ┌───────────┴────────────┐                       │
│        ↓                        ↓                        │
│    RGB Image              Depth Image                   │
│        │                        │                        │
│        └────────────┬───────────┘                       │
│                     ↓                                     │
│        ┌────────────────────────┐                       │
│        │  YOLOv8 Detector Node  │ (pallet_detector)    │
│        │  - Block Detection     │                       │
│        │  - Front Detection     │                       │
│        └────────────┬───────────┘                       │
│                     ↓                                     │
│        ┌────────────────────────┐                       │
│        │  Pose Estimation       │                       │
│        │  - 3D Localization     │                       │
│        │  - Angle Calculation   │                       │
│        └────────────┬───────────┘                       │
│                     ↓                                     │
│     ┌───────────────┼───────────────┐                   │
│     ↓               ↓               ↓                    │
│ Detection      Pose Stamped    Angle (Float64)         │
│ Array          Message         Message                  │
│     │               │               │                    │
│     └───────────────┼───────────────┘                   │
│                     ↓                                     │
│         ┌───────────────────────┐                       │
│         │  Debug Visualization  │ (rqt_image_view)     │
│         │  - Bounding Boxes     │                       │
│         │  - Depth Overlay      │                       │
│         │  - Angle Annotation   │                       │
│         └───────────────────────┘                       │
│                                                          │
│                  ↓ (to Forklift Control)                │
│         Upper Computer / Control System                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
High-Precision-Pallet-Pose-Estimation/
├── docs/
│   ├── pallet.mp4                          # Demo video
│   ├── thumbnail.jpg                       # Video thumbnail
│   └── 托盘识别技术方案.docx                # Technical documentation
│
├── src/
│   └── yolov8_ros/                         # ROS 2 workspace
│       ├── README.md
│       ├── requirements.txt                # Python dependencies
│       │
│       ├── yolov8_bringup/
│       │   └── launch/
│       │       ├── yolov8.launch.py        # Basic launch file
│       │       └── yolov8_3d.launch.py     # 3D launch file (with tracking)
│       │
│       ├── yolov8_msgs/
│       │   └── msg/                        # Custom message definitions
│       │       └── DetectionArray.msg      # Detection result message
│       │
│       └── yolov8_ros/
│           ├── setup.py
│           ├── weights/
│           │   └── fu3.pt                  # YOLOv8 model weights
│           │
│           └── yolov8_ros/
│               ├── pallet_detector_node.py  # Main detection node
│               ├── debug_node.py            # Debug visualization
│               ├── tracking_node.py         # Object tracking
│               └── detect_3d_node.py        # 3D detection
│
└── README.md                               # This document
```

---

## 🔧 System Requirements

| Component | Version | Description |
|-----------|---------|-------------|
| **ROS 2** | Humble+ | Core framework |
| **Python** | 3.8+ | Programming language |
| **PyTorch** | 2.0+ | Deep learning framework |
| **CUDA** | 11.8+ | GPU acceleration (optional) |
| **OpenCV** | 4.5+ | Image processing |
| **Ultralytics** | 8.0+ | YOLOv8 official library |
| **Camera** | Orbbec Gemini | RGB-D depth camera |

### Complete Dependencies

See: [requirements.txt](src/yolov8_ros/requirements.txt)

```bash
torch>=2.0.0
torchvision>=0.15.0
ultralytics>=8.0.0
opencv-python>=4.5.0
numpy>=1.21.0
```

---

## ⚙️ Installation & Build

### Prerequisites
```bash
# Install ROS 2 Humble
# Reference: https://docs.ros.org/en/humble/Installation.html

# Install required tools
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev build-essential
```

### Build Steps

```bash
# 1. Navigate to ROS 2 workspace root directory
cd /path/to/workspace

# 2. Install Python dependencies
pip3 install -r src/yolov8_ros/requirements.txt

# 3. Install ROS 2 system dependencies
rosdep install --from-paths src --ignore-src -r -y

# 4. Build workspace
colcon build

# 5. Source environment
source install/setup.bash
```

### Special Platform Configuration

**Jetson/Embedded GPU Platforms:**

> ⚠️ Ensure PyTorch, CUDA, TensorRT, and Ultralytics versions match your device

```bash
# PyTorch installation for Jetson
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/torch_jetson

# Verify CUDA availability
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

---

## 🎮 Quick Start

### Basic Launch

```bash
# Launch detection, pose estimation, and debug visualization
ros2 launch yolov8_bringup yolov8.launch.py
```

### Advanced Parameter Launch

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

### Complete 3D Detection with Tracking

```bash
ros2 launch yolov8_bringup yolov8_3d.launch.py
```

### Common Launch Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | `weights/fu3.pt` | Model weights path |
| `input_image_topic` | str | `/camera/color/image_raw` | RGB input topic |
| `input_depth_topic` | str | `/camera/depth/image_raw` | Depth image input topic |
| `input_depth_info_topic` | str | `/camera/depth/camera_info` | Camera info topic |
| `device` | str | `cuda:0` | Computing device (`cuda:0` or `cpu`) |
| `threshold` | float | `0.5` | Detection confidence threshold |
| `pallet_width_mm` | float | `830.0` | Pallet feet spacing (mm) |

---

## 📡 Node Documentation

### 🔴 `pallet_detector_node`

**Main Detection Node** - Performs YOLOv8 detection and pose calculation

**Source:** [pallet_detector_node.py](src/yolov8_ros/yolov8_ros/yolov8_ros/pallet_detector_node.py)

#### Subscribed Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/camera/color/image_raw` | `sensor_msgs/Image` | RGB color image |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | Depth image (mm or other units) |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | Depth camera intrinsics and distortion |

#### Published Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/yolo/detections` | `yolov8_msgs/DetectionArray` | YOLOv8 detection array |
| `/yolo/pallet_pose` | `geometry_msgs/PoseStamped` | Pallet pose (3D position + quaternion) |
| `/yolo/pallet_angle_degrees` | `std_msgs/Float64` | Pallet relative angle (unit: degrees) |

#### Services

| Service | Type | Description |
|---------|------|-------------|
| `/yolo/enable` | `std_srvs/SetBool` | Enable/pause detection |

---

### 🟠 `debug_node`

**Debug Visualization Node** - Renders bounding boxes, depth heatmap, and angle annotations

**Source:** [debug_node.py](src/yolov8_ros/yolov8_ros/yolov8_ros/debug_node.py)

**Subscribes to:** `image_raw`, `depth_image`, `depth_info`, `detections`

**Publishes:** `/yolo/dbg_image` - Annotated image viewable in RViz2 or rqt_image_view in real-time

---

### 🟡 `tracking_node` (Optional)

**Object Tracking Node** - Assigns tracking IDs to detection results

---

### 🟢 `detect_3d_node` (Optional)

**3D Detection Node** - Enhanced 3D position estimation

---

## 🧮 Pose and Angle Calculation Algorithm

### Detection Requirements

Per frame must detect:
- **3 blocks** (pallet feet)
- **1 front** (pallet front edge)

### Processing Pipeline

```
Step 1: Obtain bounding box centers of 3 blocks
         ↓
Step 2: Identify left/center/right feet by image X coordinate
         ↓
Step 3: Read depth values for left and right feet from depth map
         ↓
Step 4: Apply cubic polynomial depth correction
         ↓
Step 5: Calculate depth difference
         ↓
Step 6: Compute angle using pallet geometry
         ↓
Step 7: Project to camera coordinate system for 3D position
         ↓
Publish pose and angle topics
```

### Mathematical Formulas

#### Depth Difference Calculation

```
depth_difference = depth_right_corrected - depth_left_corrected
```

#### Relative Angle Estimation

```
angle_degrees = arcsin(depth_difference / pallet_width_mm) × (180 / π)
```

Where:
- `depth_difference`: Corrected depth difference between left and right feet (mm)
- `pallet_width_mm`: Pallet feet spacing (mm) - default 830mm

#### 3D Position Projection

```
X_3d = (u - cx) × Z / fx
Y_3d = (v - cy) × Z / fy
Z_3d = Z (from depth map)
```

Where:
- `u, v`: Pixel coordinates
- `cx, cy`: Camera principal point
- `fx, fy`: Focal lengths
- `Z`: Depth value

---

## 📊 Detection Class Definition

| Class ID | Class Name | Description |
|----------|-----------|-------------|
| 0 | `block` | Pallet feet - structural support columns, typically 3 per pallet |
| 1 | `front` | Pallet front edge - used for directional orientation |

---

## 🔍 Output Verification

### View Detection Results

```bash
ros2 topic echo /yolo/detections
```

**Example Output:**
```
detections:
- detection:
    bbox:
      center:
        x: 320.5
        y: 240.2
      size_x: 60.0
      size_y: 80.0
    class_name: 'block'
    score: 0.95
```

### View Pallet Pose

```bash
ros2 topic echo /yolo/pallet_pose
```

**Example Output:**
```
header:
  frame_id: 'camera_link'
pose:
  position:
    x: 0.45
    y: -0.12
    z: 1.23
  orientation:
    x: 0.0
    y: 0.0
    z: 0.707
    w: 0.707
```

### View Estimated Angle

```bash
ros2 topic echo /yolo/pallet_angle_degrees
```

**Example Output:**
```
data: 3.45
```

### Real-time Debug Image Visualization

```bash
# Method 1: Using rqt
rqt_image_view

# Method 2: Using RViz2
rviz2
# Then add Image display in RViz2 and subscribe to /yolo/dbg_image
```

---

## 🎯 Model Weights

### Default Model

System uses the following model by default:

```
src/yolov8_ros/yolov8_ros/weights/fu3.pt
```

### Custom Model

Specify alternative models via launch parameter:

```bash
ros2 launch yolov8_bringup yolov8.launch.py model:=/path/to/custom_model.pt
```

### Model Class Configuration

Ensure custom models define classes in this order:
- `class 0`: `block` (pallet feet)
- `class 1`: `front` (pallet front edge)

---

## 📚 References & Resources

### Official Documentation
- 🔗 [Ultralytics YOLOv8 GitHub](https://github.com/ultralytics/ultralytics)
- 🔗 [YOLOv8 Official Documentation](https://docs.ultralytics.com)
- 🔗 [ROS 2 Official Documentation](https://docs.ros.org)
- 🔗 [ROS 2 Humble Installation Guide](https://docs.ros.org/en/humble/Installation.html)

### Depth Camera Drivers
- 🔗 [Orbbec SDK](https://github.com/orbbec/OrbbecSDK)
- 🔗 [ROS 2 Orbbec Wrapper](https://github.com/orbbec/ros2_wrapper)

---

## 📖 Citation

If you use this project or YOLOv8 in papers, reports, or project documentation, please cite using the following formats:

```bibtex
@software{ultralytics_yolov8,
  author = {Ultralytics},
  title = {YOLOv8},
  year = {2023},
  url = {https://github.com/ultralytics/ultralytics}
}

@software{pallet_pose_estimation,
  author = {Yunrui Guo},
  title = {High-Precision Pallet Pose Estimation for Autonomous Forklift Operation},
  year = {2024},
  url = {https://github.com/yunruiguo/High-Precision-Pallet-Pose-Estimation-for-Autonomous-Forklift-Operation}
}
```

---

## 📄 License

This project adopts the GPL-3.0 License from the upstream ROS 2 YOLOv8 wrapper.

See: [GPL-3.0 License](src/yolov8_ros/LICENSE)

---

## 🤝 Contributing Guide

We welcome Issues and Pull Requests!

### Bug Reports

When reporting issues, please provide:
- Environment details (ROS version, Python version, GPU model)
- Complete error logs
- Steps to reproduce

### Code Contributions

- Fork this repository
- Create a feature branch (`git checkout -b feature/your-feature`)
- Commit changes (`git commit -am 'Add new feature'`)
- Push to branch (`git push origin feature/your-feature`)
- Open a Pull Request

---

## 📞 Technical Support

Encountering issues?

1. 📖 Check the [Complete Documentation](docs/托盘识别技术方案.docx)
2. 🔍 Search [Existing Issues](../../issues)
3. 💬 Create a [New Issue](../../issues/new)

---

<div align="center">

**Made with ❤️ for Autonomous Forklift Operation**

⭐ If you find this helpful, please give it a Star! ⭐

</div>
