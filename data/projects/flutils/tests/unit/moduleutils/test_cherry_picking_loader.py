import keyword
import types
import unittest
from importlib.machinery import ModuleSpec
from unittest.mock import (
    MagicMock,
    call,
    patch,
)

from flutils.moduleutils import (
    _CHERRY_PICK,
    _CherryPickingLoader,
)

from .base import CherryPickingMixin


class Test(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        patcher = patch(
            'flutils.moduleutils._parse_attr_map',
            return_value=self.cherry_pick_map
        )
        self.parse_attr_map = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils._CherryPickingModule',
            types.ModuleType
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        self.spec = ModuleSpec(
            'testmod',
            MagicMock(),
            loader_state=dict(
                attr_map=self.attr_map,
                addtl_attrs=self.additional_attrs
            )
        )

    def test_cherry_picking_loader_create_module(self):
        loader = _CherryPickingLoader()
        module = loader.create_module(self.spec)
        attr_map = module.__spec__.loader_state.get('attr_map')
        addtl_attrs = module.__spec__.loader_state.get('addtl_attrs')
        self.assertEqual(attr_map, self.attr_map)
        self.assertEqual(addtl_attrs, self.additional_attrs)

    def test_cherry_picking_loader_exec_module(self):
        loader = _CherryPickingLoader()
        module = loader.create_module(self.spec)
        loader.exec_module(module)
        self.parse_attr_map.assert_called_with(
            self.attr_map,
            self.spec.name
        )
        for key in self.cherry_pick_map.identifiers.keys():
            expect = getattr(module, key)
            self.assertEqual(expect, _CHERRY_PICK)

        for key, expect in self.additional_attrs.items():
            val = getattr(module, key)
            self.assertEqual(expect, val)

        self.assertEqual(self.all_value, module.__all__)
