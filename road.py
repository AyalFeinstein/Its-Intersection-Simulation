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

    def get_length(self):
        return self._length

    def get_direction(self):
        return self._direction
