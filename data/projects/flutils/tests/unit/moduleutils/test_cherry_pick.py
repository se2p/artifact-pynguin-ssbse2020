import keyword
import types
import unittest
from importlib.machinery import ModuleSpec
from unittest.mock import (
    MagicMock,
    call,
    patch,
    sentinel,
)

from flutils.moduleutils import cherry_pick

from .base import CherryPickingMixin


class TestOne(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.namespace = dict()
        self.namespace['__name__'] = 'testmod'
        self.namespace['__file__'] = '/home/test_user/tmp/flutils/__init__.py'
        self.namespace['__path__'] = ['/home/test_user/tmp/flutils']
        self.namespace['__attr_map__'] = self.attr_map
        self.namespace['__additional_attrs__'] = self.additional_attrs

        self.spec = ModuleSpec(
            'testmod',
            sentinel.loader,
            loader_state=dict(
                attr_map=self.attr_map,
                addtl_attrs=self.additional_attrs
            )
        )

        patcher = patch(
            'flutils.moduleutils.importlib.util.find_spec',
            return_value=self.spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils._CherryPickFinder.add',
            return_value=None
        )
        self.add = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.sys.modules',
            dict(testmod=sentinel.testmod)
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.importlib.reload',
            return_value=None
        )
        self.reload = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.importlib.import_module',
            return_value=sentinel.new_testmod
        )
        self.import_module = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick(self):
        cherry_pick(self.namespace)
        kwargs = dict()
        kwargs['__loader__'] = sentinel.loader
        kwargs['__path__'] = self.namespace['__path__']
        kwargs['__file__'] = self.namespace['__file__']
        kwargs.update(self.additional_attrs)

        self.add.assert_called_once_with(
            'testmod',
            self.namespace['__file__'],
            self.namespace['__path__'],
            self.attr_map,
            **kwargs
        )

        self.reload.assert_called_once_with(sentinel.testmod)
        self.import_module.assert_not_called()

    def test_cherry_pick_empty_additional_attrs(self):
        namespace = self.namespace.copy()
        del namespace['__additional_attrs__']
        cherry_pick(namespace)
        kwargs = dict()
        kwargs['__loader__'] = sentinel.loader
        kwargs['__path__'] = self.namespace['__path__']
        kwargs['__file__'] = self.namespace['__file__']

        self.add.assert_called_once_with(
            'testmod',
            self.namespace['__file__'],
            self.namespace['__path__'],
            self.attr_map,
            **kwargs
        )

        self.reload.assert_called_once_with(sentinel.testmod)
        self.import_module.assert_not_called()

    def test_cherry_pick_attr_map_error_wrong_type(self):
        namespace = self.namespace.copy()
        namespace['__attr_map__'] = list(namespace['__attr_map__'])
        self.assertRaises(ImportError, cherry_pick, namespace)

    def test_cherry_pick_attr_map_error_empty_tuple(self):
        namespace = self.namespace.copy()
        namespace['__attr_map__'] = tuple()
        self.assertRaises(ImportError, cherry_pick, namespace)

    def test_cherry_pick_attr_map_error_not_defined(self):
        namespace = self.namespace.copy()
        del namespace['__attr_map__']
        self.assertRaises(ImportError, cherry_pick, namespace)

    def test_cherry_pick_additional_attr_error(self):
        namespace = self.namespace.copy()
        namespace['__additional_attrs__'] = tuple()
        self.assertRaises(ImportError, cherry_pick, namespace)


class TestTwo(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.namespace = dict()
        self.namespace['__name__'] = 'testmod'
        self.namespace['__file__'] = '/home/test_user/tmp/flutils/__init__.py'
        self.namespace['__path__'] = ['/home/test_user/tmp/flutils']
        self.namespace['__attr_map__'] = self.attr_map
        self.namespace['__additional_attrs__'] = self.additional_attrs

        self.spec = ModuleSpec(
            'testmod',
            sentinel.loader,
            loader_state=dict(
                attr_map=self.attr_map,
                addtl_attrs=self.additional_attrs
            )
        )

        patcher = patch(
            'flutils.moduleutils.importlib.util.find_spec',
            return_value=self.spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils._CherryPickFinder.add',
            return_value=None
        )
        self.add = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.sys.modules',
            dict()
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.importlib.reload',
            return_value=None
        )
        self.reload = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'flutils.moduleutils.importlib.import_module',
            return_value=sentinel.new_testmod
        )
        self.import_module = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick_import_module(self):
        cherry_pick(self.namespace)
        kwargs = dict()
        kwargs['__loader__'] = sentinel.loader
        kwargs['__path__'] = self.namespace['__path__']
        kwargs['__file__'] = self.namespace['__file__']
        kwargs.update(self.additional_attrs)

        self.add.assert_called_once_with(
            'testmod',
            self.namespace['__file__'],
            self.namespace['__path__'],
            self.attr_map,
            **kwargs
        )

        self.reload.assert_not_called()
        self.import_module.assert_called_once_with('testmod')


class TestThree(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.namespace = dict()
        self.namespace['__name__'] = 'testmod'
        self.namespace['__file__'] = '/home/test_user/tmp/flutils/__init__.py'
        self.namespace['__path__'] = ['/home/test_user/tmp/flutils']
        self.namespace['__attr_map__'] = self.attr_map
        self.namespace['__additional_attrs__'] = self.additional_attrs

        self.spec = ModuleSpec(
            'testmod',
            sentinel.loader,
            loader_state=dict(
                attr_map=self.attr_map,
                addtl_attrs=self.additional_attrs
            )
        )

        patcher = patch(
            'flutils.moduleutils.importlib.util.find_spec',
            return_value=None
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick_find_spec_raises(self):
        with self.assertRaises(ImportError):
            cherry_pick(self.namespace)


class TestFour(unittest.TestCase, CherryPickingMixin):

    def setUp(self):

        self.namespace = dict()
        self.namespace['__name__'] = 'testmod'
        self.namespace['__file__'] = '/home/test_user/tmp/flutils/__init__.py'
        self.namespace['__path__'] = ['/home/test_user/tmp/flutils']
        self.namespace['__attr_map__'] = self.attr_map
        self.namespace['__additional_attrs__'] = {
            'a': 'foo',
            22: 'bar'
        }
        self.spec = ModuleSpec(
            'testmod',
            sentinel.loader,
            loader_state=dict(
                attr_map=self.attr_map,
                addtl_attrs=self.additional_attrs
            )
        )

        patcher = patch(
            'flutils.moduleutils.importlib.util.find_spec',
            return_value=self.spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cherry_pick_additional_attrs_key_raises(self):
        with self.assertRaises(ImportError):
            cherry_pick(self.namespace)
