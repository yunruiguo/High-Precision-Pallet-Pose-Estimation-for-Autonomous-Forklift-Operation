# 🚀 High-Precision Pallet Pose Estimation for Autonomous Forklift Operation

[![Python](https://img.shields.io/badge/Python-98.1%25-blue?style=flat-square&logo=python)](https://www.python.org/)
[![CMake](https://img.shields.io/badge/CMake-1.9%25-brightgreen?style=flat-square&logo=cmake)](https://cmake.org/)
[![ROS2](https://img.shields.io/badge/ROS-2%20Humble-blueviolet?style=flat-square&logo=ros)](https://docs.ros.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-orange?style=flat-square)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-GPL--3.0-red?style=flat-square)](LICENSE)

基于 YOLOv8 和 RGB-D 深度相机的**托盘柱脚检测与高精度位姿估计** ROS 2 工程。

本项目通过深度学习检测托盘部件类别 `block` (柱脚) 和 `front` (前沿)，结合深度图计算托盘中心位置、距离和相对角度，向上位机发布结构化 ROS 话题，为自主叉车提供实时精确的目标定位。

---

## 📹 Demo Video

> 点击下方观看演示视频（或使用下载链接查看本地文件）

<div align="center">

[![Video Demo](docs/thumbnail.jpg)](docs/pallet.mp4)

**[📥 Download Full Video](docs/pallet.mp4)** | **[🎬 Watch on GitHub](docs/pallet.mp4)**

</div>

---

## ✨ 功能特性

<table>
<tr>
<td>

### 🎯 检测与识别
- YOLOv8 高精度目标检测
- 同时识别托盘柱脚和前沿
- 多类别置信度输出
- 实时检测框可视化

</td>
<td>

### 📍 位姿估计
- RGB-D 深度相机融合
- 三维位置精确计算
- 相对角度实时估计
- 多项式深度校正算法

</td>
<td>

### 🔄 ROS 2 集成
- 标准几何消息格式
- DetectionArray 结构化输出
- PoseStamped 位姿发布
- 独立角度话题接口

</td>
</tr>
</table>

---

## 📊 系统架构

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

## 📁 工程结构

```
High-Precision-Pallet-Pose-Estimation/
├── docs/
│   ├── pallet.mp4                          # 演示视频
│   ├── thumbnail.jpg                       # 视频封面
│   └── 托盘识别技术方案.docx                # 技术方案文档
│
├── src/
│   └── yolov8_ros/                         # ROS 2 工作空间
│       ├── README.md
│       ├── requirements.txt                # Python 依赖
│       │
│       ├── yolov8_bringup/
│       │   └── launch/
│       │       ├── yolov8.launch.py        # 基础启动文件
│       │       └── yolov8_3d.launch.py     # 3D 启动文件 (含 tracking)
│       │
│       ├── yolov8_msgs/
│       │   └── msg/                        # 自定义消息定义
│       │       └── DetectionArray.msg      # 检测结果消息
│       │
│       └── yolov8_ros/
│           ├── setup.py
│           ├── weights/
│           │   └── fu3.pt                  # YOLOv8 模型权重
│           │
│           └── yolov8_ros/
│               ├── pallet_detector_node.py  # 主检测节点
│               ├── debug_node.py            # 调试可视化
│               ├── tracking_node.py         # 目标跟踪
│               └── detect_3d_node.py        # 3D 检测
│
└── README.md                               # 本文档
```

---

## 🔧 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| **ROS 2** | Humble+ | 核心框架 |
| **Python** | 3.8+ | 编程语言 |
| **PyTorch** | 2.0+ | 深度学习框架 |
| **CUDA** | 11.8+ | GPU 加速 (可选) |
| **OpenCV** | 4.5+ | 图像处理 |
| **Ultralytics** | 8.0+ | YOLOv8 官方库 |
| **Camera** | Orbbec Gemini | RGB-D 深度相机 |

### 完整依赖列表

详见：[requirements.txt](src/yolov8_ros/requirements.txt)

```bash
torch>=2.0.0
torchvision>=0.15.0
ultralytics>=8.0.0
opencv-python>=4.5.0
numpy>=1.21.0
```

---

## ⚙️ 安装与构建

### 前置条件
```bash
# 安装 ROS 2 Humble
# 参考: https://docs.ros.org/en/humble/Installation.html

# 安装依赖工具
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev build-essential
```

### 构建步骤

```bash
# 1. 进入 ROS 2 workspace 根目录
cd /path/to/workspace

# 2. 安装 Python 依赖
pip3 install -r src/yolov8_ros/requirements.txt

# 3. 安装 ROS 2 系统依赖
rosdep install --from-paths src --ignore-src -r -y

# 4. 编译工作空间
colcon build

# 5. 加载环境
source install/setup.bash
```

### 特殊平台配置

**Jetson/嵌入式 GPU 平台：**

> ⚠️ 确保 PyTorch、CUDA、TensorRT 和 Ultralytics 与设备版本匹配

```bash
# 针对 Jetson 的 PyTorch 安装
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/torch_jetson

# 验证 CUDA 可用性
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

---

## 🎮 快速启动

### 基础启动

```bash
# 启动检测、位姿估计和调试可视化
ros2 launch yolov8_bringup yolov8.launch.py
```

### 高级参数启动

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

### 完整 3D 检测与跟踪

```bash
ros2 launch yolov8_bringup yolov8_3d.launch.py
```

### 常用启动参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | str | `weights/fu3.pt` | 模型权重路径 |
| `input_image_topic` | str | `/camera/color/image_raw` | RGB 输入话题 |
| `input_depth_topic` | str | `/camera/depth/image_raw` | 深度图输入话题 |
| `input_depth_info_topic` | str | `/camera/depth/camera_info` | 相机内参话题 |
| `device` | str | `cuda:0` | 计算设备 (`cuda:0` 或 `cpu`) |
| `threshold` | float | `0.5` | 检测置信度阈值 |
| `pallet_width_mm` | float | `830.0` | 托盘柱脚间距 (mm) |

---

## 📡 节点说明

### 🔴 `pallet_detector_node`

**主检测节点** - 执行 YOLOv8 检测和位姿计算

**源码：** [pallet_detector_node.py](src/yolov8_ros/yolov8_ros/yolov8_ros/pallet_detector_node.py)

#### 订阅话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/camera/color/image_raw` | `sensor_msgs/Image` | RGB 彩色图像 |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 深度图 (mm 或其他单位) |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | 深度相机内参和畸变参数 |

#### 发布话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/yolo/detections` | `yolov8_msgs/DetectionArray` | YOLOv8 检测结果数组 |
| `/yolo/pallet_pose` | `geometry_msgs/PoseStamped` | 托盘位姿 (3D 位置 + 四元数) |
| `/yolo/pallet_angle_degrees` | `std_msgs/Float64` | 托盘相对角度 (单位：度) |

#### 提供服务

| 服务 | 类型 | 说明 |
|------|------|------|
| `/yolo/enable` | `std_srvs/SetBool` | 启用/暂停检测 |

---

### 🟠 `debug_node`

**调试可视化节点** - 渲染检测框、深度热力图和角度注释

**源码：** [debug_node.py](src/yolov8_ros/yolov8_ros/yolov8_ros/debug_node.py)

**订阅：** `image_raw`, `depth_image`, `depth_info`, `detections`

**发布：** `/yolo/dbg_image` - 带注释的图像，可在 RViz2 或 rqt_image_view 中实时查看

---

### 🟡 `tracking_node` (可选)

**目标跟踪节点** - 为检测结果分配追踪 ID

---

### 🟢 `detect_3d_node` (可选)

**3D 检测节点** - 增强的 3D 位置估计

---

## 🧮 位姿与角度计算算法

### 检测要求

同一帧需检测到：
- **3 个 `block`** (托盘柱脚)
- **1 个 `front`** (托盘前沿)

### 处理流程

```
步骤 1: 获取 3 个 block 的检测框中心
         ↓
步骤 2: 按图像 X 坐标识别左/右/中间柱脚
         ↓
步骤 3: 在深度图中读取左右柱脚的深度值
         ↓
步骤 4: 应用三阶多项式深度校正
         ↓
步骤 5: 计算深度差
         ↓
步骤 6: 根据托盘几何尺寸反三角计算角度
         ↓
步骤 7: 投影到相机坐标系得到 3D 位置
         ↓
发布位姿和角度话题
```

### 数学公式

#### 深度差计算

```
depth_difference = depth_right_corrected - depth_left_corrected
```

#### 相对角度估计

```
angle_degrees = arcsin(depth_difference / pallet_width_mm) × (180 / π)
```

其中：
- `depth_difference`: 左右柱脚校正后的深度差 (mm)
- `pallet_width_mm`: 托盘柱脚间距 (mm) - 默认 830mm

#### 三维位置投影

```
X_3d = (u - cx) × Z / fx
Y_3d = (v - cy) × Z / fy
Z_3d = Z (from depth map)
```

其中：
- `u, v`: 像素坐标
- `cx, cy`: 相机主点
- `fx, fy`: 焦距
- `Z`: 深度值

---

## 📊 检测类别定义

| Class ID | Class Name | 中文名称 | 说明 |
|----------|-----------|--------|------|
| 0 | `block` | 柱脚 | 托盘的支��柱脚，通常有 3 个 |
| 1 | `front` | 前沿 | 托盘的前端标识，用于方向定向 |

---

## 🔍 输出验证

### 查看检测结果

```bash
ros2 topic echo /yolo/detections
```

**输出示例：**
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

### 查看托盘位姿

```bash
ros2 topic echo /yolo/pallet_pose
```

**输出示例：**
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

### 查看估计角度

```bash
ros2 topic echo /yolo/pallet_angle_degrees
```

**输出示例：**
```
data: 3.45
```

### 实时可视化调试图像

```bash
# 方法 1: 使用 rqt
rqt_image_view

# 方法 2: 使用 RViz2
rviz2
# 然后在 RViz2 中添加 Image 显示器，订阅 /yolo/dbg_image
```

---

## 🎯 模型权重

### 默认模型

系统默认使用以下模型：

```
src/yolov8_ros/yolov8_ros/weights/fu3.pt
```

### 自定义模型

通过 launch 参数指定其他模型：

```bash
ros2 launch yolov8_bringup yolov8.launch.py model:=/path/to/custom_model.pt
```

### 模型类别配置

确保自定义模型按以下顺序定义类别：
- `class 0`: `block` (托盘柱脚)
- `class 1`: `front` (托盘前沿)

---

## 📚 参考资源

### 官方文档
- 🔗 [Ultralytics YOLOv8 GitHub](https://github.com/ultralytics/ultralytics)
- 🔗 [YOLOv8 官方文档](https://docs.ultralytics.com)
- 🔗 [ROS 2 官方文档](https://docs.ros.org)
- 🔗 [ROS 2 Humble 安装指南](https://docs.ros.org/en/humble/Installation.html)

### 深度相机驱动
- 🔗 [Orbbec SDK](https://github.com/orbbec/OrbbecSDK)
- 🔗 [ROS 2 Orbbec Wrapper](https://github.com/orbbec/ros2_wrapper)

---

## 📖 引用

如在论文、报告或项目文档中使用本项目或 YOLOv8，请使用以下引用格式：

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

本项目沿用上游 ROS 2 YOLOv8 wrapper 的 **GPL-3.0 License**。

详见：[GPL-3.0 License](src/yolov8_ros/LICENSE)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 问题反馈

如遇到问题，请提供：
- 运行环境 (ROS 版本、Python 版本、GPU 型号)
- 完整的错误日志
- 复现步骤

### 代码提交

- Fork 本仓库
- 创建特性分支 (`git checkout -b feature/your-feature`)
- 提交更改 (`git commit -am 'Add new feature'`)
- 推送到分支 (`git push origin feature/your-feature`)
- 开启 Pull Request

---

## 📞 技术支持

遇到问题？

1. 📖 查阅 [完整文档](docs/托盘识别技术方案.docx)
2. 🔍 搜索 [已有 Issue](../../issues)
3. 💬 发起 [新 Issue](../../issues/new)

---

<div align="center">

**Made with ❤️ for Autonomous Forklift Operation**

⭐ 如果有帮助，请给一个 Star! ⭐

</div>
