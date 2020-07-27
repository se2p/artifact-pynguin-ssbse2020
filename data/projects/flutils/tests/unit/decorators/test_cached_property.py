import keyword
import types
import unittest
from functools import wraps
from importlib.machinery import ModuleSpec
from unittest.mock import (
    MagicMock,
    call,
    patch,
    sentinel,
)

from flutils.decorators import cached_property


def coroutine_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


class Obj:

    def __init__(self, value):
        self.value = value

    @cached_property
    def new_value(self):
        return self.value + 1


class TestCachedPropertyAsync(unittest.TestCase):

    def setUp(self):
        patcher = patch(
            'asyncio.ensure_future',
            return_value=5
        )
        self.asyncio_ensure_future = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'asyncio.coroutine',
            coroutine_decorator
        )
        self.asyncio_coroutine = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'asyncio.iscoroutinefunction',
            return_value=True
        )
        self.asyncio_iscoroutinefunction = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cached_property_async(self):
        obj = Obj(4)
        self.assertEqual(obj.new_value, 5)


class TestCachedPropertyClassProperty(unittest.TestCase):

    def test_cached_property_class_property(self):
        prop = Obj.new_value
        self.assertIsInstance(prop, cached_property)
