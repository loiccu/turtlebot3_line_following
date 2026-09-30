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

       # Define your ROI, for example, part of the lower half of the image
        height, width = cv_image.shape[:2]
        ## TODO: adapt the ROI corners to your need :
        top_y = int(height * 0.7)     # Start at 70% of the image height
        bottom_y = height             # Go to the bottom of the image
        left_x = int(width * 0.05)     # Start at 5% of the width (skip the left border)
        right_x = int(width * 0.95)    # Stop at 95% of the width (skip the right border)

        # Create the image ROI to focus on the close track (bottom of the image)
        # (.copy() so that drawings on the full image don't appear in the ROI display)
        image_roi = cv_image[top_y:bottom_y, left_x:right_x].copy()

        hsv_image_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)

        # Mask keeping only the ROI pixels within the HSV range
        mask_roi = cv2.inRange(hsv_image_roi, self.lower_color, self.upper_color)

        # Draw the ROI boundaries in blue on the full image
        cv2.rectangle(cv_image, (left_x, top_y), (right_x - 1, bottom_y - 1), (255, 0, 0), 2)

        # Compute the image moments of the binary ROI mask to find the centroid of the detected pixels:
        M = cv2.moments(mask_roi)
        if M['m00'] > 0:  # at least one pixel detected -> avoids division by zero
            # Centroid in ROI coordinates
            cx_roi = int(M['m10'] / M['m00'])
            cy_roi = int(M['m01'] / M['m00'])
            # Centroid in full-image coordinates
            cx = cx_roi + left_x
            cy = cy_roi + top_y
            # Draw a red (0,0,255 in BGR color) circle at the center position
            cv2.circle(cv_image, (cx, cy), 10, (0, 0, 255), -1)

        # Display the ROI, its mask (binary image) and the image with red dot
        cv2.imshow("ROI", image_roi)
        cv2.imshow("mask ROI", mask_roi)
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