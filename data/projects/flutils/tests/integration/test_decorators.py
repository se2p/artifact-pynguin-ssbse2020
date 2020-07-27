import unittest

from flutils.decorators import cached_property


class MyClass:

    def __init__(self):
        self.x = 5

    @cached_property
    def y(self):
        return self.x + 1


class TestCachedPropertyBasic(unittest.TestCase):

    def test_cached_property_value(self):
        obj = MyClass()
        self.assertEqual(6, obj.y)
