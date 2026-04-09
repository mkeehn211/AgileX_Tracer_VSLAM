// Steps to run the teleop:
// 1. Power on RC and Tracer - plug in CAN bus
// 2. Run the following lines to set up CAN communication:
        // cd ~/ros2_ws/src/ugv_sdk/scripts/
        // bash bringup_can2usb_500k.bash
// 1. Run the base node: ros2 run tracer_base tracer_base_node
// 2. Run the teleop node: ros2 run tracer_base teleop_test
// 3. Use the keyboard to control the robot


#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <termios.h>
#include <unistd.h>
#include <iostream>
#include <csignal>
#include <thread>
#include <chrono>

class TeleopRobot : public rclcpp::Node
{
public:
    TeleopRobot() : Node("teleop_robot"), linear_velocity_(0.0), angular_velocity_(0.0)
    {
        instance_ = this;
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
        std::thread{std::bind(&TeleopRobot::keyboardLoop, this)}.detach();
        std::thread{std::bind(&TeleopRobot::publishLoop, this)}.detach();
        // Set up signal handler for SIGINT
        std::signal(SIGINT, TeleopRobot::signalHandler);
    }

    ~TeleopRobot()
    {
        // Restore the terminal settings
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt_);
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    struct termios oldt_, newt_;
    static TeleopRobot* instance_;
    double linear_velocity_;
    double angular_velocity_;
    std::mutex velocity_mutex_;

    // Function to handle keyboard input for controlling the robot
    void keyboardLoop()
    {
        char c; // Variable to store the keyboard input character

        // Get the terminal settings for stdin
        tcgetattr(STDIN_FILENO, &oldt_);
        newt_ = oldt_; // Copy the old settings to new settings
        // Disable canonical mode and echo
        newt_.c_lflag &= ~(ICANON | ECHO);
        // Set the new settings immediately
        tcsetattr(STDIN_FILENO, TCSANOW, &newt_);

        // Print instructions for the user
        std::cout << "Use WASD keys to control the robot. Press X to stop. Press Q to quit." << std::endl;

        // Loop to continuously check for keyboard input
        while (rclcpp::ok())
        {
            c = getchar(); // Get the keyboard input character

            // Lock the mutex to safely update the velocities
            std::lock_guard<std::mutex> lock(velocity_mutex_);

            // Switch case to handle different keyboard inputs
            switch (c)
            {
            case 'w':
                linear_velocity_ += 0.1; // Increase forward velocity
                break;
            case 's':
                linear_velocity_ -= 0.1; // Decrease forward velocity
                break;
            case 'a':
                angular_velocity_ += 0.1; // Increase left turn velocity
                break;
            case 'd':
                angular_velocity_ -= 0.1; // Increase right turn velocity
                break;
            case 'x':
                linear_velocity_ = 0.0; // Stop the robot
                angular_velocity_ = 0.0;
                break;
            case 'q':
                // Restore the terminal settings and exit the loop
                tcsetattr(STDIN_FILENO, TCSANOW, &oldt_);
                return;
            default:
                break;
            }
        }
    }

    // Function to continuously publish the current velocities
    void publishLoop()
    {
        while (rclcpp::ok())
        {
            publishVelocities();
            std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Publish every 100 milliseconds
        }
    }

    // Function to publish and print the current velocities
    void publishVelocities()
    {
        geometry_msgs::msg::Twist twist;

        // Lock the mutex to safely read the velocities
        {
            std::lock_guard<std::mutex> lock(velocity_mutex_);
            twist.linear.x = linear_velocity_;
            twist.angular.z = angular_velocity_;
        }

        // Publish the twist message
        publisher_->publish(twist);

        // Print the current velocities
        {
            std::lock_guard<std::mutex> lock(velocity_mutex_);
            std::cout << "Linear Velocity: " << linear_velocity_ << ", Angular Velocity: " << angular_velocity_ << std::endl;
        }
    }

    // Static signal handler function
    static void signalHandler(int signum)
    {
        if (instance_)
        {
            // Restore the terminal settings
            tcsetattr(STDIN_FILENO, TCSANOW, &instance_->oldt_);
        }
        // Exit the program
        std::exit(signum);
    }
};

