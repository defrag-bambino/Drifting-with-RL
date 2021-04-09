
from utility import *
import configs
import math
import codecs, json


def create_circle(radius=1, point_spacing=0.5):
    circumference = 2 * math.pi * radius
    waypointAmount = int(round(circumference / point_spacing))
    wps = []
    json_wps = []

    for i in range(waypointAmount):
        rad = math.radians(i * 360 / waypointAmount)
        wps.append(Vector2(math.sin(rad) * radius , math.cos(rad) * radius))
        #json_wps.append([math.sin(rad) * radius , math.cos(rad) * radius])
        #print(Vector2(math.sin(rad) * radius , math.cos(rad) * radius))

    #file_path = "wps_pos.json" 
    #json.dump(json_wps, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)

    return wps

def create_8():
    #lemniscate of bernoulli
    waypointAmount = 30
    wps = []

    for i in range(waypointAmount):
        rad = math.radians(i * 360 / waypointAmount)

        scale = 2 / (3 - math.cos(2*rad))
        x = scale * math.cos(rad) * 1.75
        y = scale * math.sin(2*rad) * 1.5

        wps.append(Vector2(y,x))
    
    return wps

class Path:
    def __init__(self):
        self.waypoints = create_8()#create_circle(radius=configs.CIRCLE_RADIUS, point_spacing=configs.WAYPOINT_SPACING)
        self.current_waypoint_idx = 0
        self.path_global_pos_offset = Vector2(0,0)#use this to move the path around

        self.orthgLineStart = None
        self.orthgLineEnd = None


    def evaluate(self, carPos):
        self.calc_orthg_line(self.get_waypoint_relative_to_current(-1), self.get_waypoint_relative_to_current(0), configs.ORTHG_LINE_HALF_LENGTH)
        #print(project_point_onto_line(Vector2(0.8,0.3), self.orthgLineStart, self.orthgLineEnd))
        #print(distance_point_to_line(Vector2(0.8,0.3), self.orthgLineStart, self.orthgLineEnd))

        eval = 0#distance to center of waypoint (when passed)
        if (distance_point_to_line(carPos, self.orthgLineStart, self.orthgLineEnd) < 0.1):
            eval = Vector2.distance(project_point_onto_line(carPos, self.orthgLineStart, self.orthgLineEnd), self.get_waypoint_relative_to_current(0))

            self.switchToNextWaypoint()

        return eval

    def switchToNextWaypoint(self):
        self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)
        #print("curr wp idx: ", self.current_waypoint_idx)

    def get_waypoint_relative_to_current(self, relative):
        idx = (self.current_waypoint_idx + relative) % len(self.waypoints)
        #print("getting wp idx: ", idx, )
        return self.waypoints[idx]

    def calc_orthg_line(self, start, end, half_length):
        directn = (end - start).normalize();
        orthg = Vector2.perpendicular(directn);

        self.orthgLineStart = end - ( half_length*orthg);
        self.orthgLineEnd = end + ( half_length*orthg);
