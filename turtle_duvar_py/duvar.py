import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class Duvar(Node):
    def __init__(self):
        super().__init__('duvar')
        self.declare_parameter('hiz', 1.5)
        self.declare_parameter('alt_sinir', 1.0)
        self.declare_parameter('ust_sinir', 10.0)
        self.declare_parameter('donus_hizi', 3.0)

        self.pose = None
        self.donuyor = False
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_cb, 10)
        self.timer = self.create_timer(1.0, self.log_cb)

    def pose_cb(self, msg):
        self.pose = msg
        hiz = self.get_parameter('hiz').value
        alt = self.get_parameter('alt_sinir').value
        ust = self.get_parameter('ust_sinir').value
        donus = self.get_parameter('donus_hizi').value

        disarida = (msg.x < alt or msg.x > ust or
                    msg.y < alt or msg.y > ust)

        # Merkeze bakan aci ile mevcut aci arasindaki hata
        merkez = (alt + ust) / 2.0
        hedef = math.atan2(merkez - msg.y, merkez - msg.x)
        hata = math.atan2(math.sin(hedef - msg.theta),
                          math.cos(hedef - msg.theta))

        if disarida:
            self.donuyor = True
        elif self.donuyor and abs(hata) < 0.3:
            self.donuyor = False

        cmd = Twist()
        cmd.linear.x = hiz
        if self.donuyor:
            cmd.angular.z = max(-donus, min(donus, 3.0 * hata))
        self.pub.publish(cmd)

    def log_cb(self):
        if self.pose is not None:
            self.get_logger().info(
                f'Konum: x={self.pose.x:.2f}, y={self.pose.y:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = Duvar()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
