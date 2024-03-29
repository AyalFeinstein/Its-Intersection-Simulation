import logging

from utils import cal_distance
from vehicle import Vehicle, Car, Motorcycle, Truck, Pedestrian, Bicycle
from random import randint, choices, gauss, random, choice
from driver import Quality, Driver
from objects import GlobalObjectList
from settings import Settings
from enum import Enum
from numpy.random import poisson


class LaneDirection(Enum):
    FORWARD = 1
    BOTH = 0
    BACKWARD = -1


class Generator:

    def __init__(self, objects: GlobalObjectList, settings: Settings, flow_direction: LaneDirection, angle: float = 0):
        self.objects = objects  # global objects list
        self.settings = settings  # generator settings
        self.flow_direction = flow_direction
        self.angle = angle

        self._flow = self.settings["flow"]
        self._next_generation_time = poisson(self._flow)
        self._next_id = 0
        self.__last_generation = None

    # TODO: HINT: WRITE TESTS FOR THIS FUNCTION
    def should_generate(self, timestep, lane) -> bool:
        """ Return True if a vehicle should be generated this timestep """
        x, y = lane.get_position(0)
        endx, endy = lane.get_position(1)
        if self.__last_generation not in self.objects.values():
            objects_in_lane = lane.get_objects()
            if not objects_in_lane:
                self.__last_generation = None
            else:
                self.__last_generation = objects_in_lane[-1]
        if self._next_generation_time <= timestep:
            if self.__last_generation is not None:
                rear_x, rear_y = self.__last_generation.my_vehicle.get_rear()
                distance = cal_distance((x, y, rear_x, rear_y))
                safe_following_distance = self.__last_generation.get_safe_following_distance()
                if (distance <= safe_following_distance
                    or not (x <= rear_x <= endx)  # rear has not yet passed beginning of road
                    or not (y <= rear_y <= endy)
                ):
                    logging.debug(f"generator will not generate because: {distance} <= {safe_following_distance=} or {not (x < rear_x < endx)=} or {not (y < rear_y < endy)=}")
                    return False
            new_next_generation_time = poisson(self._flow)
            self._next_generation_time += new_next_generation_time
            logging.debug(f"generator will generate at {timestep}. {self._next_generation_time=}")
            return True
        else:
            logging.debug(f"generator will not generate at {timestep}. waiting for {self._next_generation_time=}")
            return False

    def pick_vehicle_type(self):
        """ Pick a Vehicle's type """
        settings = self.settings['vehicle_distribution']
        the_type = choices([Car, Truck, Motorcycle, Bicycle, Pedestrian],
                           [settings.get('car', 0.0), settings.get('truck', 0.0), settings.get('motorcycle', 0.0),
                            settings.get('bike', 0.0), settings.get('pedestrian', 0.0)])
        return the_type[0]

    def generate_vehicle(self, x, y, driver_max, road_max, speeding, settings):
        """ pick parameters + type of vehicle and turn them into a Vehicle object """
        my_type = self.pick_vehicle_type()
        vehicle_settings = my_type.get_settings(settings)
        length = vehicle_settings['length']
        if self.__last_generation is not None:
            speed = min(Driver.calc_max_possible_speed(vehicle_settings['max_speed'], road_max, speeding), self.__last_generation.my_vehicle.speed)
            acceleration = max(min(self.__last_generation.my_vehicle.acceleration, 0), -vehicle_settings['max_acceleration'])
        else:
            speed = Driver.calc_max_possible_speed(vehicle_settings['max_speed'], road_max, speeding)
            acceleration = 0
        width = vehicle_settings['width']
        self.__last_generation = Vehicle(x=x, y=y,
                       length=length,
                       speed=speed,
                       acceleration=acceleration,
                       max_speed=vehicle_settings['max_speed'],
                       max_acceleration=vehicle_settings['max_acceleration'],
                       max_angle=vehicle_settings['max_angle'],
                       angle=self.angle,
                       width=width)
        return self.__last_generation

    def init_following_distance(self):
        self.following_distance = randint(2, 7)
        if self.following_distance == 7:
            self.following_distance = randint(7, 10)
        return self.following_distance

    def generate(self, x0: float, y0: float, visibility: float, endx: float, endy: float, road_max, settings):
        """ Generate a new vehicle and driver at (x0, y0) pointing in the given direction.
        Return the newly generated object
        """
        attentiveness = gauss(self.settings['attentiveness']['average'], self.settings['attentiveness']['width'])
        attentiveness = min(attentiveness, 1.0)
        attentiveness = max(attentiveness, 0.1)

        speeding = gauss(1, 0.2)
        speeding = min(speeding, 1.25)
        speeding = max(0.75, speeding)

        following_distance = gauss(1.0, 0.15)
        following_distance = min(following_distance, 1.4)
        following_distance = max(following_distance, 0.6)

        quality = Quality(speeding=speeding, following_distance=following_distance, attentiveness=attentiveness)
        driver = Driver(self.objects.get_next_id(),
                        self.generate_vehicle(x0, y0, road_max + speeding, road_max, speeding, settings), visibility,
                        (endx, endy), quality)
        self.__last_generation = driver
        return driver
