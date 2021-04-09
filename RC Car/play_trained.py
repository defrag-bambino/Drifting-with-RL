import gym
import numpy as np
from lab_gym import LabEnv


#from stable_baselines.common.policies import MlpPolicy
#from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
from stable_baselines3 import SAC
#from stable_baselines3.common.evaluation import evaluate_policy
#import stable_baselines


env = LabEnv()


#modelName = "8_2x64"#/lab/current_model_new_tape
model = PPO.load("NetSmallToBig")#, env)

#model = SAC.load("model_result_SAC")
#model.policy.load("model_result_SAC" + "_policy.pkl")


# Evaluate the agent
#mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
#print("REWARD: mean: " + str(mean_reward) + " , std: " + str(std_reward))

for j in range(500):
    obs = env.reset()
    dones = False
    while(not dones):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
