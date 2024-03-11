import unittest
from vehicle import Vehicle


class TestVehicle(unittest.TestCase):
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

    def test_update(self):
        # Nothing changes
        me = Vehicle(x=0, y=0, length=1, speed=0, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        me.update(1)
        assert me.speed == 0
        assert me.x == 0
        assert me.y == 0

        # Nothing changes, but x == 1
        me = Vehicle(x=1, y=0, length=1, speed=0, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        me.update(1)
        assert me.speed == 0
        assert me.x == 1
        assert me.y == 0

        # speed is now 1, every thing else is down at 0. Angle == 0.
        me = Vehicle(x=0, y=0, length=1, speed=1, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        me.update(1)
        assert me.speed == 1
        assert me.x == 1
        assert me.y == 0

        # speed is now 1, acceleration is 1, every thing else is down at 0. Angle == 90.
        me = Vehicle(x=0, y=0, length=1, speed=1, acceleration=1, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        me.update(timestep_length=1)
        assert me.speed == 2
        assert me.acceleration == 1
        assert me.x == 1.5
        assert me.y == 0

        # speed is now -1, acceleration is 0, every thing else is down at 0. Angle == 90.
        me = Vehicle(x=0, y=0, length=1, speed=-1, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        with self.assertRaises(ValueError):
            me.update(1)

        # speed is now 1, acceleration is 0, every thing else is down at 0. Angle == 90.
        me = Vehicle(x=0, y=0, length=1, speed=1, acceleration=-2, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        me.update(1)
        print(f'{me.x=}')
        assert me.speed == 0
        assert me.acceleration == -2
        assert me.x == 0.25
        assert me.y == 0

    def test_pretend_update(self):
        me = Vehicle(x=0, y=0, length=1, speed=0, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        x, y = me.pretend_update(1)
        assert x == 0
        assert y == 0

        me = Vehicle(x=0, y=1, length=1, speed=1, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=0, width=1)
        x, y = me.pretend_update(1)
        assert x == 1
        assert y == 1

        me = Vehicle(x=0, y=0, length=1, speed=2, acceleration=0, max_speed=10, max_acceleration=10, max_angle=90,
                     angle=270, width=1)
        x, y = me.pretend_update(1)
        assert x == 0
        assert y == -2

    def test_get_rear_with_length_3_and_angle_270(self):
        me = self.GetRearMockVehicle(0, 0, 3, 270)
        back = me.get_rear()
        print(back)
        assert back == (0, 3)


if __name__ == '__main__':
    unittest.main()
