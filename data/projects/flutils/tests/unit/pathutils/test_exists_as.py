import unittest
from unittest.mock import patch

from flutils.pathutils import exists_as

from ..mocks.pathlib import PosixPathMock


class TestExistsAsDirectory(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/directory',
            is_dir=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_directory(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'directory')


class TestExistsAsFile(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/file',
            is_file=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_file(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'file')


class TestExistsAsBlockDevice(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/block_device',
            is_block_device=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_block_device(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'block device')


class TestExistsAsCharDevice(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/char_device',
            is_char_device=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_char_device(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'char device')


class TestExistsAsFifo(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/fifo',
            is_fifo=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_fifo(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'FIFO')


class TestExistsAsSocket(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock(
            '/home/test_user/socket',
            is_socket=True
        )
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_socket(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, 'socket')


class TestExistsAsEmpty(unittest.TestCase):

    def setUp(self):

        self.path = PosixPathMock('/home/test_user/empty')
        # Patch normalize_path() to return self.path
        patcher = patch(
            'flutils.pathutils.normalize_path',
            return_value=self.path
        )
        self.normalize_path = patcher.start()
        self.addCleanup(patcher.stop)

    def test_exists_as_socket(self):
        path_type = exists_as(self.path.as_posix())
        self.normalize_path.assert_called_with(self.path.as_posix())
        self.assertEqual(path_type, '')
