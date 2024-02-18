import unittest
from collision_detector import Detector
from vehicle import Vehicle
from driver import Driver, Quality
from objects import GlobalObjectList

class MockVehicle(Vehicle):
    def __init__(self, x,
                 y,
                 length,
                 angle):
        self.x = x
        self.y = y
        self.length = length
        self.angle = angle

mock_quality = Quality(1,1,1)

class TestDetector(unittest.TestCase):
    def test_one_vehicle_only(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(1, 1, 1, 1), visibility=2, destination=(4, 4), quality=mock_quality)
        assert Detector(gol).detect_crashes() == []

    def test_two_crashed_vehicles_overlap_back(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=1, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=0.05, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        detected = Detector(gol).detect_crashes()

        assert 0 in detected
        assert 1 in detected

    def test_two_crashed_vehicles_overlap_front(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=1, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=1.95, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        detected = Detector(gol).detect_crashes()

        assert 0 in detected
        assert 1 in detected

    def test_3_vehicles_where_two_crashed_simultaneously(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(0.75, 1, 1, 0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(1, 1, 1, 0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[2] = Driver(object_id=2, my_vehicle=MockVehicle(4, 1, 1, 0), visibility=2, destination=(4, 4), quality=mock_quality)
        detected = Detector(gol).detect_crashes()

        assert 0 in detected
        assert 1 in detected
        assert 2 not in detected

    def test_2_vehicles_that_havent_crashed(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(-47.98435, 1, 1, 1), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(-48.9960875, 1, 1, 1), visibility=2, destination=(4, 4), quality=mock_quality)
        detected = Detector(gol).detect_crashes()
        assert detected == []

    def test_two_crashed_vehicles_perpendicular(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=0.5, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=0, y=0.1, length=1, angle=90), visibility=2, destination=(4, 4), quality=mock_quality)

        detected = Detector(gol).detect_crashes()
        assert 0 in detected
        assert 1 in detected

    def test_two_safe_vehicles_perpendicular(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=10, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=0, y=0.1, length=1, angle=90), visibility=2, destination=(4, 4), quality=mock_quality)

        detected = Detector(gol).detect_crashes()
        assert 0 not in detected
        assert 1 not in detected

    def test_two_vehicles_at_n50x_n50y(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=-50, y=0, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=0, y=-50, length=1, angle=90), visibility=2, destination=(4, 4), quality=mock_quality)

        detected = Detector(gol).detect_crashes()
        assert 0 not in detected
        assert 1 not in detected

class TestRealCases(unittest.TestCase):
    def test_two_far_apart_vehicles(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=0, y=50.38263828432855, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=31.565, y=0, length=1, angle=90), visibility=2, destination=(4, 4), quality=mock_quality)

        detected = Detector(gol).detect_crashes()
        assert 0 not in detected
        assert 1 not in detected

    def test_two_far_apart_vehicles_2(self):
        gol = GlobalObjectList()
        gol[0] = Driver(object_id=0, my_vehicle=MockVehicle(x=0, y=10, length=1, angle=0), visibility=2, destination=(4, 4), quality=mock_quality)
        gol[1] = Driver(object_id=1, my_vehicle=MockVehicle(x=-15.34, y=0, length=1, angle=90), visibility=2, destination=(4, 4), quality=mock_quality)
        print('nose')
        detected = Detector(gol).detect_crashes()
        assert 0 not in detected
        assert 1 not in detected


if __name__ == '__main__':
    unittest.main()


