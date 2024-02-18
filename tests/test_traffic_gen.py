import unittest
from generator import Generator


class MyTestCase(unittest.TestCase):
    def test_generator(self):
        assert Generator(4, 7).should_generate() == False
        assert Generator(1, 2).should_generate() == True
        assert Generator(9, 32).should_generate() == False
        assert Generator(10, 90).should_generate() == True


if __name__ == '__main__':
    unittest.main()
