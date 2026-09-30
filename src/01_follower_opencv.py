#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2


class ImageViewer(Node):
    def __init__(self):
        super().__init__('image_viewer')
        self.bridge = CvBridge()
        self.quit_requested = False  # set to True when 'q' / Esc is pressed

        # Subscription to the compressed image topic
        self.image_sub = self.create_subscription(
            CompressedImage,
            '/image_raw/compressed',    # TODO: change topic name if required
            self.image_callback,
            qos_profile_sensor_data
        )
        self.get_logger().info('Image viewer node started. Waiting for images...')

    def image_callback(self, msg):
        # Conversion of ROS CompressedImage msg into an OpenCV image (BGR)
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Error in image conversion: {e}',
                                    throttle_duration_sec=2.0)
            return

        # Image display
        cv2.imshow("Camera stream ROS2", cv_image)

        # 'q' or Esc to quit (the OpenCV window must have focus)
        key = cv2.waitKey(1) & 0xFF #  Update image display and wait 1ms (1) for a pressed key  
        if key in (ord('q'), 27): # 'q' or Esc key 
            self.get_logger().info('Close requested from display window.')
            self.quit_requested = True  # just raise the flag, no shutdown here


def main(args=None):
    rclpy.init(args=args)
    node = ImageViewer()
    try:
        # Own spin loop: exits cleanly as soon as the flag is raised
        while rclpy.ok() and not node.quit_requested:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # lets OpenCV actually close the window (Linux)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()