import unittest

import constants
from driver import Driver, Quality
from vehicle import Vehicle
from objects import GlobalObjectList


class LookVehicle(Vehicle):
    """ Vehicle that only implements what's needed for look() """

    def __init__(self, x, y, length, angle=0, max_acceleration=0, speed=0, max_speed=1, acceleration=0):
        self.x = x
        self.y = y
        self.length = length
        self.angle = angle
        self.max_acceleration = max_acceleration
        self.speed = speed
        self.max_speed = max_speed
        self.acceleration = acceleration


class TestDriver(unittest.TestCase):
    def test_calc_max_possible_speed(self):
        mps = Driver.calc_max_possible_speed(road_max=10.0, vehicle_max=20.0, speeding=1.0)
        assert mps == 10.0, "no speeding, road max < vehicle max"

        mps = Driver.calc_max_possible_speed(road_max=10.0, vehicle_max=20.0, speeding=1.2)
        assert mps == 12.0, "speeding, road max < vehicle max"

        mps = Driver.calc_max_possible_speed(road_max=10.0, vehicle_max=5.0, speeding=1.2)
        assert mps == 5.0, "road max > vehicle max"

    def test_look_with_two_drivers_next_to_each_other(self):
        me = Driver(0, Vehicle(1, 1, 1, 1, 1, 1, 1, 1), 9, (2, 2), Quality(1, 1))
        drv1 = Driver(0, Vehicle(1, 2, 1, 1, 1, 1, 1, 1), 9, (2, 2), Quality(1, 1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        assert me.look(object_list) == [drv1]

    def test_look_object_out_of_range(self):
        me = Driver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=0.5, angle=0), visibility=3,
                    destination=(2, 2), quality=Quality(1, 1))
        drv1 = Driver(object_id=1, my_vehicle=LookVehicle(x=6, y=1, length=0.5, angle=0), visibility=9,
                      destination=(2, 2), quality=Quality(1, 1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        assert me.look(object_list) == []

    def test_look_one_in_range_one_out(self):
        me = Driver(0, LookVehicle(x=1, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        drv1 = Driver(1, LookVehicle(x=2, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        drv2 = Driver(3, LookVehicle(x=3, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        object_list[2] = drv2
        visible_objects = me.look(object_list)
        assert visible_objects == [drv1]

    def test_look_all_in_range(self):
        me = Driver(0, LookVehicle(x=1, y=1, length=0.5), visibility=999999, destination=(2, 2), quality=Quality(1, 1))
        drv1 = Driver(1, LookVehicle(x=2, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        drv2 = Driver(2, LookVehicle(x=3, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        drv3 = Driver(3, LookVehicle(x=4, y=1, length=0.5), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        object_list[2] = drv2
        object_list[4] = drv3
        visible_objects = me.look(object_list)
        assert drv1 in visible_objects
        assert drv2 in visible_objects
        assert drv3 in visible_objects
        assert len(visible_objects) == 3

    def test_look_back_in_front_out(self):
        me = Driver(0, LookVehicle(x=1, y=1, length=0.5), visibility=8, destination=(2, 2), quality=Quality(1, 1))
        drv1 = Driver(1, LookVehicle(x=5, y=4, length=4), visibility=1, destination=(2, 2), quality=Quality(1, 1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        visible_objects = me.look(object_list)
        assert visible_objects == [drv1]


class SimplifiedDriver(Driver):
    def __init__(self, object_id: int, my_vehicle: Vehicle,
                 quality: Quality):
        self.object_id = object_id
        self.my_vehicle = my_vehicle
        self.quality = quality


class TestDriverPlan(unittest.TestCase):

    def test_get_safe_following_distance(self):
        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1.0, angle=0.0, max_acceleration=1.0, speed=10.0),
                              Quality(following_distance=2.0))
        assert me.get_safe_following_distance() == constants.SAFE_GAP_IN_SECONDS * 10.0 * 2.0, "If speed is positive"

        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1.0, angle=0.0, max_acceleration=1.0, speed=-10.0),
                              Quality(following_distance=2.0))
        assert me.get_safe_following_distance() == constants.SAFE_GAP_IN_SECONDS * 10.0 * 2.0, "If speed is negative"

    def test_get_desired_accel_change(self):
        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1.0, angle=0.0, max_acceleration=1.0, speed=10.0, max_speed=30),
                              Quality())
        desired_accel = me._get_desired_acceleration_change(20.0, 1.0)
        assert desired_accel == 10, "your speed < desired speed"

        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1.0, angle=0.0, max_acceleration=1.0, speed=25.0, max_speed=30),
                              Quality())
        desired_accel = me._get_desired_acceleration_change(20.0, 1.0)
        assert desired_accel == -5, "your speed > desired speed"

        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1.0, angle=0.0, max_acceleration=1.0, speed=20.0, max_speed=30),
                              Quality())
        desired_accel = me._get_desired_acceleration_change(20.0, 1.0)
        assert desired_accel == 0, "your speed = desired speed"

    def test_check_when_vehicle_hits_a_location_in_d(self):
        me = SimplifiedDriver(0, LookVehicle(x=0, y=0, length=1, angle=0, max_acceleration=0, speed=10, max_speed=10, acceleration=0), quality=Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=10, y=0, length=1, angle=0, max_acceleration=0, speed=0, max_speed=10, acceleration=0), quality=Quality())
        time_to_intercept = me._when_vehicle_hits_a_location_in_d(drv1.my_vehicle.x, 'x')
        assert time_to_intercept == 1

        time_to_intercept = me._when_vehicle_hits_a_location_in_d(drv1.my_vehicle.x, 'y')
        print(time_to_intercept)
        assert time_to_intercept == 0

        me = SimplifiedDriver(0, LookVehicle(x=0, y=4, length=1, angle=0, max_acceleration=0, speed=10, max_speed=10, acceleration=0), quality=Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=5, y=0, length=1, angle=0, max_acceleration=0, speed=0, max_speed=10, acceleration=0), quality=Quality())
        time_to_intercept = me._when_vehicle_hits_a_location_in_d(drv1.my_vehicle.x, 'x')
        assert time_to_intercept == 0.5

        time_to_intercept = me._when_vehicle_hits_a_location_in_d(drv1.my_vehicle.x, 'y')
        assert time_to_intercept is None

    def test_get_time_to_intercept(self):
        me = SimplifiedDriver(0, LookVehicle(x=10, y=0, length=1, speed=5, acceleration=0), Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=0, y=0, length=1, speed=5, acceleration=0), Quality())
        time_to_intercept, s = me._to_intercept(drv1)
        assert time_to_intercept is None, "me is in front of drv1"
        print(s)
        assert s == -9

        me = SimplifiedDriver(0, LookVehicle(x=5, y=0, length=1, speed=5, acceleration=0), Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=10, y=0, length=1, speed=5, acceleration=0), Quality())
        time_to_intercept, d = me._to_intercept(drv1)
        assert time_to_intercept is None, "speeds are equal"
        print(d)
        assert d == 4

        me = SimplifiedDriver(0, LookVehicle(x=10, y=0, length=1, speed=5, acceleration=0), Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=12, y=0, length=1, speed=10, acceleration=0), Quality())
        time_to_intercept, d = me._to_intercept(drv1)
        print(time_to_intercept)
        assert time_to_intercept is None, "me.speed < drv1.speed"
        assert d == 1

        me = SimplifiedDriver(0, LookVehicle(x=5, y=0, length=1, speed=5, acceleration=0), Quality())
        drv1 = SimplifiedDriver(1, LookVehicle(x=10, y=0, length=1, speed=0, acceleration=0), Quality())
        time_to_intercept, d = me._to_intercept(drv1)
        print(time_to_intercept)
        assert time_to_intercept == 0.8, "me.speed > drv1.speed"
        assert d == 4

    def test_plan_with_just_me(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=6666, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([], 50, 1.0)
        assert change == 5

    def test_plan_with_one_more_driver(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=0, length=0.5, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=1,
                                my_vehicle=LookVehicle(x=2, y=0, length=0.5, angle=0, max_acceleration=5, speed=1,
                                                       max_speed=45, acceleration=0),
                                quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1], 90, 1.0)
        print(change)
        assert change == -0.4

    def test_plan_with_one_other_driver_right_in_front_of_me(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=0, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=1,
                                my_vehicle=LookVehicle(x=3, y=0, length=1, angle=0, max_acceleration=5, speed=1,
                                                       max_speed=45, acceleration=0),
                                quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1], 90, 1.0)
        print(change)
        assert change == -5

    def test_plan_with_one_behind_me(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=2, y=1, length=1, angle=0, max_acceleration=5, speed=45,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=1,
                                my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1,
                                                       max_speed=45, acceleration=0),
                                quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1], 90, 1.0)
        print(change)
        assert change == 0

    def test_plan_with_two_drivers_with_one_behind_me(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=0,
                                my_vehicle=LookVehicle(x=-1, y=1, length=1, angle=0, max_acceleration=5, speed=1,
                                                       max_speed=45, acceleration=0),
                                quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv2 = SimplifiedDriver(object_id=0,
                                my_vehicle=LookVehicle(x=5, y=1, length=1, angle=0, max_acceleration=5, speed=1,
                                                       max_speed=45, acceleration=0),
                                quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1, drv2], 90, 1.0)
        assert change

    def test_get_direction_x_or_y(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=0, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=0.5))
        direction = me._get_direction_x_or_y()
        assert direction == 'x'

    def test_to_intercept(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=0, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=5, y=0, length=1, angle=0, max_acceleration=5, speed=0,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        time, distance = me._to_intercept(drv1)
        assert time == 3
        assert distance == 3

    def test_to_intercept_w_accel(self):
        me = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=1, y=0, length=1, angle=0, max_acceleration=5, speed=1,
                                                     max_speed=45, acceleration=1),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=0,
                              my_vehicle=LookVehicle(x=5, y=0, length=1, angle=0, max_acceleration=5, speed=0,
                                                     max_speed=45, acceleration=0),
                              quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        time, distance = me._to_intercept(drv1)
        print(time)
        assert time == 1.6457513110645907
        assert distance == 3



if __name__ == '__main__':
    unittest.main()
