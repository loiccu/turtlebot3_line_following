#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np


class ImageViewer(Node):
    def __init__(self):
        super().__init__('image_viewer')
        self.bridge = CvBridge()
        self.quit_requested = False

        self.image_sub = self.create_subscription(
            CompressedImage,
            '/image_raw/compressed',    # TODO: change topic name if required
            self.image_callback,
            qos_profile_sensor_data
        )

        # HSV boundaries (yellow line). OpenCV: H in [0,179], S,V in [0,255]
        self.lower_color = np.array([20, 100, 100])
        self.upper_color = np.array([35, 255, 255])

        self.get_logger().info('Image viewer node started. Waiting for images...')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Error in image conversion: {e}',
                                    throttle_duration_sec=2.0)
            return

        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Mask keeping only the pixels within the HSV range
        mask = cv2.inRange(hsv_image, self.lower_color, self.upper_color)

        # Compute the image moments of the binary mask to find the centroid of the detected pixels:
        #   m00 = sum of pixel values (= 255 x number of white pixels, i.e. proportional to the area)
        #   m10 = sum of x * pixel value, m01 = sum of y * pixel value
        # Centroid: cx = m10 / m00, cy = m01 / m00
        # (if several blobs are detected, this gives the center of all of them combined)
        M = cv2.moments(mask)
        if M['m00'] > 0:  # at least one pixel detected -> avoids division by zero# Using the moments() function to calculate the centroid or arithmetic center within the mask
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # Draw a red (0,0,255 in BGR color) circle at the center position
            cv2.circle(cv_image, (cx, cy), 10, (0, 0, 255), -1)

        # Display the mask (binary image) and the image with red dot
        cv2.imshow("mask", mask)
        cv2.imshow("image+dot", cv_image)

        # Single waitKey: refreshes all windows + handles 'q' / Esc to quit
        key = cv2.waitKey(3) & 0xFF
        if key in (ord('q'), 27):
            self.get_logger().info('Close requested from display window.')
            self.quit_requested = True


def main(args=None):
    rclpy.init(args=args)
    node = ImageViewer()
    try:
        while rclpy.ok() and not node.quit_requested:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()