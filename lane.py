from dataclasses import dataclass, field
from typing import Optional

import driver
import objects
from objects import GlobalObjectList
from generator import Generator
from road import Road
from constants import LaneDirection, LINE_WIDTH, LINE_COLOR
from collision_detector import Detector
from visuals import Visual
from signal import TrafficLight, StopSign
from typing import Optional

class SanityError(Exception):
    pass

class Lane:
    def __init__(self,
                 lane_num: int,
                 my_road: Road,
                 width: float,
                 global_objects: GlobalObjectList,
                 generator: Generator,
                 flow_direction: LaneDirection,
                 objects_in_lane: list = [],
                 traffic_light: Optional[TrafficLight] = None):
        """ objects is the global list of objects """
        # the global object list
        self.road = my_road
        self.width = width
        self.objects = global_objects
        self.generator = generator
        self.direction = flow_direction
        self.lane_num = lane_num
        # a list of object identifiers
        self.objects_in_lane = objects_in_lane
        self.traffic_light = traffic_light

    def add(self, driver_id: int):
        """ add an object from the global objects list """
        self.objects_in_lane.append(driver_id)
        return self

    def get_angle(self):
        if self.direction == LaneDirection.FORWARD:
            return self.road.get_direction()
        else:
            return (self.road.get_direction() + 180) % 360

    def get_speed_limit(self):
        return self.road.get_speed_limit()


    def get_position(self, fraction: float):
        """ Return the position of this lane a fraction of a length down the road
         0 = beginning, 1 = end
        """
        road_length = self.road.get_length()
        x = road_length*fraction-road_length/2
        lanes = self.objects.get_lanes_by_road(self.road)
        road_width = 0
        my_center = 0

        for lane in lanes:
            road_width += lane.width
            if self.lane_num < lane.lane_num:
                my_center += lane.width

        my_center += self.width/2
        y = my_center - road_width/2
        if self.direction == LaneDirection.BACKWARD:
            y = -y
            x = -x
        if self.road.get_direction() == 90:
            return y, x
        elif self.road.get_direction() == 0:
            return x, y
        else:
            raise SanityError('BETA version, remember?')


    def get_objects(self) -> list:
        """ return a list of objects in the lane """
        return list(self)

    def __iter__(self) -> driver.Driver:
        for obj in self.objects_in_lane:
            yield self.objects[obj]

    def remove(self, obj: int):
        """ removes the given object id from the lane """
        if obj in self.objects_in_lane:
            self.objects_in_lane.remove(obj)
        return self

    def detect_end(self):
        begin_x, begin_y = self.get_position(0.0)
        end_x, end_y = self.get_position(1.0)
        finished = []

        max_x = max(begin_x, end_x)
        max_y = max(begin_y, end_y)
        min_x = min(begin_x, end_x)
        min_y = min(begin_y, end_y)

        for obj_id in self.objects_in_lane:
            obj = self.objects[obj_id]
            x = obj.my_vehicle.x
            y = obj.my_vehicle.y
            length = self.road.get_length()
            if (x > length/2
            or y > length/2):
                finished.append(obj_id)
        return finished

    def draw(self):
        drawings = []
        edge_0_right_x, edge_0_right_y = self.get_position(0)
        edge_1_left_x, edge_1_left_y = self.get_position(1)
        edge_1_right_x, edge_1_right_y = self.get_position(1)
        edge_0_left_x, edge_0_left_y = self.get_position(0)
        if self.road.get_direction() % 180 == 90:
            edge_0_left_x -= self.width/2
            edge_1_left_x -= self.width/2
            edge_0_right_x += self.width/2
            edge_1_right_x += self.width/2
        else:
            edge_0_left_y -= self.width/2
            edge_1_left_y -= self.width/2
            edge_0_right_y += self.width/2
            edge_1_right_y += self.width/2
        drawings += [Visual(LINE_COLOR, [(edge_0_left_x, edge_0_left_y), (edge_1_left_x, edge_1_left_y), (edge_1_left_x, edge_1_left_y), (edge_0_left_x, edge_0_left_y+1)]),
                  Visual(LINE_COLOR, [(edge_0_right_x, edge_0_right_y), (edge_1_right_x, edge_1_right_y), (edge_1_right_x, edge_1_right_y), (edge_0_right_x, edge_0_right_y)])]
        return drawings

    def update(self, the_time):
        if not self.traffic_light:
            pass
        road_num = self.objects.get_road_num(self.road)
        green_time = self.road.get_green_time(road_num)
        if the_time % green_time == 0:
            self.traffic_light.change_color(the_time)
        if self.traffic_light.yellow_time == the_time:
            self.traffic_light.change_color(the_time)


