# Unity Project file(s)

## Usage
Import the **DeepDrifting** folder as a Project into Unity. Open the "SampleScene", if not already open.
Play around with the settings and adapt the simulation to your liking.
Hit *build* to create an executable(REF_TO_EXECUTABLES_FOLDER) or train your AI directly in the editor (See ML Agents Documentation).
(new_rew_func is highly experimental and does not work currently)


## Advanced use
If you know what you're doing, you can change anything you'd like.
However, I personally only play around with the following:
+ Add a new trajectory! The (under VPP Sport Coupe Object -> Drift Agent (Script)) you can add/remove trajectories that will be randomly selected.
	- Create a new trajectory by duplicating one of the existing prefabs.
	- Double click your new prefab and edit the path. See *PathCreator/Documentation/PDF*.
	- Add your new trajectory to the list by pressing "+" and drag it in.
+ Play around with the *DriftAgent* parameters (located on the VPP Sport Coupe Object -> Drift Agent (Script)), for example:
	- amount of waypoints the Agent can see (adapt the Behavior Parameters' observation space size accordingly)
	- maximum allowed distance from the desired path
	- steering speed
	- add and tweak your own settings!
+ Modify the *DriftAgent.cs* script itself. You could change the reward function or even the inputs and outputs of the Agent (adapt the Behavior Parameters accordingly).
+ Change the vehicle's settings. On the VPP Sport Coupe Object edit the Vehicle Controller component. You could change:
	- friction of the tires
	- maximum RPM
	- maximum steering angle
	- anything you want, really. I don't know much about cars, so I just leave most of it as is.
	- color of the car?

*Notice that since this is using only the free version of Edys Vehicle Phsysics, we cannot have multiple cars in one scene.*



## Used Packages & (minimum tested) Versions
+ Unity 2020.2.0f1 & 2020.3.1.f1 (should be fine with higher versions)
	- [ML Agents](https://github.com/Unity-Technologies/ml-agents/blob/release_12_docs/docs/Installation.md) Package *(com.unity.ml-agents)* 1.7.2
	- Edys Vehicle Physics (from late 2020)
	- PathCreator (from early 2021)
