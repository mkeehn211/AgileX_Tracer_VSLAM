import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
import math

class ImuCovRepublisher(Node):
    def __init__(self):
        super().__init__('imu_cov_republisher')
        self.sub_imu = self.create_subscription(Imu, '/imu/data_raw', self.on_imu, 50)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.on_odom, 10)
        self.pub_imu = self.create_publisher(Imu, '/imu/data_cov', 50)

        # Bias estimation (only when robot is stationary)
        self.bias_z = 0.0
        self.alpha = 0.05
        self.stationary_lin_thresh = 0.03  # m/s
        self.stationary_ang_thresh = 0.01   # rad/s
        self.deadband = 0.05 #rad/s
        self.is_stationary = False

        # Covariances
        self.orient_cov = [0.1, 0.0, 0.0,
                           0.0, 0.1, 0.0,
                           0.0, 0.0, 0.04]        # yaw variance
        self.ang_cov = [0.5, 0.0, 0.0,
                        0.0, 0.5, 0.0,
                        0.0, 0.0, 0.2]         # yaw-rate variance
        self.acc_cov = [999.0, 0.0, 0.0,
                        0.0, 999.0, 0.0,
                        0.0, 0.0, 999.0]         # de-weight accel

    def on_odom(self, msg: Odometry):
        v = msg.twist.twist
        lin = math.hypot(v.linear.x, v.linear.y)
        ang = abs(v.angular.z)
        self.is_stationary = (lin < self.stationary_lin_thresh and ang < self.stationary_ang_thresh)

    def on_imu(self, msg: Imu):
        out = Imu()
        out.header = msg.header
        out.orientation = msg.orientation
        out.angular_velocity = msg.angular_velocity
        out.linear_acceleration = msg.linear_acceleration
        self.deadband_z = 0.05 # rad/s


        # Bias-correct yaw rate when stationary
        wz = msg.angular_velocity.z
        if self.is_stationary and abs(wz) < 1.0:
            self.bias_z = (1.0 - self.alpha) * self.bias_z + self.alpha * wz
        out.angular_velocity.z = wz - self.bias_z

        # Deadband at rest: clamp tiny yaw rates to 0
        if self.is_stationary and abs(out.angular_velocity.z) < self.deadband_z:
            out.angular_velocity.z = 0.0

        # Inject covariances
        out.orientation_covariance = self.orient_cov
        out.angular_velocity_covariance = self.ang_cov
        out.linear_acceleration_covariance = self.acc_cov

        self.pub_imu.publish(out)

def main():
    rclpy.init()
    node = ImuCovRepublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()