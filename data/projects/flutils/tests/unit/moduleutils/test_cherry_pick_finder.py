import keyword
import types
import unittest
from importlib.machinery import ModuleSpec
from unittest.mock import (
    MagicMock,
    call,
    patch,
)

from flutils.moduleutils import _CherryPickFinder

from .base import CherryPickingMixin


class TestOne(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.meta_path = list()
        patcher = patch(
            'flutils.moduleutils.sys.meta_path',
            self.meta_path
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick_finder_load(self):
        _CherryPickFinder.load()
        self.assertEqual(len(self.meta_path), 1)
        self.assertTrue(isinstance(self.meta_path[0], _CherryPickFinder))

    def test_cherry_pick_finder_add(self):
        fullname = 'testobj'
        _CherryPickFinder.add(
            fullname,
            '__init__',
            'apath',
            self.attr_map,
            **self.additional_attrs
        )
        finder = self.meta_path[0]
        self.assertEqual('testobj', finder._cache[fullname]['fullname'])
        self.assertEqual('__init__', finder._cache[fullname]['origin'])
        self.assertEqual('apath', finder._cache[fullname]['path'])
        self.assertEqual(
            self.attr_map,
            finder._cache[fullname]['attr_map']
        )
        self.assertEqual(
            self.additional_attrs,
            finder._cache[fullname]['addtl_attrs']
        )

    def test_cherry_pick_finder_find_spec(self):
        fullname = 'testobj'
        _CherryPickFinder.add(
            fullname,
            '__init__',
            'apath',
            self.attr_map,
            **self.additional_attrs
        )
        finder = self.meta_path[0]
        spec = finder.find_spec(fullname, 'unusedpath')
        self.assertEqual(fullname, spec.name)
        loader_state = spec.loader_state
        self.assertEqual('testobj', loader_state['fullname'])
        self.assertEqual('__init__', loader_state['origin'])
        self.assertEqual('apath', loader_state['path'])


class TestTwo(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.meta_path = [_CherryPickFinder()]
        patcher = patch(
            'flutils.moduleutils.sys.meta_path',
            self.meta_path
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick_finder_repr(self):
        obj = _CherryPickFinder.load()
        repr(obj)
