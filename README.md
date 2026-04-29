# AgileX_Tracer_VSLAM
# ROS2 Packages for Tracer Mobile Robot

## Packages

This repository contains packages to control the tracer.

* my_nav2_pkg: a ROS2 package to run the navigation stack (contains custom yaml file for Tracer)
* wit_ros2_imu: a ROS2 package that allows communication with the external IMU
* tracer_description: a ROS2 package containing a simple model of the Tracer (used in the nav stack)
* [Tracer_ros2](https://github.com/ckwan02/tracer_ros2)
    * tracer_base: a ROS wrapper around [ugv_sdk](https://github.com/agilexrobotics/ugv_sdk) to monitor and control the tracer robot
    * tracer_msgs: tracer related message definitions
* [ugv_sdk](https://github.com/agilexrobotics/ugv_sdk)
* [Simple-2D-LiDAR-Odometry](https://github.com/dawan0111/Simple-2D-LiDAR-Odometry): turns LiDAR readings into odometry values
* [sllidar_ros2](https://github.com/Slamtec/sllidar_ros2): starts the LiDAR and starts publishing data

## Supported Hardware

* Tracer
* Tracer-mini



## Installation
 
### 1. Clone the repository (including submodules)
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone --recurse-submodules https://github.com/mkeehn211/AgileX_Tracer_VSLAM.git
```
 
> **Important:** You must use `--recurse-submodules` to pull the external packages. If you already cloned without it, run:
> ```bash
> git submodule update --init --recursive
> ```
 
### 2. Build the workspace
```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Basic usage of the ROS packages

### 1. Setup CAN-To-USB adapter

* Enable gs_usb kernel module(If you have already added this module, you do not need to add it)
    ```
    sudo modprobe gs_usb
    ```
    
* first time use tracer-ros2 package
   ```
   cd ~/ros2_ws/src/ugv_sdk/scripts/
   bash setup_can2usb.bash
   ```
   
* if not the first time use tracer-ros2 package(Run this command every time you turn off the power) 
   ```
   cd ~/ros2_ws/src/ugv_sdk/scripts/
   bash bringup_can2usb_500k.bash
   ```
   
* Testing command
    ```
    # receiving data from can0
    candump can0
    ```
### 2. Launch ROS nodes
 
* Start the base node for the Tracer robot

    ```
    ros2 run tracer_base tracer_base_node
    ```

* Then you can send command to the robot
    ```
    ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "linear:
    x: 0.0
    y: 0.0
    z: 0.0
    angular:
    x: 0.0
    y: 0.0
    z: 0.0" 
    ```
* You can use the teleop test to control the robot with your keyboard
    ```
    ros2 run tracer_base teleop_test
    
    ```
### 3. Running the sensors

* To run the LiDAR (the nav2 package does this already)
    1. Install Slidar
    ```
    sudo apt install -y ros-humble-sllidar-ros2
    
    ```
    2. Add port permissions (if needed)
    ```
    sudo chmod 777 /dev/ttyUSB0

    # Or permanently, add yourself to the dialout group:
    sudo usermod -aG dialout $USER
    # (log out and back in for this to take effect)
    
    ```
    3. Run the Lidar
    ```
    ros2 run sllidar_ros2 sllidar_node
    
    ```
    
* To run the IMU
   1. Install pyserial
  
   ```
    sudo apt install python3-serial
    
    ```
   2. Bind port
   ```
   cd ros2_ws/src wit_ros2_imu
   sudo chmod +x bind_usb.sh
   sudo ./bind_usb.sh
    
    ```
   3. Build the worksapce and launch the IMU

    ```
    colcon build
    source install/setup.bash
    ros2 launch wit_ros2_imu rviz_and_imu.launch.py
    
    ```
* To run the RealSense Depth Camera
    1. Install RealSense libraries
    ```
    sudo apt install -y librealsense2-dkms librealsense2-utils librealsense2-dev
    ```
    2. Launch RealSense publisher
    ```
    sudo modprobe uvcvideo

    ros2 launch realsense2_camera rs_launch.py \
        align_depth.enable:=true \
        enable_gyro:=false \
        enable_accel:=false
    
    ```
    3. Alternatively if you would like to just stream the camera and test the features use the RealSense GUI
    ```
    realsense-viewer
    
    ```
    
    
### 4. Navigation stack and VSLAM

* Launch the nav stack in a seperate terminal (the tracer base node, IMU, and RealSense should also be running)
    ```
    ros2 launch my_nav2_pkg bringup_launch.py
    
    ```
* Launch rtabmap
    ```
    ros2 launch rtabmap_launch rtabmap.launch.py \
        rgb_topic:=/camera/camera/color/image_raw \
        depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
        camera_info_topic:=/camera/camera/color/camera_info \
        odom_topic:=/odom \
        frame_id:=base_link \
        odom_frame_id:=odom \
        rviz:=true \
        approx_sync_max_interval:=0.02 \
        Reg/Force3DoF:=true
    ```
* Rviz will automatically pull up and mapping will begin (set goal pose to navigate)

* To stop mapping and use the current map to localize add the following line to launch:
```
  localization:=true
```

* The map is automatically saved when the program ends to delete the map data run:
```
  rm ~/.ros/rtabmap.db
```
    
**SAFETY PRECAUSION**: 

Always have your remote controller ready to take over the control whenever necessary. 
You can flip the SWB switch to remote control mode to cut off any velocity commands from CAN communication
