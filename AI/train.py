import os

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv

from stable_baselines3 import PPO


#Settings
model_name = "my_trained_model"
sim_executable_path = "../Simulation executables/linux_x86_64/simulation-v0.1"
sim_timescale = 4.0
n_parallel_sims = 4 # ~number of CPU cores
visualize_sim = True #if False, you can not watch the agent while it trains
learning_timesteps = 100000

log_dir = "logs/reward-logs/"
tb_logs = "logs/tb-logs/"
models_dir = "models/"



#this creates the parallel simulations
def make_unity_env(env_directory, num_env, render=True, visual=True, start_index=0):
    """
    Create a wrapped, monitored Unity environment.
    """
    def make_env(rank, use_visual=True): # pylint: disable=C0111
        def _thunk():
            unity_env = UnityEnvironment(env_directory, worker_id=rank, no_graphics=(not render), side_channels=[channel])
            env = UnityToGymWrapper(unity_env, rank)
            env = Monitor(env, (log_dir + "_agentNo" + str(rank)))
            return env
        return _thunk
    if visual:
        return SubprocVecEnv([make_env(i + start_index) for i in range(num_env)])
    else:
        rank = MPI.COMM_WORLD.Get_rank() if MPI else 0
        return DummyVecEnv([make_env(rank, use_visual=False)])




if __name__ == '__main__':
    channel = EngineConfigurationChannel()
    channel.set_configuration_parameters(time_scale = sim_timescale)

    # Create log dirs
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(tb_logs, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    #init and start simulation
    env = make_unity_env(sim_executable_path, n_parallel_sims, visualize_sim)

    #create the model
    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=tb_logs ,n_steps=512, learning_rate=0.0002, gamma=0.999, policy_kwargs=dict(net_arch=[128, 256, 128]))
    
    #you can instead also load a model and continue training it
    #model = PPO.load(model_name)
    #model.set_env(env)

    #begin learning
    model.learn(total_timesteps=learning_timesteps)

    #save to disk
    model.save(models_dir + model_name)

