import os
from glob import glob
from setuptools import setup

package_name = 'my_nav2_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Michael',
    maintainer_email='mkeehn211@gmail.com',
    description='Nav2 bringup with IMU republisher',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'imu_cov_republisher = my_nav2_pkg.imu_cov_republisher:main',
        ],
    },
)