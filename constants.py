from enum import Enum
from dataclasses import dataclass

# How many digits to round numbers by
ROUNDING = 3
# How many seconds to keep from the car front you
SAFE_GAP_IN_SECONDS = 3


class LaneDirection(Enum):
    FORWARD = 1
    BOTH = 0
    BACKWARD = -1


@dataclass
class Ratio:
    numerator: float
    denominator: float

    def multiply(self, number):
        return number * self.numerator / self.denominator


PI = 3.14
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800
BACKGROUND = (144, 238, 144)
ROAD_COLOR = (128, 128, 128)
LINE_WIDTH = 4
LINE_COLOR = (255, 255, 255)
DRIVER_COLOR = (255, 0, 0)


@dataclass
class Visual:
    length: float
    width: float
    color: tuple[float, float, float]

# TODO: Get pixels
