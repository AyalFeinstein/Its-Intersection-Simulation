import time

from constants import Ratio, Visual, LINE_WIDTH, ROAD_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from visuals import Visual
from settings import Settings

class Road:
    """ Roads always center at (0,0).
    """

    def __init__(self,
                 length: int,
                 direction: float,
                 speed_limit: int,
                 ):
        self._length = length
        self._speed_limit = speed_limit
        self._direction = direction

    def get_speed_limit(self):
        return self._speed_limit

    def get_width(self, objects):
        width = 0
        for lane in objects.get_lanes_by_road(self):
            width += lane.width
        return width

    def get_green_time(self, road_num):
        return Settings['roads'][road_num]['green_time']


    def get_length(self):
        return self._length

    def get_direction(self):
        return self._direction

    def draw_line(self, ratio: Ratio):
        length = ratio.multiply(self._length)
        return Visual(length, LINE_WIDTH, (255, 255, 255))

    def draw_lane(self, ratio, lane):
        length = ratio.multiply(self._length)
        return Visual(length, lane.width, ROAD_COLOR)

    def draw(self, objects):
        half_road_length = self.get_length()/2
        half_width = self.get_width(objects)/2
        top_left = (-half_road_length, half_width)
        top_right = (half_road_length, half_width)
        bottom_left = (-half_road_length, -half_width)
        bottom_right = (half_road_length, -half_width)
        if self._direction % 180 == 90:
            top_left = (half_width, -half_road_length)
            top_right = (half_width, half_road_length)
            bottom_left = (-half_width, -half_road_length)
            bottom_right = (-half_width, half_road_length)
        return [Visual(ROAD_COLOR, [top_left, top_right, bottom_right, bottom_left])]


