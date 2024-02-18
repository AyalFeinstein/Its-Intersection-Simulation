from road import Road


class GlobalObjectList(dict):
    """ Global list of moving objects and map objects.
    key is the unique identifier
    value is an object (driver, obstacle)
    """
    _next_id: int = 0
    _roads: list[Road] = []
    _lanes: list = []

    def get_next_id(self):
        """ return the next global identifier to use. """
        self._next_id += 1
        return self._next_id

    def add_road(self, road: Road):
        self._roads.append(road)

    def add_lane(self, lane):
        self._lanes.append(lane)

    def get_lanes(self) -> list:
        return self._lanes

    def get_lanes_by_road(self, road) -> list:
        return [lane for lane in self._lanes if lane.road is road]


