from visuals import Visual
from settings import Settings
class StopSign:
    def __init__(self,
                 location,
                 direction):
        self.location = location
        self.direction = direction


class TrafficLight:
    def __init__(self,
                 color: str):
        self.color = color
        self.yellow_time = 0

    def change_color(self, the_time):
        if self.color == 'red':
            self.color = 'green'
        elif self.color == 'yellow':
            self.color = 'red'
        else:
            self.color = 'yellow'
            self.yellow_time = the_time + 3







