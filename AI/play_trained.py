from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper

from stable_baselines3 import PPO



#Settings
model_name = "my_trained_model"
sim_executable_path = "../Simulation executables/linux_x86_64/simulation-v0.1"
models_dir = "models/"



#create the simulation
env = UnityEnvironment(sim_executable_path, worker_id=0)
env = UnityToGymWrapper(env, allow_multiple_obs=True)


model = PPO.load(models_dir + model_name)


#run the model on the simulation
for j in range(500):
    obs = env.reset()
    dones = False
    while(not dones):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)