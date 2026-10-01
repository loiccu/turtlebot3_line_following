#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

## TODO: tune these values for your robot
LINEAR_VEL = 0.1   # Constant forward velocity (m/s)
KP = 0.01         # Proportional gain (rad/s per pixel of error)

class ImageViewer(Node):
    def __init__(self):
        super().__init__('image_viewer')
        self.bridge = CvBridge()
        self.quit_requested = False  # set to True when 'q' / Esc is pressed
        self.last_error = 0.0        # previous error, for the derivative term

        # Subscription to the compressed image topic
        self.image_sub = self.create_subscription(
            CompressedImage,
            '/image_raw/compressed',  # TODO: change topic name if required
            self.image_callback,
            qos_profile_sensor_data
        )

        # Publisher for the velocity commands sent to the robot
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)
        self.twist = Twist()

        # HSV boundaries. OpenCV: H in [0,179], S,V in [0,255]
        # Yellow line (assumed on the LEFT of the lane)
        self.lower_yellow = np.array([20, 100, 100])
        self.upper_yellow = np.array([35, 255, 255])
        # Blue line (assumed on the RIGHT of the lane)
        self.lower_blue = np.array([100, 100, 50])
        self.upper_blue = np.array([130, 255, 255])

        self.get_logger().info('Image viewer node started. Waiting for images...')

    def stop_robot(self):
        # Send zero velocities to stop the robot
        self.twist = Twist()  # all fields initialized to 0.0
        # Published several times to make sure it is received before the node is destroyed
        for _ in range(3):
            self.cmd_vel_pub.publish(self.twist)
            time.sleep(0.05)
        self.get_logger().info('Robot stopped (zero velocities sent).')

    def image_callback(self, msg):
        # Conversion of ROS CompressedImage msg into an OpenCV image (BGR)
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Error in image conversion: {e}',
                                    throttle_duration_sec=2.0)
            return

        # Define your ROI, for example, part of the lower half of the image
        height, width = cv_image.shape[:2]
        ## TODO: adapt the ROI corners to your need :
        top_y = int(height * 0.7)     # Start at 70% of the image height
        bottom_y = height             # Go to the bottom of the image
        left_x = int(width * 0.05)     # Start at 5% of the width (skip the left border)
        right_x = int(width * 0.95)    # Stop at 95% of the width (skip the right border)

        # Create the image ROI to focus on a specific area
        # (.copy() so that drawings on the full image don't appear in the ROI display)
        image_roi = cv_image[top_y:bottom_y, left_x:right_x].copy()

        # Conversion of the ROI to HSV colorspace
        hsv_image_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)

        # One mask per line color (inRange returns ONLY the mask)
        mask_yellow = cv2.inRange(hsv_image_roi, self.lower_yellow, self.upper_yellow)
        mask_blue = cv2.inRange(hsv_image_roi, self.lower_blue, self.upper_blue)

        # Draw the ROI boundaries in blue on the full image
        cv2.rectangle(cv_image, (left_x, top_y), (right_x - 1, bottom_y - 1), (255, 0, 0), 2)

        # Compute the image moments of each binary mask to find the centroid of its detected pixels:
        #   m00 = sum of pixel values (= 255 x number of white pixels, i.e. proportional to the area)
        #   m10 = sum of x * pixel value, m01 = sum of y * pixel value
        # Centroid: cx = m10 / m00, cy = m01 / m00  (in ROI coordinates)
        M_yellow = cv2.moments(mask_yellow)
        M_blue = cv2.moments(mask_blue)

        cx_yellow, cy_yellow, cx_blue, cy_blue = None, None, None, None

        # If yellow detected (coordinates converted from ROI to full image)
        if M_yellow['m00'] > 0:
            cx_yellow = int(M_yellow['m10'] / M_yellow['m00']) + left_x   # offset X
            cy_yellow = int(M_yellow['m01'] / M_yellow['m00']) + top_y    # offset Y
            cv2.circle(cv_image, (cx_yellow, cy_yellow), 5, (0, 255, 255), -1)  # yellow dot

        # If blue detected (coordinates converted from ROI to full image)
        if M_blue['m00'] > 0:
            cx_blue = int(M_blue['m10'] / M_blue['m00']) + left_x   # offset X
            cy_blue = int(M_blue['m01'] / M_blue['m00']) + top_y    # offset Y
            cv2.circle(cv_image, (cx_blue, cy_blue), 5, (255, 0, 0), -1)  # blue dot

        # Estimate the lane center (target point to follow)
        cx_combined, cy_combined = None, None
        if cx_yellow is not None and cx_blue is not None:
            # Both lines seen: combined barycentre (middle of yellow & blue)
            cx_combined = int((cx_yellow + cx_blue) / 2)
            cy_combined = int((cy_yellow + cy_blue) / 2)
            cv2.circle(cv_image, (cx_combined, cy_combined), 5, (0, 0, 255), -1)  # red dot (target)

            # PD Controller for following the lane
            # error = image center (robot axis) - target, in full-image coordinates (valid even with an asymmetric ROI)
            # error > 0: target on the left -> positive angular.z -> turn left (ROS convention)
            error = width / 2 - cx_combined
            command = KP * error
            self.twist.linear.x = LINEAR_VEL
            self.twist.angular.z = command
            self.cmd_vel_pub.publish(self.twist)
        else:
            # No line detected: stop the robot rather than keep the last command
            self.twist = Twist()
            self.cmd_vel_pub.publish(self.twist)

        # Display the ROI, the masks and the image with barycentres
        cv2.imshow("ROI", image_roi)
        cv2.imshow("Yellow Mask", mask_yellow)
        cv2.imshow("Blue Mask", mask_blue)
        cv2.imshow("Image with barycentres", cv_image)

        # Single waitKey: refreshes all windows + handles 'q' / Esc to quit
        key = cv2.waitKey(3) & 0xFF
        if key in (ord('q'), 27): # 'q' or Esc key
            self.get_logger().info('Close requested from display window.')
            self.quit_requested = True  # just raise the flag, no shutdown here


def main(args=None):
    # Disable rclpy's own Ctrl+C handler: otherwise the ROS context is shut down
    # immediately on Ctrl+C and the final zero-velocity command could not be published
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = ImageViewer()
    try:
        # Own spin loop: exits cleanly as soon as the flag is raised
        while rclpy.ok() and not node.quit_requested:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot before quitting (for 'q', Esc and Ctrl+C)
        if rclpy.ok():
            node.stop_robot()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # lets OpenCV actually process the window closing (Linux)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()