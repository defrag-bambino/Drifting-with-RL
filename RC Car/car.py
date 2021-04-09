#import sys
#print(sys.path)
#sys.path.insert(0,'/opt/ros/kinetic/lib/python2.7/dist-packages')

import rospy
from utility import *
import configs
#from pyquaternion import Quaternion

from std_msgs.msg import Float64
from geometry_msgs.msg import PoseStamped, TwistStamped
from sensor_msgs.msg import Imu, Joy




class Car:
    def __init__(self):

        self.position = Vector2(0, 0)
        self.rotationInEulers = 0
        #self.rotationInQuat = Quaternion()

        self.globalVelocity = Vector2(0, 0)
        self.localVelocity = Vector2(0, 0)
        self.angularVelocityYAW = 0
        self.sideSlip = 0
        self._last_imu_timestamp = current_milli_time()

        self.throttle = 0 #-1 to 1
        self.steer = 0 #-1 to 1
        self.gamepad_speed = 0
        self.gamepad_steer = 0
        self.rpm = 0
        self.servo = 0
        self.dead_man_button_pressed = False



        self.pub_speed = rospy.Publisher(configs.CAR_THROTTLE_TOPIC, Float64, queue_size=10)
        self.pub_steer = rospy.Publisher(configs.CAR_STEER_TOPIC, Float64, queue_size=10)

        rospy.init_node("drift_car", anonymous=False)

        self.sub_gamepad_speed = rospy.Subscriber( (configs.CAR_THROTTLE_GAMEPAD_TOPIC) , Float64, self.receive_gamepad_speed_data)
        self.sub_gamepad_steer = rospy.Subscriber( (configs.CAR_STEER_GAMEPAD_TOPIC) , Float64, self.receive_gamepad_steer_data)
        rospy.Subscriber( (configs.CAR_POSITION_TOPIC) , PoseStamped, self.receive_pose_data)
        self.sub = rospy.Subscriber( (configs.CAR_VELOCITY_TOPIC) , TwistStamped, self.receive_velocity_data)
        rospy.Subscriber( (configs.CAR_RPM_TOPIC) , Float64, self.receive_rpm_data)#only for measuring the resulting rpm on the actual car (due to throttle_interpolator node)
        rospy.Subscriber( (configs.CAR_SERVO_TOPIC) , Float64, self.receive_servo_data)#only for measuring the resulting steering on the actual car (due to throttle_interpolator node)
        rospy.Subscriber( (configs.CAR_GAMEPAD_JOY_TOPIC), Joy, self.receive_joy_data)
        #rospy.Subscriber( (configs.CAR_IMU_TOPIC) , Imu, self.receive_imu_data)
        




    def receive_pose_data(self, data):
        self.position = Vector2(data.pose.position.x, data.pose.position.y)#assuming z-axis is up/down
        quat = data.pose.orientation
        #self.rotationInQuat = Quaternion(quat.w, 0, 0, quat.z)
        new_euls = quaternion_to_euler_angle(quat.w, 0, 0, quat.z) #this only returns yaw, we dont care about quat.x and quat.y, and qaut.z is negative because the cars z axis is facing down
        #if abs(abs(new_euls) - abs(self.rotationInEulers)) < 160 or self.rotationInEulers == 0:
        self.rotationInEulers = new_euls
        #else:
        #    print("rotation too fast", abs(new_euls), abs(self.rotationInEulers))
        #    pass
        #print(quat.w, quat.x, quat.y, quat.z)
        #print(self.rotationInEulers)

    def receive_rpm_data(self, data):
        self.rpm = data.data

    def receive_servo_data(self, data):
        self.servo = data.data

    def receive_joy_data(self, data):
        self.dead_man_button_pressed = (data.buttons[4] > 0)


    #def receive_imu_data(self, data):
        #self.angularVelocityYAW = data.angular_velocity.z

        #delta_time = (current_milli_time() - self._last_imu_timestamp) / 1000
        #self._last_imu_timestamp = current_milli_time()

        #locVelX = data.linear_acceleration.x
        #locVelY = data.linear_acceleration.y
        #self.localVelocity += Vector2(locVelX, locVelY) * delta_time #+=

        #self.sideSlip = calc_side_slip(self.localVelocity)
        #print(self.sideSlip)

    def receive_gamepad_steer_data(self, data):
        #override other control
        if self.dead_man_button_pressed:
            self.pub_steer.publish(data)

    def receive_gamepad_speed_data(self, data):
        #override other control
        if self.dead_man_button_pressed:
            self.pub_speed.publish(data)

    def receive_velocity_data(self, data):
        self.angularVelocityYAW = data.twist.angular.z
        self.globalVelocity = Vector2(data.twist.linear.x, data.twist.linear.y)#assuming z-axis is up/down
        #self.angularVelocity = -data.twist.angular.z
        self.localVelocity = globalDirectionToLocal(self.globalVelocity, self.rotationInEulers)
        self.sideSlip = calc_side_slip(self.localVelocity)

        #print("current sideslip: ", self.sideSlip)

    def set_throttle(self, new_throttle):
        #check for gamepad (override) input, if there is: dont use new input
        if self.dead_man_button_pressed:
            return

        self.throttle += new_throttle * 0.1
        self.throttle = sanity_clip_one_to_minus_one(new_throttle)
        self.pub_speed.publish(self.throttle * configs.CAR_MAX_RPM)
        #print("setting throttle: ", self.throttle* configs.CAR_MAX_RPM)

    def set_steer(self, new_steer):
        #check for gamepad (override) input, if there is: dont use new input
        if self.dead_man_button_pressed:
            return

        #experimental gyro steering aid
        if new_steer == 0.0:
                new_steer = self.angularVelocityYAW*30 #self.sideSlip / 180
                #print(self.angularVelocityYAW*100)
        new_steer = sanity_clip_one_to_minus_one(new_steer)
        self.steer = remap(new_steer, -1, 1, configs.CAR_STEER_MAX_LEFT, configs.CAR_STEER_MAX_RIGHT)
        self.pub_steer.publish(self.steer)
        #print("setting steer: ", self.steer)

            
    #def inverseTransformPoint(self, globalP):
        '''This transforms a given point (world coords) into a point relative to the car (local cords)'''

        #Vector3 sInv = new Vector3(1 / s.x, 1 / s.y, 1 / s.z);
        #quat_inv = self.rotationInQuat.inverse
        #localPointWithoutRot = (globalP - self.position)
        #locP = Quaternion(0, localPointWithoutRot.x, localPointWithoutRot.y, 0)
        #v = quat_inv * locP
        #tupleLocalP = quat_inv.rotate((localPointWithoutRot.x, localPointWithoutRot.y, 0)) # Returns a tuple
        #return Vector2(-tupleLocalP[1], -tupleLocalP[0])
        #return Vector2(-v[2], v[1])
