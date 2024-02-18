import unittest
from pprint import pprint

from lane import Lane
from road import Road
from objects import GlobalObjectList
from constants import LaneDirection



class TestLane(unittest.TestCase):
    def test_get_position_0_degrees(self):
        my_lane = Lane(lane_num=0, my_road=Road(length=10, direction=0, speed_limit=90), width=5, objects=GlobalObjectList(), generator=None, flow_direction=LaneDirection.FORWARD)
        my_lane.objects.add_lane(my_lane)
        position_x, position_y = my_lane.get_position(0)
        assert position_x == -5
        assert position_y == 0
        position_x, position_y = my_lane.get_position(1)
        assert position_x == 5
        assert position_y == 0
        position_x, position_y = my_lane.get_position(0.5)
        assert position_x == 0
        assert position_y == 0

    def test_get_position_90_degrees(self):
        my_lane = Lane(lane_num=0, my_road=Road(length=10, direction=90, speed_limit=90), width=5, objects=GlobalObjectList(), generator=None, flow_direction=LaneDirection.FORWARD)
        my_lane.objects.add_lane(my_lane)
        position_x, position_y = my_lane.get_position(0)
        assert position_x == 0
        assert position_y == -5
        position_x, position_y = my_lane.get_position(1)
        assert position_x == 0
        assert position_y == 5
        position_x, position_y = my_lane.get_position(0.5)
        assert position_x == 0
        assert position_y == 0

    def test_get_position_90_degrees_backwards_flow(self):
        my_lane = Lane(lane_num=0, my_road=Road(length=10, direction=90, speed_limit=90), width=5, objects=GlobalObjectList(), generator=None, flow_direction=LaneDirection.BACKWARD)
        my_lane.objects.add_lane(my_lane)
        position_x, position_y = my_lane.get_position(0)
        assert position_x == 0
        assert position_y == 5
        position_x, position_y = my_lane.get_position(1)
        assert position_x == 0
        assert position_y == -5
        position_x, position_y = my_lane.get_position(0.5)
        assert position_x == 0
        assert position_y == 0




if __name__ == '__main__':
    unittest.main()
