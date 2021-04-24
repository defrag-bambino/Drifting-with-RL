# Ready-to-run executable files of the simulation.
(currently only for linux 64bit systems)

They can be run on their own, but don't really do much.
They are used by the AI to train in. See REF_TO_AI_FOLDER.


Most important changes in V2:
- Changed the reward function such that a reward is given continiously, rather than only when a waypoint is passed. Feel free to play around with this yourself. I found it results in smoother training progress, as this is easier for the optimization algorithm.
- Played around with the vehicle parameters. Such as tire friction, center of mass, steering speed, max RPM. I tried to get the simulated car's behavior as close to our RC car as possible. Feel free to adjust these according to your needs.
- Added a visual indication of the momentary reward, which is displayed as the car passes a waypoint. This is just a text object that always faces the camera and its color is linearly interpolated from 0 (yellow) to 100 (green), for easier understanding.


CircleNoWPs:
This is a very simple setup. There are no waypoints and no fancy measurements. Local velocities XY, yaw angle and slipangle for input and steering as output, throttle is locked in. Similar to MIT's autonomous drifting video.
