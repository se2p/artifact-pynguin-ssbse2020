import keyword
import unittest

from flutils.moduleutils import (
    _DUNDERS,
    _validate_attr_identifier,
)

_BUILTIN_NAMES = tuple(filter(
    lambda x: x.startswith('__') and x.endswith('__'),
    dir('__builtins__')
))


class TestModuleUtils(unittest.TestCase):

    def test_validate_attr_identifier__00(self):
        val = _validate_attr_identifier('foo', 'line')
        self.assertEqual(val, 'foo')

    def test_validate_attr_identifier__01(self):
        for name in keyword.kwlist:
            with self.subTest(name=name):
                msg = (
                    f"_validate_attr_identifier({name!r}, 'line')\n\n"
                    f"A keyword has been passed in and expecting\n"
                    f"an AttributeError to be raised.\n"
                )
                with self.assertRaises(AttributeError, msg=msg):
                    _validate_attr_identifier(name, 'line')

    def test_validate_attr__identifier__02(self):
        for name in _BUILTIN_NAMES:
            with self.subTest(name=name):
                msg = (
                    f"_validate_attr_identifier({name!r}, 'line')\n\n"
                    f"A dunder builtin name has been passed in and\n"
                    f"expecting an AttributeError to be raised.\n"
                )
                with self.assertRaises(AttributeError, msg=msg):
                    _validate_attr_identifier(name, 'line')

    def test_validate_attr_identifier_dunders_error(self):
        for name in _DUNDERS:
            with self.subTest(name=name):
                msg = (
                    f"_validate_attr_identifier({name!r}, 'line')\n\n"
                    f"A special dunder name has been passed in and\n"
                    f"expecting an AttributeError to be raised.\n"
                )
                with self.assertRaises(AttributeError, msg=msg):
                    _validate_attr_identifier(name, 'line')
