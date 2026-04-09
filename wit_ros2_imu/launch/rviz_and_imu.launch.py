from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    imu_node = Node(
        package='wit_ros2_imu',
        executable='wit_ros2_imu',        # <-- Updated for Humble
        name='imu',                       # <-- Updated
        remappings=[('/wit/imu', '/imu/data')],
        parameters=[
            {'port': '/dev/imu_usb'},
            {'baud': 9600}
        ],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',               # <-- Updated
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        imu_node,
        # rviz_node     # Enable this if you want RViz to auto-start
    ])

