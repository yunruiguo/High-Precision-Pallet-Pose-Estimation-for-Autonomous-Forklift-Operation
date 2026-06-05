from glob import glob
from os.path import join

from setuptools import setup


package_name = "yolov8_ros"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [join("resource", package_name)]),
        (join("share", package_name), ["package.xml"]),
        (join("share", package_name, "weights"), glob(join("weights", "*"))),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Miguel Angel Gonzalez Santamarta",
    maintainer_email="mgons@unileon.es",
    description="YOLOv8 pallet detection and pose estimation for ROS 2",
    license="GPL-3",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pallet_detector_node = yolov8_ros.pallet_detector_node:main",
            "debug_node = yolov8_ros.debug_node:main",
            "tracking_node = yolov8_ros.tracking_node:main",
            "detect_3d_node = yolov8_ros.detect_3d_node:main",
        ],
    },
)
