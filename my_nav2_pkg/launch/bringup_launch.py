import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # File paths
    pkg_share = get_package_share_directory('my_nav2_pkg')
    map_file = os.path.join(pkg_share, 'config', 'my_map.yaml')
    params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    ekf_file = os.path.join(pkg_share, 'config', 'ekf_scanodom.yaml')

    return LaunchDescription([
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen'
            ),

        # -----------------------------------------------------
        # 1. Load your URDF robot model (robot_state_publisher)
        # -----------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('tracer_description'),
                    'launch',
                    'display.launch.py'
                )
            )
        ),

        # Launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'map',
            default_value=map_file,
            description='Full path to map yaml file'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=params_file,
            description='Full path to the Nav2 parameters file'
        ),

        # Static TF: base_link → laser_frame (lidar is backwards)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_base_laser',
            output='screen',
            arguments=[
                '--x','0.18','--y','0','--z','0.5',
                '--roll','0','--pitch','0','--yaw','3.14159',
                '--frame-id','base_link','--child-frame-id','laser_frame'
            ]
        ),

        # Static TF: base_link → imu_link 
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_base_imu',
            output='screen',
            arguments=[
                '--x','0.18','--y','0','--z','0.45',
                '--roll','0','--pitch','0','--yaw','0',
                '--frame-id','base_link','--child-frame-id','imu_link'
            ]
        ),

        # Static TF: base_link → camera_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_base_camera',
            output='screen',
            arguments=[
                '--x', '0.28', '--y', '0.0', '--z', '0.2',    
                '--roll', '0','--pitch', '0','--yaw', '0',
                '--frame-id', 'base_link','--child-frame-id', 'camera_link'
            ]
        ),

        # Lidar Node
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'frame_id': 'laser_frame',
                'angle_compensate': True
            }]
        ),

        # Lidar Odometry Node
        Node(
            package='lidar_odometry',
            executable='lidar_odometry_node',
            name='lidar_odometry_node',
            output='screen',
            parameters=[{
                'scan_topic_name': '/scan',
                'odom_topic_name': '/scan_odom',
                'max_correspondence_distance': 1.0,
                'transformation_epsilon': 0.005,
                'maximum_iterations': 30
            }]
        ),
 
        # IMU covariance/bias republisher
        Node(
            package='my_nav2_pkg',
            executable='imu_cov_republisher',
            name='imu_cov_republisher',
            output='screen'
        ),

        # EKF Node for sensor fusion
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_local',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'frequency': 20.0,
                'two_d_mode': True,
                'publish_tf': True,

                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_link_frame': 'base_link',
                'world_frame': 'odom',

                # Camera odom
                'odom1': '/rtabmap/odom',
                'odom1_queue_size': 50,
                'odom1_nodelay': True,
                'odom1_differential': False,
                'odom1_relative': False,
                'odom1_config': [ True, True, False,
                                  False, False, True,
                                  True, False, False,
                                  False, False, False,
                                  False, False, False ],

                # Lidar odom
                'odom2': '/scan_odom',
                'odom2_queue_size': 50,
                'odom2_nodelay': True,
                'odom2_differential': True,
                'odom2_relative': False,
                'odom2_config': [ True, True, False,
                                  False, False, True,
                                  False, False, False,
                                  False, False, False,
                                  False, False, False ],

                # IMU
                'imu0': '/imu/data_cov', #/camera/camera/gyro/sample to use camera imu, /imu/data_cov to use standalone imu
                'imu0_queue_size': 50,
                'imu0_nodelay': True,
                'imu0_differential': False,
                'imu0_relative': False,
                'imu0_remove_gravitational_acceleration': False,
                'imu0_config': [ False, False, False,
                                 False, False, False,
                                 False, False, False,
                                 False, False, True,
                                 False, False, False ],

                'sensor_timeout': 0.5,
                'print_diagnostics': True
                
            }]
        ),


        # -------------------------
        # Nav2 Bringup Components
        # -------------------------

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file],
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file],
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file],
        ),

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[params_file],
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[params_file],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'node_names': [
                    # 'map_server',
                    #'amcl',
                    'planner_server',
                    'controller_server',
                    'bt_navigator',
                    'waypoint_follower',
                    'behavior_server'
                ]
            }],
        ),
    ])
