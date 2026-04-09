from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # LiDAR node
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'frame_id': 'lidar_link',
                'angle_compensate': True
            }]
        ),
        # Static transform from base_link to lidar_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.102', '0', '0.076', '0', '0', '0', 'base_link', 'lidar_link']
        ),
        # Cartographer node
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            arguments=[
                '-configuration_directory', '/home/michael/ros2_ws/src/my_cartographer_launch/config',
                '-configuration_basename', 'your_robot.lua'
            ]
        ),
        # Occupancy grid node (needed for /map)
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{'use_sim_time': False}],
            arguments=['-resolution', '0.05', '-publish_period_sec', '1.0']
        ),
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', '/home/michael/ros2_ws/src/my_cartographer_launch/config/cartographer.rviz']
        )
    ])

