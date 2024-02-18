import unittest
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

    def test_look_with_two_drivers_next_to_each_other(self):
        me = Driver(0, Vehicle(1,1,1,1,1,1,1,1), 9, (2, 2), Quality(1,1))
        drv1 = Driver(0, Vehicle(1,2,1,1,1,1,1,1), 9, (2, 2), Quality(1,1))
        object_list = GlobalObjectList()
        object_list[0] = me
        object_list[1] = drv1
        assert me.look(object_list) == [drv1]


    def test_look_object_out_of_range(self):
        me = Driver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=0.5, angle=0), visibility=3, destination=(2, 2), quality=Quality(1,1))
        drv1 = Driver(object_id=1, my_vehicle=LookVehicle(x=6, y=1, length=0.5, angle=0), visibility=9, destination=(2, 2), quality=Quality(1,1))
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
    def test_plan_with_just_me(self):
        me = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=6666, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([], 50, 1.0)
        assert change == 5

    def test_plan_with_one_more_driver(self):
        me = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=1, my_vehicle=LookVehicle(x=2, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1], 90, 1.0)
        assert change == 0

    def test_plan_with_two_more_drivers(self):
        me = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=1, my_vehicle=LookVehicle(x=2, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1], 90, 1.0)
        print(change)
        assert change == 0

    def test_plan_with_two_drivers_with_one_behind_me(self):
        me = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=1, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv1 = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=-1, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        drv2 = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=5, y=1, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=1.0))
        change = me.plan([drv1, drv2], 90, 1.0)
        assert change

    def test_get_direction_x_or_y(self):
        me = SimplifiedDriver(object_id=0, my_vehicle=LookVehicle(x=1, y=0, length=1, angle=0, max_acceleration=5, speed=1, max_speed=45, acceleration=0), quality=Quality(speeding=1.0, following_distance=1.0, attentiveness=0.5))
        direction = me._get_direction_x_or_y()
        assert direction == 'x'


if __name__ == '__main__':
    unittest.main()
