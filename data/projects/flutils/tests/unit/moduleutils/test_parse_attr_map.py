import keyword
import unittest
from unittest.mock import patch

from flutils.moduleutils import (
    CherryPickError,
    _AttrMapping,
    _parse_attr_map,
)


class TestOne(unittest.TestCase):

    def setUp(self):
        self.return_value = [
            _AttrMapping(
                'dname',
                'os.path',
                'dirname',
                'os.path:dirname,dname'
            ),
            _AttrMapping(
                'basename',
                'os.path',
                'basename',
                'os.path:basename',
            )
        ]
        self.attr_map = tuple([x.item for x in self.return_value])
        patcher = patch(
            'flutils.moduleutils._expand_attr_map',
            return_value=self.return_value
        )
        self._expand_attr_map = patcher.start()
        self.addCleanup(patcher.stop)

    def test_parse_attr_map(self):
        res = _parse_attr_map(self.attr_map, 'foo')
        self._expand_attr_map.assert_called_once_with(self.attr_map)
        expect = {
            'os.path': self.return_value
        }
        self.assertEqual(res.modules, expect)
        expect = dict(
            dname='os.path',
            basename='os.path'
        )
        self.assertEqual(res.identifiers, expect)

    def test_parse_attr_map_not_tuple_error(self):
        self.assertRaises(
            CherryPickError,
            _parse_attr_map,
            list(self.attr_map),
            'foo'
        )


class TestTwo(unittest.TestCase):

    def setUp(self):
        self.return_value = [
            _AttrMapping(
                'dname',
                'os.path',
                'dirname',
                'os.path:dirname,dname',
            ),
            _AttrMapping(
                'dname',
                'os.path',
                'basename',
                'os.path:basename,dname',
            )
        ]
        self.attr_map = tuple([x.item for x in self.return_value])
        patcher = patch(
            'flutils.moduleutils._expand_attr_map',
            return_value=self.return_value
        )
        self._expand_attr_map = patcher.start()
        self.addCleanup(patcher.stop)

    def test_parse_attr_map_duplicate(self):
        with self.assertRaises(CherryPickError):
            _parse_attr_map(self.attr_map, 'foo')
        self._expand_attr_map.assert_called_once_with(self.attr_map)


class TestThree(unittest.TestCase):

    def setUp(self):
        self.attr_map = tuple(['os.0path'])
        patcher = patch(
            'flutils.moduleutils._expand_attr_map',
            side_effect=AttributeError('test')
        )
        self._expand_attr_map = patcher.start()
        self.addCleanup(patcher.stop)

    def test_parse_attr_map_duplicate(self):
        with self.assertRaises(CherryPickError):
            _parse_attr_map(self.attr_map, '0path')
        self._expand_attr_map.assert_called_once_with(self.attr_map)
