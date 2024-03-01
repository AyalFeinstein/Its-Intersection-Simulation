import unittest
import objects
import constants

class Rd:
    def get_length(self):
        return 100
    def get_width(self, objects):
        return 10

class MyTestCase(unittest.TestCase):
    def test_coord_to_pixels_with_all_0rs(self):
        gob = objects.GlobalObjectList()
        gob.add_road(Rd())
        x, y = gob.coord_to_pixels(0, 0)
        assert x == constants.WINDOW_WIDTH/2
        assert y == constants.WINDOW_HEIGHT/2

if __name__ == '__main__':
    unittest.main()
