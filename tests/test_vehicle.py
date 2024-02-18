import unittest
from vehicle import Vehicle

class TestVehicle(unittest.TestCase):
    def test_move(self):
        assert Vehicle(1, 1, 1, 1).move() == 2
        assert Vehicle(4, 1, 1, 0).move() == 4
        assert Vehicle(14, 657, 2, -13).move() == 1

    class GetRearMockVehicle(Vehicle):
        def __init__(self, x, y, length, angle):
            self.x = x
            self.y = y
            self.length = length
            self.angle = angle

    def test_get_rear_with_length_3_and_angle_90(self):
        me = self.GetRearMockVehicle(1, 2, 3, 90)
        back = me.get_rear()
        print(back)
        assert back == (1, -1)

    def test_get_rear_where_length_3_and_angle_0(self):
        me = self.GetRearMockVehicle(1, 2, 3, 0)
        back = me.get_rear()
        print(back)
        assert back == (-2, 2)

    def test_get_rear_where_front_is_at_180(self):
        me = self.GetRearMockVehicle(1, 2, 3, 180)
        back = me.get_rear()
        print(back)
        assert back == (4, 2)

    def test_get_rear_with_length_3_and_angle_270(self):
        me = self.GetRearMockVehicle(1, 2, 3, 5)
        back = me.get_rear()
        print(back)
        assert back == (1, 5)



if __name__ == '__main__':
    unittest.main()
