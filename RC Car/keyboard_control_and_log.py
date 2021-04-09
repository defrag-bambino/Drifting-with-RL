import gym
import numpy as np
#import keyboard
from lab_gym import LabEnv

#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')


#start the simulation
env = LabEnv()
#env.reset()


#this will handle keyboard input
def human_control(_obs):

    servo=0
    throttle=-1

    #if keyboard.is_pressed('d'):
      #servo = 1.0
    #if keyboard.is_pressed('a'):
      #servo = -1.0
    #if keyboard.is_pressed("w"):
      #throttle=1.0
    #if keyboard.is_pressed("s"):
      #throttle=-1.0

    #print(servo, throttle)

    return np.array([servo, throttle])



obs_over_time = []


for j in range(1):
    obs = env.reset()
    dones = False
    while(not dones):
        action = human_control(obs)
        obs, rewards, dones, info = env.step(action)
        
        #log observations
        obs_over_time.append(obs)
print("keyboard control done...")

#save obsv. to file
obs_as_np = np.asarray(obs_over_time)
np.savetxt('obs_data_rc.txt', obs_as_np, fmt='%f')
