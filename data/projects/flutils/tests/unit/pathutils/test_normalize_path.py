import sys
import unittest
from unittest.mock import patch

from flutils.pathutils import normalize_path

from ..mocks.pathlib import (
    Path,
    PosixPathMock,
)


class TestNormalizePath(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock('~/tmp/foo/../$TEST')

        # Mock pathlib.Path.expanduser
        patcher = patch('flutils.pathutils.Path', Path)
        self.path_func = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.expanduser
        patcher = patch(
            'flutils.pathutils.os.path.expanduser',
            return_value='/home/test_user/tmp/foo/../$TEST'
        )
        self.expanduser = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.expandvars
        patcher = patch(
            'flutils.pathutils.os.path.expandvars',
            return_value='/home/test_user/tmp/foo/../test'
        )
        self.expandvars = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.isabs
        patcher = patch(
            'flutils.pathutils.os.path.isabs',
            return_value=True
        )
        self.isabs = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.getcwd
        patcher = patch(
            'flutils.pathutils.os.getcwd',
            return_value='/home/test_user/tmp'
        )
        self.getcwd = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.join
        patcher = patch(
            'flutils.pathutils.os.path.join',
            return_value=None
        )
        self.join = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.normpath
        patcher = patch(
            'flutils.pathutils.os.path.normpath',
            return_value='/home/test_user/tmp/test'
        )
        self.normpath = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.normcase
        patcher = patch(
            'flutils.pathutils.os.path.normcase',
            return_value='/home/test_user/tmp/test'
        )
        self.normcase = patcher.start()
        self.addCleanup(patcher.stop)

    def test_normalize_path(self):
        path = normalize_path('~/tmp/foo/../$TEST')
        self.expanduser.assert_called_with('~/tmp/foo/../$TEST')
        self.expandvars.assert_called_with('/home/test_user/tmp/foo/../$TEST')
        self.isabs.assert_called_once()
        self.getcwd.assert_not_called()
        self.join.assert_not_called()
        self.normpath.assert_called_with('/home/test_user/tmp/foo/../test')
        self.assertEqual(path.as_posix(), '/home/test_user/tmp/test')

    def test_normalize_path_bytes(self):
        path = normalize_path(
            '~/tmp/foo/../$TEST'.encode(sys.getfilesystemencoding())
        )
        self.assertEqual(path.as_posix(), '/home/test_user/tmp/test')

    def test_normalize_path_posix_path(self):
        path = normalize_path(self.path)
        self.assertEqual(path.as_posix(), '/home/test_user/tmp/test')


class TestNormalizePathCwd(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock('foo/../$TEST')

        # Mock pathlib.Path.expanduser
        patcher = patch('flutils.pathutils.Path', Path)
        self.path_func = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.expanduser
        patcher = patch(
            'flutils.pathutils.os.path.expanduser',
            return_value='foo/../$TEST'
        )
        self.expanduser = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.expandvars
        patcher = patch(
            'flutils.pathutils.os.path.expandvars',
            return_value='foo/../test'
        )
        self.expandvars = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.isabs
        patcher = patch(
            'flutils.pathutils.os.path.isabs',
            return_value=False
        )
        self.isabs = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.getcwd
        patcher = patch(
            'flutils.pathutils.os.getcwd',
            return_value='/home/test_user/tmp'
        )
        self.getcwd = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.join
        patcher = patch(
            'flutils.pathutils.os.path.join',
            return_value='/home/test_user/tmp/foo/../test'
        )
        self.join = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.normpath
        patcher = patch(
            'flutils.pathutils.os.path.normpath',
            return_value='/home/test_user/tmp/test'
        )
        self.normpath = patcher.start()
        self.addCleanup(patcher.stop)

        # Mock os.path.normcase
        patcher = patch(
            'flutils.pathutils.os.path.normcase',
            return_value='/home/test_user/tmp/test'
        )
        self.normcase = patcher.start()
        self.addCleanup(patcher.stop)

    def test_normalize_path_cwd(self):
        path = normalize_path('foo/../$TEST')
        self.expanduser.assert_called_with('foo/../$TEST')
        self.expandvars.assert_called_with('foo/../$TEST')
        self.isabs.assert_called_once_with('foo/../test')
        self.getcwd.assert_called_once()
        self.join.assert_called_once_with('/home/test_user/tmp', 'foo/../test')
        self.normpath.assert_called_with('/home/test_user/tmp/foo/../test')
        self.assertEqual(path.as_posix(), '/home/test_user/tmp/test')
