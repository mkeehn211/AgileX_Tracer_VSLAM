from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    urdf_path = os.path.join(
        get_package_share_directory("tracer_description"),
        "urdf",
        "tracer.urdf"
    )

    with open(urdf_path, 'r') as infp:
        robot_description = infp.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='both',
            parameters=[{'robot_description': robot_description}]
        )
    ])

