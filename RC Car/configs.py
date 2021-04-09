
#f1tenth
CAR_NAME = "DriftCar2"
CAR_MAX_RPM = 25000
CAR_STEER_MAX_LEFT = 0.015
CAR_STEER_MAX_RIGHT = 0.985

#waypoints (path)
WAYPOINT_SPACING = 0.5
CIRCLE_RADIUS = 1
ORTHG_LINE_HALF_LENGTH = 1.2

#ROS
CAR_STEER_TOPIC = "/vesc/commands/servo/unsmoothed_position" #"/vesc/commands/servo/position"
CAR_THROTTLE_TOPIC = "/vesc/commands/motor/unsmoothed_speed"#"/vesc/commands/motor/speed"
CAR_POSITION_TOPIC = "/vrpn_client_node/" + CAR_NAME + "/pose"
CAR_VELOCITY_TOPIC = "/vrpn_client_node/" + CAR_NAME + "/twist"
CAR_IMU_TOPIC = "/imu"
CAR_STEER_GAMEPAD_TOPIC = "/vesc/commands/servo/unsmoothed_position2"
CAR_THROTTLE_GAMEPAD_TOPIC = "/vesc/commands/motor/unsmoothed_speed2"
CAR_RPM_TOPIC = "/vesc/commands/motor/speed"
CAR_SERVO_TOPIC = "/vesc/commands/servo/position"
CAR_GAMEPAD_JOY_TOPIC = "/vesc/joy"

#training
#PRETRAINING_EPISODES = 6
EPISODE_LENGTH = 500
NEXT_KNOWN_WAYPOINTS = 5
DECISIONS_PER_SECOND = 10

#reward
DIST_TO_WP_CENTER_IMPORTANCE_FACTOR = 1/16
SLIP_ANGLE_IMPORTANCE_FACTOR = 1 - DIST_TO_WP_CENTER_IMPORTANCE_FACTOR # = 15/16v
