import os
import numpy as np
from typing import Callable

from mlagents_envs.environment import UnityEnvironment
from gym_unity.envs import UnityToGymWrapper

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv

from stable_baselines3 import PPO


from stable_baselines3 import SAC
from stable_baselines3.sac import MlpPolicy

from stable_baselines3.common import results_plotter
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.callbacks import BaseCallback



class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True


#from stable_baselines.common.policies import MlpPolicy

#unset PYTHONPATH in cmd
#export PYTHONPATH=/home/user/Desktop/DeepDriftingVENV/drift_env/lib/python3.7/site-packages

#def make_env(rank):
    #env = UnityEnvironment("/home/user/Desktop/unity_projects/DeepDrifting/build/FirstTest/FirstTest",side_channels=[channel], worker_id=rank)
    #env = UnityToGymWrapper(env, rank)
    #env = Monitor(env, log_dir)
    #return env

def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: Initial learning rate.
    :return: schedule that computes
      current learning rate depending on remaining progress
    """
    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining:
        :return: current learning rate
        """
        return progress_remaining * initial_value

    return func



#Settings
model_name = "my_trained_model"
sim_executable_path = "../Simulation executables/linux_x86_64 V2/simulation-v0.2"
sim_timescale = 4.0
n_parallel_sims = 4 # ~number of CPU cores
visualize_sim = True #if False, you can not watch the agent while it trains
learning_timesteps = 100000*30

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
    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="tb-logs/",n_steps=512, learning_rate=linear_schedule(0.0002), gamma=0.999, policy_kwargs=dict(net_arch=[64, 128, 265]))
    
    #you can instead also load a model and continue training it
    #model = PPO.load(model_name)
    #model.set_env(env)

    #begin learning
    callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)

    model.learn(total_timesteps=learning_timesteps, callback=callback)

    #save to disk
    model.save(models_dir + model_name)

