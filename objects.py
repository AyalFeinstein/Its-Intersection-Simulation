from constants import WINDOW_WIDTH, WINDOW_HEIGHT, LINE_WIDTH, ROAD_COLOR, Ratio
import pygame
from road import Road
import time
from visuals import Visual


class GlobalObjectList(dict):
    """ Global list of moving objects and map objects.
    key is the unique identifier
    value is an object (driver, obstacle)
    """
    _next_id: int = 0
    _roads: list = []
    _lanes: list = []
    _max_length: float = 0.0

    def coord_to_pixels(self, x, y):
        ''' Returns pixels/meter '''

        ratio_width = WINDOW_WIDTH / self._max_length
        ratio_height = WINDOW_HEIGHT / self._max_length
        return (x + self._max_length / 2) * ratio_width, (y + self._max_length / 2) * ratio_height

    def get_next_id(self):
        """ return the next global identifier to use. """
        self._next_id += 1
        return self._next_id

    def get_road_num(self, road):
        counter = -1
        for r in self._roads:
            counter += 1
            if r is road:
                return counter

    def add_road(self, road):
        self._roads.append(road)
        self._max_length = max(self._max_length, road.get_length())

    def add_lane(self, lane):
        self._lanes.append(lane)

    def get_lanes(self) -> list:
        return self._lanes

    def find_lane(self, lane_id):
        for lane in self.get_lanes():
            if lane.lane_num == lane_id:
                return lane
        return None

    def get_lanes_by_road(self, road) -> list:
        return [lane for lane in self._lanes if lane.road is road]

    def draw(self):
        all_visuals = []
        all_visuals_pixels = []
        for road in self._roads:
            all_visuals += road.draw(self)
        for lane in self._lanes:
            all_visuals += lane.draw()
            for driver in self.values():
                if driver.object_id in lane.objects_in_lane:
                    all_visuals.append(driver.draw())

        for obj in all_visuals:
            newlocs = [self.coord_to_pixels(*loc) for loc in obj.locations]
            all_visuals_pixels.append(Visual(obj.color, newlocs))
        return all_visuals_pixels



