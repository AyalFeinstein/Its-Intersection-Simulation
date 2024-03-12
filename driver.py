import logging
from dataclasses import dataclass
from random import randint, random
from typing import Optional
from visuals import Visual
from constants import LaneDirection, ROUNDING, SAFE_GAP_IN_SECONDS, DRIVER_COLOR, MAX_CARE_RANGE, MIN_FOLLOWING_DISTANCE, PERPENDICULAR_FOLLOWING_DISTANCE
from utils import cal_distance, quadratic_equation, split_vector, dot, intervals_overlap
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
                closest = self.get_closest(driver)
                min_distance = cal_distance(closest)
                # distance = fabs(sqrt(
                #     pow((driver.my_vehicle.x - self.my_vehicle.x), 2) + pow((driver.my_vehicle.y - self.my_vehicle.y),
                #                                                             2)))
                # rear_x, rear_y = driver.my_vehicle.get_rear()
                # distance_to_back = fabs(
                #     (sqrt(pow((rear_x - self.my_vehicle.x), 2) + pow((rear_y - self.my_vehicle.y), 2))))
                # if distance <= self.visibility or distance_to_back <= self.visibility:
                if min_distance <= self.visibility:
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
        return max(SAFE_GAP_IN_SECONDS * abs(self.my_vehicle.speed),
                   self.my_vehicle.length * MIN_FOLLOWING_DISTANCE) * self.quality.following_distance

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

        time_to_intercept = set(t for t in time_to_intercept if t >= 0)
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
        logging.debug(f"{self.object_id} and {driver.object_id}: {min_time_to_be_safe=} {distance_to_intercept=}")

        their_new_speed = max(
            (
                (driver.my_vehicle.speed + driver.my_vehicle.acceleration * min_time_to_be_safe)
                if min_time_to_be_safe is not None
                else driver.my_vehicle.speed),
            0)
        my_current_acceleration = self.my_vehicle.acceleration
        if distance_to_intercept < safe_following_distance:
            logging.debug(f"{self.object_id} planning to STOP because {distance_to_intercept=} < {safe_following_distance=}")
            return -self.my_vehicle.max_acceleration - my_current_acceleration
        elif distance_to_intercept < SAFE_GAP_IN_SECONDS * MAX_CARE_RANGE * self.quality.following_distance * self.my_vehicle.speed:
            logging.debug(f"{self.object_id} planning to FOLLOW because {distance_to_intercept=} inside the care range")
            your_final_speed = their_new_speed
        elif min_time_to_be_safe is None:
            logging.debug(f"{self.object_id} planning to GO because no traffic ahead")
            return None
        elif min_time_to_be_safe > SAFE_GAP_IN_SECONDS * MAX_CARE_RANGE * self.quality.following_distance:
            logging.debug(f"{self.object_id} planning to GO because no traffic within the care time")
            return None
        elif min_time_to_be_safe <= SAFE_GAP_IN_SECONDS * self.quality.following_distance:
            logging.debug(f"{self.object_id} planning to STOP because there's traffic within safe time range")
            return -self.my_vehicle.max_acceleration - my_current_acceleration
        else:
            logging.debug(f"{self.object_id} planning to GO because nothing else to do")
            return None  # your_final_speed = their_new_speed

        speed_diff = your_final_speed - self.my_vehicle.speed
        if min_time_to_be_safe == 0:
            new_accel = -self.my_vehicle.max_acceleration
        else:
            new_accel = speed_diff / fabs(min_time_to_be_safe or 1.0)  # always change in 1s if no time to intercept
        accel_change = new_accel - self.my_vehicle.acceleration
        logging.debug(
            f"{self.object_id} and {driver.object_id}: {their_new_speed=} {your_final_speed=} {new_accel=} {accel_change=}")
        return accel_change

    def _to_intercept_loc_parallel(self, loc: tuple):
        cal_distance((self.my_vehicle.x, self.my_vehicle.y, loc[0], loc[1]))

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

    def _when_vehicle_hits_a_location_in_d(self, position: float, space) -> tuple[Optional[float], float]:
        """position=my x or y coordinate
        space=spot in x or y that you want to find the time to
         d=x or y dimension
         returns tuple[time, distance]"""
        loc0 = position

        distance = space - loc0
        time_to_intercepts = quadratic_equation(0.5 * self.my_vehicle.acceleration, self.my_vehicle.speed, loc0 - space)
        time_to_intercepts = set(
            time_to_intercept for time_to_intercept in time_to_intercepts if time_to_intercept >= 0)
        if not time_to_intercepts:
            return None, distance
        else:
            return min(time_to_intercepts), distance

    def _to_intercept_perpendicular(self, driver) -> tuple[Optional[float], float, Optional[float], Optional[float]]:
        """ Returns a tuple[time, distance, when they leave]
        If they will never intercept, time = None."""
        my_front = (self.my_vehicle.x, self.my_vehicle.y)
        my_rear = self.my_vehicle.get_rear()

        their_front = (driver.my_vehicle.x, driver.my_vehicle.y)
        their_rear = driver.my_vehicle.get_rear()

        if driver.my_vehicle.angle % 180 == 90:
            their_direction = 1
            my_direction = 0
        else:
            their_direction = 0
            my_direction = 1
        your_time_to_intercept_front, your_distance_to_intercept_front = self._when_vehicle_hits_a_location_in_d(
            my_front[my_direction], their_front[my_direction])
        your_time_to_intercept_rear, your_distance_to_leave = self._when_vehicle_hits_a_location_in_d(
            my_rear[my_direction], their_rear[my_direction])
        their_time_to_intercept_front, their_distance_to_intercept_front = driver._when_vehicle_hits_a_location_in_d(
            their_front[their_direction], my_front[their_direction])
        their_time_to_intercept_rear, their_distance_to_leave = driver._when_vehicle_hits_a_location_in_d(
            their_rear[their_direction], my_rear[their_direction])
        min_distance = min(your_distance_to_intercept_front, your_distance_to_leave)
        if (your_time_to_intercept_front is None
                or their_time_to_intercept_rear is None
                or your_time_to_intercept_rear is None
                or their_time_to_intercept_front is None):
            return None, min_distance, their_time_to_intercept_rear, their_distance_to_intercept_front
        if intervals_overlap(your_time_to_intercept_front, your_time_to_intercept_rear, their_time_to_intercept_front,
                             their_time_to_intercept_rear, SAFE_GAP_IN_SECONDS):
            return min(their_time_to_intercept_front,
                       your_time_to_intercept_front), min_distance, their_time_to_intercept_rear, their_distance_to_intercept_front
        else:
            return None, min_distance, their_time_to_intercept_rear, their_distance_to_intercept_front

    def plan(self, visible_objects, road_limit, timestep_length):
        # the default will be trying to get to my desired acceleration
        changes = [self._get_desired_acceleration_change(road_limit, timestep_length)]
        for driver in visible_objects:
            # Check if the driver is perpendicular to you
            if self._check_whether_perpendicular(driver):
                accel_change = self._adjust_acceleration_for_other_driver_perpendicular(driver)
            else:
                accel_change = self._adjust_acceleration_for_other_driver(driver)
            if accel_change is not None:
                changes.append(accel_change)
        changes = min(changes)
        logging.debug(f'{self.object_id=} {changes=}')
        return round(changes, ROUNDING)

    def get_needed_angle_change(self):
        """ plan weather to turn or not """
        needed_angle_change = 0
        if self.destination[1] < self.my_vehicle.y or self.destination[0] < self.my_vehicle.x:
            needed_angle_change = 90
        elif self.destination[1] > self.my_vehicle.y or self.destination[0] > self.my_vehicle.x:
            needed_angle_change = 270
        return needed_angle_change

    def _adjust_acceleration_for_other_driver_perpendicular(self, driver):
        min_time_to_be_safe, distance_to_intercept, their_time_to_leave, their_distance_to_intercept = self._to_intercept_perpendicular(driver)
        logging.debug(f"{self.object_id} and {driver.object_id}: {min_time_to_be_safe=} {distance_to_intercept=}")
        safe_following_distance = self.get_safe_following_distance()*PERPENDICULAR_FOLLOWING_DISTANCE
        my_speed_x, my_speed_y = split_vector(self.my_vehicle.speed, self.my_vehicle.angle)

        my_closest_x, my_closest_y, his_closest_x, his_closest_y = self.get_closest(driver)
        my_closest_x, my_closest_y, their_closest_x, their_closest_y = self.get_closest(driver)
        direct_distance = cal_distance((my_closest_x, my_closest_y, their_closest_x, their_closest_y))

        distance_x, distance_y = his_closest_x - my_closest_x, his_closest_y - my_closest_y
        if distance_to_intercept <= 0:
            return None
        if direct_distance <= safe_following_distance:
            if their_distance_to_intercept <= distance_to_intercept:
                return -self.my_vehicle.max_acceleration
        if min_time_to_be_safe is None:
            return None

        t = their_time_to_leave + SAFE_GAP_IN_SECONDS
        new_accel = (2.0 / (t * t)) * (distance_to_intercept - self.my_vehicle.speed * t)
        accel_change = new_accel - self.my_vehicle.acceleration
        logging.debug(
            f"{self.object_id} and {driver.object_id}: {self.my_vehicle.speed=} time to modify speed={t} {new_accel=} {accel_change=}")

        return accel_change

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

    def copy(self):
        return Driver(object_id=self.object_id,
                      my_vehicle=self.my_vehicle,
                      visibility=self.visibility,
                      destination=self.destination,
                      quality=self.quality)

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
        half_length = length / 2
        half_width = width / 2
        top_left_x = self.my_vehicle.x + half_length
        bottom_left_x = self.my_vehicle.x - half_length
        top_right_x = self.my_vehicle.x + half_length
        bottom_right_x = self.my_vehicle.x - half_length
        top_left_y = self.my_vehicle.y - half_width
        top_right_y = self.my_vehicle.y + half_width
        bottom_left_y = self.my_vehicle.y - half_width
        bottom_right_y = self.my_vehicle.y + half_width
        return Visual(DRIVER_COLOR,
                      [(top_left_x, top_left_y), (top_right_x, top_right_y), (bottom_right_x, bottom_right_y),
                       (bottom_left_x, bottom_left_y)])

    def __repr__(self):
        return f"Driver: object_id={self.object_id} destination={self.destination} visibility={self.visibility} quality={self.quality} vehicle={self.my_vehicle}"

    # def change_signal(self, direction: vehicle.Direction()):
    # self.turn_signal = direction
    # return self.turn_signal
