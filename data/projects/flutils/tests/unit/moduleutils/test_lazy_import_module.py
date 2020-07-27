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

from flutils.moduleutils import lazy_import_module


class TestOne(unittest.TestCase):

    def setUp(self):
        # Mock isinstance
        patcher = patch(
            '__main__.isinstance',
            return_value=True
        )
        self.isinstance = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'importlib.util.resolve_name',
            return_value='foo'
        )
        self.resolve_name = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'sys.modules',
            dict(bar=True)
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        spec = types.SimpleNamespace()
        spec.loader = types.SimpleNamespace()

        patcher = patch(
            'importlib.util.find_spec',
            return_value=spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

        lazy_loader = types.SimpleNamespace()
        lazy_loader.exec_module = MagicMock(return_value=None)
        patcher = patch(
            'flutils.moduleutils._LazyLoader',
            return_value=lazy_loader
        )
        self.lazy_loader = patcher.start()
        self.addCleanup(patcher.stop)

    def test_lazy_import_module(self):
        mod = lazy_import_module('foo')
        self.find_spec.assert_called_once_with('foo')
        self.lazy_loader.assert_called_once()

    def test_lazy_import_module_with_package(self):
        lazy_import_module('foo', package='bar')
        self.find_spec.assert_called_once_with('foo')
        self.lazy_loader.assert_called_once()


class TestTwo(unittest.TestCase):

    def setUp(self):
        # Mock isinstance
        patcher = patch(
            '__main__.isinstance',
            return_value=True
        )
        self.isinstance = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'importlib.util.resolve_name',
            return_value='foo'
        )
        self.resolve_name = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'sys.modules',
            dict(foo=True)
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        spec = types.SimpleNamespace()
        spec.loader = types.SimpleNamespace()

        patcher = patch(
            'importlib.util.find_spec',
            return_value=spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

        lazy_loader = types.SimpleNamespace()
        lazy_loader.exec_module = MagicMock(return_value=None)
        patcher = patch(
            'flutils.moduleutils._LazyLoader',
            return_value=lazy_loader
        )
        self.lazy_loader = patcher.start()
        self.addCleanup(patcher.stop)

    def test_lazy_import_module_already_loaded(self):
        _ = lazy_import_module('foo')
        self.find_spec.assert_not_called()
        self.lazy_loader.assert_not_called()


class TestThree(unittest.TestCase):

    def setUp(self):
        # Mock isinstance
        patcher = patch(
            '__main__.isinstance',
            return_value=True
        )
        self.isinstance = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'importlib.util.resolve_name',
            return_value='foo'
        )
        self.resolve_name = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'sys.modules',
            dict()
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'importlib.util.find_spec',
            return_value=None
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

    def test_lazy_import_module_no_spec(self):
        with self.assertRaises(ImportError):
            lazy_import_module('foo')
        self.find_spec.assert_called_once()


class TestFour(unittest.TestCase):

    def setUp(self):
        # Mock isinstance
        patcher = patch(
            '__main__.isinstance',
            return_value=True
        )
        self.isinstance = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'importlib.util.resolve_name',
            return_value='foo'
        )
        self.resolve_name = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch(
            'sys.modules',
            dict(bar=True)
        )
        self.modules = patcher.start()
        self.addCleanup(patcher.stop)

        spec = types.SimpleNamespace()
        spec.loader = types.SimpleNamespace()
        spec.loader.create_module = MagicMock(
            return_value=types.SimpleNamespace()
        )

        patcher = patch(
            'importlib.util.find_spec',
            return_value=spec
        )
        self.find_spec = patcher.start()
        self.addCleanup(patcher.stop)

        lazy_loader = types.SimpleNamespace()
        lazy_loader.create_module = MagicMock(return_value=None)
        lazy_loader.exec_module = MagicMock(return_value=None)
        patcher = patch(
            'flutils.moduleutils._LazyLoader',
            return_value=lazy_loader
        )
        self.lazy_loader = patcher.start()
        self.addCleanup(patcher.stop)

    def test_lazy_import_module(self):
        _ = lazy_import_module('foo')
        self.find_spec.assert_called_once_with('foo')
        self.lazy_loader.assert_called_once()

    def test_lazy_import_module_with_package(self):
        lazy_import_module('foo', package='bar')
        self.find_spec.assert_called_once_with('foo')
        self.lazy_loader.assert_called_once()
