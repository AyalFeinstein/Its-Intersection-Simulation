from utils import split_vector
from visuals import Visual
from settings import Settings
from enum import IntEnum
from constants import TRAFFIC_HEAD_SIZE


class StopSign:
    def __init__(self,
                 location,
                 direction):
        self.location = location
        self.direction = direction

class Signal:
    def update(self, the_time):
        pass

    def draw(self):
        return []

    def get_position(self):
        return 0, 0

    def get_light(self, lane):
        return TrafficLightColor.GREEN

    def controls(self, lane):
        return False


class TrafficLightColor(IntEnum):
    GREEN = 0
    YELLOW = 1
    RED = 2
    _MAX_COLOR = 3

    def next(self):
        return self.__class__((int(self.value) + 1) % self._MAX_COLOR)

    def drawing_color(self):
        drawing_colors = {
            self.RED: (255, 0, 0),
            self.YELLOW: (255, 255, 0),
            self.GREEN: (0, 255, 0)
        }
        return drawing_colors[self.value]


class TrafficHead:
    def __init__(self,
                 position: float,
                 my_lane,
                 color: TrafficLightColor = TrafficLightColor.RED):
        self.lane = my_lane
        self.position = position
        self.color = color

    def change(self):
        self.color = self.color.next()

    def draw(self):
        dx, dy = self.get_position()
        half_width = TRAFFIC_HEAD_SIZE / 2
        top_left = (-half_width + dx, half_width + dy)
        top_right = (half_width + dx, half_width + dy)
        bottom_right = (half_width + dx, -half_width + dy)
        bottom_left = (-half_width + dx, -half_width + dy)
        return [Visual(self.color.drawing_color(), [top_left, top_right, bottom_right, bottom_left])]

    def get_position(self):
        return split_vector(self.position, self.lane.get_angle())


class TrafficLight(Signal):
    def __init__(self,
                 cycle_time: float,
                 yellow_time: float,
                 traffic_heads: list[TrafficHead]):
        self.cycle_time = cycle_time
        self.yellow_time = yellow_time
        self.traffic_heads = traffic_heads
        self._next_change = cycle_time
        self._traffic_heads_by_lane = {
            th.lane: th
            for th in traffic_heads
        }

    def update(self, the_time):
        if (self._next_change - self.yellow_time) <= the_time:
            for traffic_light in self.traffic_heads:
                if traffic_light.color.value == TrafficLightColor.GREEN:
                    traffic_light.change()
        if self._next_change <= the_time:
            self._next_change += self.cycle_time
            for traffic_light in self.traffic_heads:
                traffic_light.change()

    def draw(self):
        drawings = []
        for d in self.traffic_heads:
            drawings.extend(d.draw())
        return drawings

    def get_light(self, lane) -> TrafficLightColor:
        """ Get the light color facing a lane """
        head = self._traffic_heads_by_lane[lane]
        return head.color

    def get_position(self, lane) -> tuple[float, float]:
        head = self._traffic_heads_by_lane[lane]
        return head.get_position()

    def controls(self, lane):
        return True
