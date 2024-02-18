from enum import Enum
# How many digits to round numbers by
ROUNDING = 3
# How many seconds to keep from the car front you
SAFE_GAP_IN_SECONDS = 3
class LaneDirection(Enum):
    FORWARD = 1
    BOTH = 0
    BACKWARD = -1

PI = 3.14
