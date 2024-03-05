import logging
from dataclasses import dataclass
from random import randint, random
from typing import Optional
from visuals import Visual
from constants import LaneDirection, ROUNDING, SAFE_GAP_IN_SECONDS, DRIVER_COLOR
from utils import cal_distance, quadratic_equation, split_vector, dot
from vehicle import Vehicle
import sys
from math import pow, sqrt, fabs
from objects import GlobalObjectList


@dataclass
class Quality:
    """ Behavior """
    # how far above the speed limit the self wants to go
    speeding: float = 1.0
    # how many fractions of safe gap distance to keep
    following_distance: float = 1.0
    # chance I look every time step (1 = always attentive, 0 = never)
    attentiveness: float = 1.0

    def __repr__(self):
        return f'Quality: speeding={self.speeding}, following_distance={self.following_distance}, attentiveness={self.attentiveness}'


class Driver:
    def __init__(self,
                 object_id: int,
                 my_vehicle: Vehicle,
                 visibility: float,
                 destination: tuple[float, float],
                 quality: Quality):
        """
        object_id = this self's identifier
        my_vehicle = the vehicle being driven
        visibility = max distance to look ahead (meters)
        destination = x, y endpoint
        quality = behavior
        """
        self.my_vehicle = my_vehicle
        self.visibility = visibility
        self.destination = destination
        self.quality = quality
        self.object_id = object_id

    def look(self, objects: GlobalObjectList):
        occupied = []
        for driver in objects.values():
            if driver is not self:
                distance = fabs(sqrt(
                    pow((driver.my_vehicle.x - self.my_vehicle.x), 2) + pow((driver.my_vehicle.y - self.my_vehicle.y),
                                                                            2)))
                rear_x, rear_y = driver.my_vehicle.get_rear()
                distance_to_back = fabs(
                    (sqrt(pow((rear_x - self.my_vehicle.x), 2) + pow((rear_y - self.my_vehicle.y), 2))))
                if distance <= self.visibility or distance_to_back <= self.visibility:
                    occupied.append(driver)
        return occupied

    def get_closest(self, driver):
        my_front_x, my_front_y = self.my_vehicle.x, self.my_vehicle.y
        my_rear_x, my_rear_y = self.my_vehicle.get_rear()

        his_front_x, his_front_y = driver.my_vehicle.x, driver.my_vehicle.y
        his_rear_x, his_rear_y = driver.my_vehicle.get_rear()

        return (
            min([(my_front_x, my_front_y, his_front_x, his_front_y),
                 (my_front_x, my_front_y, his_rear_x, his_rear_y),
                 (my_rear_x, my_rear_y, his_rear_x, his_rear_y),
                 (my_rear_x, my_rear_y, his_front_x, his_front_y)],
                key=cal_distance))
  
    def get_safe_following_distance(self):
        return SAFE_GAP_IN_SECONDS * abs(self.my_vehicle.speed) * self.quality.following_distance

    def _get_desired_acceleration_change(self, road_limit: float, timestep_length: float):
        """ gets to my desired acceleration change """
        max_possible_speed = self.get_max_possible_speed(road_limit)
        return (max_possible_speed - self.my_vehicle.speed) / timestep_length - self.my_vehicle.acceleration

    def _to_intercept(self, driver) -> tuple[Optional[float], float]:
        """ Gets the minimum time to intercept another driver and the distance to intercept.
         1 solution: time to intercept, distance.
         None, distance: Never crashes"""
        my_speed_x, my_speed_y = split_vector(self.my_vehicle.speed, self.my_vehicle.angle)
        my_acceleration_x, my_acceleration_y = split_vector(self.my_vehicle.acceleration, self.my_vehicle.angle)

        his_speed_x, his_speed_y = split_vector(driver.my_vehicle.speed, driver.my_vehicle.angle)
        his_acceleration_x, his_acceleration_y = split_vector(driver.my_vehicle.acceleration, driver.my_vehicle.angle)

        his_speed_in_direction_of_my_speed = dot(his_speed_x, his_speed_y, my_speed_x, my_speed_y)
        his_acceleration_in_direction_of_my_acceleration = dot(his_acceleration_x, his_acceleration_y,
                                                               my_acceleration_x, my_acceleration_y)

        my_closest_x, my_closest_y, their_closest_x, their_closest_y = self.get_closest(driver)
        distance_in_direction_of_my_speed = dot(their_closest_x - my_closest_x,
                                                their_closest_y - my_closest_y,
                                                my_speed_x, my_speed_y)

        time_to_intercept = quadratic_equation(0.5 * (
                                                      his_acceleration_in_direction_of_my_acceleration - self.my_vehicle.acceleration),
                                              his_speed_in_direction_of_my_speed - self.my_vehicle.speed,
                                              distance_in_direction_of_my_speed)

        if not time_to_intercept:
            return None, distance_in_direction_of_my_speed
        return min(time_to_intercept), distance_in_direction_of_my_speed

    def _adjust_acceleration_for_other_driver(self, driver):
        # try to find how much we need to slow down in order not to crash with this self
        # I need to check whether I am getting too close to the car in front of me
        safe_following_distance = self.get_safe_following_distance()
        my_speed_x, my_speed_y = split_vector(self.my_vehicle.speed, self.my_vehicle.angle)

        my_closest_x, my_closest_y, his_closest_x, his_closest_y = self.get_closest(driver)

        distance_x, distance_y = his_closest_x - my_closest_x, his_closest_y - my_closest_y
        distance_in_direction_of_my_speed = dot(distance_x, distance_y, my_speed_x, my_speed_y)

        if distance_in_direction_of_my_speed <= 0:
            return None

        min_time_to_be_safe, distance_to_intercept = self._to_intercept(driver)
        if min_time_to_be_safe is None:
            # if these will never impact, they make no changes in the plan
            return None

        their_new_speed = max(driver.my_vehicle.speed + driver.my_vehicle.acceleration * min_time_to_be_safe, 0)
        if ((min_time_to_be_safe <= SAFE_GAP_IN_SECONDS * self.quality.following_distance)
                or distance_to_intercept < safe_following_distance):
            your_final_speed = 0
        else:
            your_final_speed = their_new_speed

        speed_diff = your_final_speed - self.my_vehicle.speed
        if min_time_to_be_safe == 0:
            new_accel = -self.my_vehicle.max_acceleration
        else:
            new_accel = speed_diff / fabs(min_time_to_be_safe)
        accel_change = new_accel - self.my_vehicle.acceleration
        return accel_change

    def _get_direction_x_or_y(self):
        if self.my_vehicle.angle % 180 == 90:
            direction = 'y'
        else:
            direction = 'x'
        return direction

    def _check_whether_perpendicular(self, driver):
        my_direction = self._get_direction_x_or_y()
        their_direction = driver._get_direction_x_or_y()
        return my_direction != their_direction


    def _check_when_vehicle_hits_a_location_in_d(self, space, d: str) -> Optional[float]:
        """ space=spot in x or y that you want to find the time to
         d=x or y dimension"""
        if d == "x":
            loc0 = self.my_vehicle.x
        elif d == "y":
            loc0 = self.my_vehicle.y
        else:
            logging.error('Direction inputted is not x or y for _check_when_vehicle_hits_a_location_in_d()')
        time_to_intercepts = quadratic_equation(0.5 * self.my_vehicle.acceleration, self.my_vehicle.speed, loc0 - space)
        time_to_intercepts = list(time_to_intercepts)
        for t in time_to_intercepts:
            if t < 0:
                time_to_intercepts.remove(t)
        if not time_to_intercepts:
            return None
        else:
            return time_to_intercepts[0]

    def _calc_needed_accel_change(self, time_to_intercept_bubble, distance):
        """get the needed acceleration_change to not hit bubble"""
        distance_to_bubble = distance - self.get_safe_following_distance()
        if time_to_intercept_bubble is None:
            # They will never crash, so you don't need to change the acceleration
            return 0
        try:
            required_speed = distance_to_bubble / time_to_intercept_bubble
        except ZeroDivisionError:
            required_speed = 0
        speed_diff = required_speed - self.my_vehicle.speed
        try:
            needed_accel = speed_diff / time_to_intercept_bubble
        except ZeroDivisionError:
            needed_accel = -self.my_vehicle.max_acceleration
        accel_change = needed_accel - self.my_vehicle.acceleration
        return accel_change

    def plan(self, visible_objects, road_limit, timestep_length):
        # the default will be trying to get to my desired acceleration
        changes = [self._get_desired_acceleration_change(road_limit, timestep_length)]
        my_x = self.my_vehicle.x
        my_y = self.my_vehicle.y
        for driver in visible_objects:
            their_x = driver.my_vehicle.x
            their_y = driver.my_vehicle.y
            # Check if the driver is perpendicular to you
            if self._check_whether_perpendicular(driver):
                distance_to_bubble = abs(self.my_vehicle.x)-self.get_safe_following_distance()
                when_intercept = self._to_intercept(driver)
                accel_change = self._calc_needed_accel_change(when_intercept, distance_to_bubble)
            else:
                accel_change = self._adjust_acceleration_for_other_driver(driver)
            if accel_change:
                changes.append(accel_change)
        changes = min(changes + [self.my_vehicle.max_acceleration])
        return changes

    def get_needed_angle_change(self):
        """ plan weather to turn or not """
        needed_angle_change = 0
        if self.destination[1] < self.my_vehicle.y or self.destination[0] < self.my_vehicle.x:
            needed_angle_change = 90
        elif self.destination[1] > self.my_vehicle.y or self.destination[0] > self.my_vehicle.x:
            needed_angle_change = 270
        return needed_angle_change

    def check_for_needed_lanes(self, lanes, direction):
        """ Check which lanes go in direction that is the same as the one the self wants to go in.
        Direction is an angle of 0, 90, 180, 270"""
        good_lanes = []

        for lane in lanes:
            if ((lane.get_angle() == direction)
                    or (lane.get_angle() == direction)
                    or (lane.get_angle() == direction)
                    or (lane.get_angle() == direction)):
                good_lanes.append(lane)
        return good_lanes

        # take your (x, y), advance it by min_time_to_impact
        # take their (x, y), advance it by min_time_to_impact

    def should_plan(self):
        return random() <= self.quality.attentiveness

    def get_max_possible_speed(self, road_max: float):
        """ returns the maximum speed a driver would be willing to go """
        vehicle_max = self.my_vehicle.max_speed
        return self.calc_max_possible_speed(road_max, vehicle_max, self.quality.speeding)

    @classmethod
    def calc_max_possible_speed(cls, road_max: float, vehicle_max: float, speeding: float):
        driver_max = road_max * speeding
        speed = min(vehicle_max, driver_max)
        return speed

    def accelerate(self, change):
        self.my_vehicle.accelerate(change)

    def draw(self):
        """Width is the width of the lane"""
        if self.my_vehicle.angle % 180 == 90:
            length = self.my_vehicle.width
            width = self.my_vehicle.length
        else:
            length = self.my_vehicle.length
            width = self.my_vehicle.width
        half_length = length/2
        half_width = width/2
        top_left_x = self.my_vehicle.x+half_length
        bottom_left_x = self.my_vehicle.x-half_length
        top_right_x = self.my_vehicle.x+half_length
        bottom_right_x = self.my_vehicle.x-half_length
        top_left_y = self.my_vehicle.y-half_width
        top_right_y = self.my_vehicle.y+half_width
        bottom_left_y = self.my_vehicle.y-half_width
        bottom_right_y = self.my_vehicle.y+half_width
        return Visual(DRIVER_COLOR, [(top_left_x, top_left_y), (top_right_x, top_right_y), (bottom_right_x, bottom_right_y), (bottom_left_x, bottom_left_y)])

    def __repr__(self):
        return f"Driver: object_id={self.object_id} destination={self.destination} visibility={self.visibility} quality={self.quality} vehicle={self.my_vehicle}"

    def __str__(self):
        return f"Driver: object_id={self.object_id} destination={self.destination} visibility={self.visibility} quality={self.quality} vehicle={self.my_vehicle}\n"

    # def change_signal(self, direction: vehicle.Direction()):
    # self.turn_signal = direction
    # return self.turn_signal