// Initialize the static member
TeleopRobot* TeleopRobot::instance_ = nullptr;

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TeleopRobot>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

// #include <rclcpp/rclcpp.hpp>
// #include <geometry_msgs/msg/twist.hpp>
// #include <termios.h>
// #include <unistd.h>
// #include <iostream>
// #include <csignal>
// #include <thread>
// #include <chrono>

// class TeleopRobot : public rclcpp::Node
// {
// public:
//     TeleopRobot() : Node("teleop_robot"), linear_velocity_(0.0), angular_velocity_(0.0)
//     {
//         instance_ = this;
//         publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
//         std::thread{std::bind(&TeleopRobot::keyboardLoop, this)}.detach();
//         std::thread{std::bind(&TeleopRobot::printVelocitiesLoop, this)}.detach();
//         // Set up signal handler for SIGINT
//         std::signal(SIGINT, TeleopRobot::signalHandler);
//     }

//     ~TeleopRobot()
//     {
//         // Restore the terminal settings
//         tcsetattr(STDIN_FILENO, TCSANOW, &oldt_);
//     }

// private:
//     rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
//     struct termios oldt_, newt_;
//     static TeleopRobot* instance_;
//     double linear_velocity_;
//     double angular_velocity_;

//     // Function to handle keyboard input for controlling the robot
//     void keyboardLoop()
//     {
//         char c; // Variable to store the keyboard input character

//         // Get the terminal settings for stdin
//         tcgetattr(STDIN_FILENO, &oldt_);
//         newt_ = oldt_; // Copy the old settings to new settings
//         // Disable canonical mode and echo
//         newt_.c_lflag &= ~(ICANON | ECHO);
//         // Set the new settings immediately
//         tcsetattr(STDIN_FILENO, TCSANOW, &newt_);

//         // Print instructions for the user
//         std::cout << "Use WASD keys to control the robot. Press X to stop. Press Q to quit." << std::endl;

//         // Loop to continuously check for keyboard input
//         while (rclcpp::ok())
//         {
//             c = getchar(); // Get the keyboard input character
//             geometry_msgs::msg::Twist twist; // Message to store the robot's movement commands

//             // Switch case to handle different keyboard inputs
//             switch (c)
//             {
//             case 'w':
//                 linear_velocity_ += 0.1; // Increase forward velocity
//                 break;
//             case 's':
//                 linear_velocity_ -= 0.1; // Decrease forward velocity
//                 break;
//             case 'a':
//                 angular_velocity_ += 0.1; // Increase left turn velocity
//                 break;
//             case 'd':
//                 angular_velocity_ -= 0.1; // Increase right turn velocity
//                 break;
//             case 'x':
//                 linear_velocity_ = 0.0; // Stop the robot
//                 angular_velocity_ = 0.0;
//                 break;
//             case 'q':
//                 // Restore the terminal settings and exit the loop
//                 tcsetattr(STDIN_FILENO, TCSANOW, &oldt_);
//                 return;
//             default:
//                 break;
//             }

//             twist.linear.x = linear_velocity_;
//             twist.angular.z = angular_velocity_;

//             // Publish the twist message
//             publisher_->publish(twist);
//         }
//     }

//     // Function to continuously print the current velocities
//     void printVelocitiesLoop()
//     {
//         while (rclcpp::ok())
//         {
//             std::cout << "Linear Velocity: " << linear_velocity_ << ", Angular Velocity: " << angular_velocity_ << std::endl;
//             std::this_thread::sleep_for(std::chrono::seconds(1)); // Print every second
//         }
//     }

//     // Static signal handler function
//     static void signalHandler(int signum)
//     {
//         if (instance_)
//         {
//             // Restore the terminal settings
//             tcsetattr(STDIN_FILENO, TCSANOW, &instance_->oldt_);
//         }
//         // Exit the program
//         std::exit(signum);
//     }
// };

// // Initialize the static member
// TeleopRobot* TeleopRobot::instance_ = nullptr;

// int main(int argc, char *argv[])
// {
//     rclcpp::init(argc, argv);
//     auto node = std::make_shared<TeleopRobot>();
//     rclcpp::spin(node);
//     rclcpp::shutdown();
//     return 0;
// }
