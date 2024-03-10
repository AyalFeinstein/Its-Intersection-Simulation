from visuals import Visual
class StopSign:
    def __init__(self,
                 location,
                 direction):
        self.location = location
        self.direction = direction

class TrafficLight:
    def __init__(self,
                 location: tuple,
                 direction: float,
                 color: str):
        self.location = location
        self.direction = direction
        self.color = color





