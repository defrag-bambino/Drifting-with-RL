
import numpy as np

from gym import Env
from gym.spaces import Box

from car import Car
from path import Path
#import visualizer
from driftVisTest import DriftDataLiveVisualizer

from utility import *
import time
#import keyboard
from inputs import get_key, get_gamepad
import configs

#from pyquaternion import Quaternion
#import codecs, json


current_milli_time = lambda: int(round(time.time() * 1000))

c_pos = []
c_slipangle = []
c_throttle = []
c_rpm = []
c_currSteer = []
c_pathDist = []

curr_thr_command = 0;


class LabEnv(Env):
    N_OBSERVATIONS = 16
    N_ACTIONS = 2


    def __init__(self):
        super(LabEnv,self).__init__()

        #action space
        high = np.array([1] * self.N_ACTIONS)
        self.action_space = Box(low= -high, high= high,dtype=np.float32)

        #observation space
        high = np.array([np.inf] * self.N_OBSERVATIONS)
        self.observation_space = Box(low= -high, high=high,dtype=np.float32)

        self.ep_length = configs.EPISODE_LENGTH

        self.last_step_time = current_milli_time()
        self.drift_car = Car()

        #visualizer.init()
        #A BROWSERWINDOW NEEDS TO BE OPEN TO ALLOW THIS VISUALIZER TO OPEN NEW TAB, otherwise: nvrm: error
        self.live_visualizer = DriftDataLiveVisualizer([0, 0, 0, 0, 0, 0], [0, 0], np.array([[0], [0]]), [0, 0, 0], np.array([[0], [0]]), [Vector2(0,0), Vector2(0,0)])
        print("Initializing lab env gym...")

    def reset(self):
        self.current_step = 0
        self.path = Path()
        self.path.evaluate(self.drift_car.position)

        print('\nRESETTING: please move the car to its starting position, then press: BLUE (X)')
        self.drift_car.set_steer(0)
        self.drift_car.set_throttle(0)
        
        waiting = True
        while waiting:
            self.render(mode="human")
            #gamepad input, if available
            events = get_gamepad()# + get_key()
            if events:
                for event in events:
                    if event.code == 'KEY_SPACE' or (event.code == 'BTN_SOUTH' and event.state == 1):
                        waiting = False
                        print("resetting complete!")

        obs = self._get_observations()
        #self.drift_car.rotaionInEulers = 0
        return obs

    def step(self, action):
        while current_milli_time() < self.last_step_time + (1000 / configs.DECISIONS_PER_SECOND):
            pass
        self.last_step_time = current_milli_time()
        
        self.current_step += 1
        #print("step: ",self.current_step)
        done = self.current_step >= self.ep_length

        
        #take the action
        #if action[1] > 0:
        self.drift_car.set_throttle(1 * remap(action[1], -1.0, 1.0, 0.0, 1.0))
        #curr_thr_command = action[1]
        self.drift_car.set_steer(action[0])

        dist_curr_wp_passed = self.path.evaluate(self.drift_car.position)
        reward = self._calc_reward(dist_curr_wp_passed, self.drift_car.sideSlip)
        #print(reward)
        obs = self._get_observations()

        
        #dist_to_path = distance_point_to_line(self.drift_car.position,self.path.get_waypoint_relative_to_current(-1) , self.path.get_waypoint_relative_to_current(0))
        #print(dist_to_path)
        #if dist_to_path > configs.WAYPOINT_SPACING * 1.0:
        #print(self.drift_car.position)
        #print(self.drift_car.rotationInEulers)
        #if Vector2.get_length(self.drift_car.position) > 1.8:
            #done = True #end when too far from target waypoint
            #print("resetting...")
            #self.drift_car.set_throttle(0)
            #self.reset()

        self.render()
        return obs, reward, done, {}

    def render(self, mode='human'):
        #visualizer.visualize(car_pos=self.drift_car.position, car_rot=self.drift_car.rotationInEulers, waypoints=self.path.waypoints, current_waypoint_index=self.path.current_waypoint_idx, curr_waypt_line_start=self.path.orthgLineStart, curr_waypt_line_end=self.path.orthgLineEnd)
        #collect data
        pos_and_rot = [self.drift_car.position.x, self.drift_car.position.y, np.deg2rad(self.drift_car.rotationInEulers)]
        wpsX = []
        wpsY = []
        for wp in self.path.waypoints:
            wpsX.append(wp.x)
            wpsY.append(wp.y)
        wps_all = np.array([wpsX, wpsY])

        wpsX = []
        wpsY = []
        for i in range(configs.NEXT_KNOWN_WAYPOINTS):
            wp = self.path.get_waypoint_relative_to_current(i)
            wpsX.append(wp.x)
            wpsY.append(wp.y)
        wps_seen = np.array([wpsX, wpsY])

        #update the liveplot
        self.live_visualizer.update_car_posWP_data(wps_all, pos_and_rot, wps_seen, [self.path.orthgLineStart, self.path.orthgLineEnd])
        self.live_visualizer.update_car_measurement_data([self.drift_car.localVelocity.x, self.drift_car.localVelocity.y, self.drift_car.angularVelocityYAW, self.drift_car.sideSlip, self.drift_car.rpm, self.drift_car.servo])
        self.live_visualizer.update_car_action_data([self.drift_car.steer, self.drift_car.throttle])
    
    def _get_observations(self):
        #collect observations
        observations = []
        observations.append(self.drift_car.localVelocity.y / 36)
        observations.append(self.drift_car.localVelocity.x / 36)
        if abs(self.drift_car.angularVelocityYAW * 5) > 1:
             self.drift_car.angularVelocityYAW = 0
        observations.append(self.drift_car.angularVelocityYAW * 5*1.6)
        observations.append((-self.drift_car.sideSlip / 180)*2.6)
	
       # print(globalPointToLocal(self.drift_car.position, self.path.get_waypoint_relative_to_current(0), self.drift_car.rotationInEulers))

        max_wp_dist = configs.WAYPOINT_SPACING * configs.NEXT_KNOWN_WAYPOINTS
        for i in range(configs.NEXT_KNOWN_WAYPOINTS):
            ##angle = self.drift_car.rotationInEulers + 90
            ##if angle < -180:
            #    angle += 360
            #elif angle > 180
            #    angle -= 360
            wp = globalPointToLocal(self.drift_car.position, self.path.get_waypoint_relative_to_current(i), self.drift_car.rotationInEulers)
            #wp = self.drift_car.inverseTransformPoint(self.path.get_waypoint_relative_to_current(i))
            observations.append(wp.x / max_wp_dist)
            observations.append(wp.y / max_wp_dist)
            #print(wp.x, wp.y, self.drift_car.rotationInEulers, self.drift_car.rotationInQuat)

        #print("-----obs----")

        observations.append(self.drift_car.rpm/23000)
        observations.append(self.drift_car.servo)

        #observations.append(Vector2.distance(self.drift_car.position, self.path.get_waypoint_relative_to_current(0)) / 10)

        #print(observations, '\n\n')

        #write_obs_to_json()

        return np.asarray(observations)

    # def _write_obs_to_json(self):
    #     c_pos.append([self.drift_car.position.x, self.drift_car.position.y])
    #     file_path = "pos.json" 
    #     json.dump(c_pos, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)


    #     c_slipangle.append([self.drift_car.sideSlip])
    #     file_path = "sideslip.json" 
    #     json.dump(c_slipangle, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)


    #     c_rpm.append([self.drift_car.throttle])
    #     file_path = "rpm.json" 
    #     json.dump(c_rpm, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)


    #     c_throttle.append([curr_thr_command])
    #     file_path = "throttle.json" 
    #     json.dump(c_throttle, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)


    #     c_currSteer.append([self.drift_car.steer])
    #     file_path = "steer.json" 
    #     json.dump(c_currSteer, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)


    #     c_pathDist.append([distance_point_to_line(self.drift_car.position,self.path.get_waypoint_relative_to_current(-1) , self.path.get_waypoint_relative_to_current(0))])
    #     file_path = "pathDist.json" 
    #     json.dump(c_pathDist, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

    #     #waypoint positions are being written to json file in path.py

    #     return

    def _calc_reward(self, dist_to_center_when_wp_passed, slipAngle):
        if dist_to_center_when_wp_passed <= 0:
            return 0

        center_dist_part_rewrd = np.exp(-3 * (np.power(dist_to_center_when_wp_passed, 2)/(np.power(configs.ORTHG_LINE_HALF_LENGTH, 2)))) * configs.DIST_TO_WP_CENTER_IMPORTANCE_FACTOR
        slip_angle_part_reward = 0        

        desiredAngleSign = Point_Left_Or_Right_From_Line(self.path.get_waypoint_relative_to_current(-1), self.path.get_waypoint_relative_to_current(1), self.path.get_waypoint_relative_to_current(0))
        currentAngleSign = np.sign(slipAngle)  
        if(abs(slipAngle) < 100 and (abs(slipAngle) > 10) or desiredAngleSign == 0):
            PathCurvatureFactor = 1
                #if(desiredAngleSign != 0 && desiredAngleSign == currentAngleSign) PathCurvatureFactor = 1f;//print("desired");
            if(desiredAngleSign != 0 and desiredAngleSign != currentAngleSign):
                PathCurvatureFactor = 0 #//print("not desired");
                #else PathCurvatureFactor = 1f;//print("dont care");
            slip_angle_part_reward = (abs(slipAngle) / 100) * configs.SLIP_ANGLE_IMPORTANCE_FACTOR * PathCurvatureFactor

        #print("center_dist_part_rewrd: ", center_dist_part_rewrd)
        #print("slip_angle_part_reward: ", slip_angle_part_reward)
        #print("reward: ", (center_dist_part_rewrd + slip_angle_part_reward))
        return (center_dist_part_rewrd + slip_angle_part_reward)


