import logging
from dataclasses import dataclass
from time import sleep
from enum import Enum
from math import sin, cos, radians, fabs
from settings import Settings
import constants
from utils import quadratic_equation, cal_distance, cos_degrees, sin_degrees, cal_length_compared_to_screen


class Direction(Enum):
    """ indicator directions """
    LEFT = -1
    OFF = 0
    RIGHT = 1


class Vehicle:
    def __init__(self, x: float,
                 y: float,
                 length: float,
                 speed: float,
                 acceleration: float,
                 max_speed: float,
                 max_acceleration: float,
                 max_angle: float,
                 angle: float = 0,
                 width: float = 1):

        self.x = x
        self.y = y
        self.length = length
        self.speed = min(speed, max_speed)
        self.acceleration = min(acceleration, max_acceleration)
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.max_angle = max_angle
        self.turn_signal: Direction = Direction.OFF
        self.angle = angle  # direction you are facing
        self.width = width
        self.my_time = 0
        self.my_distance = 0

    # speed_limit: int
    # turn_signal: str
    # max_accelaration: int
    # wheel: int

    def pretend_update(self, timestep: float):
        if self.acceleration < 0:
            time_to_stop = -self.speed/self.acceleration
            timestep = min(time_to_stop, timestep)
        speed_x = cos_degrees(self.angle)*self.speed
        speed_y = sin_degrees(self.angle)*self.speed
        acceleration_x = cos_degrees(self.angle)*self.acceleration
        acceleration_y = sin_degrees(self.angle)*self.acceleration
        new_x = speed_x * timestep + 0.5 * acceleration_x * timestep * timestep + self.x
        new_y = speed_y * timestep + 0.5 * acceleration_y * timestep * timestep + self.y
        return new_x, new_y

    def update(self, timestep_length: float):
        """ Changes the x and y of the vehicle in question as well as changing the speed """
        if self.speed < 0:
            raise ValueError('Speed must be more then or equal to 0')
        if self.acceleration < 0:
            time_to_stop = -self.speed/self.acceleration
            timestep_length = min(time_to_stop, timestep_length)
        old_x = self.x
        old_y = self.y
        self.x, self.y = self.pretend_update(timestep_length)
        self.my_distance += cal_distance((self.x, self.y, old_x, old_y))
        self.speed += self.acceleration * timestep_length
        self.speed = max(self.speed, 0)
        self.speed = min(self.speed, self.max_speed)
        self.speed = round(self.speed, constants.ROUNDING)
        self.my_time += timestep_length

    def accelerate(self, amount: float):
        """ Changes acceleration positively or negatively """
        self.acceleration += amount
        self.acceleration = min(self.acceleration, self.max_acceleration)
        self.acceleration = max(-self.max_acceleration, self.acceleration)
        self.acceleration = round(self.acceleration, constants.ROUNDING)

    def signal(self, direction: Direction):
        """ Changes direction of turn signal """
        self.turn_signal = direction

    @classmethod
    def get_settings(cls, global_settings: Settings):
        return global_settings['vehicles'][cls.__name__.lower()]

    def get_rear(self) -> tuple[float, float]:
        back_angle = self.angle+180
        xl = self.x + self.length*cos_degrees(back_angle)
        yl = self.y + self.length*sin_degrees(back_angle)
        return xl, yl

    def steer(self, angle: float):
        """ Changes the angle of a vehicle by an angle relative to yourself """
        angle = min(angle, self.max_angle)
        angle = max(angle, -self.max_angle)
        angle = max(angle, -360)
        self.angle += angle
        self.angle = self.angle % 360
        return self.angle

    def __repr__(self):
        return f'{self.__class__.__name__}: x={self.x} y={self.y}, length={self.length}, speed={self.speed}, acceleration={self.acceleration}, angle={self.angle}'

    def average_speed(self):
        try:
            return self.my_distance/self.my_time
        except ZeroDivisionError:
            return 0
    def draw(self):
        length = cal_length_compared_to_screen((NotImplemented, NotImplemented), self.length)

class Pedestrian(Vehicle):
    def __init__(self, x: float, y: float, speed: float, acceleration: float, max_speed: float = 3, length: float = 0.3,
                 max_acceleration: float = 8, max_angle: float = 360, angle: float = 0):
        super().__init__(x, y, length, speed, acceleration, max_speed, max_acceleration, max_angle, angle)


class Bicycle(Vehicle):
    def __init__(self, x: float, y: float, speed: float, acceleration: float, max_speed: float = 13, length: float = 3,
                 max_acceleration: float = 5, max_angle: float = 270, angle: float = 0):
        super().__init__(x, y, length, speed, acceleration, max_speed, max_acceleration, max_angle, angle)


class Truck(Vehicle):
    def __init__(self, x: float, y: float, speed: float, acceleration: float, max_speed: float = 31, length: float = 21,
                 max_acceleration: float = 8, max_angle: float = 30, angle: float = 0):
        super().__init__(x, y, length, speed, acceleration, max_speed, max_acceleration, max_angle, angle)


class Car(Vehicle):
    def __init__(self, x: float, y: float, speed: float, acceleration: float, max_speed: float = 54, length: float = 5,
                 max_acceleration: float = 15, max_angle: float = 45, angle: float = 0):
        super().__init__(x, y, length, speed, acceleration, max_speed, max_acceleration, max_angle, angle)


class Motorcycle(Vehicle):
    def __init__(self, x: float, y: float, speed: float, acceleration: float, max_speed: float = 45, length: float = 3,
                 max_acceleration: float = 8, max_angle: float = 30, angle: float = 0):
        super().__init__(x, y, length, speed, acceleration, max_speed, max_acceleration, max_angle, angle)
