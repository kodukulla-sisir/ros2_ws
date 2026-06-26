#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial
import time

class Ros2XboxBridge(Node):
    def __init__(self):
        super().__init__('ros2_xbox_bridge')
        
        # Connect to Arduino
        self.arduino_port = '/dev/ttyACM0'
        self.baud_rate = 115200
        
        try:
            self.arduino = serial.Serial(self.arduino_port, self.baud_rate, timeout=0.05)
            time.sleep(2) # Wait for Arduino to reset
            self.get_logger().info(f"Successfully connected to Arduino on {self.arduino_port}")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to Arduino: {e}")
            self.arduino = None
            
        # Subscribe to the controller data
        self.subscription = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        self.get_logger().info("Listening for joystick inputs...")

    def joy_callback(self, msg):
        # 1. Grab your PS5 mapped numbers
        left_stick_y = msg.axes[1]  
        action_button = msg.buttons[0] 
        
        # 2. Format the string exactly as the Arduino expects it
        command_str = f"{left_stick_y:.2f},{action_button}\n"
        
        # 3. Only trigger if you are actually moving the stick or pressing the button
        # (This prevents spamming the terminal with "0.00,0" a hundred times a second)
        if abs(left_stick_y) > 0.05 or action_button == 1:
            
            if self.arduino is not None:
                # Hardware is connected! Send it over USB.
                self.arduino.write(command_str.encode('utf-8'))
            else:
                # Hardware is missing! Print it to the screen instead.
                self.get_logger().info(f"DRY RUN - Would have sent: {command_str.strip()}")

def main(args=None):
    rclpy.init(args=args)
    bridge = Ros2XboxBridge()
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        if bridge.arduino:
            bridge.arduino.close()
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
    #source /opt/ros/foxy/setup.bash
#ros2 run joy joy_node