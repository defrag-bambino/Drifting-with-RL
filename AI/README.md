# Python Scripts for training the Neural Network

## Prerequisites & Installation
+ Python 3 (I use a venv)
+ Packages: *mlagents==0.23*, *gym_unity==0.23* (see [ML Agents](https://github.com/Unity-Technologies/ml-agents/blob/release_12_docs/docs/Installation.md))
+ [Stable Baselines 3](https://github.com/DLR-RM/stable-baselines3) (You can use SB2 if you change a few minor things)


## Usage
To train, run `python3 train.py` and sit back. You might want to adapt some things within the script first though:
+ total_timesteps
+ model name
+ path to the simulation executable (especially if using your own)
+ various (hyper-)parameters like:
	- learning rate
	- Network Architecture (I get good results with a 128x265x128 Network)
	- the actual learning algorithm (I use PPO, have also tried SAC, but there are more (see stable baselines 3 doc))
	- timescale (you can speed up the simulation)
	- amount of parallel simulations to run (don't overdo it, I use as many as my CPU has cores (4))
	- whether or not you want to see the simulation during training, might improve performance when not having to render and display the sim

To run a trained model, execute `python3 play_trained.py` and enjoy! Make sure you select the correct model name and simulation executable path.

