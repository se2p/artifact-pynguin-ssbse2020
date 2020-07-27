import keyword
import types
import unittest
from unittest.mock import (
    MagicMock,
    call,
    patch,
)

from flutils.moduleutils import (
    _CHERRY_PICK,
    _CherryPickingModule,
)

from .base import CherryPickingMixin


class Test(unittest.TestCase, CherryPickingMixin):

    # noinspection PyUnresolvedReferences
    def setUp(self):

        # Mock out a couple of modules
        self.foomod = types.ModuleType('foomod')
        self.foomod.foo = MagicMock(return_value='foo')

        self.barmod = types.ModuleType('barmod')
        self.barmod.bar = MagicMock(return_value='bar')

        patcher = patch(
            'flutils.moduleutils.importlib.import_module',
            side_effect=[self.foomod, self.barmod]
        )
        self.import_module = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_picking_module_import_module(self):
        mod = types.ModuleType('testmod')
        mod.__cherry_pick_map__ = self.cherry_pick_map
        mod.foomod = _CHERRY_PICK
        mod.bar = _CHERRY_PICK
        mod.__class__ = _CherryPickingModule

        getattr(mod, 'foomod')
        getattr(mod, 'bar')
        getattr(mod, 'bar')
        self.import_module.assert_has_calls([call('foomod'), call('barmod')])
        self.assertEqual(self.import_module.call_count, 2)

    def test_cherry_picking_module_attrs(self):
        mod = types.ModuleType('testmod')
        mod.__cherry_pick_map__ = self.cherry_pick_map
        mod.foomod = _CHERRY_PICK
        mod.bar = _CHERRY_PICK
        mod.__class__ = _CherryPickingModule

        foo_val = mod.foomod.foo('foo test')
        bar_val = mod.bar('bar_test')
        self.assertEqual(foo_val, 'foo')
        self.assertEqual(bar_val, 'bar')
        self.import_module.assert_has_calls([call('foomod'), call('barmod')])
        self.assertEqual(self.import_module.call_count, 2)
        mod.foomod.foo.assert_called_with('foo test')
        mod.bar.assert_called_with('bar_test')
        self.assertRaises(AttributeError, getattr, mod, 'barmod')
