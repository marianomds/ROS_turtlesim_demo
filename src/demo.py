#!/usr/bin/env python
import roslib; roslib.load_manifest('ros_turtlesim_demo')
import rospy
from geometry_msgs.msg  import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from math import pow,atan2,sqrt


# Star coordinates
points = ((4,2),(6.25,3.25),(9,2),(8.25,4.5),(10,6.25),(7.5,6.5),(6.25,9),(5.5,6.5),(3,6.25),(4.75,4.5),(4,2))

# Class from which the turtle object will be instanced
class turtlebot():

	# Initialization funcion
    def __init__(self):
    	# Create the velocity publisher
        self.velocity_publisher = rospy.Publisher('turtle1/cmd_vel', Twist, queue_size=10)

        # Create the position subscriber
        self.pose_subscriber = rospy.Subscriber('turtle1/pose', Pose, self.callback)
        self.pose = Pose()
        self.rate = rospy.Rate(10) # Refresh frequency [Hz]

    # Callback function formatting the pose value received
    def callback(self, data):
        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)

    # Calculate the linear (euclidean) distance to the goal point
    def get_linear_distance(self, goal_x, goal_y):
        distance = sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2))
        return distance

    # Calculate the angular distance to the goal point
    def get_angular_distance(self, goal_x, goal_y):
        distance = atan2(goal_y - self.pose.y, goal_x - self.pose.x) - self.pose.theta
        return distance

    # Move the turtle to the specified point 
    def move(self, point): # Receives a tuple with the point coordinates
    	# Format the point coordinates
        goal_pose = Pose()
        goal_pose.x = point[0]
        goal_pose.y = point[1]

        # Create the velocity vector atribute
        self.vel_msg = Twist()

        # Linear velocity only in the x-axis
        self.vel_msg.linear.y = 0
        self.vel_msg.linear.z = 0

        # Angular velocity only in the z-axis
        self.vel_msg.angular.x = 0
        self.vel_msg.angular.y = 0
        
        # The turtle will first rotate => linear velocity = 0
        self.vel_msg.linear.x = 0

        # The loop will remain until the angular distance starts to increase again
        prev_angular_distance = 100
        angular_distance = self.get_angular_distance(goal_pose.x, goal_pose.y)
        while abs(angular_distance) <= abs(prev_angular_distance) and abs(angular_distance) > 0.001:

            # Porportional Controller
            self.vel_msg.angular.z = 2 * angular_distance

            # Publish the velocity
            self.velocity_publisher.publish(self.vel_msg)
            self.rate.sleep()

            # Re-calculate the distance
            prev_angular_distance = angular_distance
            angular_distance = self.get_angular_distance(goal_pose.x, goal_pose.y)


        # The turtle will now translate => angular velocity = 0
        self.vel_msg.angular.z = 0

        # The loop will remain until the linear distance starts to increase again
        prev_linear_distance = 100
        linear_distance = self.get_linear_distance(goal_pose.x, goal_pose.y)
        while linear_distance <= prev_linear_distance and linear_distance != 0:

            # Porportional Controller
            self.vel_msg.linear.x = 5 * linear_distance 

            # Publish the velocity
            self.velocity_publisher.publish(self.vel_msg)
            self.rate.sleep()

            # Re-calculate the distance
            prev_linear_distance = linear_distance
            linear_distance = self.get_linear_distance(goal_pose.x, goal_pose.y)
        
        # Stop turtle
        self.vel_msg.linear.x = 0
        self.vel_msg.angular.z =0
        self.velocity_publisher.publish(self.vel_msg)


if __name__ == '__main__':
    try:
        # Initialize node
        rospy.init_node('turtlebot_figure', anonymous=True)

        # Clear the screen
        rospy.wait_for_service('clear')
        clear = rospy.ServiceProxy('clear', Empty)
        clear()

        # Instance a turtle objet       
        x = turtlebot()

        # Move the turtle object to each point
        for p in points:
            x.move(p)

    except rospy.ROSInterruptException: pass
