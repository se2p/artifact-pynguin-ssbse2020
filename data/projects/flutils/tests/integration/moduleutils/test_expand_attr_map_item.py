import keyword
import unittest

from flutils.moduleutils import (
    _AttrMapping,
    _expand_attr_map_item,
)


class Test(unittest.TestCase):

    def test_integration_expand_attr_map_item_module(self):
        item = 'os'
        expect = _AttrMapping(
            'os',
            'os',
            '',
            item
        )
        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    def test_integration_expand_attr_map_item_sub_module(self):
        item = 'os.path'
        expect = _AttrMapping(
            'path',
            'os.path',
            '',
            item
        )
        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    def test_integration_expand_attr_map_item_module_attr(self):
        item = 'os.path:dirname'
        expect = _AttrMapping(
            'dirname',
            'os.path',
            'dirname',
            item
        )

        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    def test_integration_expand_attr_map_item_alias(self):
        item = 'os, _os'
        expect = _AttrMapping(
            '_os',
            'os',
            '',
            item
        )

        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    def test_integration_expand_attr_map_item_sub_module_alias(self):
        item = 'os.path,_path'
        expect = _AttrMapping(
            '_path',
            'os.path',
            '',
            item
        )
        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    def test_integration_expand_attr_map_item_module_attr_alias(self):
        item = 'os.path:dirname,dname'
        expect = _AttrMapping(
            'dname',
            'os.path',
            'dirname',
            item
        )
        val = list(map(_expand_attr_map_item, (item,)))
        self.assertEqual(val, [expect])

    # noinspection PyTypeChecker
    def test_integration_expand_attr_map_item_not_string_error(self):
        msg = "name=1"
        with self.assertRaises(AttributeError, msg=msg):
            list(map(_expand_attr_map_item, (1, )))
